from __future__ import print_function

import os
import sys
import threading
from functools import wraps

import yaml
from flask import Flask, request, jsonify, Response
from pip._vendor import requests

app = Flask(__name__)


def load_conf():
    directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(directory, "\config.yml"), 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e, file=sys.stderr)


conf = load_conf()

try:
    import youtube_dl

    ydl = youtube_dl.YoutubeDL({"outtmpl": conf["path"] + "%(title)s.%(ext)s"})
except ImportError:
    ydl = None


def check_auth(username, password):
    users = conf["users"]
    for user_settings in users:
        if username == user_settings["username"] and password == user_settings["password"]:
            return True

    return False


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
def download():
    try:
        data = request.get_json()

        if data is None:
            raise Exception("Missing or wrong Content-Type, should be: application/json")

        data["user"] = request.authorization.username

        if url_check(data["url"]):
            threading.Thread(target=lambda: download_in_background(data)).start()
            result = {"success": True}
            return jsonify(result)
    except Exception as e:
        result = {"error": True, "reason": str(e)}
        return jsonify(result), 500


def on_complete(user, filename):
    curr_user = filter(lambda person: person['username'] == user, conf["users"])[0]
    if curr_user["notify_via_pushbullet"]:
        try:
            from pushbullet import Pushbullet
            pb = Pushbullet(curr_user["pushbullet_token"])
            pb.push_note("Download finished", filename)
            return True
        except ImportError:
            print("Cant notify via PushBullet. Missing librabry. Install via pip install pushbullet.py",
                  file=sys.stderr)
            return False
        except Exception:
            print("Invalid Api key for PushBullet. Please insert correct one.", file=sys.stderr)
            return False


def download_in_background(data):
    url = data["url"]

    if "name" in data:
        file_extension = url.split("?")[0].split(".")[-1]
        name = data["name"] + "." + file_extension
    else:
        name = url.split("/")[-1]

    if "category" in data:
        path = conf["path"] + data["category"] + "/" + name
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path))
    else:
        path = conf["path"] + name

    if "youtube" in url or "oload" in url:
        if ydl is not None:
            with ydl:
                info = ydl.extract_info(url=url, download=True)
                on_complete(data["user"], info["title"])

    else:
        r = requests.get(url)
        with open(path, "wb+") as code:
            code.write(r.content)
        on_complete(data["user"], name)


def url_check(url):
    req = requests.get(url)
    if "youtube" in url or "oload" in url:
        if ydl is None:
            raise Exception("Trying to download from Youtube/Openload without youtube-dl library")
    return req.status_code == 200


if __name__ == '__main__':
    app.run(port=9000)
