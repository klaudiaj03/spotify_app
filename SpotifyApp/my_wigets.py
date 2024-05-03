import json
import time
import os.path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
import sqlite3

from kivy.uix.scrollview import ScrollView

from download_info import song_data, playlist_cover, artist_data, album_cover
from GUI import ColoredBoxLayout


def download_user_data():
    conn = sqlite3.connect('spotify.data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return rows


def currently_listening2():
    file = ".cache"
    if os.path.exists(file):
        os.remove(file)
    main_layout = BoxLayout(orientation='vertical', size_hint=(0.97, None), spacing=10)
    layout = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])

    # Funkcja do pobierania danych użytkownika
    def update_data(dt):
        layout.clear_widgets()  # Wyczyść istniejące widżety
        rows = download_user_data()  # Pobierz nowe dane użytkownika
        for row in rows:
            currently_playing = row[8]
            recently = row[9]
            title1 = currently_playing.split('"')[3]
            if not title1 == "Unknown":
                track_id1 = currently_playing.split('"')[7]
                print(track_id1)
                data = song_data(track_id1)
                print(data)
                track_name = data[0]
                track_artist = data[1]
                track_url = data[2]
                print(track_id1)
                print(title1)
            else:
                track_id = recently.split('"')[7]
                data = song_data(track_id)
                track_name = data[0]
                track_artist = data[1]
                track_url = data[2]
                print(track_url)
            box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            profile_image = AsyncImage(source=track_url, size_hint_x=None, size_hint_y=1, width=70)

            box.add_widget(profile_image)
            name_label = Label(text=f"{track_artist} ~{track_name}~", size_hint_x=1, size_hint_y=1, color=(0, 0, 0, 1),
                               bold=True)
            box.add_widget(name_label)
            if not title1 == "Unknown":
                clock_image = AsyncImage(source='icons8-audio-wave-unscreen.gif', size_hint_x=None, size_hint_y=1,
                                         width=50)
                box.add_widget(clock_image)
            if title1 == "Unknown":
                clock_image = AsyncImage(source='icons8-clock-100.png', size_hint_x=None, size_hint_y=1, width=50)
                box.add_widget(clock_image)
            layout.add_widget(box)

    # Harmonogramowanie aktualizacji danych co 5 sekund
    Clock.schedule_interval(update_data, 5)

    main_layout.add_widget(layout)
    main_layout.height = Window.height  # Przykładowa wysokość, dostosuj do swoich potrzeb
    main_layout = all_functions(main_layout)
    scroll_view = ScrollView(size_hint=(0.97, 0.7), do_scroll_x=True, bar_width='2dp', bar_color=[1, 0, 0, 1],
                             bar_inactive_color=[1, 0, 0, 1])
    scroll_view.add_widget(main_layout)
    return scroll_view



def all_functions(main_layout):
    top_tracks_label = Label(text=f"My top tracks: ", size_hint_x=0.2, size_hint_y=0.2, color=(1, 0, 0, 1), bold=True)
    top_tracks_layout = top_tracks()
    top_artists_label = Label(text=f"My top artists: ", size_hint_x=0.2, size_hint_y=0.2, color=(1, 0, 0, 1), bold=True)
    top_artists_layout = top_artists()
    followed_artists_label = Label(text=f"Followed artists: ", size_hint_x=0.2, size_hint_y=0.2, color=(1, 0, 0, 1),
                                  bold=True)
    saved_albums_label = Label(text=f"My saved albums: ", size_hint_x=0.2, size_hint_y=0.2, color=(1, 0, 0, 1),
                              bold=True)
    playlist_label = Label(text=f"My playlists: ", size_hint_x=0.2, size_hint_y=0.2, color=(1, 0, 0, 1), bold=True)
    following_layout = following()
    albums_layout = albums()
    playlist_layout = playlists()  # Create playlist_layout after the loop
    main_layout.add_widget(playlist_label)
    main_layout.add_widget(playlist_layout)  # Add playlist_layout to main_layout after adding layout
    main_layout.add_widget(followed_artists_label)
    main_layout.add_widget(following_layout)
    main_layout.add_widget(saved_albums_label)
    main_layout.add_widget(albums_layout)
    main_layout.add_widget(top_artists_label)
    main_layout.add_widget(top_artists_layout)
    main_layout.add_widget(top_tracks_label)
    main_layout.add_widget(top_tracks_layout)

    return main_layout


