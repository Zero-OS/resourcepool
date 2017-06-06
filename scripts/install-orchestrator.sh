#!/bin/bash


error_handler() {
    EXITCODE=$?

    if [ -z $2 ]; then
        echo "[-] line $1: unexpected error"
        exit ${EXITCODE}
    else
        echo $2
    fi

    exit 1
}

trap 'error_handler $LINENO' ERR

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

logfile="/tmp/install.log"

if [ -z $1 ] || [ -z $2 ] || [ -s $3 ]; then
  echo "Usage: installgrid.sh <BRANCH> <ZEROTIERNWID> <ZEROTIERTOKEN>"
  echo
  echo "  BRANCH: 0-orchestrator development branch."
  echo "  ZEROTIERNWID: Zerotier network id."
  echo "  ZEROTIERTOKEN: Zerotier api token."
  echo
  exit 1
fi
BRANCH=$1
ZEROTIERNWID=$2
ZEROTIERTOKEN=$3

CODEDIR="/root/gig/code"
if [ "$GIGDIR" != "" ]; then
    CODEDIR="$GIGDIR/code"
fi

echo "[+] Waiting for zerotier connectivity"
if ! zerotier-cli listnetworks | egrep -q 'OK PRIVATE|OK PUBLIC'; then
    echo "[-] ZeroTier interface zt0 does not have an ipaddress."
    echo "[-] Make sure you authorized this docker into your ZeroTier network"
    echo "[-] ZeroTier Network ID: ${ZEROTIERNWID}"

    while ! zerotier-cli listnetworks | egrep -q 'OK PRIVATE|OK PUBLIC'; do
        sleep 0.2
    done
fi

echo "[+] Configuring zerotier"
mkdir -p /etc/my_init.d > ${logfile} 2>&1
ztinit="/etc/my_init.d/10_zerotier.sh"

echo '#!/bin/bash -x' > ${ztinit}
echo 'zerotier-one -d' >> ${ztinit}
echo 'while ! zerotier-cli info > /dev/null 2>&1; do sleep 0.1; done' >> ${ztinit}
echo "[ $ZEROTIERNWID != \"\" ] && zerotier-cli join $ZEROTIERNWID" >> ${ztinit}

chmod +x ${ztinit} >> ${logfile} 2>&1
bash $ztinit >> ${logfile} 2>&1

echo "[+] Installing orchestrator dependencies"
pip3 install -U "git+https://github.com/zero-os/0-core.git@${BRANCH}#subdirectory=client/py-client" >> ${logfile} 2>&1
pip3 install -U "git+https://github.com/zero-os/0-orchestrator.git@${BRANCH}#subdirectory=pyclient" >> ${logfile} 2>&1
pip3 install -U zerotier >> ${logfile} 2>&1
python3 -c "from js9 import j; j.tools.prefab.local.development.golang.install()" >> ${logfile} 2>&1
mkdir -p /usr/local/go >> ${logfile} 2>&1

echo "[+] Updating AYS orchestrator server"
mkdir -p $CODEDIR/github >> ${logfile} 2>&1
pushd $CODEDIR/github
mkdir -p zero-os >> ${logfile} 2>&1
pushd zero-os

if [ ! -d "0-orchestrator" ]; then
    git clone https://github.com/zero-os/0-orchestrator.git >> ${logfile} 2>&1
fi
pushd 0-orchestrator
git pull
git checkout ${BRANCH} >> ${logfile} 2>&1
popd

if [ ! -d "0-core" ]; then
    git clone https://github.com/zero-os/0-core.git >> ${logfile} 2>&1
fi
pushd 0-core
git pull
git checkout ${BRANCH} >> ${logfile} 2>&1
popd

echo "[+] Start AtYourService server"

aysinit="/etc/my_init.d/10_ays.sh"
echo '#!/bin/bash -x' > ${aysinit}
echo 'ays start > /dev/null 2>&1' >> ${aysinit}

chmod +x ${aysinit} >> ${logfile} 2>&1
bash $aysinit >> ${logfile} 2>&1

echo "[+] Building orchestrator api server"
mkdir -p /opt/go/proj/src/github.com >> ${logfile} 2>&1
if [ ! -d /opt/go/proj/src/github.com/zero-os ]; then
    ln -sf ${CODEDIR}/github/zero-os /opt/go/proj/src/github.com/zero-os >> ${logfile} 2>&1
fi
cd /opt/go/proj/src/github.com/zero-os/0-orchestrator/api
GOPATH=/opt/go/proj GOROOT=/opt/go/root/ /opt/go/root/bin/go get -d ./... >> ${logfile} 2>&1
GOPATH=/opt/go/proj GOROOT=/opt/go/root/ /opt/go/root/bin/go build -o /usr/local/bin/orchestratorapiserver >> ${logfile} 2>&1
if [ ! -d /optvar/cockpit_repos/orchestrator-server ]; then
    ays repo create -n orchestrator-server -g js9 >> ${logfile} 2>&1
fi

echo "[+] Starting orchestrator api server"
orchinit="/etc/my_init.d/11_orchestrator.sh"
ZEROTIERIP=`ip -4 addr show zt0 | grep -oP 'inet\s\d+(\.\d+){3}' | sed 's/inet //' | tr -d '\n\r'`
if [ "$ZEROTIERIP" == "" ]; then
    echo "zerotier doesn't have an ip. make sure you have authorize this docker in your netowrk"
    exit 1
fi

# create orchestrator service
echo '#!/bin/bash -x' > ${orchinit}
echo 'cmd="orchestratorapiserver --bind '"${ZEROTIERIP}"':8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server"' >> ${orchinit}
echo 'tmux new-session -d -s main -n 1 || true' >> ${orchinit}
echo 'tmux new-window -t main -n orchestrator' >> ${orchinit}
echo 'tmux send-key -t orchestrator.0 "$cmd" ENTER' >> ${orchinit}

chmod +x ${orchinit} >> ${logfile} 2>&1
bash $orchinit >> ${logfile} 2>&1

echo "[+] Deploying bootstrap service"
echo -e "bootstrap.g8os__grid1:\n  zerotierNetID: '"${ZEROTIERNWID}"'\n  zerotierToken: '"${ZEROTIERTOKEN}"'\n\nactions:\n  - action: install\n" > /optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp
cd /optvar/cockpit_repos/orchestrator-server; ays blueprint >> ${logfile} 2>&1
cd /optvar/cockpit_repos/orchestrator-server; ays run create --follow -y >> ${logfile} 2>&1

echo "Your ays server is ready to bootstrap nodes into your zerotier network."
echo "Download your ipxe boot iso image https://bootstrap.gig.tech/iso/${BRANCH}/${ZEROTIERNWID} and boot up your nodes!"
echo "Enjoy your orchestrator api server: http://${ZEROTIERIP}:8080/"
