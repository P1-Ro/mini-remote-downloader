from __future__ import print_function
import threading
from functools import wraps
import sys
import os

import sys
from flask import Flask, request, jsonify, Response
from pip._vendor import requests
from pushbullet import InvalidKeyError

app = Flask(__name__)
PATH_TO_SAVE = "{PATH}"
user = '{UserName}'
user_pass = '{Password}'
notify_via_pushbullet = True
pushbullet_token = "{TOKEN}"

try:
    import youtube_dl

    ydl = youtube_dl.YoutubeDL({"outtmpl": PATH_TO_SAVE + "%(title)s.%(ext)s"})
except ImportError:
    ydl = None


def check_auth(username, password):
    return username == user and password == user_pass


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/', methods=['POST'])
@requires_auth
def hello_world():
    try:
        data = request.get_json()
        if url_check(data["url"]):
            threading.Thread(target=lambda: download_in_background(data)).start()
            result = {"success": True}
            return jsonify(result)
    except Exception as e:
        result = {"error": True, "reason": str(e)}
        return jsonify(result), 400


def on_complete(filename):
    if notify_via_pushbullet:
        try:
            from pushbullet import Pushbullet
            pb = Pushbullet(pushbullet_token)
            pb.push_note("Download finished", filename)
        except ImportError:
            print("Cant notify via PushBullet. Missing librabry. Install via pip install pushbullet.py", file=sys.stderr)
        except InvalidKeyError:
            print("Invalid Api key for PushBullet. Please insert correct one.", file=sys.stderr)


def download_in_background(data):
    url = data["url"]

    if "name" in data:
        file_extension = url.split("?")[0].split(".")[-1]
        name = data["name"] + "." + file_extension
    else:
        name = url.split("/")[-1]

    if "category" in data:
        path = PATH_TO_SAVE + data["category"] + "/" + name
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path))
    else:
        path = PATH_TO_SAVE + name

    if "youtube" in url or "oload" in url:
        if ydl is not None:
            with ydl:
                info = ydl.extract_info(url=url, download=True)
                on_complete(info["title"])

    else:
        r = requests.get(url)
        with open(path, "wb+") as code:
            code.write(r.content)
        on_complete(name)


def url_check(url):
    req = requests.get(url)
    if "youtube" in url or "oload" in url:
        if ydl is None:
            raise Exception("Trying to download from Youtube/Openload without youtube-dl library")
    return req.status_code == 200


if __name__ == '__main__':
    app.run(port=9000, debug=True)
