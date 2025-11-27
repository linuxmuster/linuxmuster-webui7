#!/bin/bash

# Check if samba is already installed
installed=$(grep active\ directory\ domain\ controller /etc/samba/smb.conf)
ACLS="/usr/lib/linuxmuster-webui/etc/install_scripts/webuiUpload.ntacl"

if [ -d "/srv/webuiUpload/" ]; then
    rm -R /srv/webuiUpload/
fi

mkdir -p /srv/webuiUpload/
if [ -z "$installed" ]; then
    echo "Samba is not installed, skip setting acl on webuiUpload."
elif [ ! -e "/var/lib/linuxmuster/setup.ini" ]; then
    echo "linuxmuster.net is not configured, skip setting acl on webuiUpload."
else
    workgroup=$(testparm -l -s --parameter-name=workgroup 2>/dev/null)
    sed -i "s/LINUXMUSTER/$workgroup/" $ACLS
    setfacl --set-file $ACLS /srv/webuiUpload
    echo "ACl set on webuiUpload with WORKGROUP $workgroup"
fi
