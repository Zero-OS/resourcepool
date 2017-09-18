# Export VM

### Requirements:
* To export a vm, FTP server should be already set up. FTP server container could be build by [vsftpd flist](https://hub.gig.tech/gig-official-apps/vsftpd.flist) or to build your own with [vsftpd-buildscript](../../buildscripts/builder-vsftpd.sh)

### Flow
* First FTP server url should be passed to the Orchestrator API like it's described in [api docs](https://rawgit.com/zero-os/0-orchestrator/master/raml/api.html)

* API will trigger the `export` action in the `vm` service
* The vm's `export` action will trigger the `export` action for each vdisk service attached to that vm
* Finally, a metadata for the vm will be stored in the ftp server to be used for import.

**Example of the metadata**

```
cpu: 1
cryptoKey: 9cdf6eacf7df008bdb8d9b4fcbabd214
disks:
- maxIOps: 2000
  vdiskid: vm1_1505657778
memory: 512
nics: []
node: '525400123456'
snapshotIDs:
- '1505658476515867'
vdisks:
- blockSize: 4096
  readOnly: false
  size: 4
  type: boot
```


# Import VM

### Requirements:
* To import a vm, FTP server should be already set up and already has the metadata from which we import the vm

### Flow
* First FTP server url of the metadata should be passed to the Orchestrator API like it's described in [api docs](https://rawgit.com/zero-os/0-orchestrator/master/raml/api.html)

* In the API, the metadata will be read from the ftp server
* The API will start creating vdisk services according to vdisks found, and trigger the `import` for each service
* Finally, VM will be created and started using the metadata provided and new vdisk services created
