from kivy.uix.floatlayout import FloatLayout
from kivy.uix.colorpicker import ColorPicker

def build():
    layout = FloatLayout(size_hint=(0.5, 0.7))
    clr_picker = ColorPicker()
    clr_picker.bind(color=on_color)
    layout.add_widget(clr_picker)

    return layout

def on_color(instance, value):
    RGBA = [round(x, 2) for x in value]
    print(str(value))
    with open("selected_color.txt", "w") as f:
            f.write(format(str(value)))


