# -*- coding: utf-8 -*-
# standard library
from abc import ABC, abstractmethod
from typing import Dict

# pypi/conda library
import requests

# scip plugin
from spring_cloud.utils import logging

__author__ = "Chaoyuuu (chaoyu2330@gmail.com)"
__license__ = "Apache 2.0"

# scip plugin
from spring_cloud.commons.http import RestTemplate
from spring_cloud.gateway.filter import HEADER_FILTERS, GatewayFilterChain, HttpHeadersFilter
from spring_cloud.gateway.server import ServerWebExchange
from spring_cloud.gateway.server.utils import GATEWAY_ROUTE_ATTR, is_already_routed, set_already_routed


class GlobalFilter(ABC):
    @abstractmethod
    def filter(self, exchange: ServerWebExchange, chain: GatewayFilterChain):
        return NotImplemented


class RestTemplateRouteFilter(GlobalFilter):
    def __init__(self, rest_template: RestTemplate):
        self.logger = logging.getLogger("spring_cloud.gateway.RestTemplateRouteFilter")
        self.api = rest_template

    def filter(self, exchange: ServerWebExchange, chain: GatewayFilterChain):
        self.logger.debug("Start filtering...")
        if is_already_routed(exchange):
            return chain.filter(exchange)
        set_already_routed(exchange)

        method = exchange.request.method
        route = exchange.attributes[GATEWAY_ROUTE_ATTR]

        url = self.compose_url(route.uri, exchange.request.path)
        filtered_headers = HttpHeadersFilter.filter_request(HEADER_FILTERS, exchange)
        headers = self.compose_headers(exchange.request.cookies, filtered_headers)
        self.remove_host_headers(headers)
        params = exchange.request.query
        data = exchange.request.body

        res = self.map_api_request_method(method)(url, headers=headers, params=params, data=data)
        self.logger.debug("Sending response...")
        self.send(res, exchange)
        self.logger.debug("Successfully responded.")

    def map_api_request_method(self, method: str):
        method = method.lower()
        mapping = {
            "get": self.api.get,
            "put": self.api.put,
            "post": self.api.post,
            "patch": self.api.patch,
            "options": self.api.options,
            "delete": self.api.delete,
            "head": self.api.head,
        }
        return mapping[method]

    def send(self, res: requests.Response, exchange: ServerWebExchange):
        # TODO: response body has been unzip by RestTemplate, but we want the raw compressed body
        self.modify_content_headers(res.headers, res.content)
        exchange.response.set_body(res.content)
        exchange.response.set_status_code(res.status_code)
        exchange.response.set_headers(**res.headers)
        exchange.response.commit()

    @classmethod
    def compose_url(cls, uri: str, path: str):
        return uri + path

    @classmethod
    def compose_headers(cls, cookies: Dict[str, str], filtered_headers: Dict[str, str]):
        cookies = [f"{key}={value}" for key, value in cookies.items()]
        filtered_headers["Cookie"] = "; ".join(cookies)
        return filtered_headers

    def remove_host_headers(self, headers: Dict[str, str]):
        headers.pop("Host", None)
        headers.pop("X-Forwarded-For", None)

    def modify_content_headers(self, headers: Dict[str, str], body: bytes):
        headers.pop("Content-Encoding", None)
        headers["Content-Length"] = str(len(body))
