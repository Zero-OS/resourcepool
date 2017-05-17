#!/bin/bash
set -e
source $(dirname $0)/tools.sh
ensure_go

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

apt-get update
apt-get install -y curl git

BLOCKSTOR=$GOPATH/src/github.com/g8os/blockstor

pushd $BLOCKSTOR
git fetch origin
git checkout -B "${branch}" origin/${branch}
rm -rf bin/*
make
popd

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/blockstor-${branch}.tar.gz" -C $BLOCKSTOR/ bin
