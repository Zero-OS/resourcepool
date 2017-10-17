from testcases.testcases_base import TestcasesBase
import unittest


class TestNodeidAPI(TestcasesBase):

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1215')
    def test001_check_processes_after_node_reboot(self):
        """ GAT-018
        **Test Scenario:**

        #. Choose one random node (N0) from list of running nodes.
        #. Create a gateway with processes that corresponds to certain services.
        #. Create a bridge on node (N0), should succeed.
        #. Create storagepool (SP0) on node (N0), should succeed
        #. Reboot the node, should succeed.
        #. Make sure that all the processes are running.
        #. Make sure the Bridge is recreated and the Storagepool is remounted
        """
        """
        ## This test case is never been executed
        ## This bp need to be executed in the installation
        ## for influx, grafana and statscollector
        statsdb__two:
            node: '54a9f715dbb1'
            port: 9086

        actions:
            - action: install
        """

        self.lg.info('Create a gateway with processes that corresponds to certain services')
        nics = {"name": "nic2", "type": "vxlan", "id": "100",
                "config": {"cidr": "192.168.112.22/24"},
                "dhcpserver":
                {"nameservers": ["8.8.8.8"],
                 "hosts": [
                 {"macaddress": "00:A0:C9:14:C8:29",
                  "hostname": "test", "ipaddress": "192.168.112.11",
                  "cloudinit":
                        {"metadata": "{\"local-hostname\":\"myvm\"}",
                         "userdata": "{\"users\":[{\"name\":\"myuser\",\"plain_text_passwd\":\"mypassword\"}]}"
                         }}]}}
        httpproxies = [
            {"host": "192.168.58.22",
             "types": ["http", "https"],
             "destinations":["192.168.58.11"]
             }]
        response_gw, data_gw = self.gateways_api.post_nodes_gateway(self.nodeid, nics=nics, httpproxies=httpproxies)
        self.assertEqual(response_gw.status_code, 201, response.content)

        self.lg.info('Create a bridge, should succeed')
        response_b, data_b = self.bridges_api.pst_nodes_bridges(node_id=self.nodeid)
        self.assertEqual(response_b.status_code, 201)

        self.lg.info('Create a storagepool, should succeed')
        freeDisks = [x['name'] for x in self.core0_client.getFreeDisks()]
        response_sp, data_sp = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                        free_devices=freeDisks)
        self.assertEqual(response_sp.status_code, 201)


        self.lg.info('Reboot the node, should succeed')
        response = self.nodes_api.post_nodes_nodeid_reboot(self.nodeid)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Make sure that all the processes are running')
        processes = str(self.core0_client.get_processes_list())
        self.assertIn('caddy-http', processes)
        self.assertIn('cloud-init', processes)
        self.assertIn('dhcp', processes)
        self.assertIn('grafana', processes)
        self.assertIn('influx', processes)
        self.assertIn('statscollector', processes)

        self.lg.info('Make sure the Bridge is recreated and the Storagepool is remounted')
        response = str(client.bash('ip a').get())
        self.assertIn(data_b['name'], response)
        response = str(client.bash('df -h').get())
        self.assertIn('/mnt/storagepools/%s' % data_sp['name'], response)

        self.lg.info('Delete the gateway')
        self.gateways_api.delete_nodes_gateway(self.nodeid, data_gw['name'])

        self.lg.info('Delete the bridge, should succeed')
        self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, data_b['name'])

        self.lg.info('Delete the storagepool, should succeed')
        self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, data_sp['name'])
