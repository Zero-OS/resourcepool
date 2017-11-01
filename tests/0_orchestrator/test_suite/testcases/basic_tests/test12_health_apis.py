import random
import time
import unittest
from testcases.testcases_base import TestcasesBase


class TesthealthcheckAPI(TestcasesBase):
    @classmethod
    def setUpClass(cls):
        self = cls()
        super(TesthealthcheckAPI, self).setUp()

        self.lg.info("Get list of nodes . ")
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        Nodes_result = response.json()

        self.lg.info("Get list of a nodes healthcheck api request.")
        response = self.healthcheck_api.get_all_nodes_health()
        self.assertEqual(response.status_code, 200)
        health_result = response.json()

        self.lg.info(" Check that all nodes have health check, should succeed. ")
        self.assertEqual(len(health_result), len(Nodes_result))

    def setUp(self):
        self.lg.info(' [*] Get healthcheck of random node ')
        self.random_node = self.get_random_node()
        response = self.healthcheck_api.get_node_health(self.random_node)
        self.assertEqual(response.status_code, 200)
        self.healthchecks = response.json()["healthchecks"]
