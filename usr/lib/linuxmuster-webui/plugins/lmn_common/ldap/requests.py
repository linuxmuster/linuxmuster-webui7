import re

from aj.plugins.lmn_common.ldap.connector import LdapConnector
from aj.plugins.lmn_common.ldap.models import *


def lmnapi(pattern):
    """
    API decorator to associate with an URL.
    """

    def decorator(f):
        f.url_pattern = re.compile(f'^{pattern}$')
        return f
    return decorator

class LMNLdapRequests:
    def __init__(self, context):
        self.context = context
        self.lc = LdapConnector(self.context)
        self.methods = [getattr(self,method) for method in dir(self) if method.startswith('get_')]

    def get(self, url, **kwargs):
        """
        Parse all urls and find the correct API to handle the request.
        """

        for method in self.methods:
            match = method.url_pattern.match(url)
            if match:
                data = match.groupdict()
                return method(**data, **kwargs)


    # SINGLE ENTRIES
    # TODO : . in username should not be allowed here because it may cause some problems with CLI
    # (like chown). It's allowed only for compatibility reasons in some schools.
    @lmnapi(r'/user/(?P<username>[\w\-\.]*)')
    def get_user(self, username, **kwargs):
        """
        Get all details from a specific user.
        Return a LMNUser data object.
        """

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

    @lmnapi(r'/schoolclass/(?P<schoolclass>[\w ]*)')
    def get_schoolclass(self, schoolclass, **kwargs):
        """
        Get all details from a specific schoolclass.
        Return a LMNSchoolClass data object
        """

        ldap_filter = f"""(&(cn={schoolclass})(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_single(LMNSchoolClass, ldap_filter, **kwargs)

    @lmnapi(r'/project/(?P<project>[a-z0-9_\-]*)')
    def get_project(self, project, **kwargs):
        """
        Get all details from a specific project.
        Return a LMNProject data object
        """

        ldap_filter = f"""(&(cn={project})(objectClass=group)(sophomorixType=project))"""

        return self.lc.get_single(LMNProject, ldap_filter, **kwargs)

    # COLLECTION OF ENTRIES
    @lmnapi(r'/schoolclass/(?P<schoolclass>[a-z0-9\-]*)/students')
    def get_all_students_from_schoolclass(self, schoolclass, **kwargs):
        """
        Get all students details from a specific schoolclass.
        Return a list of LMNUser data objects.
        """

        ldap_filter = f"""(&
                                    (objectClass=user)
                                    (sophomorixAdminClass={schoolclass})
                                    (sophomorixRole=student)
                                )"""

        return self.lc.get_collection(LMNUser, ldap_filter, **kwargs)

    @lmnapi(r'/schoolclasses')
    def get_all_schoolclasses(self, **kwargs):
        """
        Get all schoolclasses details.
        Return a list of LMNSchoolClass data objects.
        """

        ldap_filter = """(&(objectClass=group)(sophomorixType=adminclass))"""

        return self.lc.get_collection(LMNSchoolClass, ldap_filter, **kwargs)

    @lmnapi(r'/schoolclasses/search/(?P<query>\w*)')
    def get_results_search_schoolclasses(self, query, **kwargs):
        """
        Get all details from a search about schoolclasses.
        Return a list of LMNSchoolClass data objects.
        """

        ldap_filter = f"""(&(objectClass=group)(sophomorixType=adminclass)(cn=*{query}*))"""

        return self.lc.get_collection(LMNSchoolClass, ldap_filter, **kwargs)

    @lmnapi(r'/projects')
    def get_all_projects(self, **kwargs):
        """
        Get all projects details.
        Return a list of LMNProject data objects.
        """

        ldap_filter = """(&(objectClass=group)(sophomorixType=project))"""

        return self.lc.get_collection(LMNProject, ldap_filter, **kwargs)

    @lmnapi(r'/role/(?P<role>.*)')
    def get_all_from_role(self, role='teacher', **kwargs):
        """
        Get all user from a same role.
        Return a list of LMNUser data objects.
        """

        ldap_filter = f"(&(objectClass=user)(sophomorixRole={role}))"

        return self.lc.get_collection(LMNUser, ldap_filter, **kwargs)

    @lmnapi(r'/users/search/(?P<selection>\w*)/(?P<query>\w*)')
    def get_results_search_user(self, query, selection=[], **kwargs):
        """
        Get all details from a search on a specific user login scheme and a
        selection of roles.
        Return a list of LMNUser data object.
        """

        role_filter = {
            'all': """
                    (sophomorixRole=globaladministrator)
                    (sophomorixRole=schooladministrator)
                    (sophomorixRole=teacher)
                    (sophomorixRole=student)
                """,
            'admins': """
                    (sophomorixRole=globaladministrator)
                    (sophomorixRole=schooladministrator)
                """,
        }

        for role in ['globaladministrator', 'schooladministrator', 'teacher', 'student']:
            role_filter[role] = f'(sophomorixRole={role})'

        ldap_filter = f"""(&
                                    (sAMAccountName=*{query}*)
                                    (objectClass=user)
                                    (|
                                        {role_filter[selection]}
                                    )
                                )"""

        return self.lc.get_collection(LMNUser, ldap_filter, **kwargs)