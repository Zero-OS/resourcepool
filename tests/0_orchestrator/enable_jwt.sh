zerotier_network=$1
zerotier_token=$2
js_branch=$3
travis_branch=$4
core_0_branch=$5
client_id=$6
client_secret=$7
organization=$8
name_space=$9

export_jwt(){
    jwt=$(ays generatetoken --clientid ${client_id} --clientsecret ${client_secret} --organization ${organization} --validity 3600)
    eval $jwt
}

export_server_ip(){
    server_ip=$(ip addr show zt0 | grep 'inet')
    export server_ip=$(echo ${server_ip} | awk '{print $2}' | awk -F"/" '{print $1}')
}

export_runnig_nodes(){
    export nodes=$(curl -H 'Authorization: Bearer '${JWT} -X  GET http://${server_ip}:8080/nodes | python3 -c "import sys, json; print(','.join([str(x['id']) for x in json.load(sys.stdin)]))")
}

create_bootstrap_blueprint(){
cat >>  /optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp << EOL
bootstrap.zero-os__grid1:
  zerotierNetID: '${zerotier_network}'
  zerotierToken: '${zerotier_token}'
  wipedisks: true
  networks:
    - storage
EOL
}

create_packet_network_blueprint(){
 echo "network.publicstorage__storage:" >> /optvar/cockpit_repos/orchestrator-server/blueprints/network.bp
}

create_configration_blueprint(){
cat >>  /optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp << EOL
configuration__main:
  configurations:
  - key: '0-core-version'
    value: '${core_0_branch}'
  - key: 'js-version'
    value: '${js_branch}'
  - key: 'gw-flist'
    value: 'https://hub.gig.tech/gig-official-apps/zero-os-gw-${core_0_branch}.flist'
  - key: 'ovs-flist'
    value: 'https://hub.gig.tech/gig-official-apps/ovs-${core_0_branch}.flist'
  - key: '0-disk-flist'
    value: 'https://hub.gig.tech/gig-official-apps/0-disk-${core_0_branch}.flist'
  - key: 'jwt-token'
    value: '${JWT}'
  - key: 'jwt-key'
    value: 'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv'
  - key: 'iyo_org'
    value: '${organization}'
  - key: 'iyo_namespace'
    value: '${name_space}'
  - key: 'iyo_clientID'
    value: '${client_id}'
  - key: 'iyo_secret'
    value: '${client_secret}'
EOL
}

create_etcd_cluster_blueprint(){
cat > /optvar/cockpit_repos/orchestrator-server/blueprints/etcd_cluster.bp << EOL
etcd_cluster__myetcd:
  nodes:
EOL

for node in ${1//,/ }
do
    echo "  - ${node}" >> /optvar/cockpit_repos/orchestrator-server/blueprints/etcd_cluster.bp
done

cat >> /optvar/cockpit_repos/orchestrator-server/blueprints/etcd_cluster.bp << EOL
actions:
  - action: install
  - actor: etcd_cluster
EOL
}

# Adding tester keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDh9OvsqboBV1AHblyiLEWKeH6bfC+/MPmsKDAk+9XkFrAC9b2VGmQrIlTg1Su+R9IOWrueywxbtd5GdWHJkC1+2SUlxm2ALWThyNg88MWogHgmR9CDlxr9cCMFyhOkFpIGLfiD/ZKYLqP43a8edxnEEx/PB4O4Utn9zkw6Dp7AFXki6tCJWJkT12AVS1mk8Ii/uRUbKQyxnuy5rSzNMcDyV/i/r7qdg7K5eys4B3VmsdN7y9l9H6p4VHAHALkuyYHrVJNMp/wPVZyd99h7iCB9LnXkFhPw/t6o4R7/2czXTBTxuUbvkxvEFqdNHuDQ0bhF+YuWHzarixKwVA68b4EZ john@john-Inspiron-5423" >> /root/.ssh/authorized_keys

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCr7qYad105onUnDQnfShLozEsGtVemWKKKM7Vco9O6DBXFbSaDhIJAk81Oh49dUuUZsxI1SnHsvTalqF0915pWnlD2c0lGvNI+H1XylzxT9nFIz8OaIJYSe7T9VIAfA5VqEhYWkLNXn7CuWneJSEKVyjeGkS5shIPwy5Fl9FL0203FbOP3V3RF5fsY+WBsb+VbOLT1UiFLiqKLA00v25qRl/i1xiRxES1ozkAHTZR+1iYTZHfpnMEar1iekI8WQ8p2/dCLRgxyFTpFO6WT8lYl+2qDgUR8lYNIIDqSRTBZsS5IemPKiovJ52+LRiJTWsoFMkyzC3xI8XWUiiInL/Tx elsayed@elsayed" >> /root/.ssh/authorized_keys

cat /root/.ssh/authorized_keys


VL=$(git ls-remote --heads https://github.com/zero-os/0-core.git $core_0_branch | wc -l)
if [ $VL == 0 ]
then
  core_0_branch=master
fi
echo " [*] 0_core_branch " ${core_0_branch}

export_jwt
export_server_ip

echo " [*] server IP : " ${server_ip}

create_configration_blueprint
create_packet_network_blueprint
create_bootstrap_blueprint

cd /optvar/cockpit_repos/orchestrator-server

ays blueprint configuration.bp
ays blueprint network.bp
ays service delete -n grid1 -y
ays blueprint bootstrap.bp

echo " [*] sleeping 240 second"
sleep 240

export_runnig_nodes
create_etcd_cluster_blueprint ${nodes}
ays blueprint etcd_cluster.bp
ays run create -fy
