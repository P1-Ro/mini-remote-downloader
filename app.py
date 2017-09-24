import threading
from functools import wraps

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
        request_json = request.get_json()
        url = request_json.get('url')
        if url_check(url):
            threading.Thread(target=lambda: download_in_background(url)).start()
            result = {"success": True}
    except Exception as e:
        result = {"error": True, "reason": str(e)}
    return jsonify(result)


def download_in_background(url):
    r = requests.get(url)
    name = url.split("/")[-1]
    with open(PATH_TO_SAVE + name, "wb+") as code:
        code.write(r.content)


def url_check(url):
    req = requests.get(url)
    return req.status_code == 200


if __name__ == '__main__':
    app.run(port=9000)
