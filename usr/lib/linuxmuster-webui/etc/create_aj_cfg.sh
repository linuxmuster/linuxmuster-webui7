#!/bin/bash
setupini="/var/lib/linuxmuster/setup.ini"
ajtemplate="/usr/lib/linuxmuster-webui/etc/template.yml"
ajcfg="/etc/ajenti/config.yml"

basedn=$(cat $setupini |  grep basedn | awk '{print $3}')
bindpw=$(cat /etc/linuxmuster/.secret/global-binduser)
binduser=CN=global-binduser,OU=Management,OU=GLOBAL,$basedn
language=$(cat $setupini |  grep country | awk '{print $3}')
servername=$(cat $setupini |  grep servername | awk '{print $3}')
domainname=$(cat $setupini |  grep domainname | awk '{print $3}')

if [ -f $ajcfg ]; then
   rm  $ajcfg
else
   echo "File $ajcfg does not exist."
fi

cp $ajtemplate $ajcfg

sed -i s/%%BINDUSER%%/$binduser/ $ajcfg
sed -i s/%%BINDPW%%/$bindpw/ $ajcfg
sed -i s/%%BASEDN%%/$basedn/ $ajcfg
sed -i s/%%LANGUAGE%%/$language/ $ajcfg
sed -i s/%%SERVERNAME%%/$servername/ $ajcfg
sed -i s/%%DOMAINNAME%%/$domainname/ $ajcfg

echo "Bundle certificate for webui"
cat /etc/linuxmuster/ssl/$servername.key.pem /etc/linuxmuster/ssl/$servername.cert.pem >  /etc/linuxmuster/ssl/$servername.cert.bundle.pem

echo "Run Sophomorix-UI to add permissions"
sophomorix-ui >/dev/null 2>&1
