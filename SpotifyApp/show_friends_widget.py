from functools import partial

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
import sqlite3
from my_wigets import wait_for_file



class ShowFriendsScreen(Screen):
    def __init__(self, **kwargs):
        super(ShowFriendsScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.size_hint_y = None
#        self.view_friends()

    def get_user_friends_from_file(self):
        conn = sqlite3.connect('spotify.users.db')
        conn2 = sqlite3.connect('spotify.data.db')
        cursor = conn.cursor()
        cursor2 = conn2.cursor()
        cursor.execute('SELECT sender_spotify_id, user_spotify_id, name, image_url, friendship_status FROM friends')
        cursor2.execute('SELECT user_spotify_id FROM users')
        rows = cursor.fetchall()
        row = cursor2.fetchone()
        cursor.close()
        cursor2.close()
        conn.close()
        conn2.close()
        return rows, row

    def view_friends(self):
        friends_waiting = []
        friends_accepted = []
        rows, row = self.get_user_friends_from_file()

        for ro in row:
            spotify_id = ro
            for row in rows:
                sender_spotify_id, user_spotify_id, name, image_url, friendship_status = row

                if spotify_id == sender_spotify_id:
                    friend_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=100)
                    profile_image = AsyncImage(source=image_url, size_hint=(None, None), size=(70, 70))
                    friend_layout.add_widget(profile_image)
                    name_label = Label(text=name, size_hint_y=None, height=40, font_size='15sp')
                    friend_layout.add_widget(name_label)
                    info_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
                    if friendship_status == 'waiting...':
                        accept = Button(text="Accept", size_hint=(None, None), size=(150, 50))
                        accept.bind(on_press=lambda btn, sid=sender_spotify_id: self.confirm_friend(btn, sid))
                        reject = Button(text="Reject", size_hint=(None, None), size=(150, 50))
                        reject.bind(on_press=lambda btn, sid=sender_spotify_id: self.reject_friend(btn, sid))
                        info_layout.add_widget(accept)
                        info_layout.add_widget(reject)
                        friends_waiting.append((friend_layout, info_layout))
                    elif friendship_status == 'accepted':
                        show = Button(text="Show", size_hint=(None, None), size=(150, 50))
                        show.bind(on_press=partial(self.show_info, user_id=user_spotify_id))
                        info_layout.add_widget(show)
                        friends_accepted.append((friend_layout, info_layout))

        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for friend_layout, info_layout in friends_accepted:
            friend_layout.add_widget(info_layout)
            layout.add_widget(friend_layout)

        for friend_layout, info_layout in friends_waiting:
            friend_layout.add_widget(info_layout)
            layout.add_widget(friend_layout)

        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)
        self.clear_widgets()
        self.add_widget(scrollview)

    def confirm_friend(self, button, sender_spotify_id):
        conn = sqlite3.connect('spotify.users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE friends SET friendship_status=? WHERE sender_spotify_id=?',
                       ('accepted', sender_spotify_id))
        conn.commit()
        conn.close()
        self.view_friends()

    def reject_friend(self, button, sender_spotify_id):
        conn = sqlite3.connect('spotify.users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM friends WHERE sender_spotify_id=?', (sender_spotify_id,))
        conn.commit()
        conn.close()
        self.view_friends()

    def show_user(self, button, sender_spotify_id):
        self.view_friends()

    def show_info(self, instance, user_id):
        widget_screen = self.manager.get_screen('widget')
        widget_screen.view(instance, user_id)
        self.manager.current = 'widget'


