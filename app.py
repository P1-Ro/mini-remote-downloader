import threading
from functools import wraps

import os
from flask import Flask, request, jsonify, Response
from pip._vendor import requests

app = Flask(__name__)
PATH_TO_SAVE = "{PATH}"


def check_auth(username, password):
    return username == '{UserName}' and password == '{Password}'


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


def download_in_background(data):
    url = data["url"]
    r = requests.get(url)

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

    with open(path, "wb+") as code:
        code.write(r.content)


def url_check(url):
    req = requests.get(url)
    return req.status_code == 200


if __name__ == '__main__':
    app.run(port=9000)
