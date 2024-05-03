import os
import sqlite3
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

API_BASE_URL = 'https://api.spotify.com/v1/'
os.chdir('C:/Users/Sprzetowo/PycharmProjects/spotifyWidgetApp/SpotifyApp/')
DATABASE_URL = 'sqlite:///spotify.users.db'

Base = declarative_base()


class Users(Base):
    __tablename__ = 'friends'

    sender_spotify_id = Column(String, unique=True)
    id = Column(Integer, primary_key=True)
    user_spotify_id = Column(String, unique=True)
    name = Column(String)
    image_url = Column(String)
    friendship_status = Column(String)

def friends_info(username):
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine, checkfirst=True)  # Sprawdzenie czy tabela już istnieje, jeśli nie, utwórz ją
    Session = sessionmaker(bind=engine)

    conn = sqlite3.connect('spotify.users.db')
    conn2 = sqlite3.connect('spotify.data.db')
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    cursor.execute('SELECT user_spotify_id, name, image_url FROM spotify_users')
    cursor2.execute('SELECT user_spotify_id from users')

    rows = cursor.fetchall()
    rows2 = cursor2.fetchone()

    cursor.close()
    cursor2.close()
    conn.close()

    db_session = sessionmaker(bind=engine)()

    user_spotify_id2 = rows2[0]

    for row in rows:
        user_spotify_id, name, image_url = row

        if user_spotify_id2 == user_spotify_id:
            print("lol")
        else:
            user = Users(sender_spotify_id=user_spotify_id2, user_spotify_id=user_spotify_id, name=name,
                         image_url=image_url, friendship_status='waiting...')
            db_session.add(user)
            print("Dodano do bazy danych")

    db_session.commit()
    db_session.close()


