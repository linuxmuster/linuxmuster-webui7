# check if samba already installed
installed=$(cat /etc/samba/smb.conf | grep active\ directory\ domain\ controller)
rm -R /srv/webuiUpload/
mkdir -p /srv/webuiUpload/
if [ -z "$installed" ];then
    echo "not installed skip setting acl on webuiUpload"
else
    workgroup=$(cat /etc/samba/smb.conf | grep workgroup | awk '{print $3}')
    sed -i "s/LINUXMUSTER/$workgroup/" /usr/lib/linuxmuster-webui/etc/webuiUpload.ntacl
    setfacl --set-file /usr/lib/linuxmuster-webui/etc/webuiUpload.ntacl /srv/webuiUpload
fi