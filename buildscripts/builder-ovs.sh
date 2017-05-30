#!/bin/bash
set -e

source $(dirname $0)/tools.sh

apt-get update
apt-get install -y openvswitch-switch
ensure_lddcopy
ensure_go

OVSPLUGIN=$GOPATH/src/github.com/zero-os/openvswitch-plugin

go get -u -v -d github.com/zero-os/openvswitch-plugin


TARGET=/tmp/target-ovs

mkdir -p /tmp/archives
rm -rf "$TARGET"
mkdir "$TARGET"
mkdir -p "$TARGET/var/lib/corex/plugins"
mkdir -p "$TARGET/bin"
mkdir -p "$TARGET/etc/openvswitch"
mkdir -p "$TARGET/run/openvswitch"
mkdir -p "$TARGET/var/run/openvswitch"
mkdir -p "$TARGET/tmp"

pushd "$TARGET"
ln -s lib lib64
popd

pushd $OVSPLUGIN
go build -o "$TARGET/var/lib/corex/plugins/ovs-plugin"
cp startup.toml "$TARGET/.startup.toml"
cp plugin.toml "$TARGET/.plugin.toml"
popd


copypkg openvswitch-switch "$TARGET"
copypkg openvswitch-common "$TARGET"
pushd "$TARGET/usr/sbin"
ln -s /usr/lib/openvswitch-switch/ovs-vswitchd
popd
#bash /opt/lddcopy/lddcopy.sh "/bin/mkdir" "$TARGET"
#cp /bin/mkdir "$TARGET/bin/mkdir"

cd "$TARGET"
tar -czf /tmp/archives/ovs.tar.gz .
