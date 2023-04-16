import ldap
import ldap.filter
from datetime import datetime
from dataclasses import fields, asdict

from aj.plugins.lmn_common.api import ldap_config as params
from aj.plugins.lmn_common.ldap.models import *


class LdapConnector:

    def get_single(self, objectclass, ldap_filter, dict=True):
        result = self._request(ldap_filter)[0][1]
        d = {}
        for f in fields(objectclass):
            value = result.get(f.name, None)
            d[f.name] = self._filter_value(f, value)
        if dict:
            return asdict(objectclass(**d))
        return objectclass(**d)
        
    def get_collection(self, objectclass, ldap_filter, dict=True, sortkey=None):
        result = self._request(ldap_filter)
        response = []
        for r in result:
            if r[0] is not None:
                d = {}
                for f in fields(objectclass):
                    value = r[1].get(f.name, None)
                    d[f.name] = self._filter_value(f, value)
                if dict:
                    response.append(asdict(objectclass(**d)))
                else:
                    response.append(objectclass(**d))
        if sortkey is not None:
            return sorted(response, key=lambda d: getattr(d, sortkey))
        return response

    @staticmethod
    def _filter_value(field, value):
        # TODO : more exception catch on values
        if value is None:
            return None

        if field.type.__name__ == 'str':
            # Something like [b'']
            return value[0].decode() if value is not None else ''

        if field.type.__name__ == 'list':
            # Something like [b'a', b'c']
            return [v.decode() for v in value] if value is not None else []

        if field.type.__name__ == 'bool':
            # Something like [b'FALSE']
            return value[0].capitalize() == b'True'

        if field.type.__name__ == 'datetime':
            # Something like [b'20210520111726.0Z']
            return datetime.strptime(value[0].decode(), '%Y%m%d%H%M%S.%fZ')

        if field.type.__name__ == 'int':
            # Something like [b'20']
            return int(value[0].decode())

        if field.type.__name__ == 'List':
            # Creepy test
            if 'LMNSession' in str(field.type.__args__[0]):
                result = []
                for v in value:
                    data = v.decode().split(';')
                    participants = data[2].split(',')
                    result.append(LMNSession(data[0], data[1], participants))
                return result

    def _request(self, ldap_filter):
        l = ldap.initialize("ldap://localhost:389/")
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = ldap.VERSION3
        l.bind_s(params['binddn'], params['bindpw'])
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, ldap_filter, attrlist=['*'])
        l.unbind_s()
        return res

