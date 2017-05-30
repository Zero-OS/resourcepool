# Block Device Performance Test


- Requirements:

    * `pip3 install git+https://github.com/zero-os/0-rest-api.git#subdirectory=pyclient`
    * `pip3 install git+https://github.com/zero-os/0-core.git#subdirectory=pyclient`

- Run [bd-performance.py](./bd-performance.py)

```
python3 bd-performance.py [Options]

Options:
  --restapiserver TEXT       0-rest-api api server endpoint. Eg
                             http://192.168.193.212:8080
  --storagecluster TEXT      Name of the storage cluster in which the vdisks
                             need to be created
  --vdiskCount INTEGER       Number of vdisks that need to be created

  --vdiskSize INTEGER        Size of disks in GB
  --runtime INTEGER          Time fio should be run
  --vdiskType TEXT           Type of disk, should be: boot, db, cache, tmp

  --resultDir TEXT           Results directory path
  --nodeLimit                Limit the number of nodes
  --help                     Show this message and exit.
```
