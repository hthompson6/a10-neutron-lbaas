# Copyright 2017,  A10 Networks
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

"""

This module includes fake objects used for testing db extensions as well as service plugins.
These classes have primarily been constructed to handle cases in which the data needs to be
tested on in dictionary and object form.

"""

class FakeA10Device(object):

    def __init__(self):
        self.name = 'fake-name'
        self.description = 'fake-description'
        self.host = 'fake-host'
        self.api_version = 'fake-version'
        self.username = 'fake-username'
        self.password = 'fake-password'
        self.autosnat = False
        self.default_virtual_server_vrid = None
        self.nova_instance_id = None
        self.ipinip = False
        self.use_float = False
        self.v_method = 'LSI'
        self.shared_partition = 'shared'
        self.write_memory = False
        self.project_id = 'fake-tenant-id'
        self.protocol = 'https'
        self.port = 442
        self.config = []
        super(FakeA10Device, self).__init__()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def get_extra_resource_mapping(self):
        mapped_resource = {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:string': None,
                },
            'is_visible': True,
            'default': 'fake-value'
            }
        return mapped_resource


class FakeA10DeviceKey(object):
    
    def __init__(self):
        self.name = 'fake-name'
        self.description = 'fake-description'

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class FakeA10DeviceValue(object):

    def __init__(self):
        self.name = 'fake-name'
        self.key_id = 'fake-key-id'
        self.associated_obj_id = 'fake-obj-id'
        self.value = 'fake-value'
        self.description = 'fake-description'
        self.associated_key = FakeA10DeviceKey()

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)
