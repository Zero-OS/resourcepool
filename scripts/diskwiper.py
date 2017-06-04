#!/usr/bin/env python3
from zeroos.core0.client import Client
import sys


def main():
    args = sys.argv[1:]
    for nodehost in args:
        client = Client(nodehost)
        print('Wiping node {hostname}'.format(**client.info.os()))
        mounteddevices = {mount['device']: mount for mount in client.info.disk()}

        def getmountpoint(device):
            for mounteddevice, mount in mounteddevices.items():
                if mounteddevice.startswith(device):
                    return mount

        for disk in client.disk.list()['blockdevices']:
            devicename = '/dev/{}'.format(disk['kname'])
            mount = getmountpoint(devicename)
            if not mount:
                print('   * Wiping disk {kname}'.format(**disk))
                client.system('dd if=/dev/zero of={} bs=1M count=50'.format(devicename))
            else:
                print('   * Not wiping {device} mounted at {mountpoint}'.format(device=devicename, mountpoint=mount['mountpoint']))


if __name__ == '__main__':
    main()
