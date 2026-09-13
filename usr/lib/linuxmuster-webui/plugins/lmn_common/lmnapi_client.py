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

    def set_first_password(self, user, password=None, set_current=False):
        """
        Call POST /v1/users/{user}/set-first-password.

        If password is None, linuxmuster-api resets the user's current
        password back to their existing first password instead of setting a
        new one (set_current is then meaningless and ignored on that path).
        """

        self._request('POST', f'/v1/users/{user}/set-first-password', json={'password': password, 'set_current': set_current})

    def set_current_password(self, user, password, set_first=False):
        """
        Call POST /v1/users/{user}/set-current-password.
        """

        self._request('POST', f'/v1/users/{user}/set-current-password', json={'password': password, 'set_first': set_first})

    def set_random_first_password(self, user):
        """
        Call POST /v1/users/{user}/set-random-first-password: linuxmuster-api
        generates a password satisfying the current password policy and sets
        it as the user's first and current password.

        :return: the generated password
        """

        return self._request('POST', f'/v1/users/{user}/set-random-first-password')['password']

    def check_first_password(self, user):
        """
        Call GET /v1/users/{user}?check_first_pw=true.

        :return: True if the user's current password still matches their
                 stored first password, False otherwise.
        """

        return self._request('GET', f'/v1/users/{user}', params={'check_first_pw': True})['FirstPasswordSet']

    def get_first_password(self, user):
        """
        Call GET /v1/users/{user} and return the user's stored first password.

        :return: The user's sophomorixFirstPassword, in clear text.
        """

        return self._request('GET', f'/v1/users/{user}')['sophomorixFirstPassword']

    def get_user_quotas(self, user):
        """
        Call GET /v1/users/{user}/quotas.

        Unlike sophomorix-query, this resolves quotas hosted on a separate
        fileserver (MSDFS) instead of always querying the local domain
        controller.

        :return: {<share>: {'used', 'soft_limit', 'hard_limit'} or {'ERROR': ...},
                  ..., 'cloud': ..., 'mail': ...}
        """

        return self._request('GET', f'/v1/users/{user}/quotas')

    def add_management_group_members(self, group, users, school):
        """
        Call POST /v1/managementgroups/{group}/members to add users
        (wifi, internet, intranet, webfilter, printing) to a management group.

        `school` is required: linuxmuster-api has no notion of the webui's
        current school context, and a global-administrator's own JWT carries
        no single school at all.
        """

        self._request('POST', f'/v1/managementgroups/{group}/members', json={'users': users}, params={'school': school})

    def remove_management_group_members(self, group, users, school):
        """
        Call DELETE /v1/managementgroups/{group}/members to remove users
        from a management group. See add_management_group_members for `school`.
        """

        self._request('DELETE', f'/v1/managementgroups/{group}/members', json={'users': users}, params={'school': school})

    def add_parent(self, student, parent):
        """
        Call POST /v1/users/{student}/parents to assign an existing parent
        to an existing student.
        """

        self._request('POST', f'/v1/users/{student}/parents', json={'users': [parent]})

    def remove_parent(self, student, parent):
        """
        Call DELETE /v1/users/{student}/parents to unassign a parent from a student.
        """

        self._request('DELETE', f'/v1/users/{student}/parents', json={'users': [parent]})

    def patch_printer_members(self, printer, changes):
        """
        Call PATCH /v1/printers/{printer} to add or remove members and member
        groups in a single LDAP modify, instead of one sophomorix-group call
        per entity.

        `changes` maps the API's list fields (addmembers, removemembers,
        addmembergroups, removemembergroups) to lists of cn. Attributes that
        are not sent are left untouched.

        Reserved to administrators by the API (RoleChecker "GS"). Unlike the
        management group routes, this one takes no `school`: it reads it from
        the caller's JWT, and printer names already carry their school prefix
        in a multischool setup.
        """

        self._request('PATCH', f'/v1/printers/{printer}', json=changes)

    def join_printer(self, printer):
        """
        Call POST /v1/printers/{printer}/join to add the caller themselves to
        a joinable printer. This is the route a teacher may use: the API
        checks sophomorixJoinable and ignores any member name sent to it.
        """

        self._request('POST', f'/v1/printers/{printer}/join')

    def quit_printer(self, printer):
        """
        Call POST /v1/printers/{printer}/quit to remove the caller themselves
        from a printer. See join_printer.
        """

        self._request('POST', f'/v1/printers/{printer}/quit')

    def _request(self, method, path, **kwargs):
        if not self.token:
            raise LmnapiUnavailable('No linuxmuster-api session token available.')

        try:
            r = requests.request(
                method,
                f'https://{self.host}:{self.port}{path}',
                headers={'X-API-Key': self.token},
                verify=False,
                timeout=10,
                **kwargs,
            )
        except requests.exceptions.RequestException as e:
            raise LmnapiUnavailable(str(e))

        if not r.ok:
            try:
                detail = r.json().get('detail', r.text)
            except ValueError:
                detail = r.text
            raise LmnapiError(detail)

        return r.json() if r.content else None
