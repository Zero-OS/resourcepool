import random
import time
import unittest
from testcases.testcases_base import TestcasesBase


class TesthealthcheckAPI(TestcasesBase):

    def setUp(self):
        self.lg.info(' [*] Get healthcheck of random node ')
        self.random_node = self.get_random_node()
        response = self.healthcheck_api.get_node_health(self.random_node)
        self.assertEqual(response.status_code, 200)
        self.healthchecks = response.json()["healthchecks"]

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/950')
    def test001_list_healthcheck(self):
        """ GAT-168

        **Test Scenario:**

        #. Get list of nodes .
        #. Get list of a nodes healthcheck,should succeed.
        #. Check that all nodes have health check, should succeed.
        #. Check that all nodes have the same status result.
        """

        self.lg.info("Get list of nodes . ")
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        nodes_result = response.json()

        self.lg.info("Get list of a nodes healthcheck,should succeed.")
        response = self.healthcheck_api.get_all_nodes_health()
        self.assertEqual(response.status_code, 200)
        health_result = response.json()

        self.lg.info(" Check that all nodes have health check, should succeed. ")
        self.assertEqual(len(health_result), len(nodes_result))

        self.lg.info("Check that all nodes have the same status result")
        for node in health_result:
            status = [n['status']for n in nodes_result if n['id'] == node['id']]
            self.assertEqual(node['status'], status[0])
