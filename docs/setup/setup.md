# Setup

This is the recommended and currently the only supported option to setup a Zero-OS cluster.

In order to have a full Zero-OS cluster you'll need to perform the following steps:
1. JumpScale9 development Docker container
2. Install the Zero-OS orchestrator into the container
3. Setup the configuration service in AYS
4. Configure the backplane network service in AYS
5. Boot your Zero-OS nodes

## Installing JumpScale9

Create the Docker container with JumpScale9 by following the documentation at https://github.com/Jumpscale/developer#jumpscale-9.
> **Important:** Make sure you set the GIGBRANCH environment variable to 9.0.0 before running jsinit. This version of 0-orchestrator will only work with this version of JumpScale.

## Setting up the 0-orchestrator server

You now have your JumpScale9 Docker container running, before you start the 0-orchestrator setup you need to join your docker into the ZeroTier management network that will be used to manage the ZeroTier nodes in your cluster.

SSH into your JumpScale9 docker and continue with installing the 0-orchestrator server by means of the [`install-orchestrator.sh`](../../scripts/install-orchestrator.sh) script.

This script takes 3 parameters:
- BRANCH: 0-orchestrator development branch
- ZEROTIERNWID: ZeroTier network id
- ZEROTIERTOKEN: ZeroTier API token

So:
```
(gig) root@js9:/root$ export BRANCH="1.1.0-alpha-3"
(gig) root@js9:/root$ export ZEROTIERNWID="<Your ZeroTier network id>"
(gig) root@js9:/root$ export ZEROTIERTOKEN="<Your ZeroTier token>"
(gig) root@js9:/root$ curl -o install-orchestrator.sh https://raw.githubusercontent.com/zero-os/0-orchestrator/${BRANCH}/scripts/install-orchestrator.sh
(gig) root@js9:/root$ bash install-orchestrator.sh $BRANCH $ZEROTIERNWID $ZEROTIERTOKEN
```
> **Important:**
- The ZeroTier network needs to be a private network
- The script will wait until you authorize your JumpScale9 docker into the network.

## Setup the configuration service in AYS
In order for the 0-orchestrator to use the correct versions of flists, Zero-OS nodes and JumpScale9, create the following blueprint in `/optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp`

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
```
(gig) root@js9:/root$ cd /optvar/cockpit_repos/orchestrator-server
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays blueprint configuration.bp
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays run create -y
```

## Setup the backplane network
This optional setup allows you to use the 10GE+ network infrastructure that interconnect the nodes in your cluster if available. If you don't have this in your nodes, please skip this step.

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
(gig) root@js9:/optvar/cockpit_repos/orchestrator-server$ ays run create -y
```

Then we need to update the bootstrap service so that is deploys the storage network when bootstrapping the nodes. So edit `/optvar/cockpit_repos/orchestrator-server/blueprints/network.bp` as follows:
```yaml
bootstrap.zero-os__grid1:
  zerotierNetID: '<Your ZeroTier network id>'
  zerotierToken: '<Your ZeroTier token>'
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
