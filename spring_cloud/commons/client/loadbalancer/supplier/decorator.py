# -*- coding: utf-8 -*-
# standard library
from typing import List

# scip plugin
from spring_cloud.commons.client import ServiceInstance
from spring_cloud.utils import validate

__author__ = "Waterball (johnny850807@gmail.com)"
__license__ = "Apache 2.0"
# standard library
from abc import ABC

# scip plugin
from spring_cloud.commons.helpers import CacheManager

from .base import ServiceInstanceListSupplier


class DelegatingServiceInstanceListSupplier(ServiceInstanceListSupplier, ABC):
    """
    An application of decorator pattern that adds behaviors to ServiceInstanceListSupplier.
    The decorators should inherit this class.
    """

    def __init__(self, delegate: ServiceInstanceListSupplier):
        self.delegate = validate.not_none(delegate)

    @property
    def service_id(self) -> str:
        return self.delegate.service_id


class CachingServiceInstanceListSupplier(DelegatingServiceInstanceListSupplier):
    CACHE_NAME = "CacheKey"

    def __init__(self, cache_manager: CacheManager, delegate: ServiceInstanceListSupplier):
        super().__init__(delegate)
        self.__cache_manager = cache_manager

    def get(self, request=None) -> List[ServiceInstance]:
        return self.__cache_manager.get(self.CACHE_NAME).on_cache_miss(self.delegate.get)
