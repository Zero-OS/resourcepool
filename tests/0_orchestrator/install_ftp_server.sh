#!/usr/bin bash

update_proftp_configuration(){
sudo bash -c "cat >> /etc/proftpd/proftpd.conf" << EOL
 <Anonymous ~ftp>
   User                         ftp
   Group                                nogroup
   # We want clients to be able to login with "anonymous" as well as "ftp"
   UserAlias                    anonymous ftp
   # Cosmetic changes, all files belongs to ftp user
   DirFakeUser  on ftp
   DirFakeGroup on ftp

   RequireValidShell            off

 </Anonymous>
Include /etc/proftpd/conf.d/
EOL
                          }
upload_file_in_ftp(){
lftp  $1 <<END_SCRIPT
mkdir pub
cd pub
put $2
quit
END_SCRIPT
exit 0
~
}
sudo apt-get update
sudo apt-get install debconf-utils
echo "proftpd-basic shared/proftpd/inetd_or_standalone select standalone" | debconf-set-selections
sudo apt-get install proftpd-basic -y
sudo apt-get install lftp
sudo cp /etc/proftpd/proftpd.conf /etc/proftpd/proftpd.conf.orig
update_proftp_configuration
sudo service proftpd restart
File_name=test.text
touch ${File_name}
ftpserver_ip=$(hostname -I|awk '{ print $1}')
server_ip=$(ip addr show zt0 | grep 'inet')
echo "*************************************ftpserver${server_ip}*****************************"
server_ip=$(echo ${server_ip} | awk '{print $2}' | awk -F"/" '{print $1}')
echo "*******************************************************************************************"
echo "*************************************ftpserver*${server_ip}*****************************"
sed -ie "s/^ftp_server.*$/ftp_server=ftp:\/\/${server_ip}:21\//" test_suite/config.ini
#upload_file_in_ftp ${ftpserver_ip}  ${File_name}
