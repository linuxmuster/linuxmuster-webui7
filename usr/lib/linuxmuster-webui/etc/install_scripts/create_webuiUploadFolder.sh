#!/bin/bash
# check if samba already installed
installed=$(cat /etc/samba/smb.conf | grep active\ directory\ domain\ controller)
ACLS="/usr/lib/linuxmuster-webui/etc/install_scripts/webuiUpload.ntacl"

if [ -d "/srv/webuiUpload/" ];then
    rm -R /srv/webuiUpload/
fi

mkdir -p /srv/webuiUpload/
if [ -z "$installed" ];then
    echo "not installed skip setting acl on webuiUpload"
else
    workgroup=$(cat /etc/samba/smb.conf | grep workgroup | awk '{print $3}')
    sed -i "s/LINUXMUSTER/$workgroup/" $ACLS
    setfacl --set-file $ACLS /srv/webuiUpload
fi
