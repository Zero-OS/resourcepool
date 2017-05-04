#!/bin/bash
set -e

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

apt-get update
apt-get install -y curl git

curl https://storage.googleapis.com/golang/go1.8.linux-amd64.tar.gz > /tmp/go1.8.linux-amd64.tar.gz
tar -C /usr/local -xzf /tmp/go1.8.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
mkdir -p /gopath
export GOPATH=/gopath

git clone -b "${branch}" https://github.com/g8os/grid.git $GOPATH/src/github.com/g8os/grid

cd $GOPATH/src/github.com/g8os/grid/api
go get -v

CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' .

mkdir -p /tmp/archives/
tar -czf "/tmp/archives/grid-api-${branch}.tar.gz" api
