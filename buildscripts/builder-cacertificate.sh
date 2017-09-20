#!/bin/bash
set -e

source $(dirname $0)/tools.sh

# aptupdate
# aptinstall ca-certificates

TARGET=/tmp/catarget
rm -rf $TARGET

mkdir -p $TARGET
mkdir -p /tmp/archives
mkdir -p $TARGET/etc
mkdir -p $TARGET/usr/sbin
mkdir -p $TARGET/usr/share
mkdir -p $TARGET/lib

pushd $TARGET
ln -fs lib lib64
popd

cp -r /etc/ssl $TARGET/etc/ssl
cp -r /etc/ca-certificates $TARGET/etc/ca-certificates
cp /usr/sbin/update-ca-certificates $TARGET/usr/sbin/update-ca-certificates
cp -r /usr/share/ca-certificates $TARGET/usr/share/ca-certificates


cd $TARGET
tar -czf /tmp/archives/cacertificates.tar.gz *
