import json

import youtube_dl

import app
import unittest


class DownloaderTestCase(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        self.headers = {
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ=",
            "Content-Type": "application/json"
        }

    def test_general_download(self):
        tmp = self.app.post("/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png",
            name="test png",
            category="test"
        )), headers=self.headers)
        assert tmp.status_code == 200

    def test_download_without_auth(self):
        tmp = self.app.post("/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png"
        )), headers={
            "Content-Type": "application/json"
        })
        assert tmp.status_code == 401

    def test_download_without_content_type(self):
        tmp = self.app.post("/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png"
        )), headers={
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ="
        })
        assert tmp.status_code == 500

    def test_youtubedl_crash(self):
        ydl_tmp = app.ydl
        app.ydl = None
        tmp = self.app.post("/", data=json.dumps(dict(
            url="https://www.youtube.com/watch?v=Pfq8f59u3kk"
        )), headers=self.headers)
        assert tmp.status_code == 500
        app.ydl = ydl_tmp

    def test_youtubedl(self):
        tmp = self.app.post("/", data=json.dumps(dict(
            url="https://www.youtube.com/watch?v=Pfq8f59u3kk"
        )), headers=self.headers)
        assert tmp.status_code == 200

    def test_pushbullet_crash(self):
        oldKey = app.conf["pushbullet_token"]
        app.conf["pushbullet_token"] = "Invalid"
        tmp = app.on_complete("test")
        assert tmp is False
        app.conf["pushbullet_token"] = oldKey

    def test_pushbullet(self):
        app.notify_via_pushbullet = True
        app.pushbullet_token = "o.sGzTGwxlOz16GGh2OwwjYpJnrRaciUNU"
        tmp = app.on_complete("test")
        assert tmp is True


if __name__ == '__main__':
    unittest.main()
