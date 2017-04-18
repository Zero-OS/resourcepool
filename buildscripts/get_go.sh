#!/bin/bash
set -e

if ! which go || ! go version | grep go1.8 ; then
    curl https://storage.googleapis.com/golang/go1.8.linux-amd64.tar.gz > /tmp/go1.8.linux-amd64.tar.gz
    tar -C /usr/local -xzf /tmp/go1.8.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin
fi
if [ -z "$GOPATH" ]; then
    mkdir -p /gopath
    export GOPATH=/gopath
fi

