from api_testing.grid_apis.orchestrator_client.nodes_apis import NodesAPI

def get_node_info():
    nodes_info = []
    response = nodes_api.get_nodes()
    for node in response.json():
        if node['status'] == 'halted':
            continue
        nodes_info.append({"id":node['id'],
                            "ip": node['ipaddress'],
                            "status":node['status']})
    return nodes_info

nodes_api = NodesAPI()
NODES_INFO = get_node_info()