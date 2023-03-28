import re

from aj.plugins.lmn_common.ldap.connector import LdapConnector
from aj.plugins.lmn_common.ldap.models import *


def lmnapi(pattern):
    def decorator(f):
        f.url_pattern = re.compile(f'^{pattern}$')
        return f
    return decorator

class LMNLdapRequests:
    def __init__(self):
        self.lc = LdapConnector()
        self.methods = [getattr(self,method) for method in dir(self) if method.startswith('get_')]

    def get(self, url, **kwargs):
        for method in self.methods:
            match = method.url_pattern.match(url)
            if match:
                data = match.groupdict()
                return method(**data, **kwargs)


    # SINGLE ENTRIES
    @lmnapi(r'/user/(?P<username>\w*)')
    def get_user(self, username, **kwargs):
        ldap_filter = f"""(&
                                    (cn={username})
                                    (objectClass=user)
                                    (|
                                        (sophomorixRole=globaladministrator)
                                        (sophomorixRole=schooladministrator)
                                        (sophomorixRole=teacher)
                                        (sophomorixRole=student)
                                    )
                                )"""

        return self.lc.get_single(LMNUser, ldap_filter, **kwargs)

    @lmnapi(r'/schoolclass/(?P<schoolclass>\w*)')
    def get_schoolclass(self, schoolclass, **kwargs):

        ldap_filter = f"""(&(cn={schoolclass})(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_single_entry(LMNSchoolClass, ldap_filter, **kwargs)

    # COLLECTION OF ENTRIES
    @lmnapi(r'/schoolclass/(?P<schoolclass>[a-z0-9\-]*)/students')
    def get_all_students_from_schoolclass(self, schoolclass, **kwargs):
        ldap_filter = f"""(&
                                    (objectClass=user)
                                    (sophomorixAdminClass={schoolclass})
                                    (sophomorixRole=student)
                                )"""

        return self.lc.get_collection(LMNUser, ldap_filter, **kwargs)

    @lmnapi(r'/schoolclasses')
    def get_all_schoolclasses(self, **kwargs):

        ldap_filter = """(&(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_collection(LMNSchoolClass, ldap_filter, **kwargs)

    @lmnapi(r'/role/(?P<role>.*)')
    def get_all_from_role(self, role='teacher', **kwargs):

        ldap_filter = f"(&(objectClass=user)(sophomorixRole={role}))"

        return self.lc.get_collection(LMNUser, ldap_filter, **kwargs)
