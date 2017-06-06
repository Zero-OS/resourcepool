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

git clone -b "${branch}" https://github.com/github.com/zero-os/0-orchestrator.git $GOPATH/src/github.com/github.com/zero-os/0-orchestrator

cd $GOPATH/src/github.com/github.com/zero-os/0-orchestrator/api
go get -v

CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' .

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/rest-api-${branch}.tar.gz" api
