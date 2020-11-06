# -*- coding: utf-8 -*-
__author__ = "Waterball (johnny850807@gmail.com)"
__license__ = "Apache 2.0"
# standard library
from abc import ABC

# scip plugin
from commons.client.loadbalancer.supplier.service_instance_list_supplier import ServiceInstanceListSupplier
from external.cache.cache_manager import CacheManager


class DelegatingServiceInstanceListSupplier(ServiceInstanceListSupplier, ABC):
    """
    An application of decorator pattern that adds behaviors to ServiceInstanceListSupplier.
    The decorators should inherit this class.
    """

    def __init__(self, delegate: ServiceInstanceListSupplier):
        assert delegate is not None
        self.delegate = delegate

    @property
    def service_id(self):
        return self.delegate.service_id


class CachingServiceInstanceListSupplier(DelegatingServiceInstanceListSupplier):
    CACHE_NAME = "CacheKey"

    def __init__(self, cache_manager: CacheManager, delegate: ServiceInstanceListSupplier):
        super().__init__(delegate)
        self.__cache_manager = cache_manager

    def get(self, request=None):
        return self.__cache_manager.get(self.CACHE_NAME).on_cache_miss(self.delegate.get)
