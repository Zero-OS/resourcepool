# Setup

This is the recommended and currently the only supported option to setup a Zero-OS cluster.

In order to have a full Zero-OS cluster you'll need to perform the following steps:
1. [Create a Docker container with a JumpScale9](#create-a-jumpscale9-docker-container)
2. [Install the Zero-OS Orchestrator into the Docker container](#install-the-orchestrator)
3. [Setup the AYS configuration service](#setup-the-ays-configuration-service)
4. [Setup the backplane network](#setup-the-backplane-network)
5. [Boot your Zero-OS nodes](#boot-your-zero-os-nodes)

## Create a JumpScale9 Docker container

Create the Docker container with JumpScale9 development environment by following the documentation at https://github.com/Jumpscale/developer#jumpscale-9.
> **Important:** Make sure you set the `GIGBRANCH` environment variable to **9.0.1** before running `jsinit.sh`. This version of 0-orchestrator will only work with this version of JumpScale.

> **Important:**: Make sure to build the js9 docker with `js9_build -l` and not directly start the docker with `js9_start -b` cause this will not install all the requires libraries.


## Install the Orchestrator

SSH into your JumpScale9 Docker container and install the Orchestrator using the [`install-orchestrator.sh`](../../scripts/install-orchestrator.sh) script.

Before actually performing the Orchestrator installation the script will first join the Docker container into the ZeroTier management network that will be used to manage the Zero-OS nodes in your cluster.
The orchestrator by default installs caddy and runs using https. If the domain is passed, it will try to create certificates for that domain, unless `--development` is used, then it will use self signed certificates.

This script takes the following parameters:
- `BRANCH`: 0-orchestrator development branch
- `ZEROTIERNWID`: ZeroTier network ID
- `ZEROTIERTOKEN`: ZeroTier API token
- `ITSYOUONLINEORG`: Itsyouonline organization to authenticate against
- `DOMAIN`: Optional domain to listen on if this is ommited caddy will listen on the zerotier network with a selfsigned certificate
- `--development`: When domain is passed and you want to force a selfsigned certificate

So:
```bash
cd /tmp
export BRANCH="1.1.0-alpha-4"
export ZEROTIERNWID="<Your ZeroTier network ID>"
export ZEROTIERTOKEN="<Your ZeroTier token>"
export ITSYOUONLINEORG="<itsyou.online organization>"
export DOMAIN="<Your domain name>"
curl -o install-orchestrator.sh https://raw.githubusercontent.com/zero-os/0-orchestrator/${BRANCH}/scripts/install-orchestrator.sh
bash install-orchestrator.sh $BRANCH $ZEROTIERNWID $ZEROTIERTOKEN <$ITSYOUONLINEORG> [<$DOMAIN> [--development]]
```

In order to see the full log details while `install-orchestrator.sh` executes:
```shell
tail -s /tmp/install.log
```

> **Important:**
- The ZeroTier network needs to be a private network
- The script will wait until you authorize your JumpScale9 Docker container into the network


## Setup the AYS configuration service

### Create a JWT token for the AYS CLI and configuration service:
Since AYS is protected with JWT, you have to generate a token so the AYS CLI can authenticate to AYS server.
The CLI provide and easy way to do it:
```shell
ays generatetoken --clientid {CLIENT_ID} --clientsecret {CLIENT_SECRET} --organization $ITSYOUONLINEORG
```
CLIENT_ID AND CLIENT_SECRET have to be generated on [Itsyou.online](https://itsyou.online)  
From the website, go to your settings, in the `API Keys` panel, generate a new id/secret pair.

This command will output something like:
```shell
# Generated Token, please run to use in client:
export JWT='eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJLa0Y0c3IyUll4cXVYWTZlWjVtMWtic0dTbVJRIiwiZXhwIjoxNDk4MTM0MDMyLCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJyZWZyZXNoX3Rva2VuIjoiU2xxLWVfY9ktSjBEalRDbmZPNzA1SDN1ZFN5UyIsInNjb3BlIjpbInVzZXI6bWVtYmVyb2Y6Z3JlZW5pdGdsb2JlLmVudmlyb25tZW50cy5iZS1nOC0zIl0sInVzZXJuYW1lIjoiemFpYm9uIn0.sKVUHPxSb6rxOMx1DKV8w0T0dpyuMya4fBgOV66VFl6-R4p53crvSkHidXRjsKbgbyxV2stsbxV67mo5JPvRN9uaf-pnJ9cXxs74lSq8OoFwre6aG9pG0JPmVt9uMy56'
```

copy the export and execute it in your terminal. This will allow the AYS CLI to be authenticate from now one.

### Configuration
In order for the Orchestrator to know which flists and version of JumpScale to use, and which Zero-OS version is required on the nodes, create the following blueprint in `/optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp`:

```yaml
configuration__main:
  configurations:
  - key: '0-core-version'
    value: '1.1.0-alpha-4'
  - key: 'js-version'
    value: '9.0.0'
  - key: 'gw-flist'
    value: 'https://hub.gig.tech/gig-official-apps/zero-os-gw-1.1.0-alpha-3.flist'
  - key: 'ovs-flist'
    value: 'https://hub.gig.tech/gig-official-apps/ovs-1.1.0-alpha-3.flist'
  - key: '0-disk-flist'
    value: 'https://hub.gig.tech/gig-official-apps/0-disk-1.1.0-alpha-3.flist'
  - key: 'jwt-token'
    value: <The JWT generted at the previous step>
  - key: 'jwt-key'
    value: 'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv'    
```

See [Versioning](versioning.md) for more details about the AYS configuration service.

After creating this blueprint, issue the following AYS command to install the configuration service:
```bash
cd /optvar/cockpit_repos/orchestrator-server
ays blueprint configuration.bp
```

## Setup the backplane network
This optional setup allows you to interconnect your nodes using the (if available) 10GE+ network infrastructure. Skip this step if you don't have this in your setup.

Create a new blueprint `/optvar/cockpit_repos/orchestrator-server/blueprints/network.bp` and depending on the available 10GE+ network infrastructure specify following configuration:

### G8 setup
```yaml
network.zero-os__storage:
  vlanTag: 101
  cidr: "192.168.58.0/24"
```
> **Important:** Change the vlanTag and the cidr according to the needs of your environment.

### Switchless setup
```yaml
network.switchless__storage:
  vlanTag: 101
  cidr: "192.168.58.0/24"
```
> **Important:** Change the vlanTag and the cidr according to the needs of your environment.

See [Switchless Setup](switchless.md) for instructions on how to interconnect the nodes in case there is no Gigabit Ethernet switch.

### Packet.net setup

```yaml
network.publicstorage__storage:
```

After creating this blueprint, issue the following AYS command to install it:
```shell
cd /optvar/cockpit_repos/orchestrator-server
ays blueprint network.bp
```

Then we need to update the bootstrap service so that it deploys the storage network when bootstrapping the nodes. So edit `/optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp` as follows:
```yaml
bootstrap.zero-os__grid1:
  zerotierNetID: '<Your ZeroTier network id>'
  zerotierToken: '<Your ZeroTier token>'
  wipedisks: true # indicate you want to wipe the disks of the nodes when adding them
  networks:
    - storage
```
Now issue the following AYS commands to reinstall the updated bootstrap service:
```shell
cd /optvar/cockpit_repos/orchestrator-server
ays service delete -n grid1 -y
ays blueprint bootstrap.bp
ays run create -y
```

## Boot your Zero-OS nodes
The final step of rounding up your Zero-OS cluster is to boot your Zero-OS nodes in to your ZeroTier network.

Via iPXE from the following URL: `https://bootstrap.gig.tech/ipxe/1.1.0-alpha-4/<Your ZeroTier network id>/organization=${ITSYOUONLINEORG}`

Or download your ISO from the following URL: `https://bootstrap.gig.tech/iso/1.1.0-alpha-4/<Your ZeroTier network id>/organization=${ITSYOUONLINEORG}`

Refer to the 0-core repository documentation for more information on booting Zero-OS.
