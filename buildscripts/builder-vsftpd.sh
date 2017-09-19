#!/bin/sh
set -e
source $(dirname $0)/tools.sh
ensure_lddcopy

TARGET=/tmp/vsftpd
url="https://security.appspot.com/downloads/vsftpd-3.0.3.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
wget "$url" -O "${TARGET}/vsftpd.tar.gz"
tar xf $TARGET/vsftpd.tar.gz -C $TARGET
VSFTPDROOT=$TARGET/vsftpd-3.0.3
pushd $VSFTPDROOT
make
popd

rm -rf "${TARGET}/bin"
mkdir "${TARGET}/bin"
mv "${VSFTPDROOT}/vsftpd" "${TARGET}/bin"
rm -rf "$VSFTPDROOT"
lddcopy "${TARGET}/bin/vsftpd" "${TARGET}"
mkdir -p /tmp/archives/
tar czf /tmp/archives/vsftpd.tar.gz -C $TARGET .
