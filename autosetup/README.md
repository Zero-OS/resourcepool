# autosetup

## orchestrator-flist
This script build a flist with all the needed orchestrator base files

This flist needs to be merged with:
- ubuntu flist, made for jumpscale based merge
- jumpscale with the right version needed by the orchestrator

At the end, you'll have theses layout:
- Default Ubuntu base system
  - Jumpscale and ays flist
    - Orchestrator apiserver, repositories and templates

## autobootstrap
This scipt automate an orchestrator deployment on a Zero-OS system.
> This system needs to be prepared before, eg: a disk need to be mounted to store container data

This script create a container based on the flist (built by orchestrator-flist) and configure everything.

TODO: arguments and explaination

## config-template
This is the `configuration.bp` template used by the orchestrator ays
