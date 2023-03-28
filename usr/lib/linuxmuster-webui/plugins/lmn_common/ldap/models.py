from dataclasses import dataclass
from datetime import datetime
from typing import List

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

def extract_management(membership):
    management = []
    for dn in membership:
        if 'OU=Management' in dn:
            group = extract_name(dn)
            if group in ['internet', 'intranet', 'printing', 'webfilter', 'wifi']:
                management.append(group)
    return management

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
    sophomorixCreationDate: datetime
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
    sophomorixCreationDate: datetime
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
    members: list

    def __post_init__(self):
        self.created = datetime.strptime(self.sid, '%Y-%m-%d_%H-%M-%S')

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
    sophomorixCreationDate: datetime
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
    sophomorixDeactivationDate: datetime
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
    sophomorixTolerationDate: datetime
    sophomorixUnid: str
    sophomorixUserToken: str
    sophomorixWebuiDashboard: list
    sophomorixWebuiPermissionsCalculated: list
    unixHomeDirectory: str

    def __post_init__(self):
        self.schoolclasses = extract_schoolclasses(self.memberOf)
        self.projects = extract_projects(self.memberOf)
        self.management = extract_management(self.memberOf)

