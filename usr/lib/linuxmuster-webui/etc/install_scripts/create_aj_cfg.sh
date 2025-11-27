#!/bin/bash
setupini="/var/lib/linuxmuster/setup.ini"
ajtemplate="/usr/lib/linuxmuster-webui/etc/config_templates/template-ajenti.yml"
wutemplate="/usr/lib/linuxmuster-webui/etc/config_templates/template-webui.yml"
wucfg="/etc/linuxmuster/webui/config.yml"
ajcfg="/etc/ajenti/config.yml"

basedn=$(cat $setupini |  grep basedn | awk '{print $3}')
bindpw=$(cat /etc/linuxmuster/.secret/global-binduser)
binduser="CN=global-binduser,OU=Management,OU=GLOBAL,$basedn"
language=$(cat $setupini |  grep country | awk '{print $3}')
servername=$(cat $setupini |  grep servername | awk '{print $3}')
domainname=$(cat $setupini |  grep domainname | awk '{print $3}')

mkdir -p /etc/linuxmuster/webui

# Remove old config files if provided
if [ -f $wucfg ]; then
   rm $wucfg
fi

if [ -f $ajcfg ]; then
   rm $ajcfg
fi

cp $ajtemplate $ajcfg
cp $wutemplate $wucfg

echo "#### Creating configuration files .............................. Success! ####"

sed -i s/%%BINDUSER%%/$binduser/ $wucfg
sed -i s/%%BINDPW%%/$bindpw/ $wucfg
sed -i s/%%SERVERNAME%%/$servername/ $wucfg
sed -i s/%%BASEDN%%/$basedn/ $wucfg

sed -i s/%%LANGUAGE%%/$language/ $ajcfg
sed -i s/%%SERVERNAME%%/$servername/ $ajcfg
sed -i s/%%DOMAINNAME%%/$domainname/ $ajcfg

SERVERKEY="/etc/linuxmuster/ssl/$servername.key.pem"
SERVERCERT="/etc/linuxmuster/ssl/$servername.cert.pem"

if [ -f $SERVERKEY ] && [ -f $SERVERCERT ]; then
  cat $SERVERKEY $SERVERCERT >  /etc/linuxmuster/ssl/$servername.cert.bundle.pem
  echo "#### Bundling certificates for Webui ........................... Success! ####"
else
  echo "#### Missing certificates in /etc/linuxmuster/ssl ................ ERROR! ####"
fi

sophomorix-ui >/dev/null 2>&1
echo "#### Running Sophomorix-UI to add permissions .................. Success! ####"
