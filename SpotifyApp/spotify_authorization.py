import json
import os
import threading
from datetime import datetime

from flask import Flask, redirect, request, jsonify, url_for, session, render_template_string
import requests
import urllib.parse

from spotify_users import testitt
from spotify_api import testit

app = Flask(__name__)
app.secret_key = os.urandom(24)

client_id = "717e531da97c4449afa44c7ffbddf670"
client_secret = "9041247e4d5f4bf89032b58f75a1fdb7"
redirect_uri = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
token_file_path = 'token.txt'
last_refresh_time = datetime.now()
refresh_interval_seconds = 3600


def get_auth_url():
    scope = ('user-read-currently-playing user-read-private user-follow-read user-read-recently-played user-top-read '
             'user-library-read')
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


@app.route('/')
def index():
    if 'access_token' in session:
        friends = session.get('friends')
        if friends:
            return jsonify({"friends": friends})
        else:
            return jsonify({"error": "No friends found"})
    else:
        return redirect(url_for('login'))


@app.route('/login')
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)


def save_tokens_to_file(token_info):
    with open('tokens.json', 'w') as f:
        json.dump(token_info, f)


def load_tokens_from_file():
    with open('tokens.json', 'r') as f:
        return json.load(f)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        code = request.args['code']
        req_body = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        print(token_info)

        if 'access_token' in token_info and 'refresh_token' in token_info and 'expires_in' in token_info:
            session['access_token'] = token_info['access_token']
            session['refresh_token'] = token_info['refresh_token']
            session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
            save_tokens_to_file(token_info)
            print(token_info)
            new_token = refresh_token()
            print(new_token)
            access_token = session['access_token']
            threading.Thread(target=testit, args=(5, access_token)).start()
            access_token = session['access_token']
            threading.Thread(target=testitt, args=(5, access_token)).start()

            return render_template_string("""
                            <html>
                                <head>
                                    <script>
                                        setTimeout(function() { window.close(); }, 1000); // Zamknięcie okna po 1 sekundzie
                                    </script>
                                </head>
                                <body>
                                    <p>Autorizacja zakończona pomyślnie. Możesz zamknąć to okno.</p>
                                </body>
                            </html>
                        """)
    else:
        return jsonify({"error": "Unable to fetch access token"})


@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        save_tokens_to_file(new_token_info)


def run_flask_server():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


if __name__ == '__main__':
    run_flask_server()
