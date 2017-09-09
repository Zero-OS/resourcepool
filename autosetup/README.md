# 0-orchestrator autosetup

This subdirectory contains scripts to deploy a 0-orchestrator based on flist and
command lines arguments to configure everything

There is two main scripts:
- `orchestrator-flist.sh`: builds an flist which contains 0-orchestrator dependencies
- `autobootstrap.py`: 0-orchestrator deployment script based on Zero-OS

## orchestrator-flist.sh
This script builds an flist with all the needed orchestrator base files.

- This script needs to be executed on a `ubuntu:16.04` fresh docker.
- The script accepts two **optional** arguments: `0-orchestrator-branch-name` and `0-core-branch-name`
  - If no arguments are set, `master` will be used
  - If only one argument is set, both will use this branch name
  - If both arguments are set, the respective branches will be used
- The resulting image will be located at `/tmp/archives/0-orchestrator.tar.gz`

When you have the archive, this flist needs to be merged (via the hub) with:
- ubuntu flist, made for jumpscale based merge (eg: `gig-official-apps/ubuntu1604-for-js.flist`)
- jumpscale with the right version needed by the orchestrator

In the end, you'll have this flist layout:
```
+- Default Ubuntu base system
 +- Jumpscale and ays flist
  +- Orchestrator apiserver, repositories and templates
```

## autobootstrap.py
This scipt automates an orchestrator deployment on a Zero-OS system.
> This system needs to be prepared before, eg: a disk needs to be mounted to store container data.

Here is the workflow of the deployment:
- connector
  - connect and authentificate to a remote Zero-OS server
- prepare
  - run a container using the 0-orchestrator flist
    - `/optvar` will be mounted from host `/var/cache/containers/orchestrator`
    - the container will join a zerotier network
  - openssh is configured and then started
  - generate an ssh key
- configure
  - configuring jumpscale and ays with its organization
  - configuring git
  - creating (or cloning) upstream repository
  - waits for being able to push to upstream, based on the generated public key
- starter
  - starts the `ays server`
  - starts the `orchestratorapiserver`
  - starts the front-end `caddy`
- blueprints
  - generate jwt tokens needed
  - create `configuration.bp`, `network.bp` and `bootstrap.bp` based on template and arguments
  - execute these 3 blueprints on ays

In order to configure this workflow, you need to pass multiple arguments to the script:
- `--server`: the remote Zero-OS server (address or hostname)
  - `--password`: optional password (jwt token) needed to connect the server
- `--container`: 0-orchestrator container name
- `--domain`: (optional) domain name used for caddy
- `--zt-net`: zerotier network the container need to join
- `--upstream`: upstream git repository (needs to be formatted: `ssh://user@host:repository`)
- `--email`: e-mail address used by git commits and caddy registration (default: `info@gig.tech`)
- `--organization`: (optional) organization to serve by 0-orchestrator
- `--client-id`: itsyou.online clientid used to generate a token
- `--client-secret`: itsyou.online clientsecret used to generate a token
- `--network`: network type to use (`g8`, `switchless` or `packet`)
  - `--network-vlan`: (only for `g8` and `switchless`) vlan tag id to use
  - `--network-cidr`: (only for `g8` and `switchless`) address CIDR to use
- `--nodes-zt-net`: zerotier network id of the nodes
- `--nodes-zt-token`: zerotier token to manage the nodes
- `--stor-organization`: 0-stor organization name as root (default: `--organization`)
- `--stor-namespace`: 0-stor root namespace to use (default: `"namespace"`)
- `--stor-client-id`: 0-stor itsyou.online client id (default: `--client-id`)
- `--stor-client-secret`: 0-stor itsyou.online client secret (default: `--client-secret`)
