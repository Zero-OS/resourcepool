# 0-orchestrator autosetup

This subdirectory contains scripts to deploy a 0-orchestrator based on flist and
command lines arguments to configure everything

There is two main scripts:
- `orchestrator-flist.sh`: build an flist which contains 0-orchestrator dependencies
- `autobootstrap.py`: 0-orchestrator deployment script based on Zero-OS

## orchestrator-flist.sh
This script build an flist with all the needed orchestrator base files.

- This script is made to be executed on a `ubuntu:16.04` fresh docker.
- The script accept two **optional** arguments: `0-orchestrator-branch-name` and `0-core-branch-name`
  - If no argument are set, `master` will be used
  - If only one argument is set, both will use this branch name
  - If both arguments are set, they will use their respective branch
- The result image will be located at `/tmp/archives/0-orchestrator.tar.gz`

When you have the archive, this flist needs to be merged (via the hub) with:
- ubuntu flist, made for jumpscale based merge (eg: `gig-official-apps/ubuntu1604-for-js.flist`)
- jumpscale with the right version needed by the orchestrator

At the end, you'll have this flist layout:
```
+- Default Ubuntu base system
 +- Jumpscale and ays flist
  +- Orchestrator apiserver, repositories and templates
```

## autobootstrap.py
This scipt automate an orchestrator deployment on a Zero-OS system.
> This system needs to be prepared before, eg: a disk need to be mounted to store container data.

Here is the workflow of the deployment:
- connector
  - connect and authentificate to a remote Zero-OS server
- prepare
  - open required port on firewall (80 and 443)
  - run a container using 0-orchestrator flist
    - `/optvar` will be mounted from host `/var/cache/containers/orchestrator`
    - the container will join a zerotier network
  - openssh is configured then started
  - generate an ssh key
- configure
  - configuring jumpscale and ays with organization
  - configuring git
  - creating (or cloning) upstream repository
  - waits for being able to push on upstream, based on public key generated
- starter
  - starts the `ays server`
  - starts the `orchestratorapiserver`
  - starts the front-end `caddy`
- blueprints
  - generate jwt tokens needed
  - create `configuration.bp`, `network.bp` and `bootstrap.bp` based on template and arguments
  - execute these 3 blueprint on ays

In order to configure this workflow, you have multiple arguments to pass to the script:
- `--server`: the remote Zero-OS server (address or hostname)
  - `--password`: optional password (jwt token) needed to connect the
- `--container`: 0-orchestrator container name
- `--domain`: (optional) domain name used for caddy
- `--ztnet`: zerotier network the container need to joins
- `--upstream`: upstream git repository (need to be formatted: `ssh://user@host:repository`)
- `--email`: e-mail address used by git commits and caddy registration (default: `info@gig.tech`)
- `--organization`: (optional) organization to server by 0-orchestrator
- `--clientid`: itsyou.online clientid used to generate a token
- `--clientsecret`: itsyou.online clientsecret used to generate a token
- `--network`: network type to use (`g8`, `switchless` or `packet`)
  - `--vlan`: (only for `g8` and `switchless`) vlan tag id to use
  - `--cidr`: (only for `g8` and `switchless`) address CIDR to use
