# -*- coding: utf-8 -*-

# standard library
from typing import Union

# scip plugin
from eureka.client.app_info import InstanceInfo
from ribbon.client.config.client_config import ClientConfig
from ribbon.eureka.discovery_enabled_server import DiscoveryEnabledServer
from ribbon.loadbalancer.load_balancer import LoadBalancer
from ribbon.loadbalancer.server import Server
from spring_cloud.commons.client.loadbalancer import LoadBalancerClient
from spring_cloud.ribbon.ribbon_server import RibbonServer
from spring_cloud.ribbon.spring_client_factory import SpringClientFactory
from spring_cloud.utils import logging


class RibbonLoadBalancerClient(LoadBalancerClient):
    def __init__(self, client_factory: SpringClientFactory):
        self.logger = logging.getLogger("spring_cloud.ribbon.RibbonLoadBalancerClient")
        self.__client_factory = client_factory

    def choose(self, service_id: str, request=None) -> Union[RibbonServer, None]:
        """
        Select a server using a 'key'.
        :param service_id: (str)
        :param request: (opt)
        :return: (ServiceInstance)
        """
        self.logger.trace("Delegating to the vendor --> Ribbon.")
        server = self.get_server(self.get_load_balancer(service_id), request)
        if not server:
            return None
        return RibbonServer(service_id, server, self.is_secure(server, service_id))

    def is_secure(self, server: Server, service_id: str) -> bool:
        config = self.get_client_config(service_id)
        if config.get_property("IS_SECURE") is not None:
            return config.get_property("IS_SECURE")
        if isinstance(server, DiscoveryEnabledServer):
            return server.instance_info.is_port_enabled(InstanceInfo.PortType.SECURE)
        return server.port in [443, 8443]

    def get_server(self, load_balancer: LoadBalancer, hint=None) -> Union[Server, None]:
        if load_balancer is None:
            return None

        return load_balancer.choose_server(hint)

    def get_load_balancer(self, service_id: str) -> LoadBalancer:
        return self.__client_factory.get_load_balancer(service_id)

    def get_client_config(self, service_id: str) -> Union[ClientConfig, None]:
        return self.__client_factory.get_client_config(service_id)

    def execute(self):
        # TODO not sure if we really need this, this was designed by spring cloud
        pass
