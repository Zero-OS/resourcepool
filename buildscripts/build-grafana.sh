#!/bin/sh
set -e

TARGET=/tmp/grafana
url="https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.3.2.linux-x64.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
mkdir -p $TARGET/bin
wget "$url" -O "${TARGET}/grafana.tar.gz"
tar xf $TARGET/grafana.tar.gz -C $TARGET/bin grafana
mkdir -p /tmp/archives/
tar czf /tmp/archives/grafana.tar.gz -C $TARGET bin