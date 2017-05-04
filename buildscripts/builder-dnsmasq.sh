#!/bin/bash
set -e

apt-get update
apt-get install -y build-essential git

cd /opt
git clone --depth=1 https://github.com/maxux/lddcopy.git
git clone --depth=1 git://thekelleys.org.uk/dnsmasq.git
cd dnsmasq

make

mkdir -p /tmp/target
mkdir -p /tmp/archives
mkdir -p /tmp/target/etc
mkdir -p /tmp/target/bin
mkdir -p /tmp/target/lib

pushd /tmp/target
ln -s lib lib64
popd


cp dnsmasq.conf.example /tmp/target/etc/dnsmasq.conf
cp src/dnsmasq /tmp/target/bin/
strip -s /tmp/target/bin/dnsmasq
bash /opt/lddcopy/lddcopy.sh /tmp/target/bin/dnsmasq /tmp/target


cd /tmp/target
tar -czf /tmp/archives/dnsmasq.tar.gz *
