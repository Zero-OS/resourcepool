#!/usr/bin/env bash

TRAVIS_BRANCH=$1
zerotierid=$2
zerotiertoken=$3
itsyouonlineorg=$ITSYOUONLINE_ORG
JS9_BRANCH=$4
CORE_0_BRANCH=$5

export SSHKEYNAME=id_rsa
export GIGBRANCH=$JS9_BRANCH
export GIGDEVELOPERBRANCH=$JS9_BRANCH
export GIGSAFE=1
export TERM=xterm-256color

## generate ssh key
echo "[#] Generate SSH key ..."
ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N ''
echo "#############################################################[#] ${ITSYOUONLINE_CL_ID}
######################################################################################
 ${ITSYOUONLINE_CL_SECRET}"
#install requirments
sudo apt-get update
sudo pip3 install -U git+https://github.com/zero-os/0-orchestrator.git${TRAVIS_BRANCH}#subdirectory=pyclient
sudo pip3 install -U git+https://github.com/zero-os/0-core.git@${CORE_0_BRANCH}#subdirectory=client/py-client

## install docker-ce
echo "[#] Installing docker ..."
sudo apt-get -y install \
apt-transport-https \
ca-certificates \
curl
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) \
stable"
sudo apt-get update
sudo apt-get -y install docker-ce

## install zerotier in packet machine
echo "[#] Installing Zerotier ..."
curl -s https://install.zerotier.com/ | sudo bash

## install Jumpscale 9
url="https://raw.githubusercontent.com/Jumpscale/developer/${JS9_BRANCH}/jsinit.sh"
echo "[#] Installing Jumpscale 9 from ${url}"
curl -s $url | bash
source ~/.jsenv.sh

js9_build -l

## start js9 docker
echo "[#] Starting JS9 container ..."
js9_start

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
docker exec -d js9 bash -c "zerotier-one -d" || true
sleep 5

docker exec js9 bash -c "zerotier-cli join ${zerotierid}"
sleep 5

## authorized js9 container as zerotier member
echo "[#] Authorizing zerotier member ..."
memberid=$(docker exec js9 bash -c "zerotier-cli info" | awk '{print $3}')
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotiertoken}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotierid}/member/${memberid}
sleep 5

## install orchestrator
echo "[#] Installing orchestrator ..."
ssh -tA root@localhost -p 2222 "export GIGDIR=~/gig; curl -sL https://raw.githubusercontent.com/zero-os/0-orchestrator/${TRAVIS_BRANCH}/scripts/install-orchestrator.sh | bash -s master ${zerotierid} ${zerotiertoken} ${itsyouonlineorg} ${ITSYOUONLINE_CL_ID} ${ITSYOUONLINE_CL_SECRET} --orchestrator ${TRAVIS_BRANCH} --core ${CORE_0_BRANCH}"

#passing jwt
echo "Enabling JWT..."
cd tests/0_orchestrator/
scp -P 2222 enable_jwt.sh root@localhost:
ssh -tA root@localhost -p 2222 "bash enable_jwt.sh ${zerotierid} ${zerotiertoken} ${JS9_BRANCH} ${TRAVIS_BRANCH} ${CORE_0_BRANCH} ${ITSYOUONLINE_CL_ID} ${ITSYOUONLINE_CL_SECRET} ${ITSYOUONLINE_ORG} ${NAME_SPACE}"

# get orch-server ip
orch_ip=$(ssh -At root@localhost -p 2222 "ip addr show zt0 | grep 'inet'")
x=$(echo ${orch_ip} | awk '{print $2}' | awk -F"/" '{print $1}')
sed -ie "s/^api_base_url.*$/api_base_url=http:\/\/${x}:8080/" test_suite/config.ini
