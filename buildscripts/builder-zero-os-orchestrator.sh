#!/bin/bash
set -e

branch="master"
echo $1

if [ "$1" != "" ]; then
    branch="$1"
fi

if ! grep 'xenial universe' /etc/apt/sources.list; then
    echo "deb http://archive.ubuntu.com/ubuntu xenial universe" >> /etc/apt/sources.list
fi

apt-get update
apt-get install -y git curl net-tools

mkdir -p /root/.ssh
touch /root/.ssh/known_hosts

# install jumpscale
export JSBRANCH="8.2.0"
cd /tmp
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh
bash install.sh

# install grid actor template
mkdir -p /opt/code/github/
git clone -b "${branch}" https://github.com/github.com/zero-os/0-orchestrator.git /opt/code/github/github.com/zero-os/0-orchestrator

pip3 install git+https://github.com/zero-os/0-orchestrator.git@"${branch}"#subdirectory=pyclient -U
pip3 install git+https://github.com/zero-os/0-core.git@"${branch}"#subdirectory=client/py-client -U

pip3 install zerotier>=1.1.0 -U

js 'x = j.tools.cuisine.local; x.apps.atyourservice.install()'
js 'x = j.tools.cuisine.local; x.apps.caddy.build(); x.apps.caddy.install()'

cd /
mkdir /tmp/archives
tar -czf /tmp/archives/orchestrator.tar.gz --exclude tmp/archives --exclude sys --exclude dev --exclude proc *
