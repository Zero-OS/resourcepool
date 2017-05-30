#!/bin/bash
set -e
source $(dirname $0)/tools.sh
ensure_go

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

CLOUDINIT=github.com/zero-os/cloud-init-server

go get -v -d $CLOUDINIT

cd $GOPATH/src/$CLOUDINIT

git fetch origin "${branch}:${branch}" || true
git checkout "${branch}" || true

mkdir -p build/bin
mkdir -p build/etc/cloud-init
CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static" -s -w' -o build/bin/cloud-init-server .

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/cloud-init-server-${branch}.tar.gz" -C $GOPATH/src/$CLOUDINIT/build .
