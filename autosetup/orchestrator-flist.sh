#!/bin/bash
set -e

echo "[+] creating base target layout: ${TARGET}"
TARGET=/mnt/target
ARCHIVE=/tmp/archives
LOCLANG="en_US.UTF-8"
BRANCH="1.1.0-alpha-7"

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

echo "[+] configuring zerotier"
ztinit="${TARGET}/etc/my_init.d/10_zerotier.sh"

echo '#!/bin/bash -x' > ${ztinit}
echo 'ZEROTIERNWID=$(cat /etc/0-orchestrator-zerotier-netid 2> /dev/null)' >> ${ztinit}
echo 'if ! pgrep -x "zerotier-one" ; then zerotier-one -d ; fi' >> ${ztinit}
echo 'while ! zerotier-cli info > /dev/null 2>&1; do sleep 0.1; done' >> ${ztinit}
echo "[ $ZEROTIERNWID != \"\" ] && zerotier-cli join $ZEROTIERNWID" >> ${ztinit}

chmod +x ${ztinit}

echo "[+] installing orchestrator dependencies"
pip3 install --root ${TARGET} --upgrade "git+https://github.com/zero-os/0-core.git@${BRANCH}#subdirectory=client/py-client"
pip3 install --root ${TARGET} --upgrade "git+https://github.com/zero-os/0-orchestrator.git@${BRANCH}#subdirectory=pyclient"
pip3 install --root ${TARGET} --upgrade zerotier

curl https://storage.googleapis.com/golang/go1.8.3.linux-amd64.tar.gz > /tmp/go1.8.3.linux-amd64.tar.gz
tar -C /usr/local -xzf /tmp/go1.8.3.linux-amd64.tar.gz

export GOPATH=/gopath
mkdir -p $GOPATH

export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

echo "[+] downloading ays orchestrator server source code"
go get -d -v -u github.com/zero-os/0-orchestrator/api

if [ "${BRANCH}" != "master"]; then
    pushd $GOPATH/src/github.com/zero-os/0-orchestrator
    git fetch origin ${BRANCH}:${BRANCH}
    git checkout ${BRANCH}
    popd
fi

echo "[+] creating ays startup script"
aysinit="${TARGET}/etc/my_init.d/10_ays.sh"

echo '#!/bin/bash -x' > ${aysinit}
echo 'ays start > /dev/null 2>&1' >> ${aysinit}

chmod +x ${aysinit}

echo "[+] creating ays service"
mkdir -p ${TARGET}/optvar/cockpit_repos/orchestrator-server
pushd ${TARGET}/optvar/cockpit_repos/orchestrator-server
mkdir -p services
mkdir -p actorTemplates
mkdir -p actors
mkdir -p blueprints
touch .ays
git init
git remote add origin /dev/null
popd

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
popd

popd


echo "[+] configuring orchestrator api server service"
orchinit="${TARGET}/etc/my_init.d/11_orchestrator.sh"

# create orchestrator service
echo '#!/bin/bash -x' > ${orchinit}
echo "cmd=ORCHESTRATOR_COMMAND" >> ${orchinit}
echo 'tmux new-session -d -s main -n 1 || true' >> ${orchinit}
echo 'tmux new-window -t main -n orchestrator' >> ${orchinit}
echo 'tmux send-key -t orchestrator.0 "$cmd" ENTER' >> ${orchinit}
chmod +x ${orchinit}

# cloning orchestrator code
mkdir -p /opt/code/github/zero-os
pushd /opt/code/github/zero-os
git clone -b "${BRANCH}" https://github.com/zero-os/0-orchestrator.git
popd

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
