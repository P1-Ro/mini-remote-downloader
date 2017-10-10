import json
import shutil
import unittest

import os

import app


class DownloaderTestCase(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        self.headers = {
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ=",
            "Content-Type": "application/json"
        }
        path = app.conf["path"] + "test"
        if os.path.exists(path):
            shutil.rmtree(path)

    def test_landing_page(self):
        tmp = self.app.get("/", headers=self.headers)
        assert tmp.status_code == 200

    def test_general_download(self):
        tmp = self.app.post("/download/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png",
            name="test",
            category="test"
        )), headers=self.headers)
        assert tmp.status_code == 200

    def test_download_without_auth(self):
        tmp = self.app.post("/download/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png"
        )), headers={
            "Content-Type": "application/json"
        })
        assert tmp.status_code == 401

    def wrong_download(self, headers):
        return self.app.post("/download/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png"
        )), headers=headers)

    def test_download_with_wrong_auth(self):
        tmp = self.wrong_download(headers={
            "Authorization": "Basic VVNFUk5BTUUyOlBBU1NXT1JEMg==",
            "Content-Type": "application/json"
        })
        assert tmp.status_code == 401

    def test_download_without_content_type(self):
        tmp = self.wrong_download(headers={
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ="
        })
        assert tmp.status_code == 500

    def test_youtubedl_crash(self):
        ydl_tmp = app.ydl
        app.ydl = None
        tmp = self.app.post("/download/", data=json.dumps(dict(
            url="https://www.youtube.com/watch?v=Pfq8f59u3kk"
        )), headers=self.headers)
        assert tmp.status_code == 500
        app.ydl = ydl_tmp

    def test_youtubedl(self):
        data = {"url": "https://www.youtube.com/watch?v=Pfq8f59u3kk",
                "user": "USERNAME"}
        res = app.download_in_background(data)
        assert res

    def test_pushbullet_crash(self):
        oldKey = app.conf["users"][0]["pushbullet_token"]
        app.conf["users"][0]["pushbullet_token"] = "Invalid"
        tmp = app.on_complete("USERNAME", "test")
        assert tmp is False
        app.conf["users"][0]["pushbullet_token"] = oldKey

    def test_pushbullet(self):
        tmp = app.on_complete("USERNAME", "test")
        assert tmp is True


if __name__ == "__main__":
    unittest.main()
