# -*- coding: utf-8 -*-
# standard library

# scip plugin
from spring_cloud.commons.client.loadbalancer import RoundRobinLoadBalancer
from spring_cloud.commons.client.loadbalancer.supplier import FixedServiceInstanceListSupplier
from tests.commons.client.loadbalancer.stubs import INSTANCES, SERVICE_ID

__author__ = "Waterball (johnny850807@gmail.com)"
__license__ = "Apache 2.0"


# TODO perform parallel RR test to ensure the race-condition won't happen
class TestRoundRobinLoadBalancer:
    def test_round_robin(self):
        instances_supplier = FixedServiceInstanceListSupplier(SERVICE_ID, INSTANCES)
        rr = RoundRobinLoadBalancer(instances_supplier, SERVICE_ID)

        for instance in INSTANCES:
            choice = rr.choose()
            assert instance == choice
