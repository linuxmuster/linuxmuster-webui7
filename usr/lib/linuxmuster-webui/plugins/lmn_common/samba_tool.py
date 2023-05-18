import os
import logging
from samba.auth import system_session
from samba.credentials import Credentials
from samba.param import LoadParm
from samba.samdb import SamDB
from samba.netcmd.gpo import get_gpo_info

lp = LoadParm()
creds = Credentials()
creds.guess(lp)
gpos_infos = {}

SAMDB_PATH = '/var/lib/samba/private/sam.ldb'

if os.path.isfile(SAMDB_PATH):
    try:
        samdb = SamDB(url=SAMDB_PATH, session_info=system_session(),credentials=creds, lp=lp)
        gpos_infos = get_gpo_info(samdb, None)
    except Exception:
        logging.error(f'Could not load {SAMDB_PATH}, is linuxmuster installed ?')
else:
    logging.warning(f'{SAMDB_PATH} not found, is linuxmuster installed ?')

def get_gpos():
    gpos = {}
    for gpo in gpos_infos:
        gpos[gpo['displayName'][0].decode()] = {
                'dn':str(gpo.dn), 
                'path':gpo['gPCFileSysPath'][0].decode(), 
                'gpo':gpo['name'][0].decode()
                }
    return gpos

GPOS = get_gpos()