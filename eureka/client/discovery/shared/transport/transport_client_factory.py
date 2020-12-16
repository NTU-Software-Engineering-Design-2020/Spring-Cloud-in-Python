# standard library
from abc import ABC, abstractmethod

__author__ = "Haribo (haribo1558599@gmail.com)"
__license__ = "Apache 2.0"

# scip plugin
from eureka.client.discovery.shared.resolver import EurekaEndpoint
from eureka.client.discovery.shared.transport.eureka_http_client import EurekaHttpClient


class TransportClientFactory(ABC):
    @abstractmethod
    def create(self, eureka_endpoint: EurekaEndpoint) -> EurekaHttpClient:
        raise NotImplemented
