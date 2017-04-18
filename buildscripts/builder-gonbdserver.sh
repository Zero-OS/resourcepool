#!/bin/bash
set -e

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

apt-get update
apt-get install -y curl git

source get_go.sh

go get -v -d github.com/g8os/blockstor/nbdserver
cd $GOPATH/src/github.com/g8os/blockstor/nbdserver

git fetch origin "${branch}:${branch}" || true
git checkout "${branch}" || true

CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' .

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/gonbdserver-${branch}.tar.gz" nbdserver
