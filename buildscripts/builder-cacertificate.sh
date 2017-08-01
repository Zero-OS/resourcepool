#!/bin/bash
set -e

source $(dirname $0)/tools.sh

aptupdate
aptinstall ca-certificates

mkdir -p /tmp/target
mkdir -p /tmp/archives
mkdir -p /tmp/target/etc
mkdir -p /tmp/target/usr/sbin
mkdir -p /tmp/target/usr/share
mkdir -p /tmp/target/lib

pushd /tmp/target
ln -fs lib lib64
popd

cp -r /etc/ssl /tmp/target/etc/ssl
cp -r /etc/ca-certificates /tmp/target/etc/ca-certificates
cp /usr/sbin/update-ca-certificates /tmp/target/usr/sbin/update-ca-certificates
cp -r /usr/share/ca-certificates /tmp/target/usr/share/ca-certificates


cd /tmp/target
tar -czf /tmp/archives/cacertificates.tar.gz *
