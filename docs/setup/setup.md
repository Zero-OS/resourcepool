# Development Setup of a Zero-OS Cluster

You can either:
- [Setup your cluster using an installation script](#automated-setup) (recommended)
- [Or manually setup the cluster](#manual-setup) (not supported)

Once done, the last step is documented in [Boot your Zero-OS nodes](#boot-nodes).

## Automated setup

This is the recommended and currently the only supported option to setup a Zero-OS cluster.

In order to have a full Zero-OS cluster you need:
1. JumpScale9 development Docker container
2. Install the Zero-OS orchestrator into the container

Create the Docker container with JumpScale9 by following the documentation at https://github.com/Jumpscale/developer#jumpscale-9.

Once you have your JumpScale9 Docker container running, SSH into it and install the rest using the [`installgrid.sh`](../../scripts/installgrid.sh) script.

This script takes 3 parameters:
- BRANCH: 0-orchestrator development branch
- ZEROTIERNWID: ZerTier network id
- ZEROTIERTOKEN: ZeroTier API token

So:
```
BRANCH="master"
ZEROTIERNWID=""
ZEROTIERTOKEN=""
./installgrid.sh $BRANCH $ZEROTIERNWID $ZEROTIERTOKEN
```

## Manual setup

The manual steps are documented here solely for your information. Currently only the above documented [Automated setup](#automated-setup) is supported. Using the manual procedure is not recommended.

Here are the steps:
1. Create a ZeroTier network
2. [Setup the AYS Server](#ays-server)
3. [Setup the Orchestrator](#orchestrator)
4. [Start the Bootstrap Service, using an AYS blueprint](#bootstrap-service)
5. [Format all hard disks](#format-disks)
6. [Boot the Zero-OS nodes](#boot-nodes)

The first step is pretty straight forward, go to https://my.zerotier.com/ and create your ZeroTier network.

For the next 3 steps you have two options:
- Do it all manually as documented here below in the linked sections
- Or run the AYS Server, the Orchestrator and the Bootstrap service in a Docker container, leveraging two bash scripts that automate all this

The automated setup is documented below in the two first sections:
- [Create and start the Docker container](#docker-container)
- [Starting AYS, the API Server and the bootstrap service](#start-services)


<a id="docker-container"></a>
### Create and start the Docker container

On your machine where you plan to host the Docker container:
```
ZT_NETWORK_ID="..."
curl -sL https://raw.githubusercontent.com/Jumpscale/developer/master/scripts/js_builder_js82_zerotier.sh | bash -s $ZT_NETWORK_ID
```

To see interactive output do the following in a separate console:
```
tail -f /tmp/lastcommandoutput.txt
```

For more details about using using `js_builder_js82_zerotier.sh` see [here](https://github.com/Jumpscale/developer/blob/master/docs/installjs8_details.md).


<a id="start-services"></a>
### Starting AYS, the API Server and the bootstrap service

From your machine, hosting the Docker container:
```
BRANCH="..."
ZT_API_TOKEN="..."
curl -sL https://raw.githubusercontent.com/Jumpscale/developer/master/scripts/g8os_grid_installer82.sh | bash -s $BRANCH $ZT_NETWORK_ID $ZT_API_TOKEN
```

Again, to see interactive output do the following in separate console:
```
tail -f /tmp/lastcommandoutput.txt
```

Next step is to boot the Zero-OS nodes, documented in [Create the Zero-OS nodes](#create-nodes), the last section on this page.

So skip all other sections here below, which are about the manual setup.


<a id="ays-server"></a>
### Setup the AYS server

* Install JumpScale

  On the machine where you want to run the AYS Server execute:

  ```shell
  cd $TMPDIR
  rm -f install.sh
  export JSBRANCH="8.2.0"
  curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh
  bash install.sh
  ```

  For more details on installing JumpScale see the [JumpScale documentation](https://gig.gitbooks.io/jumpscale-core8/content/Installation/JSDevelopment.html).

* Install the Python client

  `g8core` is the Python client that AYS uses to interact with a Zero-OS node.

  In order to install it execute:

  ```shell
  pip3 install g8core
  ```

* Install ZeroTier Python client

```shell
pip3 install zerotier
```

* Get the AYS templates for setting up a Zero-OS cluster

  The AYS templates for setting up all the Zero-OS cluster components are available in the `templates` directory of the [zero-os/0-orchestrator](https://github.com/zero-os/0-orchestrator/) repository on GitHub.

  In order to clone this repository execute:
  ```shell
  cd /opt/code/
  git clone https://github.com/zero-os/0-orchestrator/
  cd 0-orchestrator
  git checkout 1.1.0-alpha
  ```

* Start the AYS server

  Execute:
  ```shell
  ays start
  ```

* Create a new AYS repository

  This is the AYS repository that you will use for the blueprints to setup the Zero-OS cluster.

  ```shell
  ays repo create --name {repo-name} --git {git-server}
  ```

  Values:
  - **{repo-name}**: Any name you choose for your AYS repository
  - **{git-server}**: https address of your repository on a Git server, e.g. `http://github.com/user/repo`


<a id="orchestrator"></a>
### Setup the Orchestrator

* Build the Zero-OS Orchestrator

  If not already done before, first clone the [zero-os/0-orchestrator](https://github.com/zero-os/0-orchestrator) repository, and then build the server:

  ```shell
  VERSION="1.1.0-alpha"
  git clone https://github.com/zero-os/0-orchestrator
  cd 0-orchestrator
  git checkout $VERSION
  go build
  ```

* Run the Zero-OS Orchestrator

  Execute:
  ```bash
  ./api --bind :8080 --ays-url http://localhost:5000 --ays-repo {repo-name}
  ```

  Options:
  - `--bind :8080` makes the server listen on all interfaces on port 8080
  - `--ays-url` needed to point to the AYS REST API
  - `--ays-repo` is the name of the AYS repository the Orchestrator needs to use. It should be the repo you created in the previous step.


<a id="bootstrap-service"></a>
### Install the auto node discovery service

Add the following blueprint in the `blueprints` directory of your AYS repository:

```
bootstrap.g8os__restapi1:
  zerotierNetID: {ZeroTier-Network-ID}
  zerotierToken: '{ZeroTier-API-Token}'

actions:
  - action: install
```

Values:
- **{ZeroTier-Network-ID}**: a ZeroTier Network ID
- **{ZeroTier-API-Token}**: a ZeroTier API Access Token

You get both values from the ZeroTier web portal: https://my.zerotier.com/

This blueprint will install the **auto discovery service** which will auto discover all Zero-OS nodes that were setup to connect to the same ZeroTier network.

Alternatively you can also manually add a Zero-OS node to the Zero-OS cluster with following blueprint:

```
node.g8os__525400123456:
  redisAddr: 172.17.0.1

actions:
 - action: install
```

In the above example `525400123456` is the MAC address of the Zero-OS node with the ':' removed and the `redisAddr` is the IP address of the node.

After creating both blueprints, run the following commands to execute the blueprints and have the actions executed:

```shell
ays blueprint
ays run create --follow
```


<a id="format-disks"></a>
### Format all hard disks

In order to prepare for the [setup of storage clusters](../storagecluster/setup.md) it is highly recommended to format all hard disks as part of the Zero-OS cluster setup. This is achieved by using the Zero-OS Orchestrator REST API Python client, as follows.

From with in the JumpScale 8.2 he Docker container execute:

```
#!/usr/bin/env python3
from zeroos.orchestrator import  client
from zeroos.core0 import  client
import argparse

def main(url):
    api = client.APIClient(base_uri=url)
    for node in ['x.x.x.x','x.x.x.x']:     #nodes_MGMT_ip's
        print('Wiping node {}'.format(node))
        nodeclient = client.Client(node)
        for disk in nodeclient.disk.list()['blockdevices']:
            if not disk['mountpoint'] :
                print('   * Wiping disk {kname}'.format(**disk))
                nodeclient.system('dd if=/dev/zero of=/dev/{} bs=1M count=50'.format(disk['kname']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    options = parser.parse_args()
    main(options.url)
```

<a id="boot-nodes"></a>
## Boot the Zero-OS nodes

Download your iPXE boot ISO image from the Zero-OS Bootstrap Service: `https://bootstrap.gig.tech/iso/${BRANCH}/${ZeroTier-Network-ID}``

Use this image to boot your node. For all detailed instruction on how to boot a Zero-OS node see the Core0 documentation: https://github.com/g8os/core0
