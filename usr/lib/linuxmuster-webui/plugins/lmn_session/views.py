import os
import json
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from aj.auth import authorize
from aj.plugins.lm_common.api import lmn_getSophomorixValue


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
       self.context = context

    @url(r'/api/lmn/session/sessions')
    @endpoint(api=True)
    def handle_api_session_sessions(self, http_context):
        action = http_context.json_body()['action']
    #    if http_context.method == 'GET':
        if action == 'get-sessions':
            supervisor = "ba"
            sessionsList = []
            with authorize('lm:users:teachers:read'):
                sessions = lmn_getSophomorixValue('sophomorix-session -i -jj ', 'SUPERVISOR/'+supervisor+'/sophomorixSessions')
                for item in sessions:
                    #teachersList.append({'sAMAccountName': teachers[item]['sAMAccountName'], 'givenName': teachers[item]['sophomorixFirstnameASCII'], 'sn': teachers[item]['sophomorixSurnameASCII']}.copy())
                    raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(item))
                    #sessionsList.append({'sAMAccountName': users[item]['sAMAccountName'],
                    #   'givenName': users[item]['givenName'],
                    #   'sn': users[item]['sn'],
                    #   'mail': users[item]['mail'],
                    #   'sophomorixBirthdate': users[item]['sophomorixBirthdate'],
                    #   'sophomorixFirstPassword': users[item]['sophomorixFirstPassword']}.copy())
                    #raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(usersList))
        return sessionsList

        if http_context.method == 'POST':
            with authorize('lm:users:teachers:write'):
                return 0
