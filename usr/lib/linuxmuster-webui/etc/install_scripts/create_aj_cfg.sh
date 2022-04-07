#!/bin/bash
setupini="/var/lib/linuxmuster/setup.ini"
ajtemplate="/usr/lib/linuxmuster-webui/etc/config_templates/template-ajenti.yml"
wutemplate="/usr/lib/linuxmuster-webui/etc/config_templates/template-webui.yml"
wucfg="/etc/linuxmuster/webui/config.yml"
ajcfg="/etc/ajenti/config.yml"

basedn=$(cat $setupini |  grep basedn | awk '{print $3}')
bindpw=$(cat /etc/linuxmuster/.secret/global-binduser)
binduser=CN=global-binduser,OU=Management,OU=GLOBAL,$basedn
language=$(cat $setupini |  grep country | awk '{print $3}')
servername=$(cat $setupini |  grep servername | awk '{print $3}')
domainname=$(cat $setupini |  grep domainname | awk '{print $3}')

mkdir -p /etc/linuxmuster/webui

if [ -f $wucfg ]; then
   rm  $wucfg
else
   echo "File $wucfg does not exist."
fi

if [ -f $ajcfg ]; then
   rm  $ajcfg
else
   echo "File $ajcfg does not exist."
fi

cp $ajtemplate $ajcfg
cp $wutemplate $wucfg

sed -i s/%%BINDUSER%%/$binduser/ $wucfg
sed -i s/%%BINDPW%%/$bindpw/ $wucfg
sed -i s/%%SERVERNAME%%/$servername/ $wucfg
sed -i s/%%BASEDN%%/$basedn/ $wucfg

sed -i s/%%LANGUAGE%%/$language/ $ajcfg
sed -i s/%%SERVERNAME%%/$servername/ $ajcfg
sed -i s/%%DOMAINNAME%%/$domainname/ $ajcfg

echo "Bundle certificate for webui"
cat /etc/linuxmuster/ssl/$servername.key.pem /etc/linuxmuster/ssl/$servername.cert.pem >  /etc/linuxmuster/ssl/$servername.cert.bundle.pem

echo "Run Sophomorix-UI to add permissions"
sophomorix-ui >/dev/null 2>&1
