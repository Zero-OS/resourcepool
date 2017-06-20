#!/bin/bash
set -e

# This script require privileged access

apt-get update
apt-get install -y debootstrap

mkdir /mnt/ubuntu
debootstrap --include openssh-server,curl,ca-certificates --arch amd64 xenial /mnt/ubuntu

sed -i "s/main/main restricted universe multiverse/" /mnt/ubuntu/etc/apt/sources.list

rm -rf /mnt/ubuntu/etc/ssh/ssh_host_*
mkdir -p /mnt/ubuntu/root/.ssh

cd /mnt/ubuntu

mkdir -p /tmp/archives
tar -czf /tmp/archives/ubuntu1604.tar.gz *