def playlists():
    box = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])
    box.bind(minimum_height=box.setter('height'))
    rows = download_user_data()
    for row in rows:
        playlists_json = row[4]
        playlists = json.loads(playlists_json)
        for playlist in playlists:
            title = playlist['name']
            ID = playlist['id']
            playlist_url = playlist_cover(ID)
            print(title)
            image = AsyncImage(source=playlist_url, size_hint_x=None, size_hint_y=1, width=70)
            label = Label(text=f"{title}", size_hint_x=1, size_hint_y=1, color=(0, 0, 0, 1), bold=True)
            playlist_box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            playlist_box.add_widget(image)
            playlist_box.add_widget(label)
            box.add_widget(playlist_box)
    scroll_view = ScrollView(size_hint=(0.97, None), bar_color=[1, 0, 0, 1], bar_inactive_color=[1, 0, 0, 1])
    scroll_view.add_widget(box)
    return scroll_view


def top_artists():
    box = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])
    box.bind(minimum_height=box.setter('height'))
    rows = download_user_data()
    for row in rows:
        top_artists_json = row[5]
        top_artists = json.loads(top_artists_json)
        for artist in top_artists:
            title = artist['name']
            ID = artist['id']
            url = artist_data(ID)
            print(title)
            image = AsyncImage(source=url, size_hint_x=None, size_hint_y=1, width=70)
            label = Label(text=f"{title}", size_hint_x=1, size_hint_y=1, color=(0, 0, 0, 1), bold=True)
            playlist_box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            playlist_box.add_widget(image)
            playlist_box.add_widget(label)
            box.add_widget(playlist_box)
    scroll_view = ScrollView(size_hint=(0.97, None), do_scroll_y=False, bar_color=[1, 0, 0, 1], bar_inactive_color=[1, 0, 0, 1])
    scroll_view.add_widget(box)
    return scroll_view


def top_tracks():
    box = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])
    box.bind(minimum_height=box.setter('height'))
    scroll_view = ScrollView(size_hint=(0.97, None))
    scroll_view.add_widget(box)
    rows = download_user_data()
    for row in rows:
        top_tracks_json = row[6]
        top_tracks = json.loads(top_tracks_json)
        for track in top_tracks:
            title = track['name']
            ID = track['id']
            data = song_data(ID)
            track_artist = data[1]
            track_url = data[2]
            image = AsyncImage(source=track_url, size_hint_x=None, size_hint_y=1, width=70)
            label = Label(text=f"{track_artist} ~{title}~", size_hint_x=1, size_hint_y=1,
                          color=(0, 0, 0, 1), bold=True)
            top_track_box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            top_track_box.add_widget(image)
            top_track_box.add_widget(label)
            box.add_widget(top_track_box)
    return scroll_view


def following():
    box = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])
    box.bind(minimum_height=box.setter('height'))
    scroll_view = ScrollView(size_hint=(0.97, None), bar_color=[1, 0, 0, 1], bar_inactive_color=[1, 0, 0, 1])
    scroll_view.add_widget(box)
    rows = download_user_data()
    for row in rows:
        following_json = row[7]
        following = json.loads(following_json)
        for follow in following:
            title = follow['name']
            ID = follow['id']
            url = artist_data(ID)
            image = AsyncImage(source=url, size_hint_x=None, size_hint_y=1, width=70)
            label = Label(text=f"{title}", size_hint_x=1, size_hint_y=1,
                          color=(0, 0, 0, 1), bold=True)
            top_track_box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            top_track_box.add_widget(image)
            top_track_box.add_widget(label)
            box.add_widget(top_track_box)
    return scroll_view


def albums():
    box = ColoredBoxLayout(color=(1, 1, 1, 1), orientation='vertical', size_hint=(1, None), padding=[10, 0, 10, 0])
    box.bind(minimum_height=box.setter('height'))
    scroll_view = ScrollView(size_hint=(0.97, None), bar_color=[1, 0, 0, 1], bar_inactive_color=[1, 0, 0, 1])
    scroll_view.add_widget(box)
    rows = download_user_data()
    for row in rows:
        albums_json = row[10]
        albums = json.loads(albums_json)
        for album in albums:
            title = album['name']
            ID = album['id']
            url = album_cover(ID)  # Use album_cover() to get the album cover URL
            print(title)
            image = AsyncImage(source=url, size_hint_x=None, size_hint_y=1, width=70)
            label = Label(text=f"{title}", size_hint_x=1, size_hint_y=1, color=(0, 0, 0, 1), bold=True)
            album_box = BoxLayout(orientation='horizontal', size_hint=(1, None), padding=[10, 0, 10, 0])
            album_box.add_widget(image)
            album_box.add_widget(label)
            box.add_widget(album_box)
    return scroll_view

def wait_for_file(file_path):
    while not os.path.exists(file_path) or os.path.getsize(file_path) < 13312:
        time.sleep(1)

class MyApp(App):
    def build(self):
        box_layout = currently_listening2()
        return box_layout


# Uruchom aplikację
if __name__ == '__main__':
    MyApp().run()
