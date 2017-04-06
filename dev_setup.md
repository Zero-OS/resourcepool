# Grid REST API dev environment setup

## 1. Install jumpscale
```shell
cd $TMPDIR
rm -f install.sh
export JSBRANCH="8.2.0"
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh
bash install.sh
```

## 2. Install g8core python client
```shell
git clone https://github.com/g8os/core0/
cd core0
git checkout 0.12.0
cd pyclient
pip install .
```

## 3. Start jumpscale and create a AYS repository
This command will start AYS in tmux:
```shell
ays start --bind 0.0.0.0 --debug
```

Create the AYS repository:
```shell
ays repo create --name grid --git http://github.com/user/repo
```

## 4. Clone ays templates
```
cd /opt/code/
git clone https://github.com/g8os/grid/
cd grid
git checkout 0.2.0
ays reload
```

## 5. Install auto node discovery service:
Copy this in the blueprints directory of you AYS repo:
```yaml
bootstrap.g8os__grid1:

actions:
  - action: install
```
Then execute it:
```shell
ays blueprint
ays run create --follow
```

## 6. Start G8OS
For that you'll need to have the kernel compiled, see : https://github.com/g8os/initramfs

Example how to start a VM running G8OS using qemu:
```bash
qemu-system-x86_64 -kernel g8os-kernel.efi \
    -m 2048 -enable-kvm -cpu host \
    -net nic,model=e1000 -net bridge,br=lxc0 \
    -drive file=vda.qcow2,if=virtio \
    -drive file=vdb.qcow2,if=virtio \
    -drive file=vdc.qcow2,if=virtio \
    -drive file=vdd.qcow2,if=virtio \
    -drive file=vde.qcow2,if=virtio \
    -nodefaults -nographic \
    -serial null -serial mon:stdio \
    -append 'ays=localhost:5000'
```
This command start the VM with 5 disk attached to it.
Note the `-append` where we specify the address of the AYS server. This is used for autodiscovery of the node when they boot.

Once your G8OS is booted, you should have the `node.g8os` services created.
