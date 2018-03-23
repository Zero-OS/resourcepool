#!/bin/bash
set -e

echo "[+] initializing orchestrator flist builder"
pushd /0-orchestrator
ORCH_BRANCH=`git rev-parse --abbrev-ref HEAD`
echo "[+] 0-orchestrator branch: ${ORCH_BRANCH}"
popd


echo "[+] creating base target layout"
TARGET=/mnt/target
ARCHIVE=/tmp/archives
LOCLANG="en_US.UTF-8"

mkdir -p ${TARGET}
mkdir -p ${TARGET}/usr/local/bin
mkdir -p ${TARGET}/etc/my_init.d
mkdir -p ${ARCHIVE}

echo "[+] configuring local system"
if ! grep -q "^${LOCLANG}" /etc/locale.gen; then
	echo "${LOCLANG} UTF-8" >> /etc/locale.gen
	locale-gen
fi

export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"

echo "[+] installing dependencies"
apt-get update
apt-get install -y python3-pip git curl gpgv2

echo "[+] installing orchestrator dependencies"
# try to install from the same branch as orchestrator, if doens't exsit, failback on master
if ! pip3 install --root ${TARGET} --upgrade "git+https://github.com/zero-os/0-core.git@${ORCH_BRANCH}#subdirectory=client/py-client"; then
    pip3 install --root ${TARGET} --upgrade "git+https://github.com/zero-os/0-core.git@master#subdirectory=client/py-client";
fi
pip3 install --root ${TARGET} --upgrade "git+https://github.com/zero-os/0-orchestrator.git@${ORCH_BRANCH}#subdirectory=pyclient"
pip3 install --root ${TARGET} --upgrade zerotier

curl https://storage.googleapis.com/golang/go1.9.linux-amd64.tar.gz > /tmp/go1.9.linux-amd64.tar.gz
tar -C /usr/local -xzf /tmp/go1.9.linux-amd64.tar.gz

export GOPATH=/gopath
mkdir -p $GOPATH

export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

echo "[+] downloading ays orchestrator server source code"
mkdir -p $GOPATH/src/github.com/zero-os
cp -r /0-orchestrator $GOPATH/src/github.com/zero-os

echo "[+] building orchestrator api server"
cd $GOPATH/src/github.com/zero-os/0-orchestrator/api
go get -u github.com/jteeuwen/go-bindata/...
go generate
go build -o ${TARGET}/usr/local/bin/orchestratorapiserver

echo "[+] building zerotier"
pushd /tmp/
git clone --depth=1 https://github.com/zerotier/ZeroTierOne

pushd ZeroTierOne
make one -j $(grep ^processor /proc/cpuinfo | wc -l)
cp -arv zerotier-{one,cli,idtool} ${TARGET}/usr/local/bin/
popd # ZeroTierOne

popd # /tmp

echo "[+] installing orchestrator repository files"
# cloning orchestrator code
mkdir -p ${TARGET}/opt/code/github/zero-os
pushd ${TARGET}/opt/code/github/zero-os
cp -r /0-orchestrator .
popd

echo "[+] installing caddy"
# installing caddy
curl https://caddyserver.com/download/linux/amd64?plugins=http.filemanager,http.cors > /tmp/caddy.tar.gz
tar -xvf /tmp/caddy.tar.gz -C /tmp/
mv /tmp/caddy ${TARGET}/usr/local/bin/

echo "[+] optimizing size"
strip -s ${TARGET}/usr/local/bin/caddy
strip -s ${TARGET}/usr/local/bin/orchestratorapiserver

echo "[+] creating the archive"
pushd ${TARGET}
tar -czf ${ARCHIVE}/0-orchestrator.tar.gz *
popd

echo "[+] flist archive created"
