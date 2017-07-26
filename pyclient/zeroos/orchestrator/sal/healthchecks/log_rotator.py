import re
import os
import datetime

descr = """
Rotate know log files if their size hit 10G or more
"""

def action(node, locations=['/var/log'], limit=10):
    result = {}
    result['id'] = 'LOGROTATOR'
    result['name'] = 'LOGROTATOR'
    result['status'] = 'OK'
    result['resource'] = "LOG ROTATOR"
    result['message'] = 'Logs did not reach {limit}G'.format(limit=limit)

    if "/var/log" not in locations:
        locations.append("/var/log")
    logs = []
    try:
        # Get total size for all log files
        log_size = getLogSize(node, locations)

        # Rotate logs if they are larger than the limit
        if log_size/(1024 * 1024 * 1024) >= limit: #convert bytes to GIGA
            # Rotate core.log

            for location in locations:
                # Get Files for this location
                location_files = getFiles(node, location, [])
                logs.extend(location_files)

            for file_path in logs:
                if file_path == '/var/log/core.log':
                    continue
                # Delete old rotated files to free up some space
                # match file.*.date.time
                if re.match(".*\d{8}-\d{6}", file_path):
                    node.client.filesystem.remove(file_path)
                else:
                    new_path = "%s.%s" % (file_path, datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
                    # Rotate the new logs
                    node.client.filesystem.move(file_path, new_path)
                    # Create a new EMPTY file with the same name
                    fd = node.client.filesystem.open(file_path, 'x')
                    node.client.filesystem.close(fd)
            node.client.logger.reopen()
            result['message'] = 'Logs cleared'
    except Exception as e:
        result['message'] = "Error happened, Can not clear logs"
        result['status'] = "ERROR"

    return [result]

def getFiles(node, location, files=[]):
    for item in node.client.filesystem.list(location):
        if not item['is_dir']:
            files.append(os.path.join(location, item['name']))
        else:
            files = getFiles(node, os.path.join(location, item['name']), files)
    return files

def getLogSize(node, locations):
    size = 0
    for location in locations:
        items = node.client.filesystem.list(location)
        for item in items:
            size += item['size']
    return size

if __name__ == '__main__':
    action()
