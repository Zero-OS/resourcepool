#!/bin/bash
set -e
source $(dirname $0)/tools.sh
ensure_lddcopy

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

apt-get update
apt-get install -y git gcc zlib1g-dev make wget xz-utils libglib2.0-dev libaio-dev

PERFORMANCE_TEST=/tmp/performance-test
TARGET=$PERFORMANCE_TEST/target

rm -rf $PERFORMANCE_TEST
mkdir -p $PERFORMANCE_TEST/src
mkdir -p $TARGET/bin
mkdir -p /tmp/archives


cd $PERFORMANCE_TEST/src
git clone --depth=1 https://github.com/axboe/fio
wget https://netix.dl.sourceforge.net/project/nbd/nbd/3.15.2/nbd-3.15.2.tar.xz
tar xf nbd-3.15.2.tar.xz

cd $PERFORMANCE_TEST/src/fio
./configure && make
cp fio $TARGET/bin

cd $PERFORMANCE_TEST/src/nbd-3.15.2
./configure && make
cp nbd-client $TARGET/bin

lddcopy $TARGET/bin/fio $TARGET
lddcopy $TARGET/bin/nbd-client $TARGET


pushd $TARGET
tar -czf "/tmp/archives/performance-test.tar.gz" *
popd
