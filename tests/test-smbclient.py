import os
import sys
import pwd
import subprocess
import pexpect
import time
import smbclient

from smbprotocol.exceptions import SMBOSError
from pwinput import pwinput
from linuxmusterTools.samba_util import DFS
from linuxmusterTools.lmnconfig import SAMBA_REALM, SAMBA_DOMAIN, SAMBA_NETBIOS

def p(*args, end="\n"):
    print("\033[1m\033[38;5;214m", *args, "\033[39m\033[0m", end=end)

p('This script helps to test some domains to access samba shares, and you can try your own path too.', end="\n\n")

print("-"*80, "\n")
p("## Checking Samba domains:")
p(f"\tSamba realm used by the Webui   --> {SAMBA_REALM}")
p(f"\tSamba netbios used by the Webui --> {SAMBA_NETBIOS}")
p(f"\tSamba domain used by the Webui  --> {SAMBA_DOMAIN}\n")
p("Samba domain to try (optional, something like server.linuxmuster.lan):", end="")
domain_user = input()

print("-"*80, "\n")
p("## Authentication:")
p("Teacher login:", end="")
teacher = input()
uid = pwd.getpwnam(teacher).pw_uid

if not teacher:
    print("\033[1m\033[91m Please enter a valid user login \033[39m\033[0m")
    sys.exit()

pw = pwinput(prompt="\033[1m\033[38;5;214m Password:\033[39m\033[0m")

if not pw:
    print("\033[1m\033[91m No password given, trying to authenticate via an existing Kerberos ticket \033[39m\033[0m")

print("-"*80, "\n")
p("## Getting Kerberos ticket")
child = pexpect.spawn('/usr/bin/kinit', ['-c', f'/tmp/krb5cc_{uid}', teacher])
if pw:
    child.expect('.*')
    child.sendline(pw)

# Waiting until the ticket is written
time.sleep(2)

if not os.path.isfile(f'/tmp/krb5cc_{uid}'):
    print("\033[1m\033[91m No valid Kerberos ticket found ! \033[39m\033[0m")
    sys.exit()

p(f"Setting process uid={uid} and gid=100 for Kerberos ticket /tmp/krb5cc_{uid}")
os.chown(f'/tmp/krb5cc_{uid}', uid, 100)
os.setgid(100)
os.setuid(uid)

report = ""
hosts =  [SAMBA_NETBIOS, SAMBA_REALM, SAMBA_DOMAIN]
if domain_user:
    hosts.append(domain_user)

for host in hosts:
    path = f'\\\\{host}\\default-school\\teachers\\{teacher}'
    print("\n", "#"*80, "\n")
    p(f'Trying with host {host} ...', end="")
    try:
        p(f"Files located at {path}:", end="\n\n")
        files = [""]
        for f in smbclient.scandir(path):
            if f.is_dir():
                files.append(f"D --> {f.name}\n")
            else:
                files.append(f"F --> {f.name}\n")
        files.sort()
        print(*files)
        result = f"\033[1m\033[92m SUCCESS with host {host}! \033[39m\033[0m"
        print(result)
    except Exception as e:
        result = f"\033[1m\033[91m FAILED with host {host}! \033[39m\033[0m"
        print(result)
        print("\033[1m\033[91m", e, "\033[39m\033[0m")
    report += f"{result}\n"

print("\n", "-"*80, "\n")
p('REPORT:', end="\n\n")
print(report)
