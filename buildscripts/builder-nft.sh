#!/bin/bash
set -ex

apt-get update
apt-get install -y wget build-essential git autoconf libtool automake libmnl-dev pkg-config ml-yacc bison flex

ROOTDIR="/tmp/nft/root"
mkdir -p "${ROOTDIR}"/bin
mkdir -p "${ROOTDIR}"/etc

cd "${ROOTDIR}"/..

#
# nftables
#
git clone git://git.netfilter.org/libnftnl
git clone git://git.netfilter.org/nftables

# libnftnl
pushd libnftnl

./autogen.sh
./configure --prefix "${ROOTDIR}"/

make
make install

popd

# nftables
export LIBNFTNL_CFLAGS="-I${ROOTDIR}/include"
export LIBNFTNL_LIBS="-L${ROOTDIR}/lib -lnftnl"

pushd nftables

./autogen.sh
./configure --prefix "${ROOTDIR}"/usr --disable-debug --without-cli --with-mini-gmp
echo "all:" > doc/Makefile

make

cp -a src/nft "${ROOTDIR}"/bin/

popd

#
# cleaning
#
rm -rf "${ROOTDIR}"/include
rm -rf "${ROOTDIR}"/lib/pkgconfig

#
# settings
#
echo "root:x:0:0:root:/root:/bin/ash" > "${ROOTDIR}"/etc/passwd
echo "nobody:x:65534:65534:nobody:/:/bin/false" >> "${ROOTDIR}"/etc/passwd

#
# library fix
#
git clone https://github.com/maxux/lddcopy

export LD_LIBRARY_PATH="${ROOTDIR}"/lib

bash lddcopy/lddcopy.sh "${ROOTDIR}"/bin/nft "${ROOTDIR}"

pushd "${ROOTDIR}"
rm -rf lib64
ln -s lib lib64
popd
tar -czf "/tmp/archives/nft.tar.gz" -C "${ROOTDIR}" .
