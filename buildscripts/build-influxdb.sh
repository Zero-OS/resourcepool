#!/bin/sh
set -e

TARGET=/tmp/influxdb
url="https://dl.influxdata.com/influxdb/releases/influxdb-1.2.4_linux_amd64.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
wget "$url" -O "${TARGET}/influxdb.tar.gz"
tar xf $TARGET/influxdb.tar.gz -C $TARGET
INFLUXROOT=$TARGET/influxdb-1.2.4-1
rm -rf $INFLUXROOT/usr/lib $INFLUXROOT/usr/share
mkdir -p /tmp/archives/
tar czf /tmp/archives/influxdb.tar.gz -C $INFLUXROOT .