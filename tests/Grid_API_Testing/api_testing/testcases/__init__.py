from api_testing.grid_apis.apis.nodes_apis import NodesAPI

def get_node_physical_ip(nodeid):
    response = nodes_api.get_nodes_nodeid_nics(nodeid)
    for nic in response.json():
        nic_hwaddr = nic['hardwareaddr'].replace(':', '') 
        if nic_hwaddr == nodeid:
            ip = nic['addrs'][0]
            return ip[:ip.rfind('/')]

def get_node_info():
    nodes_api = NodesAPI()
    nodes_info = []
    response = nodes_api.get_nodes()
    for node in response.json():
        if node['status'] == 'halted':
            continue
        ip = get_node_physical_ip(node['id'])
        nodes_info.append({"id":node['id'],
                            "ip": ip,
                            "status":node['status']})
    return nodes_info

nodes_api = NodesAPI()
NODES_INFO = get_node_info()