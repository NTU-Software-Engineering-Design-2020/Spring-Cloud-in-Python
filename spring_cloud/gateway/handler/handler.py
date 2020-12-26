# -*- coding: utf-8 -*-
# standard library
from typing import List, Optional

# scip plugin
from spring_cloud.utils import logging

__author__ = "Chaoyuuu (chaoyu2330@gmail.com)"
__license__ = "Apache 2.0"

# scip plugin
from spring_cloud.gateway.filter import GatewayFilter, GatewayFilterChain, GlobalFilter
from spring_cloud.gateway.route import Route
from spring_cloud.gateway.route.builder.route_locator import RouteLocator
from spring_cloud.gateway.server import (
    GATEWAY_HANDLER_MAPPER_ATTR,
    GATEWAY_PREDICATE_ROUTE_ATTR,
    GATEWAY_ROUTE_ATTR,
    ServerWebExchange,
)
from spring_cloud.utils.functional_operators import filter_get_first
from spring_cloud.utils.logging import getLogger


class FilteringWebHandler:
    def __init__(self, global_filters: List[GlobalFilter]):
        self.__global_filters = self.load_filters(global_filters)

    def load_filters(self, global_filters: List[GlobalFilter]):
        return [GatewayFilterAdapter(global_filter) for global_filter in global_filters]

    # TODO: gateway_filters must be sorted by order
    def handle(self, exchange: ServerWebExchange) -> None:
        route: Route = exchange.attributes[GATEWAY_ROUTE_ATTR]
        gateway_filters = route.filters
        gateway_filters.extend(self.__global_filters)
        return DefaultGatewayFilterChain(gateway_filters).filter(exchange)


class GatewayFilterAdapter(GatewayFilter):
    def __init__(self, delegate: GlobalFilter):
        self.__delegate = delegate

    def filter(self, exchange: ServerWebExchange, chain: GatewayFilterChain) -> None:
        return self.__delegate.filter(exchange, chain)


class DefaultGatewayFilterChain(GatewayFilterChain):
    def __init__(self, filters: List[GatewayFilter], index=None):
        self.__index = index or 0
        self.__gateway_filters = filters

    @staticmethod
    def create(gateway_filters: List[GatewayFilter], index: int):
        return DefaultGatewayFilterChain(gateway_filters, index)

    def filter(self, exchange: ServerWebExchange):
        """
        Traverse filters
        """
        if self.__index < len(self.__gateway_filters):
            gateway_filter = self.__gateway_filters[self.__index]
            chain = self.create(self.__gateway_filters, self.__index + 1)
            gateway_filter.filter(exchange, chain)


class RoutePredicateHandlerMapping:
    def __init__(self, route_locator: RouteLocator):
        self.__route_locator = route_locator
        self.logger = getLogger(name="spring_cloud.gateway.handler.RoutePredicateHandlerMapping")

    def map_route(self, route: Route, exchange: ServerWebExchange):
        exchange.attributes[GATEWAY_HANDLER_MAPPER_ATTR] = "RoutePredicateHandlerMapping"
        exchange.attributes.pop(GATEWAY_PREDICATE_ROUTE_ATTR, None)
        self.logger.debug(f"\nMapping [{self.get_exchange_description(exchange)}] to {route}")
        exchange.attributes[GATEWAY_ROUTE_ATTR] = route

    def lookup_route(self, exchange: ServerWebExchange) -> Optional[Route]:
        """
        Testing each route's predicate, and return the first item that satisfy the request.
        if here is no matched route, return None
        """
        routes = self.__route_locator.get_routes()
        route = filter_get_first(lambda route: route.predicate.test(exchange), routes)

        if route:
            self.logger.info(f"Route matched: {route.route_id}")
            return route
        else:
            self.logger.info(f"No route matched.")
            return None

    # TODO: return exchange.request information for debug
    @staticmethod
    def get_exchange_description(exchange: ServerWebExchange):
        return f"Exchange: [{exchange.request.method}] {exchange.request.uri}"


class DispatcherHandler:
    def __init__(self, route_mapping: RoutePredicateHandlerMapping, filtering_web_handler: FilteringWebHandler):
        self.__logger = logging.getLogger("spring_cloud.gateway.DispatcherHandler")
        self.filtering_web_handler = filtering_web_handler
        self.__route_mapping = route_mapping

    def handle(self, exchange: ServerWebExchange):
        self.__logger.debug("Dispatching ...")
        route = self.__route_mapping.lookup_route(exchange)
        self.__route_mapping.map_route(route, exchange)
        if route:
            self.filtering_web_handler.handle(exchange)
        else:
            self.send_not_found_response(exchange)
        self.__logger.debug("Complete dispatching.")

    @staticmethod
    def send_not_found_response(exchange):
        exchange.response.set_status_code(404)
        exchange.response.set_body(b"")
        exchange.response.commit()
