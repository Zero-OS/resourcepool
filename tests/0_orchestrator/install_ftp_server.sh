#!/usr/bin bash

update_ftp_configuration(){
sudo cat >> /etc/vsftpd.conf << EOL
listen=NO
listen_ipv6=YES
allow_writeable_chroot=YES
anonymous_enable=YES
local_enable=NO
write_enable=YES
anon_upload_enable=YES
anon_other_write_enable=YES
chroot_local_user=yes
anon_root=/var/ftp/
anon_mkdir_write_enable=YES
dirmessage_enable=YES
use_localtime=YES
no_anon_password=YES
xferlog_enable=YES
connect_from_port_20=YES
EOL
                          }
upload_file_in_ftp(){
ftp -v -n  $1 <<END_SCRIPT
user ftp
cd pub
mkdir file
cd file
put $2
quit
END_SCRIPT
exit 0
~
}

sudo apt-get update
echo "[#] Installing local ftp server ..."

sudo apt-get install vsftpd -y
sudo apt-get install ftp
sudo mv /etc/vsftpd.conf /etc/vsftpd.conf.orig

echo "[#] Update ftp_server  configuration. "
update_ftp_configuration
sudo systemctl restart vsftpd

echo "[#] Make sure that ftp_server is working by upload file . "
sudo mkdir -p /var/ftp/pub
sudo chmod 777 /var/ftp/pub
cd /var/ftp/pub
File_name=test.text
touch ${File_name}
ftpserver_ip=$(ifconfig bond0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
upload_file_in_ftp ${ftpserver_ip}  ${File_name}
