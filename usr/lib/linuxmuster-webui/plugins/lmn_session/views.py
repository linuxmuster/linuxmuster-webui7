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
        # sessionsList = []
        action = http_context.json_body()['action']
        if action == 'get-sessions':
            supervisor = http_context.json_body()['username']
            with authorize('lm:users:teachers:read'):
                try:
                    sessions = lmn_getSophomorixValue('sophomorix-session -i -jj ', 'SUPERVISOR/'+supervisor+'/sophomorixSessions', True)
                # Most likeley key error 'cause no sessions for this user exist
                except Exception:
                    return 0
            return sessions
        if action == 'get-participants':
            supervisor = http_context.json_body()['username']
            session = http_context.json_body()['session']
            with authorize('lm:users:teachers:read'):
                    try:
                        participants = lmn_getSophomorixValue('sophomorix-session -i -jj ', 'SUPERVISOR/'+supervisor+'/sophomorixSessions/'+session+'/PARTICIPANTS', True)
                    except Exception:
                        return 0
                    # Convert PERL bool to python bool
                    for key, value in participants.iteritems():
                        for key in value:
                            if value[key] == 'TRUE':
                                value[key] = True
                            if value[key] == 'FALSE':
                                value[key] = False
            return participants
        if action == 'kill-sessions':
            session = http_context.json_body()['session']
            with authorize('lm:users:teachers:read'):
                # raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(session))
                result = lmn_getSophomorixValue('sophomorix-session -j --session '+session+' --kill', 'OUTPUT')
                return result
        if action == 'rename-session':
            session = http_context.json_body()['session']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:teachers:read'):
                # raise Exception('Bad value in LDAP field SophomorixUserPermissions! Python error:\n' + str(comment)+ str(session))
                result = lmn_getSophomorixValue('sophomorix-session -j --session '+session+' --comment "' + comment + '"', 'OUTPUT')
                return result
        if action == 'new-session':
            supervisor = http_context.json_body()['username']
            comment = http_context.json_body()['comment']
            with authorize('lm:users:teachers:read'):
                result = lmn_getSophomorixValue('sophomorix-session --create --supervisor ' + supervisor + ' -j --comment "' + comment + '"', 'OUTPUT')
                return result
        if http_context.method == 'POST':
            with authorize('lm:users:teachers:write'):
                return 0



    @url(r'/api/lmn/session/user-search')
    #@authorize('lmn:session:user-search')
    @endpoint(api=True)
    def handle_api_ldap_search(self, http_context):
        with authorize('lm:users:teachers:read'):
            try:
                users = lmn_getSophomorixValue('sophomorix-query -jj --student --teacher --user-full --anyname \"*' + http_context.query['q'] + '*\" ', 'USER' ,True)
            except Exception:
                return 0
        userList = []
        for user in users:
            userList.append(users[user]['displayName'])
        return userList
