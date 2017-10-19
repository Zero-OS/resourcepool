#!/bin/bash
set -e
source $(dirname $0)/tools.sh

ensure_go

apt-get update
apt-get install -y curl git


GOPATH=/gopath
ORCH=$ORCH
mkdir -p $GOPATH/src/github.com/zero-os

mv /0-orchestrator $ORCH


cd $ORCH/api
CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' .

tar -czf "/target/0-orchestrator.tar.gz" api
