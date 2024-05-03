import os
import sqlite3
import time
import webbrowser
from threading import Thread

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView

from SpotifyApp.friends_widget import WidgetScreen
from SpotifyApp.show_friends_widget import ShowFriendsScreen
from spotify_authorization import get_auth_url, run_flask_server
from add_friends_widget import AddFriendsScreen
from GUI import StyledButton
from color_palette import build
from my_wigets import currently_listening2


path = 'spotify.data.db'
if os.path.exists(path):
    os.remove(path)


class MainWidget(Screen):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.auth_button = StyledButton(text='Authorize Spotify', size_hint=(None, None), size=(500, 100),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.auth_button.bind(on_press=self.authorize_spotify)
        self.add_widget(self.auth_button)

    def authorize_spotify(self, instance):
        self.remove_widget(self.auth_button)
        spotify_auth_url = get_auth_url()
        webbrowser.open_new(spotify_auth_url)
        while not os.path.exists('spotify.data.db') or os.path.getsize('spotify.data.db') < 13312:
            time.sleep(1)
        self.second_screen()

    def second_screen(self):
        image = download_image_from_file()
        name = download_name_from_file()
        image.size_hint = (None, None)
        image.size = ('100dp', '80dp')
        image.border_radius = [50]
        name_label = Label(text=name, size_hint=(None, None), size=('150dp', '70dp'), )
        layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=('300dp', '70dp'),
                           pos_hint={'top': 1})
        layout.add_widget(name_label)
        layout.add_widget(image)
        self.add_widget(layout)
        content_layout = BoxLayout(orientation='horizontal', spacing=20)

        listening_button = StyledButton(text='My widget', size_hint=(None, None), size=(500, 100))
        listening_button.bind(on_press=self.on_press_my_widget_button)
        content_layout.add_widget(listening_button)

        add_friends_button = StyledButton(text='Add Friends', size_hint=(None, None), size=(500, 100))
        add_friends_button.bind(on_press=self.go_to_add_friends)
        content_layout.add_widget(add_friends_button)

        show_friends_button = StyledButton(text='My Friends', size_hint=(None, None), size=(500, 100))
        show_friends_button.bind(on_press=self.show_my_friends)
        content_layout.add_widget(show_friends_button)

        color = StyledButton(text='Choose Color', size_hint=(None, None), size=(500, 100))
        color.bind(on_press=self.color_button)
        content_layout.add_widget(color)

        show_friends_button = StyledButton(text='Log out', size_hint=(None, None), size=(500, 100))
        show_friends_button.bind(on_press=self.show_my_friends)
        content_layout.add_widget(show_friends_button)
        listening_layout = currently_listening2()
        self.add_widget(listening_layout)
        scrollview = ScrollView(size_hint=(None, None), size=(Window.width, 100), pos_hint={'top': 0.9})
        scrollview.add_widget(content_layout)
        self.add_widget(scrollview)


    def go_to_add_friends(self, instance):
        self.parent.current = 'build'

    def show_my_friends(self, instance):
        self.parent.current = 'show'

    def on_press_my_widget_button(self, instance):
        self.listening_layout = currently_listening2()
        self.remove_widget(self.color_layout)
        self.add_widget(self.listening_layout)

    def update_button(self, dt):
        self.remove_widget(self.listening_layout)
        self.listening_layout = currently_listening2()
        self.add_widget(self.listening_layout)

    def color_button(self, instance):
        #Clock.unschedule(self.event)
        self.remove_widget(self.listening_layout)
        self.color_layout = build()
        self.add_widget(self.color_layout)


def download_image_from_file():
    conn = sqlite3.connect('spotify.data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image_url FROM users')
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        first_image_url = row[0]
        image = AsyncImage(source=first_image_url, size_hint=(None, None), size=('50dp', '50dp'))
        return image
    else:
        return None


def download_name_from_file():
    conn = sqlite3.connect('spotify.data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM users')
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        name = row[0]
        return name
    else:
        return None


def if_user_is_logged():
    conn = sqlite3.connect('spotify.data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        return True
    cursor.close()
    conn.close()


def wait_for_file(file_path):
    while not os.path.exists(file_path) or os.path.getsize(file_path) < 13312:
        time.sleep(1)


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager(transition=FadeTransition())
        main_widget = MainWidget(name='main')
        add_friends_screen = AddFriendsScreen(name='build')
        show_friends_screen = ShowFriendsScreen(name='show')
        show_info = WidgetScreen(name='widget')
        screen_manager.add_widget(main_widget)
        screen_manager.add_widget(add_friends_screen)
        screen_manager.add_widget(show_friends_screen)
        screen_manager.add_widget(show_info)

        return screen_manager

def start_flask_server():
    run_flask_server()

if __name__ == '__main__':
    server_thread = Thread(target=start_flask_server)
    server_thread.daemon = True
    server_thread.start()

    MyApp().run()
