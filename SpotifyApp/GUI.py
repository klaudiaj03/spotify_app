from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp


class StyledButton(Button):
    background_normal = ''
    background_color = [0, 0, 0, 0]

    with open("C:/Users/Sprzetowo/PycharmProjects/spotifyWidgetApp/SpotifyApp/selected_color.txt", "r") as f:
        color_str = f.read().strip()
    color_list = [float(c) for c in color_str[1:-1].split(',')]

    border_color = ListProperty(color_list)
    font_size = dp(15)
    radius = [dp(25)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_graphics_pos, pos=self._update_graphics_pos)
        self.size_hint = (None, None)
        self.size = (dp(100), dp(50))

    def _update_graphics_pos(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

    def on_press(self):
        anim_press = Animation(size=(dp(120), dp(60)), duration=0.1)
        anim_press.bind(on_complete=self.on_release)
        anim_press.start(self)

    def on_release(self, *args):
        anim_release = Animation(size=(dp(100), dp(50)), duration=0.1)
        anim_release.start(self)


class ColoredBoxLayout(BoxLayout):

    def __init__(self, color, **kwargs):
        super(ColoredBoxLayout, self).__init__(**kwargs)
        with open("selected_color.txt", "r") as f:
            color_str = f.read().strip()
        self.border_color = [float(c) for c in color_str[1:-1].split(',')]
        with self.canvas.before:
            Color(*self.border_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            Color(0, 0, 0, 1)
            Line(rounded_rectangle=(instance.x, instance.y, instance.width, instance.height, 10), width=3.5)
