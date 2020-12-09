# -*- coding: utf-8 -*-

__author__ = "Chaoyuuu (chaoyu2330@gmail.com)"
__license__ = "Apache 2.0"

# standard library
from datetime import datetime

# scip plugin
from spring_cloud.gateway.route.builder.route_locator import RouteLocatorBuilder


class TestRouteLocatorBuilder:
    def given_route_locator_builder(self):
        self.builder = RouteLocatorBuilder()

    def test_basic_route(self):
        self.given_route_locator_builder()
        route_locator = (
            self.builder.routes()
            .route(
                lambda p: p.path("/get").filters(lambda f: f.add_request_header("Hello", "Johnny")).uri("http://a_cat")
            )
            .build()
        )

        routes = route_locator.get_routes()
        assert len(routes) == 1
        assert routes[0].uri == "http://a_cat"

    def test_routes_with_logical_opertor(self):
        self.given_route_locator_builder()
        route_locator = (
            self.builder.routes()
            .route(
                lambda p: p.path("/andnotquery")
                .and_()
                .not_(lambda p: p.after(datetime(2020, 11, 11)))
                .filters(lambda f: f.add_request_header("Hello", "Johnny"))
                .uri("http://a_cat"),
                "test1",
            )
            .route(
                lambda p: p.cookie("cookie", "chocolate")
                .filters(lambda f: f.add_response_header("Hello", "TsengMJ").add_request_header("Ha", "Haribo"))
                .metadata("A", "Apple")
                .uri("http://a_dog")
            )
            .build()
        )

        routes = route_locator.get_routes()
        assert len(routes) == 2
        route_0 = routes[0]
        assert route_0.route_id == "test1"
        assert len(route_0.filters) == 1
        assert route_0.uri == "http://a_cat"

        route_1 = routes[1]
        assert len(route_1.filters) == 2
        assert route_1.uri == "http://a_dog"
        assert route_1.metadata["A"] == "Apple"
