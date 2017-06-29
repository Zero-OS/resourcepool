#!/bin/sh
set -e
source $(dirname $0)/tools.sh
ensure_lddcopy

TARGET=/tmp/grafana
VERSION=4.3.2
url="https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-${VERSION}.linux-x64.tar.gz"

#rm -rf $TARGET
mkdir -p $TARGET
mkdir -p $TARGET/root/opt/grafana
#wget "$url" -O "${TARGET}/grafana.tar.gz"
tar xf $TARGET/grafana.tar.gz -C $TARGET grafana-${VERSION}/public grafana-${VERSION}/bin grafana-${VERSION}/conf
# restructure
pushd $TARGET
mv grafana-${VERSION}/bin root/bin
mv grafana-${VERSION}/conf root/opt/grafana
mv grafana-${VERSION}/public root/opt/grafana
popd
lddcopy "${TARGET}/root/bin/grafana-server" "${TARGET}/root"
mkdir -p /tmp/archives/
tar czf /tmp/archives/grafana.tar.gz -C $TARGET/root .
