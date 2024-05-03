import os
import threading
from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import requests

API_BASE_URL = 'https://api.spotify.com/v1/'
DATABASE_URL = 'sqlite:///spotify.data.db'

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_spotify_id = Column(String, unique=True)
    name = Column(String)
    image_url = Column(String)
    playlist = Column(JSON)
    top_artists = Column(JSON)
    top_tracks = Column(JSON)
    following = Column(JSON)
    currently_playing = Column(JSON)
    recently_played = Column(JSON)
    albums = Column(JSON)


Session = sessionmaker()

def testit(seconds, access_token):
    timer = threading.Event()
    while True:
        print(f"delay {seconds} seconds")
        timer.wait(seconds)
        get_user_info(access_token)

def get_user_info(access_token):
    if not access_token:
        print("error")
        return {'error': 'Access token not found'}

    engine = create_engine(DATABASE_URL)
    Session.configure(bind=engine)

    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    response = requests.get(API_BASE_URL + 'me', headers=headers)
    print(response)
    if response.status_code == 200:
        Base.metadata.create_all(engine)

        user_info = response.json()
        user_spotify_id = user_info.get('id')
        user_name = user_info.get('display_name', 'Unknown')
        user_image_url = user_info.get('images', [{}])[0].get('url', '')

        top_artists_response = requests.get(API_BASE_URL + 'me/top/artists', headers=headers)
        print(top_artists_response)
        if top_artists_response.status_code == 200:
            top_artists_data = top_artists_response.json().get('items', [])
            top_artists = [{'name': top_artist.get('name', 'Unknown'), 'id': top_artist.get('id')} for top_artist in
                           top_artists_data]
        else:
            top_artists = []

        following_response = requests.get(API_BASE_URL + 'me/following?type=artist', headers=headers)
        if following_response.status_code == 200:
            following_data = following_response.json().get('artists', {}).get('items', [])
            following = [{'name': artist.get('name', 'Unknown'), 'id': artist.get('id')} for artist in following_data]
        else:
            following = []

        currently_playing_response = requests.get(API_BASE_URL + 'me/player/currently-playing', headers=headers)
        if currently_playing_response.status_code == 200:
            currently_playing_data = currently_playing_response.json().get('item')
            if currently_playing_data:
                currently_playing = {'name': currently_playing_data.get('name', 'Unknown'),
                                     'id': currently_playing_data.get('id')}
            else:
                print("No currently playing track.")
                currently_playing = {'name': 'Unknown', 'id': None}
        else:
            print(f"currently playing: {currently_playing_response.text}")
            currently_playing = {'name': 'Unknown', 'id': None}

        recently_played_response = requests.get(API_BASE_URL + 'me/player/recently-played', headers=headers)
        if recently_played_response.status_code == 200:
            recently_played_data = recently_played_response.json().get('items', [])
            recently_played = [
                {'name': track.get('track', {}).get('name', 'Unknown'), 'id': track.get('track', {}).get('id')} for
                track in recently_played_data]
        else:
            print(f"recently playing: {recently_played_response.text}")
            recently_played = []

        albums_response = requests.get(API_BASE_URL + 'me/albums', headers=headers)
        if albums_response.status_code == 200:
            albums_data = albums_response.json().get('items', [])
            albums = [{'name': album.get('album', {}).get('name', 'Unknown'), 'id': album.get('album', {}).get('id')}
                      for album in albums_data]
        else:
            albums = []

        playlists_response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
        if playlists_response.status_code == 200:
            playlists_data = playlists_response.json().get('items', [])
            playlists = [{'name': playlist.get('name', 'Unknown'), 'id': playlist.get('id')} for playlist in
                         playlists_data]
        else:
            playlists = []

        top_tracks_response = requests.get(API_BASE_URL + 'me/top/tracks', headers=headers)
        if top_tracks_response.status_code == 200:
            top_tracks_data = top_tracks_response.json().get('items', [])
            top_tracks = [{'name': top_track.get('name', 'Unknown'), 'id': top_track.get('id')} for top_track in
                          top_tracks_data]
        else:
            top_tracks = []

        db_session = Session()
        existing_user = db_session.query(User).filter_by(user_spotify_id=user_spotify_id).first()
        if existing_user:
            existing_user.image_url = user_image_url
            existing_user.playlist = playlists
            existing_user.top_artists = top_artists
            existing_user.top_tracks = top_tracks
            existing_user.following = following
            existing_user.currently_playing = currently_playing
            existing_user.recently_played = recently_played
            existing_user.albums = albums
        else:
            user = User(user_spotify_id=user_spotify_id, name=user_name, image_url=user_image_url, playlist=playlists,
                        top_artists=top_artists, top_tracks=top_tracks, following=following,
                        currently_playing=currently_playing, recently_played=recently_played, albums=albums)
            db_session.add(user)
        db_session.commit()
        db_session.close()

        return {'name': user_name, 'image_url': user_image_url}
    else:
        return {"error": "Unable to fetch user information"}
