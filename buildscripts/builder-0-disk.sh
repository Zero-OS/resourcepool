#!/bin/bash
set -e
source $(dirname $0)/tools.sh
ensure_go

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

go get -u -v -d github.com/zero-os/0-Disk/nbdserver
go get -u -v -d github.com/zero-os/0-Disk/zeroctl

DISK0=$GOPATH/src/github.com/zero-os/0-Disk/

pushd $DISK0
git fetch origin
git checkout -B "${branch}" origin/${branch}
rm -rf bin/*
make
popd

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/0-disk-${branch}.tar.gz" -C $DISK0/ bin
