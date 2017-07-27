import netaddr


def combine(ip1, ip2, mask):
    """
    >>> combine('10.0.3.11', '192.168.1.10', 24)
    '10.0.3.10'
    """
    iip1 = netaddr.IPNetwork('{}/{}'.format(ip1, mask))
    iip2 = netaddr.IPNetwork('{}/{}'.format(ip2, mask))
    ires = iip1.network + int(iip2.ip & (~ int(iip2.netmask)))
    net = netaddr.IPNetwork(ires)
    net.prefixlen = mask
    return net


class Network:
    def __init__(self, node):
        self.node = node
        self._client = node.client

    def get_management_info(self):
        import netaddr

        def get_nic_ip(nics, name):
            for nic in nics:
                if nic['name'] == name:
                    for ip in nic['addrs']:
                        return netaddr.IPNetwork(ip['addr'])
                    return

        defaultgwdev = self._client.bash("ip route | grep default | awk '{print $5}'").get().stdout.strip()
        nics = self._client.info.nic()
        mgmtaddr = None
        if defaultgwdev:
            ipgwdev = get_nic_ip(nics, defaultgwdev)
            if ipgwdev:
                mgmtaddr = str(ipgwdev.ip)
        if not mgmtaddr:
            mgmtaddr = self.node.addr

        return mgmtaddr

    def get_addresses(self, network):
        mgmtaddr = self.get_management_info()
        return {
            'storageaddr': combine(str(network.ip), mgmtaddr, network.prefixlen),
            'vxaddr': combine('10.240.0.0', mgmtaddr, network.prefixlen),
        }

    def get_free_nics(self):
        nics = self._client.info.nic()
        nics.sort(key=lambda nic: nic['speed'])
        availablenics = {}
        for nic in nics:
            # skip all interface that have an ipv4 address
            if any(netaddr.IPNetwork(addr['addr']).version == 4 for addr in nic['addrs'] if 'addr' in addr):
                continue
            if nic['speed'] == 0:
                continue
            availablenics.setdefault(nic['speed'], []).append(nic['name'])
        return sorted(availablenics.items())
