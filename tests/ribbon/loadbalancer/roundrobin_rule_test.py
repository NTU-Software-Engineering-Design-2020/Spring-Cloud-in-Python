# -*- coding: utf-8 -*-

__author__ = "MJ (tsngmj@gmail.com)"
__license__ = "Apache 2.0"

# standard library
from typing import List

# pypi/conda library
import pytest

# scip plugin
from ribbon.loadbalancer.load_balancer import LoadBalancer
from ribbon.loadbalancer.round_robin_rule import RoundRobinRule
from ribbon.loadbalancer.server import Server


class FakeLoadBalancer(LoadBalancer):
    server1 = Server(uri="http://127.0.0.1:100")
    server2 = Server(uri="http://127.0.0.1:200")
    server3 = Server(uri="http://127.0.0.1:300")

    server1.is_alive = True
    server2.is_alive = True

    def add_servers(self, servers: List[Server]):
        pass

    def choose_server(self, key: object) -> Server:
        pass

    def mark_server_down(self, server: Server):
        pass

    def __init__(self):
        self.servers = [self.server1, self.server2, self.server3]

    def get_reachable_servers(self) -> List[Server]:
        return self.servers[:2]

    def get_all_servers(self) -> List[Server]:
        return self.servers


class TestRoundRobinRule:
    lb = FakeLoadBalancer()
    round_robin_rule = RoundRobinRule(lb)

    def test_fake_loadbalancer(self):
        assert None != self.lb

    def test_sequential_choose_given_loadbalancer(self):
        lb = self.lb
        server1 = self.round_robin_rule.choose(lb)
        server2 = self.round_robin_rule.choose(lb)
        server3 = self.round_robin_rule.choose(lb)

        assert server1.port == 200  # will get next index of server
        assert server2.port == 100
        assert server3.port == 200  # Cause the third server is not alive

    def test_sequential_choose_without_given_loadbalancer(self):
        round_robin_rule = RoundRobinRule(self.lb)
        server1 = round_robin_rule.choose()
        server2 = round_robin_rule.choose()
        server3 = round_robin_rule.choose()

        assert server1.port == 200  # will get next index of server
        assert server2.port == 100
        assert server3.port == 200  # Cause the third server is not alive

    def test_choose_with_no_server_in_loadbalancer(self):
        round_robin_rule = RoundRobinRule()
        server = round_robin_rule.choose()

        assert server == None
