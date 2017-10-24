
#!/usr/bin/env bash

TRAVIS_BRANCH=$1
zerotierid=$2
zerotiertoken=$3
itsyouonlineorg=$ITSYOUONLINE_ORG
JS9_BRANCH=$4
CORE_0_BRANCH=$5

export SSHKEYNAME=id_rsa
export ZUTILSBRANCH=$JS9_BRANCH
export ZBRANCH=$JS9_BRANCH
export GIGSAFE=1
export TERM=xterm-256color

## generate ssh key
echo "[#] Generate SSH key ..."
ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N ''

#install requirments
sudo apt-get update
sudo pip3 install -U git+https://github.com/zero-os/0-orchestrator.git${TRAVIS_BRANCH}#subdirectory=pyclient
sudo pip3 install -U git+https://github.com/zero-os/0-core.git@${CORE_0_BRANCH}#subdirectory=client/py-client


## install zerotier in packet machine
echo "[#] Installing Zerotier ..."
curl -s https://install.zerotier.com/ | sudo bash

## install local ftp server
bash install_ftp_server.sh

## install Jumpscale 9
url="https://raw.githubusercontent.com/Jumpscale/bash/${JS9_BRANCH}/install.sh"
echo "[#] Installing Jumpscale 9 from ${url}"
curl -s $url | sudo bash
sudo chmod 777 /tmp/zutils.log
source /opt/code/github/jumpscale/bash/zlibs.sh
source ~/.bash_profile
ssh-add
ZKeysLoad
sudo chown $USER -R /opt/code
ZInstall_ays9

## start js9 docker
echo "[#] Starting JS9 container ..."
ZDockerActive -b jumpscale/ays9 -i js9

## make local machine join zerotier network
echo "[#] Joining zerotier network (local machine) ..."
sudo zerotier-one -d || true
sleep 5

sudo zerotier-cli join ${zerotierid}
sleep 5

## authorized local machine as zerotier member
echo "[#] Authorizing zerotier member ..."
memberid=$(sudo zerotier-cli info | awk '{print $3}')
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotiertoken}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotierid}/member/${memberid}

## make js9 container join zerotier network
echo "[#] Joining zerotier network (js9 container) ..."
ZEXEC -c  "curl -s https://install.zerotier.com/ | sudo bash" || true

ZEXEC -c   "zerotier-one -d" || true
sleep 5

ZEXEC -c   "zerotier-cli join ${zerotierid}"|| true
sleep 5

## authorized js9 container as zerotier member
echo "[#] Authorizing zerotier member ..."
memberid=$(docker exec js9  bash -c "zerotier-cli info" | awk '{print $3}')
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotiertoken}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotierid}/member/${memberid}
sleep 5

## install orchestrator
echo "[#] Installing orchestrator ..."
ssh -tA root@localhost -p 2222 "curl -sL https://raw.githubusercontent.com/zero-os/0-orchestrator/${TRAVIS_BRANCH}/scripts/install-orchestrator.sh | bash -s master ${zerotierid} ${zerotiertoken} ${itsyouonlineorg} ${ITSYOUONLINE_CL_ID} ${ITSYOUONLINE_CL_SECRET} --orchestrator ${TRAVIS_BRANCH} --core ${CORE_0_BRANCH}"

#passing jwt
echo "Enabling JWT..."
cd tests/0_orchestrator/
scp -P 2222 enable_jwt.sh root@localhost:
ssh -tA root@localhost -p 2222 "bash enable_jwt.sh ${zerotierid} ${zerotiertoken} ${JS9_BRANCH} ${TRAVIS_BRANCH} ${CORE_0_BRANCH} ${ITSYOUONLINE_CL_ID} ${ITSYOUONLINE_CL_SECRET} ${ITSYOUONLINE_ORG} ${NAME_SPACE}"

# get orch-server ip
orch_ip=$(ssh -At root@localhost -p 2222 "ip addr show zt0 | grep 'inet'")
x=$(echo ${orch_ip} | awk '{print $2}' | awk -F"/" '{print $1}')
sed -ie "s/^api_base_url.*$/api_base_url=http:\/\/${x}:8080/" test_suite/config.ini
