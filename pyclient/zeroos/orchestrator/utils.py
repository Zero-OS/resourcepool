import json
import requests
import math


def write_status_code_error(job, exception):
    service = job.service
    if 499 >= exception.code >= 400:
        job.model.dbobj.result = json.dumps({'message': exception.message, 'code': exception.code}).encode()
    service.saveAll()
    return


def find_disks(disk_type, nodes, partition_name):
    """
    return a list of disk that are not used by storage pool
    or has a different type as the one required for this cluster
    """
    available_disks = {}

    def check_partition(disk):
        for partition in disk.partitions:
            for filesystem in partition.filesystems:
                if filesystem['label'].startswith(partition_name):
                    return True

    for node in nodes:
        available_disks.setdefault(node.name, [])
        for disk in node.disks.list():
            # skip disks of wrong type
            if disk.type.name != disk_type:
                continue
            # skip devices which have filesystems on the device
            if len(disk.filesystems) > 0:
                continue

            # include devices which have partitions
            if len(disk.partitions) == 0:
                available_disks[node.name].append(disk)
            else:
                if check_partition(disk):
                    # devices that have partitions with correct label will be in the beginning
                    available_disks[node.name].insert(0, disk)
    return available_disks


def send_event(event_type, data, aysrepo):
    """
    Post data to all webhooks that are registered to event_type.
    :param event_type: the event type for which the webhook is triggered
    :param data: payload of the webhook
    :param aysrepo: ays repo to search for webhooks in
    :return:
    """
    webhook_services = aysrepo.servicesFind(role='webhook')
    for webhook_service in webhook_services:
        if event_type in webhook_service.model.data.eventtypes:
            requests.post(webhook_service.model.data.url, data=data)
