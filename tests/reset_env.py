for node in c.api.nodes.ListNodes().json()
    for container in c.api.nodes.ListContainers(nodeid=node['id']).json():
        if container['flist'].endswith('/performance-test.flist'):
            c.api.nodes.DeleteContainer(nodeid=node['id'], containername=container['name'])
        if container['flist'].endswith('/blockstor-master.flist'):
            c.api.nodes.DeleteContainer(nodeid=node['id'], containername=container['name'])
    c.api.nodes.RebootNode(nodeid=node['id'], data=dict())
