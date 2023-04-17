from dataclasses import dataclass
from datetime import datetime

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
