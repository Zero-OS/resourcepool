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
> **Important:** Make sure you set the GIGBRANCH environment variable to 9.0.0 before running jsinit. This version of 0-orchestrator will only work with this version of JumpScale.

## Install the Orchestrator

SSH into your JumpScale9 Docker container and instal the Orchestrator using the [`install-orchestrator.sh`](../../scripts/install-orchestrator.sh) script.

Before actually performing the Orchestrator installation the script will first join the Docker container into the ZeroTier management network that will be used to manage the ZeroTier nodes in your cluster.

This script takes 3 parameters:
- `BRANCH`: 0-orchestrator development branch
- `ZEROTIERNWID`: ZeroTier network ID
- `ZEROTIERTOKEN`: ZeroTier API token

So:
```bash
(gig) root@js9:/root$ export BRANCH="1.1.0-alpha-3"
(gig) root@js9:/root$ export ZEROTIERNWID="<Your ZeroTier network ID>"
(gig) root@js9:/root$ export ZEROTIERTOKEN="<Your ZeroTier token>"
(gig) root@js9:/root$ curl -o install-orchestrator.sh https://raw.githubusercontent.com/zero-os/0-orchestrator/${BRANCH}/scripts/install-orchestrator.sh
(gig) root@js9:/root$ bash install-orchestrator.sh $BRANCH $ZEROTIERNWID $ZEROTIERTOKEN
```
> **Important:**
- The ZeroTier network needs to be a private network
- The script will wait until you authorize your JumpScale9 Docker container into the network


## Setup the AYS configuration service
In order for the Orchestrator to use the correct versions of flists, Zero-OS nodes and JumpScale9, create the following blueprint in `/optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp`:

```yaml
configuration__main:
  configurations:
  - key: '0-core-version'
    value: '1.1.0-alpha-3'
  - key: 'js-version'
    value: '9.0.0'
  - key: 'gw-flist'
    value: 'https://hub.gig.tech/gig-official-apps/zero-os-gw-1.1.0-alpha-3.flist'
  - key: 'ovs-flist'
    value: 'https://hub.gig.tech/gig-official-apps/ovs-1.1.0-alpha-3.flist'
  - key: '0-core-version'
    value: '1.1.0-alpha-3'
  - key: '0-disk-flist'
    value: 'https://hub.gig.tech/gig-official-apps/0-disk-1.1.0-alpha-3.flist'
```

After creating this blueprint, issue the following command to AYS to install it:
```bash
(gig) root@js9:/root$ cd /optvar/cockpit_repos/orchestrator-server
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays blueprint configuration.bp
```

## Setup the backplane network
This optional setup allows you to use the 10GE+ network infrastructure (if available) that interconnects the nodes in your cluster. If you don't have this in your nodes, please skip this step.

Create the following blueprint: `/optvar/cockpit_repos/orchestrator-server/blueprints/network.bp`
### G8 setup
```yaml
network.zero-os__storage:
  vlanTag: 101
  cidr: "192.168.58.0/24"
```
> **Important:** Change the vlanTag and the cidr according to the needs of your environment.

### Packet.net setup

```yaml
network.publicstorage__storage:
```

After creating this blueprint, issue the following command to AYS to install it:
```
(gig) root@js9:/root$ cd /optvar/cockpit_repos/orchestrator-server
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays blueprint network.bp
```

Then we need to update the bootstrap service so that is deploys the storage network when bootstrapping the nodes. So edit `/optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp` as follows:
```yaml
bootstrap.zero-os__grid1:
  zerotierNetID: '<Your ZeroTier network id>'
  zerotierToken: '<Your ZeroTier token>'
  wipedisks: true # indicate you want to wipe the disks of the nodes when adding them
  networks:
    - storage
```
Now issue the following commands to reinstall the updated bootstrap service:
```shell
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays service delete -n grid1 -y
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays blueprint bootstrap.bp
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays run create -y
```

## Boot your Zero-OS nodes
The final step of rounding up your Zero-OS cluster is to boot your Zero-OS nodes in to your ZeroTier network.

Via ipxe from the following URL: `https://bootstrap.gig.tech/ipxe/1.1.0-alpha-3-0-core-6d11a464/<Your ZeroTier network id>`

Or download your ISO from the following url: `https://bootstrap.gig.tech/iso/1.1.0-alpha-3-0-core-6d11a464/<Your ZeroTier network id>`

Refer to the 0-core repository documentation for more information on booting Zero-OS.
