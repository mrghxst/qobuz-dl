# Wrapper for Qo-DL Reborn. This is a sligthly modified version
# of qopy, originally written by Sorrow446. All credits to the
# original author.

import hashlib
import logging
import re
import time

import requests

from qobuz_dl.exceptions import (
    AuthenticationError,
    IneligibleError,
    InvalidAppIdError,
    InvalidAppSecretError,
    InvalidQuality,
)
from qobuz_dl.color import GREEN, YELLOW

RESET = "Reset your credentials with 'qobuz-dl -r'"

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, email, pwd, app_id, secrets, skip_auth=False):
        logger.info(f"{YELLOW}Logging...")
        self.secrets = secrets
        self.id = str(app_id)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
                "X-App-Id": self.id,
                "Content-Type": "application/json;charset=UTF-8"

            }
        )
        self.base = "https://www.qobuz.com/api.json/0.2/"
        self.sec = None
        if not skip_auth:
            self.auth(email, pwd)
            self.cfg_setup()

    def api_call(self, epoint, **kwargs):
        if epoint == "user/login":
            params = {
                "email": kwargs["email"],
                "password": kwargs["pwd"],
                "app_id": self.id,
            }
        elif epoint == "track/get":
            params = {"track_id": kwargs["id"]}
        elif epoint == "album/get":
            params = {"album_id": kwargs["id"]}
        elif epoint == "playlist/get":
            params = {
                "extra": "tracks",
                "playlist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
            }
        elif epoint == "artist/get":
            params = {
                "app_id": self.id,
                "artist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
                "extra": "albums",
            }
        elif epoint == "label/get":
            params = {
                "label_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs["offset"],
                "extra": "albums",
            }
        elif epoint == "favorite/getUserFavorites":
            unix = time.time()
            # r_sig = "userLibrarygetAlbumsList" + str(unix) + kwargs["sec"]
            r_sig = "favoritegetUserFavorites" + str(unix) + kwargs["sec"]
            r_sig_hashed = hashlib.md5(r_sig.encode("utf-8")).hexdigest()
            params = {
                "app_id": self.id,
                "user_auth_token": self.uat,
                "type": "albums",
                "request_ts": unix,
                "request_sig": r_sig_hashed,
            }
        elif epoint == "track/getFileUrl":
            unix = time.time()
            track_id = kwargs["id"]
            fmt_id = kwargs["fmt_id"]
            # qualities 1-4 are transcoded locally from 320kbps MP3
            api_fmt = 5 if int(fmt_id) in (1, 2, 3, 4) else fmt_id
            if int(fmt_id) not in (1, 2, 3, 4, 5, 6, 7, 27):
                raise InvalidQuality(
                    "Invalid quality id: choose between 1, 2, 3, 4, 5, 6, 7 or 27"
                )
            r_sig = "trackgetFileUrlformat_id{}intentstreamtrack_id{}{}{}".format(
                api_fmt, track_id, unix, kwargs.get("sec", self.sec)
            )
            r_sig_hashed = hashlib.md5(r_sig.encode("utf-8")).hexdigest()
            params = {
                "request_ts": unix,
                "request_sig": r_sig_hashed,
                "track_id": track_id,
                "format_id": api_fmt,
                "intent": "stream",
            }
        else:
            params = kwargs
        r = self.session.get(self.base + epoint, params=params)
        if epoint == "user/login":
            if r.status_code == 401:
                raise AuthenticationError("Invalid credentials.\n" + RESET)
            elif r.status_code == 400:
                raise InvalidAppIdError("Invalid app id.\n" + RESET)
            else:
                logger.info(f"{GREEN}Logged: OK")
        elif (
            epoint in ["track/getFileUrl", "favorite/getUserFavorites"]
            and r.status_code == 400
        ):
            raise InvalidAppSecretError(f"Invalid app secret: {r.json()}.\n" + RESET)

        r.raise_for_status()
        return r.json()

    def auth(self, email, pwd):
        # Qobuz deprecated email/password login (2026). `pwd` must be a
        # user_auth_token, obtained from 'qobuz-dl oauth' or a browser session.
        token = (pwd or "").strip()
        if len(token) < 20 or re.fullmatch(r"[0-9a-f]{32}", token):
            raise AuthenticationError(
                "Authentication requires a valid user_auth_token.\n"
                "Qobuz no longer supports email/password login.\n"
                "Run 'qobuz-dl oauth' to log in through your browser.\n" + RESET
            )
        self.uat = token
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        r = self.session.post(self.base + "user/login", data={"extra": "partner"})
        if r.status_code == 401:
            raise AuthenticationError(
                "Token expired or invalid.\nRun 'qobuz-dl oauth' to log in again.\n"
                + RESET
            )
        r.raise_for_status()
        usr_info = r.json()
        if not usr_info["user"]["credential"]["parameters"]:
            raise IneligibleError("Free accounts are not eligible to download tracks.")
        self.uat = usr_info["user_auth_token"]
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        self.label = usr_info["user"]["credential"]["parameters"]["short_label"]
        logger.info(f"{GREEN}Logged: OK")
        logger.info(f"{GREEN}Membership: {self.label}")
        self._save_token(self.uat)

    @staticmethod
    def _save_token(token):
        """Persist a refreshed auth token back to config.ini."""
        try:
            import configparser
            import os

            if os.name == "nt":
                config_dir = os.path.join(os.environ.get("APPDATA", ""), "qobuz-dl")
            else:
                config_dir = os.path.join(
                    os.environ["HOME"], ".config", "qobuz-dl"
                )
            config_file = os.path.join(config_dir, "config.ini")
            config = configparser.ConfigParser()
            config.read(config_file)
            config["DEFAULT"]["password"] = token
            with open(config_file, "w") as f:
                config.write(f)
            logger.info(f"{GREEN}Auth token saved to config.")
        except Exception as e:  # noqa
            logger.warning(f"{YELLOW}Could not save refreshed token: {e}")

    def login_with_oauth_code(self, code, private_key):
        params = {"code": code, "private_key": private_key}
        r = self.session.get(self.base + "oauth/callback", params=params)
        if r.status_code in (400, 401):
            raise AuthenticationError("OAuth code rejected.\n" + RESET)
        r.raise_for_status()
        token = r.json().get("token")
        if not token:
            raise AuthenticationError("No token in OAuth callback response")
        self.uat = token
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        r = self.session.post(self.base + "user/login", data={"extra": "partner"})
        if r.status_code == 401:
            raise AuthenticationError("OAuth token rejected.\n" + RESET)
        r.raise_for_status()
        usr_info = r.json()
        if not usr_info["user"]["credential"]["parameters"]:
            raise IneligibleError("Free accounts are not eligible to download tracks.")
        self.uat = usr_info["user_auth_token"]
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        self.label = usr_info["user"]["credential"]["parameters"]["short_label"]
        logger.info(f"{GREEN}Logged: OK")
        logger.info(f"{GREEN}Membership: {self.label}")
        self._save_token(self.uat)
        self.cfg_setup()
        return usr_info

    def multi_meta(self, epoint, key, id, type):
        total = 1
        offset = 0
        while total > 0:
            if type in ["tracks", "albums"]:
                j = self.api_call(epoint, id=id, offset=offset, type=type)[type]
            else:
                j = self.api_call(epoint, id=id, offset=offset, type=type)
            if offset == 0:
                yield j
                total = j[key] - 500
            else:
                yield j
                total -= 500
            offset += 500

    def get_album_meta(self, id):
        return self.api_call("album/get", id=id)

    def get_track_meta(self, id):
        return self.api_call("track/get", id=id)

    def get_track_url(self, id, fmt_id):
        return self.api_call("track/getFileUrl", id=id, fmt_id=fmt_id)

    def get_artist_meta(self, id):
        return self.multi_meta("artist/get", "albums_count", id, None)

    def get_plist_meta(self, id):
        return self.multi_meta("playlist/get", "tracks_count", id, None)

    def get_label_meta(self, id):
        return self.multi_meta("label/get", "albums_count", id, None)

    def search_albums(self, query, limit):
        return self.api_call("album/search", query=query, limit=limit)

    def search_artists(self, query, limit):
        return self.api_call("artist/search", query=query, limit=limit)

    def search_playlists(self, query, limit):
        return self.api_call("playlist/search", query=query, limit=limit)

    def search_tracks(self, query, limit):
        return self.api_call("track/search", query=query, limit=limit)

    def get_favorite_albums(self, offset, limit):
        return self.api_call(
            "favorite/getUserFavorites", type="albums", offset=offset, limit=limit
        )

    def get_favorite_tracks(self, offset, limit):
        return self.api_call(
            "favorite/getUserFavorites", type="tracks", offset=offset, limit=limit
        )

    def get_favorite_artists(self, offset, limit):
        return self.api_call(
            "favorite/getUserFavorites", type="artists", offset=offset, limit=limit
        )

    def get_user_playlists(self, limit):
        return self.api_call("playlist/getUserPlaylists", limit=limit)

    def test_secret(self, sec):
        try:
            self.api_call("track/getFileUrl", id=5966783, fmt_id=5, sec=sec)
            return True
        except InvalidAppSecretError:
            return False

    def cfg_setup(self):
        for secret in self.secrets:
            # Falsy secrets
            if not secret:
                continue

            if self.test_secret(secret):
                self.sec = secret
                break

        if self.sec is None:
            raise InvalidAppSecretError("Can't find any valid app secret.\n" + RESET)
