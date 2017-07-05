#!/bin/sh
set -e
source $(dirname $0)/tools.sh
ensure_lddcopy

TARGET=/tmp/influxdb
url="https://dl.influxdata.com/influxdb/releases/influxdb-1.2.4_linux_amd64.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
wget "$url" -O "${TARGET}/influxdb.tar.gz"
tar xf $TARGET/influxdb.tar.gz -C $TARGET
INFLUXROOT=$TARGET/influxdb-1.2.4-1
rm -rf $INFLUXROOT/usr/lib $INFLUXROOT/usr/share
lddcopy "${INFLUXROOT}/usr/bin/influx" "${INFLUXROOT}"
lddcopy "${INFLUXROOT}/usr/bin/influxd" "${INFLUXROOT}"
mkdir -p /tmp/archives/
tar czf /tmp/archives/influxdb.tar.gz -C $INFLUXROOT .
