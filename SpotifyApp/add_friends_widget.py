import sqlite3
from functools import partial

from kivy.uix.label import Label

from GUI import StyledButton, ColoredBoxLayout
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from friends_requests import friends_info

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.text = "Search..."
        self.background_normal = ''
        self.background_color = (0.2, 0.2, 0.2, 1)  # ciemnoszary kolor tła
        self.border_radius = [dp(10)]  # zaokrąglenie rogów
        self.border_width = (2, 2, 2, 2)  # grubość obramowania
        self.border_color = (0.5, 0.5, 0.5, 1)  # kolor obramowania
        self.padding = [dp(10), dp(5)]  # dodatkowe wypełnienie
        self.bind(focus=self.on_focus)

    def on_focus(self, instance, value):
        if value:
            if self.text == "Search...":
                self.text = ""
        else:
            if self.text == "":
                self.text = "Search..."


class AddFriendsScreen(Screen):
    def __init__(self, **kwargs):
        super(AddFriendsScreen, self).__init__(**kwargs)
        self.search_results_label = None
        self.search_input = None
        self.suggestions = DropDown()
        self.add_widget(self.build())

    def build(self):
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        button = StyledButton(text='Back', size_hint=(None, None), size=(100, 100),
                                  pos_hint={'center_x': 0.1, 'center_y': 0.1})
        self.add_widget(button)
        button.bind(on_press=self.go_back)
        self.suggestions = DropDown()
        self.text_input = StyledTextInput(size_hint_y=None, height=40)
        self.text_input.bind(text=partial(self.show_suggestions))
        main_layout.add_widget(self.text_input)

        self.suggestions_placeholder = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.suggestions_placeholder)

        return main_layout

    def show_suggestions(self, instance, value):
        self.suggestions.clear_widgets()
        suggestions, images = self.get_suggestions(value)

        for suggestion, image in zip(suggestions, images):
            suggestion_layout = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            suggestion_layout.add_widget(image)

            btn = Label(text=suggestion['name'], size_hint_x=1, size_hint_y=1, size=('150dp', '70dp'), )
            btn.bind(on_release=lambda btn: self.select_suggestion(btn))
            suggestion_layout.add_widget(btn)

            add_btn = Button(text='+', bold=True, size_hint=(None, None), size=('50dp', '50dp'),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}) # Ustawienie rozmiaru na 50x50 pikseli
            add_btn.background_color = (0.1, 0.1, 0.1, 0.2)
            add_btn.bind(on_press=lambda instance: self.send_friend_request(suggestion['name']))
            suggestion_layout.add_widget(add_btn)

            self.suggestions.add_widget(suggestion_layout)

        if not self.suggestions.parent:
            self.suggestions.open(instance)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def get_suggestions(self, filter_text):
        all_users = download_user_data()
        suggestions = []
        images = []

        for user in all_users:
            if filter_text.lower() in user['name'].lower():
                suggestions.append(user)
                image_url = user['image_url']
                image = AsyncImage(source=image_url, size_hint=(None, None), size=('70dp', '70dp'))
                images.append(image)

        return suggestions, images

    def select_suggestion(self, btn):
        self.text_input.text = btn.text
        self.suggestions.dismiss()

    def send_friend_request(self, username):
        friend = friends_info(username)

    def go_back(self, instance):
        self.parent.current = 'main'


def download_user_data():
    conn = sqlite3.connect('spotify.users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, image_url FROM spotify_users')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    data = [{'name': row[0], 'image_url': row[1]} for row in rows]
    return data


class MyApp(App):
    def build(self):
        return AddFriendsScreen()


if __name__ == '__main__':
    MyApp().run()
