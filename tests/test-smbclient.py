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


def p(*args, end="\n"):
    print("\033[1m\033[38;5;214m", *args, "\033[39m\033[0m", end=end)

p('This script helps to test some domains to access samba shares, and you can try your own path too.', end="\n")

smbconf = ConfigParser()
try:
    smbconf.read('/etc/samba/smb.conf')
    samba_realm = smbconf["global"]["realm"].lower()
    samba_netbios = smbconf["global"]["netbios name"].lower()
    samba_domain = f'{samba_netbios}.{samba_realm}'
except Exception:
    print("Can not read configuration from smb.conf")
    samba_domain, samba_netbios, samba_realm = '', '', ''

p(f"Samba realm used by the Webui --> {samba_realm}")
p(f"Samba netbios used by the Webui --> {samba_netbios}")
p(f"Samba domain used by the Webui --> {samba_domain}")
p("Samba domain to try (optional, something like server.linuxmuster.lan):", end="")
domain_user = input()

p("Teacher login:", end="")
teacher = input()

pw = getpass(prompt="\033[1m\033[38;5;214m Password:\033[39m\033[0m", stream=None)

uid = pwd.getpwnam(teacher).pw_uid

p("Getting Kerberos ticket")
child = pexpect.spawn('/usr/bin/kinit', ['-c', f'/tmp/krb5cc_{uid}', teacher])
child.expect('.*')
child.sendline(pw)

# Waiting until the ticket is written
time.sleep(2)

if not os.path.isfile(f'/tmp/krb5cc_{uid}'):
    print("\033[1m\033[91m No valid Kerberos ticket found ! \033[39m\033[0m")
    sys.exit()

p(f"Setting process uid={uid} and gid=100 for Kerberos ticket")
os.chown(f'/tmp/krb5cc_{uid}', uid, 100)
os.setgid(100)
os.setuid(uid)

report = ""
hosts =  [samba_netbios, samba_realm, samba_domain]
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

print("\n", "#"*80, "\n")
p('REPORT:', end="\n\n")
print(report)
