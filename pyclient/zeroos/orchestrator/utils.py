import json


def Write_Status_code_Error(job, exception):
    service = job.service
    if 499 >= exception.code >= 400:
        job.model.dbobj.result = json.dumps({'message': exception.message, 'code': exception.code}).encode()
    service.saveAll()
    return


def find_disks(disk_type, nodes, partitionName):
    """
    return a list of disk that are not used by storage pool
    or has a different type as the one required for this cluster
    """
    available_disks = {}
    partitionName

    def check_partition(disk):
        for partition in disk.partitions:
            for filesystem in partition.filesystems:
                if filesystem['label'].startswith(partitionName):
                    return True

    for node in nodes:
        for disk in node.disks.list():
            # skip disks of wrong type
            if disk.type.name != disk_type:
                    continue
            # skip devices which have filesystems on the device
            if len(disk.filesystems) > 0:
                continue

            # include devices which have partitions
            if len(disk.partitions) == 0:
                available_disks.setdefault(node.name, []).append(disk)
            else:
                if check_partition(disk):
                    # devices that have partitions with correct label will be in the beginning
                    available_disks.setdefault(node.name, []).insert(0, disk)
    return available_disks
