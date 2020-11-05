# scip plugin
from commons.client.discovery.composite import CompositeDiscoveryClient
from commons.client.discovery.discovery_client import static_discovery_client

__author__ = "Waterball (johnny850807@gmail.com)"
__license__ = "Apache"

client = CompositeDiscoveryClient(
    static_discovery_client("url-1", "service-1", ["1-1", "1-2", "1-3"]),
    static_discovery_client("url-2", "service-2", ["2-1", "2-2", "2-3"]),
    static_discovery_client("url-3", "service-3", ["3-1", "3-2", "3-3"]),
)


def test_get_instances():
    for service_id in range(1, 4):
        instances = client.get_instances("service-{}".format(service_id))
        for instance_id in range(1, 4):
            instance = instances[instance_id - 1]
            assert instance.instance_id == "{}-{}".format(service_id, instance_id)


def test_get_services():
    instances = client.services
    i = 0
    for service_id in range(1, 4):
        for instance_id in range(1, 4):
            assert instances[i].service_id == "service-{}".format(service_id)
            assert instances[i].instance_id == "{}-{}".format(service_id, instance_id)
            i += 1
