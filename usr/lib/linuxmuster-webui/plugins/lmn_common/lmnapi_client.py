"""
Minimal HTTP client to call linuxmuster-api from the webui
"""

import logging
import requests

from .api import lmnapi_host, lmnapi_port


class LmnapiUnavailable(Exception):
    """linuxmuster-api could not be reached at all."""


class LmnapiError(Exception):
    """linuxmuster-api was reached but rejected the request."""


class LmnapiClient:
    """
    One instance per webui session (see lmn_auth/api.py), holding the
    linuxmuster-api JWT obtained at login so callers don't have to thread it
    through every call.
    """

    def __init__(self):
        self.host = lmnapi_host
        self.port = lmnapi_port
        self.token = None

    def authenticate(self, username, password):
        """
        Exchange LDAP credentials for a linuxmuster-api JWT (GET /v1/auth/)
        and keep it on the instance for subsequent password calls.

        :return: JWT string, or None if linuxmuster-api refused the credentials
                 or could not be reached at all.
        """

        try:
            r = requests.get(
                f'https://{self.host}:{self.port}/v1/auth/',
                auth=(username, password),
                verify=False,
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            logging.warning(f"Could not reach linuxmuster-api to get a JWT for {username}: {e}")
            self.token = None
            return None

        if r.status_code != 200:
            logging.warning(f"linuxmuster-api refused to deliver a JWT for {username} (HTTP {r.status_code})")
            self.token = None
            return None

        self.token = r.json()
        return self.token

    def set_first_password(self, user, password, set_current=False):
        """
        Call POST /v1/users/{user}/set-first-password.
        """

        self._post_password(user, 'set-first-password', {'password': password, 'set_current': set_current})

    def set_current_password(self, user, password, set_first=False):
        """
        Call POST /v1/users/{user}/set-current-password.
        """

        self._post_password(user, 'set-current-password', {'password': password, 'set_first': set_first})

    def _post_password(self, user, endpoint, body):
        if not self.token:
            raise LmnapiUnavailable('No linuxmuster-api session token available.')

        try:
            r = requests.post(
                f'https://{self.host}:{self.port}/v1/users/{user}/{endpoint}',
                json=body,
                headers={'X-API-Key': self.token},
                verify=False,
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            raise LmnapiUnavailable(str(e))

        if r.status_code != 200:
            try:
                detail = r.json().get('detail', r.text)
            except ValueError:
                detail = r.text
            raise LmnapiError(detail)
