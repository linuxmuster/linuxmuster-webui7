from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import ldap

def extract_name(dn):
    # 'CN=11c,OU=11c,OU=Students,OU=default-school,OU=SCHOOLS...' becomes :
    # [[('CN', '11c', 1)], [('OU', '11c', 1)], [('OU', 'Students', 1)],...]
    try:
        return ldap.dn.str2dn(dn)[0][0][1]
    except KeyError:
        return ''

def extract_schoolclasses(membership):
    schoolclasses = []
    for dn in membership:
        if 'OU=Students' in dn:
            schoolclass = extract_name(dn)
            if schoolclass:
                schoolclasses.append(schoolclass)
    return schoolclasses

def extract_projects(membership):
    projects = []
    for dn in membership:
        if 'OU=Projects' in dn:
            project = extract_name(dn)
            if project:
                projects.append(project)
    return projects

@dataclass
class LMNProject:
    cn: str
    description: str
    distinguishedName: str
    mail: list
    member: list
    name: str
    sAMAccountName: str
    sAMAccountType: str
    sophomorixAddMailQuota: list
    sophomorixAddQuota: list
    sophomorixAdminGroups: list
    sophomorixAdmins: list
    sophomorixCreationDate: str # datetime
    sophomorixHidden: bool
    sophomorixJoinable: bool
    sophomorixMailAlias: bool
    sophomorixMailList: bool
    sophomorixMailQuota: list
    sophomorixMaxMembers: int
    sophomorixMemberGroups: list
    sophomorixMembers: list
    sophomorixQuota: list
    sophomorixSchoolname: str
    sophomorixStatus: str
    sophomorixType: str

@dataclass
class LMNSchoolClass:
    cn: str
    description: str
    distinguishedName: str
    mail: list
    member: list
    memberOf: list
    name: str
    sAMAccountName: str
    sAMAccountType: str
    sophomorixAddMailQuota: list
    sophomorixAddQuota: list
    sophomorixAdmins: list
    sophomorixCreationDate: str # datetime
    sophomorixHidden: bool
    sophomorixJoinable: bool
    sophomorixMailAlias: list
    sophomorixMailList: list
    sophomorixMailQuota: list
    sophomorixMaxMembers: int
    sophomorixMembers: list
    sophomorixQuota: list
    sophomorixSchoolname: str
    sophomorixStatus: str
    sophomorixType: str

@dataclass
class LMNSession:
    sid: str
    name: str
    participants: list

@dataclass
class LMNUser:
    cn: str
    displayName: str
    distinguishedName: str
    givenName: str
    homeDirectory: str
    homeDrive: str
    mail: list
    memberOf: list
    name: str
    proxyAddresses: list
    sAMAccountName: str
    sAMAccountType: str
    sn: str
    sophomorixAdminClass: str
    sophomorixAdminFile: str
    sophomorixBirthdate: str
    sophomorixCloudQuotaCalculated: list
    sophomorixComment: str
    sophomorixCreationDate: str # datetime
    sophomorixCustom1: str
    sophomorixCustom2: str
    sophomorixCustom3: str
    sophomorixCustom4: str
    sophomorixCustom5: str
    sophomorixCustomMulti1: list
    sophomorixCustomMulti2: list
    sophomorixCustomMulti3: list
    sophomorixCustomMulti4: list
    sophomorixCustomMulti5: list
    sophomorixDeactivationDate: str # datetime
    sophomorixExamMode: list
    sophomorixExitAdminClass: str
    sophomorixFirstnameASCII: str
    sophomorixFirstnameInitial: str
    sophomorixFirstPassword: str
    sophomorixIntrinsic2: list
    sophomorixMailQuotaCalculated: list
    sophomorixMailQuota: list
    sophomorixQuota: list
    sophomorixRole: str
    sophomorixSchoolname: str
    sophomorixSchoolPrefix: str
    sophomorixSessions: List[LMNSession]
    sophomorixStatus: str
    sophomorixSurnameASCII: str
    sophomorixSurnameInitial: str
    sophomorixTolerationDate: str # datetime
    sophomorixUnid: str
    sophomorixUserToken: str
    sophomorixWebuiDashboard: list
    sophomorixWebuiPermissionsCalculated: list
    unixHomeDirectory: str
    internet: bool = field(init=False)
    intranet: bool = field(init=False)
    printing: bool = field(init=False)
    webfilter: bool = field(init=False)
    wifi: bool = field(init=False)
    projects: list = field(init=False)
    schoolclasses: list = field(init=False)

    def extract_management(self):
        for group in ['internet', 'intranet', 'printing', 'webfilter', 'wifi']:
            setattr(self, group, False)
            for dn in self.memberOf:
                if dn.startswith(f"CN={group},OU=Management"):
                    setattr(self, group, True)

    def __post_init__(self):
        self.schoolclasses = extract_schoolclasses(self.memberOf)
        self.projects = extract_projects(self.memberOf)
        self.extract_management()

