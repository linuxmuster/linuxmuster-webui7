#!/bin/bash
# check if samba already installed
installed=$(grep active\ directory\ domain\ controller /etc/samba/smb.conf)
ACLS="/usr/lib/linuxmuster-webui/etc/install_scripts/webuiUpload.ntacl"

if [ -d "/srv/webuiUpload/" ];then
    rm -R /srv/webuiUpload/
fi

mkdir -p /srv/webuiUpload/
if [ -z "$installed" ];then
    echo "not installed skip setting acl on webuiUpload"
else
    workgroup=$(testparm -l -s --parameter-name=workgroup 2>/dev/null)
    sed -i "s/LINUXMUSTER/$workgroup/" $ACLS
    setfacl --set-file $ACLS /srv/webuiUpload
fi
