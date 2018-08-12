import json
import unittest

import app


class DownloaderTestCase(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        self.headers = {
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ=",
            "Content-Type": "application/json"
        }

    def make_request(self, data):
        return self.app.post("/download/", data=json.dumps(data), headers=self.headers)

    def make_wrong_request(self):
        data = dict(
            url="https://mrose.org/cc/png-test.png"
        )
        return self.app.post("/download/", data=json.dumps(data), headers={
            "Content-Type": "application/json"
        })

    def test_invalid_url(self):
        tmp = self.make_request(dict(
            url="https://mrose"
        ))
        assert tmp.status_code == 500

    def test_landing_page(self):
        tmp = self.app.get("/", headers=self.headers)
        assert tmp.status_code == 200

    def test_downloads_page(self):
        tmp = self.app.get("/downloads/", headers=self.headers)
        assert tmp.status_code == 200

    def test_general_download(self):
        old = app.conf["local_network_without_login"]
        app.conf["local_network_without_login"] = False
        tmp = self.make_request(dict(
            url="http://theglow666.6f.sk/image_test/",
            name="test",
            category="test"
        ))
        app.conf["local_network_without_login"] = old
        assert tmp.status_code == 200

    def test_general_download_without_name(self):
        tmp = self.make_request(dict(
            url="http://via.placeholder.com/359x150",
            category="test2"
        ))
        assert tmp.status_code == 200

    def test_download_without_auth_local(self):
        tmp = self.make_wrong_request()
        assert tmp.status_code == 200

    def test_download_without_auth_remote(self):
        old = app.conf["local_network_without_login"]
        app.conf["local_network_without_login"] = False
        tmp = self.make_wrong_request()
        app.conf["local_network_without_login"] = old
        assert tmp.status_code == 401

    def wrong_download(self, headers):
        return self.app.post("/download/", data=json.dumps(dict(
            url="https://mrose.org/cc/png-test.png"
        )), headers=headers)

    def test_download_with_wrong_auth(self):
        old = app.conf["local_network_without_login"]
        app.conf["local_network_without_login"] = False
        tmp = self.wrong_download(headers={
            "Authorization": "Basic VVNFUk5BTUUyOlBBU1NXT1JEMg==",
            "Content-Type": "application/json"
        })
        app.conf["local_network_without_login"] = old
        assert tmp.status_code == 401

    def test_download_without_content_type(self):
        tmp = self.wrong_download(headers={
            "Authorization": "Basic VVNFUk5BTUU6UEFTU1dPUkQ="
        })
        assert tmp.status_code == 500

    def test_youtubedl_crash(self):
        app.ydl_installed = False
        tmp = self.app.post("/download/", data=json.dumps(dict(
            url="https://www.youtube.com/watch?v=NxR51tUcG60"
        )), headers=self.headers)
        assert tmp.status_code == 500
        app.ydl_installed = True

    def test_youtubedl(self):
        data = {"url": "https://www.youtube.com/watch?v=NxR51tUcG60",
                "user": "USERNAME"}
        res = app.download_in_background(data)
        assert res

    def test_youtubedl_with_name(self):
        data = {"url": "https://www.youtube.com/watch?v=NxR51tUcG60",
                "user": "USERNAME",
                "name": "youtube test",
                "extension": ".mp4"}
        res = app.download_in_background(data)
        assert res

    def test_youtubedl_only_audio(self):
        data = {"url": "https://www.youtube.com/watch?v=NxR51tUcG60",
                "user": "USERNAME",
                "audioOnly": True}
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

    def test_download_without_user(self):
        tmp = app.on_complete(None, "test")
        assert tmp is None


if __name__ == "__main__":
    unittest.main()
