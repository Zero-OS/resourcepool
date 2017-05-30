from zeroos.restapi import  client
import prettytable


def main(url):
    api = client.APIClient(url)
    table = prettytable.PrettyTable(["Node", "VMS", "Containers"])
    for node in api.nodes.ListNodes().json():
        runningcontainers = 0
        totalcontainers = 0
        runningvms = 0
        totalvms = 0
        for container in api.nodes.ListContainers(node['id']).json():
            if container['status'] == 'running':
                runningcontainers += 1
            totalcontainers += 1
        for vm in api.nodes.ListVMs(node['id']).json():
            if vm['status'] == 'running':
                runningvms += 1
            totalvms += 1
        table.add_row([node['hostname'], "{}/{}".format(runningvms, totalvms), "{}/{}".format(runningcontainers, totalcontainers)])
    print(table.get_string(sortby='Node'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL of 0 rest api')
    options = parser.parse_args()
    main(options.url)
