import os
import sys
import pwd
import subprocess
import pexpect
import time
import smbclient

from smbprotocol.exceptions import SMBOSError
from getpass import getpass
from configparser import ConfigParser


def p(*args, end=""):
    print("\033[1m\033[38;5;214m", *args, "\033[39m\033[0m", end=end)

p("Samba domain to try (like server.linuxmuster.lan):")
domain =input()

smbconf = ConfigParser()
try:
    smbconf.read('/etc/samba/smb.conf')
    samba_realm = smbconf["global"]["realm"].lower()
    samba_domain = f'{smbconf["global"]["netbios name"]}.{samba_realm}'.lower()
except Exception:
    logging.error("Can not read realm and domain from smb.conf")
    samba_domain, samba_realm = '', ''

p(f"Samba domain used by the Webui --> {samba_domain}", end="\n")
p(f"Samba realm  used by the Webui --> {samba_realm}", end="\n")

p("Teacher login:")
teacher = input()

pw = getpass(prompt="\033[1m\033[38;5;214m Password:\033[39m\033[0m", stream=None)

uid = pwd.getpwnam(teacher).pw_uid
path = f'\\\\{domain}\\default-school\\teachers\\{teacher}'

p("Getting Kerberos ticket", end="\n")
child = pexpect.spawn('/usr/bin/kinit', ['-c', f'/tmp/krb5cc_{uid}', teacher])
child.expect('.*')
child.sendline(pw)

# Waiting until the ticket is written
time.sleep(2)

if not os.path.isfile(f'/tmp/krb5cc_{uid}'):
    p("No valid Kerberos ticket found !")
    sys.exit()

p(f"Setting process uid={uid} and gid=100 for Kerberos ticket", end="\n")
os.chown(f'/tmp/krb5cc_{uid}', uid, 100)
os.setgid(100)
os.setuid(uid)

try:
    p(f"Files located at {path}:", end="\n\n")
    files = []
    for f in smbclient.scandir(path):
        if f.is_dir():
            files.append(f"D --> {f.name}\n")
        else:
            files.append(f"F --> {f.name}\n")
    files.sort()
    print("\033[1m\033[92m", *files, "\033[39m\033[0m")
except Exception as e:
    print(e)

