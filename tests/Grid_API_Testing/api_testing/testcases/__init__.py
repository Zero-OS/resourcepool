from api_testing.orchestrator_api.orchestrator_client.nodes_apis import NodesAPI

def get_node_info():
    nodes_info = []
    response = nodes_api.get_nodes()
    if response.status_code == 200:
        for node in response.json():
            if node['status'] == 'halted':
                continue
            nodes_info.append({"id":node['id'],
                                "ip": node['ipaddress'],
                                "status":node['status']})
        return nodes_info
    else:
        raise RuntimeError('Cannot list nodes. Error: {error}'.format(error=response.content))


nodes_api = NodesAPI()
NODES_INFO = get_node_info()

if not NODES_INFO:
    raise RuntimeError('no nodes available')