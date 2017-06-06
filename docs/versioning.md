# Versioning

Versioning in the Orchestrator is done through the `configuration` ays service.

This is an example of a configuration blueprint:

```yaml
configuration__main:
  configurations:
  - key: 'gw-flist'
    value: 'https://hub.gig.tech/deboeckj/g8osgw.flist'
  - key: '0-core-branch'
    value: 'master'
```

The schema contains one attribute `configuration` which is a list of an objects containing `key` and `value` attributes.

The following are the available keys:

* `js-version`: specifies the Jumpscale version the orchestrator services can be installed on. If it is not configured, any version will be allowed.
* `gw-flist`: specifies the flist used for the gateway container. Defaults to 'https://hub.gig.tech/gig-official-apps/g8osgw.flist'.
* `ovs-flist`: specifies the flist used for the ovs container. Defaults to 'https://hub.gig.tech/gig-official-apps/ovs.flist'.
* `0-core-branch`: specifies the branch used to build the core0 node. If it is not configured, any branch will be allowed.
* `0-core-revision`: specifies the revision used to build the core0 node. If it is not configured, any revision will be allowed.
* `rocksdb-flist`: specifies the flist used for the rocksdb container. Defaults to 'https://hub.gig.tech/gig-official-apps/ardb-rocksdb.flist'.
* `0-disk-flist`: specifies the flist containing the 0-disk utilities (nbd and g8os-store). Defaults to 'https://hub.gig.tech/gig-official-apps/0-disk-master.flist'.

