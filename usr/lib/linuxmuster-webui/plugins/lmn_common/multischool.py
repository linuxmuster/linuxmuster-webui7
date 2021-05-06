from aj.auth import AuthenticationService
from jadi import service

@service
class School():
    def __init__(self, context):
        self.context = context
        username = AuthenticationService.get(self.context).get_identity()
        profil = AuthenticationService.get(self.context).get_provider().get_profile(username)
        self.school = profil['activeSchool']

    def switch(self, school):
        # Switch to another school
        self.school = school
        # Do stuff to effectively change the school