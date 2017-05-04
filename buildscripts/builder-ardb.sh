#!/bin/bash
set -e

apt-get update
apt-get install -y build-essential git wget bzip2 cmake libsnappy-dev libbz2-dev unzip libssl-dev

cd /opt
git clone --depth=1 https://github.com/maxux/lddcopy.git
git clone --depth=1 https://github.com/yinqiwen/ardb.git
cd ardb

sed -i 's#home  ..#home   /mnt/data#g' ardb.conf
mkdir -p /tmp/target
mkdir -p /tmp/archives

for engine in rocksdb lmdb forestdb; do
    storage_engine=$engine make

    rm -rf /tmp/target/*
    mkdir -p /tmp/target/etc
    mkdir -p /tmp/target/bin
    mkdir -p /tmp/target/mnt/data

    cp ardb.conf /tmp/target/etc/
    cp src/ardb-server /tmp/target/bin/
    strip -s /tmp/target/bin/ardb-server
    bash /opt/lddcopy/lddcopy.sh /tmp/target/bin/ardb-server /tmp/target

    pushd /tmp/target
    tar -czf /tmp/archives/ardb-$engine.tar.gz *
    popd
done
