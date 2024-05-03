import time

import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='717e531da97c4449afa44c7ffbddf670',
                                               client_secret='9041247e4d5f4bf89032b58f75a1fdb7',
                                               redirect_uri='http://localhost:5000/callback',
                                               scope='user-read-currently-playing user-read-private user-follow-read '
                                                     'user-read-recently-played user-top-read user-library-read'))


def song_data(track_id):
    print(track_id)
    while True:
        try:
            track_info = sp.track(track_id)
            track_name = track_info['name']

            artists = track_info['artists']
            artist_name = None
            if artists:
                artist_name = artists[0]['name']

            images = track_info['album']['images']
            track_cover_url = None
            if images:
                track_cover_url = images[0]['url']

            return track_name, artist_name, track_cover_url
        except spotipy.SpotifyException as e:
            print(f"SpotifyException: {e}")


def playlist_cover(playlist_id):
    playlist_info = sp.playlist(playlist_id)
    images = playlist_info['images']
    cover_url = None
    if images:
        cover_url = images[0]['url']

    return cover_url


def artist_data(artist_id):
    artist_info = sp.artist(artist_id)
    images = artist_info['images']
    cover_url = None
    if images:
        cover_url = images[0]['url']

    return cover_url


def album_cover(album_id):
    album_info = sp.album(album_id)
    images = album_info['images']
    cover_url = None
    if images:
        cover_url = images[0]['url']

    return cover_url
