# autosetup

## orchestrator-flist
This script build a flist with all the needed orchestrator base files.

- The script accept two optional arguments: `0-orchestrator-branch-name` and `0-core-branch-name`
 - If no argument are set, `master` will be used
 - If only one argument is set, both will use this branch name
 - If both arguments are set, they will use their respective branch
- This script is made to be executed on a `ubuntu:16.04` fresh docker.
- The result image will be located at `/tmp/archives/0-orchestrator.tar.gz`

When you have the archive, this flist needs to be merged (via the hub) with:
- ubuntu flist, made for jumpscale based merge (eg: `gig-official-apps/ubuntu1604-for-js.flist`)
- jumpscale with the right version needed by the orchestrator

At the end, you'll have this layout:
```
+- Default Ubuntu base system
 +- Jumpscale and ays flist
  +- Orchestrator apiserver, repositories and templates
```

## autobootstrap
This scipt automate an orchestrator deployment on a Zero-OS system.
> This system needs to be prepared before, eg: a disk need to be mounted to store container data

This script create a container based on the flist (built by orchestrator-flist) and configure everything.

TODO: arguments and explaination

## config-template
This is the `configuration.bp` template used by the orchestrator ays
