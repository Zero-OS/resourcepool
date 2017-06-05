class NodesService:
    def __init__(self, client):
        self.client = client



    def DeleteBridge(self, bridgeid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Remove bridge
        It is method for DELETE /nodes/{nodeid}/bridges/{bridgeid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/bridges/"+bridgeid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetBridge(self, bridgeid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get bridge details
        It is method for GET /nodes/{nodeid}/bridges/{bridgeid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/bridges/"+bridgeid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListBridges(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List bridges
        It is method for GET /nodes/{nodeid}/bridges
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/bridges"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateBridge(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Creates a new bridge
        It is method for POST /nodes/{nodeid}/bridges
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/bridges"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetContainerCPUInfo(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of all CPUs in the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/cpus
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/cpus"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetContainerDiskInfo(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of all the disks in the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/disks
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/disks"
        return self.client.get(uri, None, headers, query_params, content_type)


    def FileDelete(self, data, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete file from container
        It is method for DELETE /nodes/{nodeid}/containers/{containername}/filesystem
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/filesystem"
        return self.client.delete(uri, data, headers, query_params, content_type)


    def FileDownload(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Download file from container
        It is method for GET /nodes/{nodeid}/containers/{containername}/filesystem
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/filesystem"
        return self.client.get(uri, None, headers, query_params, content_type)


    def FileUpload(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Upload file to container
        It is method for POST /nodes/{nodeid}/containers/{containername}/filesystem
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/filesystem"
        return self.client.post(uri, None, headers, query_params, content_type)


    def GetContainerOSInfo(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of the container OS
        It is method for GET /nodes/{nodeid}/containers/{containername}/info
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/info"
        return self.client.get(uri, None, headers, query_params, content_type)


    def KillContainerJob(self, jobid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kills the job
        It is method for DELETE /nodes/{nodeid}/containers/{containername}/jobs/{jobid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs/"+jobid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetContainerJob(self, jobid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get details of a submitted job on the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/jobs/{jobid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs/"+jobid
        return self.client.get(uri, None, headers, query_params, content_type)


    def SendSignalToJob(self, data, jobid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Send signal to the job
        It is method for POST /nodes/{nodeid}/containers/{containername}/jobs/{jobid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs/"+jobid
        return self.client.post(uri, data, headers, query_params, content_type)


    def KillAllContainerJobs(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kill all running jobs on the container
        It is method for DELETE /nodes/{nodeid}/containers/{containername}/jobs
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs"
        return self.client.delete(uri, None, headers, query_params, content_type)


    def ListContainerJobs(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List running jobs on the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/jobs
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs"
        return self.client.get(uri, None, headers, query_params, content_type)


    def StartContainerJob(self, data, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Start a new job in this container
        It is method for POST /nodes/{nodeid}/containers/{containername}/jobs
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/jobs"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetContainerMemInfo(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information about the memory in the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/mem
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/mem"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetContainerNicInfo(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information about the network interfaces in the container
        It is method for GET /nodes/{nodeid}/containers/{containername}/nics
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/nics"
        return self.client.get(uri, None, headers, query_params, content_type)


    def PingContainer(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Ping this container
        It is method for POST /nodes/{nodeid}/containers/{containername}/ping
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/ping"
        return self.client.post(uri, None, headers, query_params, content_type)


    def KillContainerProcess(self, processid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kills the process by sending sigterm signal to the process. If it is still running, a sigkill signal will be sent to the process
        It is method for DELETE /nodes/{nodeid}/containers/{containername}/processes/{processid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/processes/"+processid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetContainerProcess(self, processid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get process details
        It is method for GET /nodes/{nodeid}/containers/{containername}/processes/{processid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/processes/"+processid
        return self.client.get(uri, None, headers, query_params, content_type)


    def SendSignalToProcess(self, data, processid, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Send signal to the process
        It is method for POST /nodes/{nodeid}/containers/{containername}/processes/{processid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/processes/"+processid
        return self.client.post(uri, data, headers, query_params, content_type)


    def ListContainerProcesses(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get running processes in this container
        It is method for GET /nodes/{nodeid}/containers/{containername}/processes
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/processes"
        return self.client.get(uri, None, headers, query_params, content_type)


    def StartContainer(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Start container instance
        It is method for POST /nodes/{nodeid}/containers/{containername}/start
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/start"
        return self.client.post(uri, None, headers, query_params, content_type)


    def GetContainerState(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get aggregated consumption of container + all processes (CPU, memory, etc.)
        It is method for GET /nodes/{nodeid}/containers/{containername}/state
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/state"
        return self.client.get(uri, None, headers, query_params, content_type)


    def StopContainer(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Stop container instance
        It is method for POST /nodes/{nodeid}/containers/{containername}/stop
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername+"/stop"
        return self.client.post(uri, None, headers, query_params, content_type)


    def DeleteContainer(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete container instance
        It is method for DELETE /nodes/{nodeid}/containers/{containername}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetContainer(self, containername, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get container
        It is method for GET /nodes/{nodeid}/containers/{containername}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers/"+containername
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListContainers(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List running containers
        It is method for GET /nodes/{nodeid}/containers
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateContainer(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new container
        It is method for POST /nodes/{nodeid}/containers
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/containers"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetCPUInfo(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of all CPUs in the node
        It is method for GET /nodes/{nodeid}/cpus
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/cpus"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetDiskInfo(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of all the disks in the node
        It is method for GET /nodes/{nodeid}/disks
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/disks"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetGWFWConfig(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get current FW config
        It is method for GET /nodes/{nodeid}/gws/{gwname}/advanced/firewall
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/advanced/firewall"
        return self.client.get(uri, None, headers, query_params, content_type)


    def SetGWFWConfig(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Set FW config
        Once used you can not use gw.portforwards any longer
        It is method for POST /nodes/{nodeid}/gws/{gwname}/advanced/firewall
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/advanced/firewall"
        return self.client.post(uri, None, headers, query_params, content_type)


    def GetGWHTTPConfig(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get current HTTP config
        It is method for GET /nodes/{nodeid}/gws/{gwname}/advanced/http
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/advanced/http"
        return self.client.get(uri, None, headers, query_params, content_type)


    def SetGWHTTPConfig(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Set HTTP config
        Once used you can not use gw.httpproxxies any longer
        It is method for POST /nodes/{nodeid}/gws/{gwname}/advanced/http
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/advanced/http"
        return self.client.post(uri, None, headers, query_params, content_type)


    def DeleteDHCPHost(self, macaddress, interface, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete dhcp host
        It is method for DELETE /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts/{macaddress}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/dhcp/"+interface+"/hosts/"+macaddress
        return self.client.delete(uri, None, headers, query_params, content_type)


    def ListGWDHCPHosts(self, interface, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List DHCPHosts for specified interface
        It is method for GET /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/dhcp/"+interface+"/hosts"
        return self.client.get(uri, None, headers, query_params, content_type)


    def AddGWDHCPHost(self, data, interface, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Add a dhcp host to a specified interface
        It is method for POST /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/dhcp/"+interface+"/hosts"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteGWForward(self, forwardid, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete portforward, forwardid = srcip:srcport
        It is method for DELETE /nodes/{nodeid}/gws/{gwname}/firewall/forwards/{forwardid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/firewall/forwards/"+forwardid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetGWForwards(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get list for IPv4 Forwards
        It is method for GET /nodes/{nodeid}/gws/{gwname}/firewall/forwards
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/firewall/forwards"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateGWForwards(self, data, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new Portforwarding
        It is method for POST /nodes/{nodeid}/gws/{gwname}/firewall/forwards
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/firewall/forwards"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteHTTPProxies(self, proxyid, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete HTTP proxy
        It is method for DELETE /nodes/{nodeid}/gws/{gwname}/httpproxies/{proxyid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/httpproxies/"+proxyid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetHTTPProxy(self, proxyid, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get info of HTTP proxy
        It is method for GET /nodes/{nodeid}/gws/{gwname}/httpproxies/{proxyid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/httpproxies/"+proxyid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListHTTPProxies(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List for HTTP proxies
        It is method for GET /nodes/{nodeid}/gws/{gwname}/httpproxies
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/httpproxies"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateHTTPProxies(self, data, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create new HTTP proxies
        It is method for POST /nodes/{nodeid}/gws/{gwname}/httpproxies
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/httpproxies"
        return self.client.post(uri, data, headers, query_params, content_type)


    def StartGateway(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Start Gateway instance
        It is method for POST /nodes/{nodeid}/gws/{gwname}/start
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/start"
        return self.client.post(uri, None, headers, query_params, content_type)


    def StopGateway(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Stop gateway instance
        It is method for POST /nodes/{nodeid}/gws/{gwname}/stop
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname+"/stop"
        return self.client.post(uri, None, headers, query_params, content_type)


    def DeleteGateway(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete gateway instance
        It is method for DELETE /nodes/{nodeid}/gws/{gwname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetGateway(self, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get gateway
        It is method for GET /nodes/{nodeid}/gws/{gwname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname
        return self.client.get(uri, None, headers, query_params, content_type)


    def UpdateGateway(self, data, gwname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Update Gateway
        It is method for PUT /nodes/{nodeid}/gws/{gwname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws/"+gwname
        return self.client.put(uri, data, headers, query_params, content_type)


    def ListGateways(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List running gateways
        It is method for GET /nodes/{nodeid}/gws
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateGW(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new gateway
        It is method for POST /nodes/{nodeid}/gws
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/gws"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetNodeOSInfo(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of the OS of the node
        It is method for GET /nodes/{nodeid}/info
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/info"
        return self.client.get(uri, None, headers, query_params, content_type)


    def KillNodeJob(self, jobid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kills the job
        It is method for DELETE /nodes/{nodeid}/jobs/{jobid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/jobs/"+jobid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetNodeJob(self, jobid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get the details of a submitted job
        It is method for GET /nodes/{nodeid}/jobs/{jobid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/jobs/"+jobid
        return self.client.get(uri, None, headers, query_params, content_type)


    def KillAllNodeJobs(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kill all running jobs
        It is method for DELETE /nodes/{nodeid}/jobs
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/jobs"
        return self.client.delete(uri, None, headers, query_params, content_type)


    def ListNodeJobs(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List running jobs
        It is method for GET /nodes/{nodeid}/jobs
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/jobs"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetMemInfo(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information about the memory in the node
        It is method for GET /nodes/{nodeid}/mem
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/mem"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetNodeMounts(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of all the mountpoints on the node
        It is method for GET /nodes/{nodeid}/mounts
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/mounts"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetNicInfo(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information about the network interfaces in the node
        It is method for GET /nodes/{nodeid}/nics
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/nics"
        return self.client.get(uri, None, headers, query_params, content_type)


    def PingNode(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Ping this node
        It is method for POST /nodes/{nodeid}/ping
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/ping"
        return self.client.post(uri, None, headers, query_params, content_type)


    def KillNodeProcess(self, processid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Kills the process by sending sigterm signal to the process. If it is still running, a sigkill signal will be sent to the process
        It is method for DELETE /nodes/{nodeid}/processes/{processid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/processes/"+processid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetNodeProcess(self, processid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get process details
        It is method for GET /nodes/{nodeid}/processes/{processid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/processes/"+processid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListNodeProcesses(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get processes
        It is method for GET /nodes/{nodeid}/processes
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/processes"
        return self.client.get(uri, None, headers, query_params, content_type)


    def RebootNode(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Immediately reboot the machine
        It is method for POST /nodes/{nodeid}/reboot
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/reboot"
        return self.client.post(uri, None, headers, query_params, content_type)


    def GetNodeState(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        The aggregated consumption of node + all processes (cpu, memory, etc...)
        It is method for GET /nodes/{nodeid}/state
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/state"
        return self.client.get(uri, None, headers, query_params, content_type)


    def DeleteStoragePoolDevice(self, deviceuuid, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Removes the device from the storage pool
        It is method for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/devices/{deviceuuid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/devices/"+deviceuuid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetStoragePoolDeviceInfo(self, deviceuuid, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get information of the device
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/devices/{deviceuuid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/devices/"+deviceuuid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListStoragePoolDevices(self, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List the devices in the storage pool
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/devices
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/devices"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateStoragePoolDevices(self, data, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Add extra devices to this storage pool
        It is method for POST /nodes/{nodeid}/storagepools/{storagepoolname}/devices
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/devices"
        return self.client.post(uri, data, headers, query_params, content_type)


    def RollbackFilesystemSnapshot(self, snapshotname, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Rollback the file system to the state at the moment the snapshot was taken
        It is method for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshots/{snapshotname}/rollback
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname+"/snapshots/"+snapshotname+"/rollback"
        return self.client.post(uri, None, headers, query_params, content_type)


    def DeleteFilesystemSnapshot(self, snapshotname, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete snapshot
        It is method for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshots/{snapshotname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname+"/snapshots/"+snapshotname
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetFilesystemSnapshotInfo(self, snapshotname, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information on the snapshot
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshots/{snapshotname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname+"/snapshots/"+snapshotname
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListFilesystemSnapshots(self, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List snapshots of this file system
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshots
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname+"/snapshots"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateSnapshot(self, data, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new read-only snapshot of the current state of the vdisk
        It is method for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshots
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname+"/snapshots"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteFilesystem(self, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete file system
        It is method for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetFilesystemInfo(self, filesystemname, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed file system information
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems/"+filesystemname
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListFilesystems(self, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List all file systems
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateFilesystem(self, data, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new file system
        It is method for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname+"/filesystems"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteStoragePool(self, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete the storage pool
        It is method for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetStoragePoolInfo(self, storagepoolname, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of this storage pool
        It is method for GET /nodes/{nodeid}/storagepools/{storagepoolname}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools/"+storagepoolname
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListStoragePools(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List storage pools present in the node
        It is method for GET /nodes/{nodeid}/storagepools
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateStoragePool(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new storage pool in the node
        It is method for POST /nodes/{nodeid}/storagepools
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/storagepools"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetVMInfo(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get statistical information about the virtual machine.
        It is method for GET /nodes/{nodeid}/vms/{vmid}/info
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/info"
        return self.client.get(uri, None, headers, query_params, content_type)


    def MigrateVM(self, data, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Migrate the virtual machine to another host
        It is method for POST /nodes/{nodeid}/vms/{vmid}/migrate
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/migrate"
        return self.client.post(uri, data, headers, query_params, content_type)


    def PauseVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Pauses the VM
        It is method for POST /nodes/{nodeid}/vms/{vmid}/pause
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/pause"
        return self.client.post(uri, None, headers, query_params, content_type)


    def ResumeVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Resumes the virtual machine
        It is method for POST /nodes/{nodeid}/vms/{vmid}/resume
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/resume"
        return self.client.post(uri, None, headers, query_params, content_type)


    def ShutdownVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Gracefully shutdown the virtual machine
        It is method for POST /nodes/{nodeid}/vms/{vmid}/shutdown
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/shutdown"
        return self.client.post(uri, None, headers, query_params, content_type)


    def StartVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Start the virtual machine
        It is method for POST /nodes/{nodeid}/vms/{vmid}/start
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/start"
        return self.client.post(uri, None, headers, query_params, content_type)


    def StopVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Stops the VM
        It is method for POST /nodes/{nodeid}/vms/{vmid}/stop
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid+"/stop"
        return self.client.post(uri, None, headers, query_params, content_type)


    def DeleteVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Deletes the virtual machine
        It is method for DELETE /nodes/{nodeid}/vms/{vmid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetVM(self, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get the virtual machine object
        It is method for GET /nodes/{nodeid}/vms/{vmid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid
        return self.client.get(uri, None, headers, query_params, content_type)


    def UpdateVM(self, data, vmid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Updates the virtual machine
        It is method for PUT /nodes/{nodeid}/vms/{vmid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms/"+vmid
        return self.client.put(uri, data, headers, query_params, content_type)


    def ListVMs(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List all virtual machines
        It is method for GET /nodes/{nodeid}/vms
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateVM(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Creates a new virtual machine
        It is method for POST /nodes/{nodeid}/vms
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/vms"
        return self.client.post(uri, data, headers, query_params, content_type)


    def ExitZerotier(self, zerotierid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Exit the ZeroTier network
        It is method for DELETE /nodes/{nodeid}/zerotiers/{zerotierid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/zerotiers/"+zerotierid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetZerotier(self, zerotierid, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get ZeroTier network details
        It is method for GET /nodes/{nodeid}/zerotiers/{zerotierid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/zerotiers/"+zerotierid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListZerotier(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        List running ZeroTier networks
        It is method for GET /nodes/{nodeid}/zerotiers
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/zerotiers"
        return self.client.get(uri, None, headers, query_params, content_type)


    def JoinZerotier(self, data, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Join ZeroTier network
        It is method for POST /nodes/{nodeid}/zerotiers
        """
        uri = self.client.base_url + "/nodes/"+nodeid+"/zerotiers"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteNode(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a node
        It is method for DELETE /nodes/{nodeid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetNode(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of a node
        It is method for GET /nodes/{nodeid}
        """
        uri = self.client.base_url + "/nodes/"+nodeid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListNodes(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all nodes
        It is method for GET /nodes
        """
        uri = self.client.base_url + "/nodes"
        return self.client.get(uri, None, headers, query_params, content_type)
