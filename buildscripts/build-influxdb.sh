#!/bin/sh
set -e

TARGET=/tmp/influxdb
url="https://dl.influxdata.com/influxdb/releases/influxdb-1.2.4_linux_amd64.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
mkdir -p $TARGET/bin
wget "$url" -O "${TARGET}/influxdb.tar.gz"
tar xf $TARGET/influxdb.tar.gz -C $TARGET/bin influxdb
mkdir -p /tmp/archives/
tar czf /tmp/archives/influxdb.tar.gz -C $TARGET bin