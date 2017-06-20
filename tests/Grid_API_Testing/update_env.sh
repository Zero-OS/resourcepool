#!/bin/bash

ZEROTIERIP='172.23.0.136'
branch='tests-travis'
GREEN='\033[0;32m'
NC='\033[0m'
echo -e "${GREEN}** Start updating environment **${NC}"

echo -e "${GREEN}** updating 0-core **${NC}"
exist=$(git ls-remote --heads git@github.com:zero-os/0-core.git ${branch} | wc -l)
if [ "${exist}" == "1" ]; then
   git pull && git checkout ${branch}
else
   git pull && git checkout master
fi
cd /opt/go/proj/src/github.com/zero-os/0-core/
git pull
pip3 install client/py-client/.

echo -e "${GREEN}** updating 0-orchestrator **${NC}"
tmux kill-window -t orchestrator
cd /opt/go/proj/src/github.com/zero-os/0-orchestrator
git pull && git checkout ${branch}
cd /opt/go/proj/src/github.com/zero-os/0-orchestrator/api
GOPATH=/opt/go/proj GOROOT=/opt/go/root/ /opt/go/root/bin/go get -d
GOPATH=/opt/go/proj GOROOT=/opt/go/root/ /opt/go/root/bin/go build -o /usr/local/bin/orchestratorapiserver

tmux new-window -n:orchestrator 'orchestratorapiserver --bind '"${ZEROTIERIP}"':8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server'

cd /optvar/cockpit_repos/orchestrator-server/
ays repo destroy
ays actor update
ays blueprint bootstrap.bp
ays run create --follow -y

echo -e "${GREEN}** updating jumpscale repos **${NC}"
cd /opt/code/github/jumpscale/prefab9
git checkout master && git pull
cd /opt/code/github/jumpscale/ays9
git checkout master && git pull
cd /opt/code/github/jumpscale/core9
git checkout master && git pull
cd /opt/code/github/jumpscale/lib9
git checkout master && git pull
cd /opt/code/github/jumpscale/developer
git checkout master && git pull

echo -e "${GREEN}** updating ays **${NC}"
ays start

