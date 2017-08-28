#!/bin/bash
set -e
source $(dirname $0)/tools.sh
ensure_go

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

go get -u github.com/zero-os/0-stor/server

STOR0=$GOPATH/src/github.com/zero-os/0-stor/

pushd $STOR0
git fetch origin
git checkout -B "${branch}" origin/${branch}
rm -rf bin/*
make server
rm -rf bin/.db
popd

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/0-stor-${branch}.tar.gz" -C $STOR0/ bin
