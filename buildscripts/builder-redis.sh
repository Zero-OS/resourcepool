#!/bin/sh
set -e
source $(dirname $0)/tools.sh
ensure_lddcopy

TARGET=/tmp/redis
url="http://download.redis.io/releases/redis-3.2.9.tar.gz"

rm -rf $TARGET
mkdir -p $TARGET
wget "$url" -O "${TARGET}/redis.tar.gz"
tar xf $TARGET/redis.tar.gz -C $TARGET
REDISROOT=$TARGET/redis-3.2.9
pushd $REDISROOT
make
popd

mkdir "${TARGET}/bin" "${TARGET}/etc"
mv "${REDISROOT}/src/redis-server" "${TARGET}/bin"
mv "${REDISROOT}/redis.conf" "${TARGET}/etc"
rm -rf "$REDISROOT" "${TARGET}/redis.tar.gz"
lddcopy "${TARGET}/bin/redis-server" "${TARGET}"
mkdir -p /tmp/archives/
tar czf /tmp/archives/redis.tar.gz -C $TARGET .
