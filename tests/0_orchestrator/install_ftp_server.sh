#!/usr/bin bash

update_proftp_configuration(){
sudo cat >> /etc/proftpd/proftpd.conf << EOL
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
sudo apt-get install proftpd-basic -y
sudo apt-get install lftp
sudo cp /etc/proftpd/proftpd.conf /etc/proftpd/proftpd.conf.orig
update_proftp_configuration
sudo systemctl restart proftpd
File_name=test.text
touch ${File_name}
ftpserver_ip=$(ifconfig bond0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
upload_file_in_ftp ${ftpserver_ip}  ${File_name}
