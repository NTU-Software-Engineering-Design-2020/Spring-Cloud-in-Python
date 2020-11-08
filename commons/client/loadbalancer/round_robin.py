# -*- coding: utf-8 -*-
"""
The built-in Round-Robin algorithm.
"""

# scip plugin
from commons.client.loadbalancer.loadbalancer import LoadBalancer
from commons.client.loadbalancer.supplier.service_instance_list_supplier import ServiceInstanceListSupplier
from commons.utils.atomic import AtomicInteger

__author__ = "Waterball (johnny850807@gmail.com)"
__license__ = "Apache 2.0"


class RoundRobinLoadBalancer(LoadBalancer):
    """
    A very easy thread-safe implementation adopting round-robin (RR) algorithm.
    """

    def __init__(self, instances_supplier: ServiceInstanceListSupplier, service_id):
        assert instances_supplier.service_id == service_id, "Inconsistent service's id."
        self.__instances_supplier = instances_supplier
        self.__service_id = service_id
        self.__position = AtomicInteger(-1)

    @property
    def service_id(self):
        return self.__service_id

    def choose(self, request=None):
        instances = self.__instances_supplier.get(request=request)
        pos = abs(self.__position.increment_and_get())
        return instances[pos % len(instances)]
