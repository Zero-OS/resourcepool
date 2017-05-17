#!/bin/bash
set -e

# This script require privileged access

apt-get update
apt-get install -y debootstrap

mkdir /mnt/ubuntu
debootstrap --arch amd64 xenial /mnt/ubuntu
sed -i "s/main/main multiverse universe/" /mnt/ubuntu/etc/apt/sources.list

cd /mnt/ubuntu

mkdir /tmp/archives
tar -czf /tmp/archives/ubuntu1604.tar.gz *
