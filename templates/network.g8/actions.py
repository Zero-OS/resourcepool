 def configure(job):
    """
    this method will be called from the node.g8os install action.
    """
    if 'node_name' not in job.model.args:
        raise ValueError("argument node_name not present in job argument")

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(node))
    # TODO: complete once we have openvswtich integrated in core0
