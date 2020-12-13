from __future__ import print_function
from __future__ import unicode_literals

import mimetypes
import os
import socket
import sys
import threading
import uuid
from functools import wraps
from os.path import splitext

import six
from six.moves.urllib.parse import urlparse

import requests
import yaml
from flask import Flask, request, jsonify, Response, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid4())
socketio = SocketIO(app, async_mode='threading')
all_downloads = {}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = '.'.join(s.getsockname()[0].split(".")[0:-1])
    except Exception:
        IP = '192.168.0'
        print("Cannot detect local IP, instead using: 192.168.0", file=sys.stderr)
    finally:
        s.close()

    return IP


def load_conf():
    directory = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.join(directory, "config.yml"), "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise SystemExit(e)


conf = load_conf()
allowed_ip_prefix = get_ip()

try:
    import youtube_dl

    ydl_installed = True
except ImportError:
    ydl_installed = False


def can_access(username, password):
    users = conf["users"]
    for user_settings in users:
        if username == user_settings["username"] and password == user_settings["password"]:
            return True

    return False


def is_allowed_ip(ip):
    return conf["local_network_without_login"] and (ip.startswith(allowed_ip_prefix) or ip == "127.0.0.1")


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        ip = request.remote_addr
        if not is_allowed_ip(ip) and (not auth or not can_access(auth.username, auth.password)):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/')
@requires_auth
def login_page():
    return render_template('index.html')


@app.route('/downloads/')
@requires_auth
def downloads():
    return render_template('downloads.html')


@app.route('/download/', methods=['POST'])
@requires_auth
def download():
    try:
        data = request.get_json()
        if data is None:
            raise Exception("Missing or wrong Content-Type, should be: application/json")
        data["user"] = request.authorization.username if (request.authorization is not None) else None

        extension = get_extension(data["url"])
        data["extension"] = extension

        threading.Thread(target=lambda: download_in_background(data)).start()
        result = {"success": True}
        return jsonify(result)
    except Exception as e:
        result = {"error": True, "reason": str(e)}
        return jsonify(result), 500


@socketio.on("get_downloads")
def get_downloads():
    return all_downloads


def send_pushbullet_notification(curr_user, filename):
    try:
        from pushbullet import Pushbullet
        pb = Pushbullet(curr_user["pushbullet_token"])
        device = pb.devices[0] if app.testing else None
        pb.push_note("MiniRemoteDownloader - Download finished", filename, device)
        return True
    except ImportError:
        print("Cant notify via PushBullet. Missing librabry. Install via pip install pushbullet.py",
              file=sys.stderr)
        return False
    except Exception:
        print("Invalid Api key for PushBullet. Please insert correct one.", file=sys.stderr)
        return False


def on_complete(user, filename):
    if not user:
        return

    if six.PY2:
        curr_user = filter(lambda person: person['username'] == user, conf["users"])[0]
    else:
        curr_user = next(filter(lambda person: person['username'] == user, conf["users"]))

    if curr_user["notify_via_pushbullet"]:
        return send_pushbullet_notification(curr_user, filename)


def download_with_ydl(data, url, name, path):
    if name:
        out_tmpl = path
    else:
        out_tmpl = os.path.join(path, "%(title)s.%(ext)s")

    ydl_options = {
        "outtmpl": out_tmpl,
        'progress_hooks': [progress_hook]
    }

    if "audioOnly" in data:
        ydl_options["out_format"] = "bestaudio/best"
        ydl_options["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': conf["audio_codec"],
            'preferredquality': str(conf["audio_kbps"]),
        }]
    else:
        ydl_options["out_format"] = "best[ext=mp4]/best"

    ydl = youtube_dl.YoutubeDL(ydl_options)
    with ydl:
        info = ydl.extract_info(url=url, download=True)
        on_complete(data["user"], info["title"])


def standard_download(data, url, name, path):
    r = requests.get(url)
    with open(path, "wb+") as code:
        code.write(r.content)
    on_complete(data["user"], name)


def get_name(data):
    url = data["url"]
    name = ""

    if "name" in data:
        name = data["name"] + data["extension"]
    elif "youtube" not in url and "oload" not in url:
        name = url.split("/")[-1] + data["extension"]

    return name


def get_path(data, name):
    if "category" in data:
        path = os.path.join(conf["path"], data["category"])
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, name)
    else:
        path = os.path.join(conf["path"], name)

    return path


def download_in_background(data):
    url = data["url"]

    name = get_name(data)
    path = get_path(data, name)

    if "youtube" in url or "oload" in url:
        download_with_ydl(data, url, name, path)
    else:
        standard_download(data, url, name, path)
    return True


def progress_hook(data):
    filename = data["filename"]
    resp = {}

    if filename not in all_downloads.keys():
        socketio.emit("new_download", {"filename": filename, "size": data["_total_bytes_str"]})

    resp["status"] = data["status"]
    resp["filename"] = filename

    if data['status'] == 'finished' and filename in all_downloads.keys():
        del all_downloads[filename]

    elif data['status'] == 'downloading':
        resp["eta"] = data["_eta_str"]
        resp["progress"] = data["_percent_str"]
        resp["speed"] = data["_speed_str"]
        all_downloads[filename] = data

    socketio.emit(filename, resp)


def already_has_extension(url):
    parsed = urlparse(url)
    ext = splitext(parsed.path)[1]
    return len(ext) != 0


def get_extension_from_content_type(url):
    try:
        res = requests.get(url)
        content_type = res.headers['content-type']
        return mimetypes.guess_extension(content_type)

    except requests.ConnectionError:
        raise Exception("Invalid or malformed URL")


def get_extension(url):
    if not already_has_extension(url):
        if is_streaming_site(url):
            if not ydl_installed:
                raise Exception("Trying to download from Youtube/Openload without youtube-dl library installed")
            else:
                return ".mp4"
        else:
            return get_extension_from_content_type(url)

    return ""


def is_streaming_site(url):
    video_urls = ["oload", "openload", "youtube", "youtu"]

    for site in video_urls:
        if site in url:
            return True

    return False


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=9000)
