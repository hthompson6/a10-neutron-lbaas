# Copyright 2015,  A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import six

from a10_openstack_lib.resources import a10_device
import a10_openstack_lib.resources.validators as a10_validators

from neutron.api import extensions as nextensions
from neutron.api.v2 import resource_helper
# neutron.services got moved to neutron_lib
try:
    # F811 (redefinition of ServicePluginBase) suppressed
    from neutron.services.service_base import ServicePluginBase  # noqa
except (ImportError, AttributeError):
    pass

try:
    # F811 (redefinition of ServicePluginBase) suppressed
    from neutron_lib.services.base import ServicePluginBase  # noqa
except (ImportError, AttributeError):
    pass

from a10_neutron_lbaas.neutron_ext.common import attributes
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.common import exceptions
from a10_neutron_lbaas.neutron_ext.common import extensions
from a10_neutron_lbaas.neutron_ext.common import resources

RESOURCE_ATTRIBUTE_MAP = resources.apply_template(a10_device.RESOURCE_ATTRIBUTE_MAP,
                                                  attributes)

attributes.add_validators(resources.apply_template(
    a10_validators.VALIDATORS, attributes.validators))

_ALIAS = constants.A10_DEVICE_EXT


# TODO(rename this to *Extension to avoid config file confusion)
class A10device(extensions.ExtensionDescriptor):

    nextensions.register_custom_supported_check(
        _ALIAS, lambda: True, plugin_agnostic=True)

    def get_name(cls):
        return "A10 Device Instances"

    @classmethod
    def get_alias(cls):
        return constants.A10_DEVICE_EXT

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/neutron/a10_device_instance/api/v1.0"

    @classmethod
    def get_updated(cls):
        return "2015-11-18T16:17:00-07:00"

    @classmethod
    def get_description(cls):
        return ("A10 Device")

    @classmethod
    def get_resources(cls):
        """Returns external resources."""
        my_plurals = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        attributes.PLURALS.update(my_plurals)
        attr_map = RESOURCE_ATTRIBUTE_MAP
        resources = resource_helper.build_resource_info(my_plurals,
                                                        attr_map,
                                                        constants.A10_DEVICE)

        return resources

    def update_attributes_map(self, attributes):
        super(A10device, self).update_attributes_map(
            attributes,
            extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


class A10DeviceNotFoundError(exceptions.NotFound):

    def __init__(self, a10_device_id):
        self.msg = _("A10 Device {} could not be found.")
        super(A10DeviceNotFoundError, self).__init__()


class A10DeviceInUseError(exceptions.InUse):

    def __init__(self, a10_device_id):
        self.message = _("A10 Device is in use and cannot be deleted.")
        self.msg = self.message
        super(A10DeviceInUseError, self).__init__()


@six.add_metaclass(abc.ABCMeta)
class A10DevicePluginBase(ServicePluginBase):

    def get_plugin_name(self):
        return constants.A10_DEVICE

    def get_plugin_description(self):
        return constants.A10_DEVICE

    def get_plugin_type(self):
        return constants.A10_DEVICE

    def __init__(self):
        super(A10DevicePluginBase, self).__init__()

    @abc.abstractmethod
    def get_vthunders(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_thunder(self, context, vthunder):
        pass

    @abc.abstractmethod
    def get_vthuner(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def delete_vthunder(self, context, id):
        pass

    @abc.abstractmethod
    def update_vthunder(self, context, id, vthunder):
        pass

    @abc.abstractmethod
    def get_a10_devices(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_device(self, context, a10_device):
        pass

    @abc.abstractmethod
    def get_a10_device(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def delete_a10_device(self, context, id):
        pass

    @abc.abstractmethod
    def update_a10_device(self, context, id, a10_device):
        pass

    @abc.abstractmethod
    def get_a10_device_keys(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_device_key(self, context, key):
        pass

    @abc.abstractmethod
    def get_a10_device_key(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def update_a10_device_key(self, context, id, key):
        pass

    @abc.abstractmethod
    def delete_a10_device_key(self, context, id):
        pass

    @abc.abstractmethod
    def get_a10_device_values(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_a10_device_value(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_a10_device_value(self, context, key_id, device_id, value):
        pass

    @abc.abstractmethod
    def update_a10_device_value(self, context, id, value):
        pass

    @abc.abstractmethod
    def delete_a10_device_value(self, context, id, value):
        pass