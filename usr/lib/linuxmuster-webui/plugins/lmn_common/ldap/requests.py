from aj.plugins.lmn_common.ldap.connector import LdapConnector
from aj.plugins.lmn_common.ldap.models import *


class LMNLdapRequests:
    def __init__(self):
        self.lc = LdapConnector()

    # SINGLE ENTRIES
    def get_user(self, username):
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

        return self.lc.get_single(LMNUser, ldap_filter)

    def get_schoolclass(self, schoolclass):

        ldap_filter = f"""(&(cn={schoolclass})(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_single_entry(LMNSchoolClass, ldap_filter)

    # COLLECTION OF ENTRIES
    def get_all_students_from_schoolclass(self, schoolclass):

        ldap_filter = f"""(&
                                    (objectClass=user)
                                    (sophomorixAdminClass={schoolclass})
                                    (sophomorixRole=student)
                                )"""

        return self.lc.get_collection(LMNUser, ldap_filter)

    def get_all_schoolclasses(self):

        ldap_filter = """(&(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_collection(LMNSchoolClass, ldap_filter)

    def get_all_from_role(self, role='teacher'):

        ldap_filter = f"(&(objectClass=user)(sophomorixRole={role}))"

        return self.lc.get_collection(LMNUser, ldap_filter, sortkey='name')
