import ldap
import ldap.filter
from datetime import datetime
from dataclasses import fields, asdict

from aj.plugins.lmn_common.api import ldap_config as params
from aj.plugins.lmn_common.ldap.models import *


class LdapConnector:

    def __init__(self, context):
        self.context = context

    def get_single(self, objectclass, ldap_filter, dict=True, school_oriented=True):
        """
        Handle a single result from a ldap request (with required ldap filter)
        and convert it in the given object class.

        :param objectclass: dataclass like LMNUser
        :type objectclass:
        :param ldap_filter: A valid ldap filter
        :type ldap_filter: basestring
        :param dict: if True, returns a dict, else an object
        :type dict: bool
        """

        result = self._get(ldap_filter)[0]
        if result[0] is not None:
            raw_data = result[1]
            data = {}
            school_node = ""
            if school_oriented:
                school_node = f",OU={self.context.schoolmgr.school},"

            dn = raw_data.get('distinguishedName', [b''])[0].decode()
            if school_node in dn:
                for field in fields(objectclass):
                    if field.init:
                        value = raw_data.get(field.name, None)
                        data[field.name] = self._filter_value(field, value)
                if dict:
                    return asdict(objectclass(**data))
                return objectclass(**data)
        return {}
        
    def get_collection(self, objectclass, ldap_filter, dict=True, sortkey=None, school_oriented=True):
        """
        Handle multiples results from a ldap request (with required ldap filter)
        and convert it in a list of given object class.

        :param objectclass: dataclass like LMNUser
        :type objectclass:
        :param ldap_filter: A valid ldap filter
        :type ldap_filter: basestring
        :param dict: if True, returns a list of dict, else a list of objects
        :type dict: bool
        :param sortkey: if given, sorts the list with the given attribute
        :type sortkey: basestring
        """

        results = self._get(ldap_filter)
        response = []
        for result in results:
            if result[0] is not None:
                data = {}
                school_node = ""
                if school_oriented:
                    school_node = f",OU={self.context.schoolmgr.school},"

                dn = result.get('distinguishedName', [b''])[0].decode()
                if school_node in dn:
                    for field in fields(objectclass):
                        if field.init:
                            value = result[1].get(field.name, None)
                            data[field.name] = self._filter_value(field, value)
                    if dict:
                        response.append(asdict(objectclass(**data)))
                    else:
                        response.append(objectclass(**data))
        if sortkey is not None:
            if dict:
                return sorted(response, key=lambda d: d.get(sortkey, None))
            else:
                return sorted(response, key=lambda d: getattr(d, sortkey))
        return response

    @staticmethod
    def _filter_value(field, value):
        """
        Middleware to decode values and convert it in an usable format (mostly
        compatible with json). Parameter field is given in order to find out the
        type of object.
        """

        # TODO : more exception catch on values
        if field.type.__name__ == 'str':
            # Something like [b'']
            if value is None:
                return ''
            return value[0].decode() if value is not None else ''

        if field.type.__name__ == 'list':
            # Something like [b'a', b'c']
            if value is None:
                return []
            return [v.decode() for v in value] if value is not None else []

        if field.type.__name__ == 'bool':
            # Something like [b'FALSE']
            if value is None:
                return False
            return value[0].capitalize() == b'True'

        # if field.type.__name__ == 'datetime':
            # Something like [b'20210520111726.0Z']
            # return datetime.strptime(value[0].decode(), '%Y%m%d%H%M%S.%fZ')

        if field.type.__name__ == 'int':
            # Something like [b'20']
            if value is None:
                return 0
            return int(value[0].decode())

        if field.type.__name__ == 'List':
            if value is None:
                return []
            # Creepy test
            if 'LMNSession' in str(field.type.__args__[0]):
                result = []
                for v in value:
                    data = v.decode().split(';')
                    members = data[2].split(',') if data[2] else []
                    membersCount = len(members)
                    result.append(LMNSession(data[0], data[1], members, membersCount))
                return result

        if value is None:
            return None

    def _get(self, ldap_filter):
        """
        Connect to ldap and perform the request.

        :param ldap_filter: Valid ldap filter
        :type ldap_filter: basestring
        :return: Raw result of the request
        :rtype: dict
        """

        l = ldap.initialize("ldap://localhost:389/")
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = ldap.VERSION3
        l.bind(params['binddn'], params['bindpw'])
        res = l.search_s(params['searchdn'], ldap.SCOPE_SUBTREE, ldap_filter, attrlist=['*'])
        l.unbind()
        return res

