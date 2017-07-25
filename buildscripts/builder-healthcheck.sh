# !/bin/bash
set -e

# This script require privileged access

apt-get update
apt-get install -y debootstrap
mkdir -p /mnt/ubuntu
debootstrap --include git-core,openssh-server,curl,ca-certificates,tcpdump  --arch amd64 xenial /mnt/ubuntu

sed -i "s/main/main restricted universe multiverse/" /mnt/ubuntu/etc/apt/sources.list
chroot /mnt/ubuntu /bin/bash -c "apt-get update && apt-get install ipmitool -y"
rm -rf /mnt/ubuntu/etc/ssh/ssh_host_*
mkdir -p /mnt/ubuntu/root/.ssh
cd /mnt/ubuntu
mkdir -p /tmp/archives
tar -czf /tmp/archives/healthcheck.tar.gz *
