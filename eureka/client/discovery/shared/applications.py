# -*- coding: utf-8 -*-

# standard library
import random
from typing import Dict, List, Optional

# pypi/conda library
from wrapt import synchronized

# scip plugin
from eureka.client.app_info import InstanceInfo
from eureka.client.discovery.shared.application import Application
from eureka.utils import AtomicInteger
from eureka.utils.concurrent import ConcurrentCircularList

__author__ = "Haribo (haribo1558599@gmail.com)"
__license__ = "Apache 2.0"


class Applications:
    """
    The class that wraps all the registry information returned by eureka server.

    See com.netflix.discovery.shared.Applications.
    """

    def __init__(self):
        self._reconciliation_hash_code = ""
        self._applications = []
        self._app_name_to_application_dict = {}
        self._virtual_host_name_to_instances_dict = {}

    @property
    def reconciliation_hash_code(self) -> str:
        """
        Gets the reconciliation hashcode. The hashcode is used to determine
        whether the applications list has changed since the last time it was
        acquired.
        """
        return self._reconciliation_hash_code

    @reconciliation_hash_code.setter
    def reconciliation_hash_code(self, reconciliation_hash_code: str):
        self._reconciliation_hash_code = reconciliation_hash_code

    @synchronized
    def add_application(self, application: Application):
        self._app_name_to_application_dict[application.name] = application
        self._add_instances(application)
        self._applications.append(application)

    def _add_instances(self, application: Application):
        for instance in application.get_instances():
            if instance.vip_address:
                virtual_host_name = instance.vip_address.upper()
                if virtual_host_name not in self._virtual_host_name_to_instances_dict:
                    self._virtual_host_name_to_instances_dict[virtual_host_name] = ConcurrentCircularList()
                self._virtual_host_name_to_instances_dict[virtual_host_name].append(instance)

    @synchronized
    def remove_application(self, application: Application):
        self._applications.remove(application)
        self._app_name_to_application_dict.pop(application.name, None)

    def get_registered_applications(self) -> List[Application]:
        return self._applications

    def get_registered_application(self, app_name: str) -> Optional[Application]:
        return self._app_name_to_application_dict.get(app_name, None)

    def get_instances_by_virtual_host_name(self, virtual_host_name: str) -> ConcurrentCircularList:
        return self._virtual_host_name_to_instances_dict.get(virtual_host_name.upper(), ConcurrentCircularList())

    @synchronized
    def shuffle_instances(self, filter_only_up_instances: bool):
        """
        Shuffle the provided instances so that they will not always be returned
        in the same order.
        """
        for application in self._applications:
            application.shuffle_and_store_instances(filter_only_up_instances)

            if filter_only_up_instances:
                for vip, instances in self._virtual_host_name_to_instances_dict.items():
                    shuffled_and_filtered_instances = list(
                        filter(lambda instance: instance.status == InstanceInfo.InstanceStatus.UP, list(instances))
                    )
                    random.shuffle(shuffled_and_filtered_instances)
                    self._virtual_host_name_to_instances_dict[vip] = ConcurrentCircularList(
                        shuffled_and_filtered_instances
                    )

    def size(self) -> int:
        size = 0
        for application in self._applications:
            size += application.size()
        return size

    def compute_reconciliation_hash_code(self) -> str:
        instance_status_count_dict = {}
        for application in self._applications:
            for instance in application.get_all_instances_from_local_cache():
                if instance.status.value not in instance_status_count_dict:
                    instance_status_count_dict[instance.status.value] = AtomicInteger(0)

                instance_status_count = instance_status_count_dict.get(instance.status.value)
                instance_status_count.increment_and_get()

        sorted_instance_status_count_dict_by_key = dict(sorted(instance_status_count_dict.items(), key=lambda d: d[0]))
        reconciliation_hash_code = ""
        delimiter = "_"
        for status, count in sorted_instance_status_count_dict_by_key.items():
            record = status + delimiter + str(count) + delimiter
            reconciliation_hash_code += record

        return reconciliation_hash_code
