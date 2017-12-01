
#!/bin/bash
setupini="/var/lib/linuxmuster/setup.ini"
ajcfg="/usr/lib/linuxmuster-webui/plugins/lm_setup_wizard/template.yml"

binddn=$(cat $setupini |  grep basedn | awk '{print $3}')
bindpw=$(cat /etc/linuxmuster/.secret/global-binduser)
binduser=CN=global-binduser,OU=Management,OU=GLOBAL,$binddn
language=$(cat $setupini |  grep country | awk '{print $3}')
servername=$(cat $setupini |  grep servername | awk '{print $3}')

cp $ajcfg /etc/ajenti/
sed -i s/%%HOSTNAME%%/$hostname/ $ajcfg
sed -i s/%%BINDDN%%/$bindn/ $ajcfg
sed -i s/%%BINDPW%%/$bindpw/ $ajcfg
sed -i s/%%SUFFIX%%/$suffix/ $ajcfg
sed -i s/%%LANGUAGE%%/$language/ $ajcfg
sed -i s/%%SERVERNAME%%/$servername/ $ajcfg
