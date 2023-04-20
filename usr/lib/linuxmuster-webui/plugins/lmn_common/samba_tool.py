from samba.auth import system_session
from samba.credentials import Credentials
from samba.param import LoadParm
from samba.samdb import SamDB
from samba.netcmd.gpo import get_gpo_info

lp = LoadParm()
creds = Credentials()
creds.guess(lp)
samdb = SamDB(url='/var/lib/samba/private/sam.ldb', session_info=system_session(),credentials=creds, lp=lp)

def get_gpos():
    gpos = {}
    gpos_infos = get_gpo_info(samdb, None)
    for gpo in gpos_infos:
        gpos[gpo['displayName'][0].decode()] = {
                'dn':str(gpo.dn), 
                'path':gpo['gPCFileSysPath'][0].decode(), 
                'gpo':gpo['name'][0].decode()
                }
    return gpos

GPOS = get_gpos()
