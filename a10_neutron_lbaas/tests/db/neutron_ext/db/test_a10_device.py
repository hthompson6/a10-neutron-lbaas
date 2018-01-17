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

import mock

from a10_openstack_lib.resources import a10_device as a10_device_resources

import a10_neutron_lbaas.tests.db.test_base as test_base
import a10_neutron_lbaas.tests.db.fake_obj as fake_obj
import a10_neutron_lbaas.tests.unit.unit_config.helper as unit_config

from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.db import a10_device
from a10_neutron_lbaas.neutron_ext.extensions import a10Device
from neutron.plugins.common import constants as nconstants


class TestA10DevicePluginBase(test_base.UnitTestBase):
    """
    The abstract class cannot be instantiated directly, therefore, it's
    non-abstract methods must be teseted via a subclass. In this case,
    A10DeviceDbMixin is used for testing purposes.
    """

    def setUp(self):
        super(TestA10DevicePluginBase, self).setUp()
        self._nm_patcher = mock.patch('neutron.manager.NeutronManager')
        nm = self._nm_patcher.start()
        nm.get_service_plugins.return_value = {
            nconstants.LOADBALANCERV2: mock.MagicMock()
        }

        self._config_cleanup = unit_config.use_config_dir()
        self.plugin_base = a10_device.A10DeviceDbMixin()

    def tearDown(self):
        self._config_cleanup()
        super(TestA10DevicePluginBase, self).tearDown()

    def context(self):
        session = self.open_session()
        context = mock.MagicMock(session=session, tenant_id='fake-tenant-id')
        return context

    def test_get_plugin_name(self):
        self.assertIsNot(self.plugin_base.get_plugin_name(), None)

    def test_get_plugin_description(self):
        self.assertIsNot(self.plugin_base.get_plugin_description(), None)

    def test_get_plugin_type(self):
        self.assertEqual(self.plugin_base.get_plugin_type(), constants.A10_DEVICE)

    def envelope_device(self, body):
        return {a10_device_resources.DEVICE: body}

    def envelope_vthunder(self, body):
        return {a10_device_resources.VTHUNDER: body}

    def envelope_device_key(self, body):
        return {a10_device_resources.DEVICE_KEY: body}

    def envelope_device_value(self, body):
        return {a10_device_resources.DEVICE_VALUE: body}

class TestA10DeviceDbMixin(TestA10DevicePluginBase):

    def setUp(self):
        super(TestA10DeviceDbMixin, self).setUp()
        self.db_extension = self.plugin_base

    def tearDown(self):
        super(TestA10DeviceDbMixin, self).tearDown()

    def fake_vthunder(self):
        return self.fake_device().update({'nova_instance_id':  'fake-instance-id'})

    def fake_device(self):
        fake_device = fake_obj.FakeA10Device()
        return fake_device

    def fake_device_options(self):
        return {
            'protocol': 'http',
            'port': 12345
        }    

    def test_make_device_dict(self):
        device = self.fake_device()
        device.id = 'new-id'
        device.tenant_id = 'new-tenant-id'

        result = self.db_extension._make_a10_device_dict(device)

        del device.config
        device.project_id = 'new-tenant-id'
        device.extra_resources = []
        self.assertEqual(result, device.__dict__)

    def test_make_device_dict_fields(self):
        pass

    def test_create_a10_device(self):
        device = self.fake_device()
        context = self.context()
        result = self.db_extension.create_a10_device(context, self.envelope_device(device.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device.__dict__)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                'extra_resources': []
            })
        del expected['config']
        self.assertEqual(expected, result)

    def test_get_a10_device(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device(create_context, self.envelope_device(device.__dict__))
        create_context.session.commit()
        context = self.context()

        result = self.db_extension.get_a10_device(context, create_result['id'])
        self.assertEqual(create_result, result)

    def test_get_a10_device_extra(self):
        device = self.fake_device()
        device.config = [self.fake_device()]
        create_context = self.context()
        create_result = self.db_extension.create_a10_device(create_context, self.envelope_device(device.__dict__))
        create_context.session.commit()
        context = self.context()

        result = self.db_extension.get_a10_device(context, create_result['id'])
        self.assertEqual(create_result, result)

    def test_get_a10_devices(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device(create_context, self.envelope_device(device.__dict__))
        create_context.session.commit()
        context = self.context()

        result = self.db_extension.get_a10_devices(context)
        self.assertEqual([create_result], result)

    def test_delete_a10_device(self):
        device = self.fake_device()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device(create_context, self.envelope_device(device.__dict__))
        create_context.session.commit()
        self.assertIsNot(create_result['id'], None)

        delete_context = self.context()
        self.db_extension.delete_a10_device(delete_context, create_result['id'])

        context = self.context()
        self.assertRaises(a10Device.A10DeviceNotFoundError, self.db_extension.get_a10_device, context, create_result['id'])
        
    def test_update_a10_device(self):
        device = self.fake_device()
        context = self.context()
        create_result =  self.db_extension.create_a10_device(context, self.envelope_device(device.__dict__))
        context.session.commit()

        device.use_float = True
        result = self.db_extension.update_a10_device(context, create_result['id'], self.envelope_device(device.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device.__dict__)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
                'extra_resources': []
            })
        del expected['config']
        self.assertEqual(expected, result)


    def fake_device_key(self):
        return fake_obj.FakeA10DeviceKey()

    def test_make_device_key_dict(self):
        device_key = self.fake_device_key()
        device_key.id = 'new-id'
        device_key.tenant_id = 'new-tenant-id'

        result = self.db_extension._make_a10_device_key_dict(device_key)

        device_key.project_id = 'new-tenant-id'
        self.assertEqual(result, device_key.__dict__)

    def test_create_a10_device_key(self):
        device_key = self.fake_device_key()
        context = self.context()
        result = self.db_extension.create_a10_device_key(context, self.envelope_device_key(device_key.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device_key.__dict__)
        expected.update(
            {   
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
            })
        self.assertEqual(expected, result)

    def test_get_a10_device_key(self):
        device_key = self.fake_device_key()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device_key(create_context, self.envelope_device_key(device_key.__dict__))
        create_context.session.commit()
        context = self.context()

        result = self.db_extension.get_a10_device_key(context, create_result['id'])
        self.assertEqual(create_result, result)

    def test_get_a10_device_keys(self):
        device_key = self.fake_device_key()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device_key(create_context, self.envelope_device_key(device_key.__dict__))
        create_context.session.commit()
        context = self.context()

        result = self.db_extension.get_a10_device_keys(context)
        self.assertEqual([create_result], result)

    def test_delete_a10_device_key(self):
        device_key = self.fake_device_key()
        create_context = self.context()
        create_result = self.db_extension.create_a10_device_key(create_context, self.envelope_device_key(device_key.__dict__))
        create_context.session.commit()
        self.assertIsNot(create_result['id'], None)

        delete_context = self.context()
        self.db_extension.delete_a10_device_key(delete_context, create_result['id'])

        context = self.context()
        self.assertRaises(a10Device.A10DeviceNotFoundError, self.db_extension.get_a10_device_key, context, create_result['id'])

    def test_update_a10_device_key(self):
        device_key = self.fake_device_key()
        context = self.context()
        create_result =  self.db_extension.create_a10_device_key(context, self.envelope_device_key(device_key.__dict__))
        context.session.commit()

        device_key.description = "i_dnt_like_spam"
        result = self.db_extension.update_a10_device_key(context, create_result['id'], self.envelope_device_key(device_key.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device_key.__dict__)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
            })
        self.assertEqual(expected, result)

    def fake_device_value(self, device_id, key_id):
        return fake_obj.FakeA10DeviceValue(device_id, key_id)

    def test_make_device_value_dict(self):
        device_value = self.fake_device_value('fake-device-id', 'fake-key-id')
        device_value.id = 'new-id'
        device_value.tenant_id = 'new-tenant-id'

        result = self.db_extension._make_a10_device_value_dict(device_value)

        device_value.project_id = 'new-tenant-id'
        self.assertEqual(result, device_value.__dict__)

    def test_create_a10_device_value(self):
        device = self.fake_device()
        device_context = self.context()
        device_result = self.db_extension.create_a10_device(device_context, self.envelope_device(device.__dict__))
        device_context.session.commit()
        self.assertIsNot(device_result['id'], None)

        key = self.fake_device_key()
        key_context = self.context()
        key_result = self.db_extension.create_a10_device_key(key_context, self.envelope_device_key(key.__dict__))
        key_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        device_value = self.fake_device_value(device_id=device_result['id'], key_id=key_result['id'])
        context = self.context()
        result = self.db_extension.create_a10_device_value(context, self.envelope_device_value(device_value.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device_value.__dict__)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
            })
        self.assertEqual(expected, result)


    def test_get_a10_device_value(self):
        device = self.fake_device()
        device_context = self.context()
        device_result = self.db_extension.create_a10_device(device_context, self.envelope_device(device.__dict__))
        device_context.session.commit()
        self.assertIsNot(device_result['id'], None)

        key = self.fake_device_key()
        key_context = self.context()
        key_result = self.db_extension.create_a10_device_key(key_context, self.envelope_device_key(key.__dict__))
        key_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        device_value = self.fake_device_value(device_id=device_result['id'], key_id=key_result['id'])
        value_context = self.context()
        create_result = self.db_extension.create_a10_device_value(value_context, self.envelope_device_value(device_value.__dict__))
        value_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        context = self.context()

        result = self.db_extension.get_a10_device_value(context, create_result['id'])
        self.assertEqual(create_result, result)

    def test_get_a10_device_values(self):
        device = self.fake_device()
        device_context = self.context()
        device_result = self.db_extension.create_a10_device(device_context, self.envelope_device(device.__dict__))
        device_context.session.commit()
        self.assertIsNot(device_result['id'], None)

        key = self.fake_device_key()
        key_context = self.context()
        key_result = self.db_extension.create_a10_device_key(key_context, self.envelope_device_key(key.__dict__))
        key_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        device_value = self.fake_device_value(device_id=device_result['id'], key_id=key_result['id'])
        value_context = self.context()
        create_result = self.db_extension.create_a10_device_value(value_context, self.envelope_device_value(device_value.__dict__))
        value_context.session.commit()

        context = self.context()

        result = self.db_extension.get_a10_device_values(context)
        self.assertEqual([create_result], result)

    def test_delete_a10_device_value(self):
        device = self.fake_device()
        device_context = self.context()
        device_result = self.db_extension.create_a10_device(device_context, self.envelope_device(device.__dict__))
        device_context.session.commit()
        self.assertIsNot(device_result['id'], None)

        key = self.fake_device_key()
        key_context = self.context()
        key_result = self.db_extension.create_a10_device_key(key_context, self.envelope_device_key(key.__dict__))
        key_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        device_value = self.fake_device_value(device_id=device_result['id'], key_id=key_result['id'])
        value_context = self.context()
        create_result = self.db_extension.create_a10_device_value(value_context, self.envelope_device_value(device_value.__dict__))
        value_context.session.commit()

        delete_context = self.context()
        self.db_extension.delete_a10_device_value(delete_context, create_result['id'])

        context = self.context()
        self.assertRaises(a10Device.A10DeviceNotFoundError, self.db_extension.get_a10_device_value, context, create_result['id'])

    def test_update_a10_device_value(self):
        device = self.fake_device()
        device_context = self.context()
        device_result = self.db_extension.create_a10_device(device_context, self.envelope_device(device.__dict__))
        device_context.session.commit()
        self.assertIsNot(device_result['id'], None)

        key = self.fake_device_key()
        key_context = self.context()
        key_result = self.db_extension.create_a10_device_key(key_context, self.envelope_device_key(key.__dict__))
        key_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        device_value = self.fake_device_value(device_id=device_result['id'], key_id=key_result['id'])
        value_context = self.context()
        create_result = self.db_extension.create_a10_device_value(value_context, self.envelope_device_value(device_value.__dict__))
        value_context.session.commit()
        self.assertIsNot(key_result['id'], None)

        context = self.context()
        device_value.value = "i_dnt_like_spam"
        result = self.db_extension.update_a10_device_value(context, create_result['id'], self.envelope_device_value(device_value.__dict__))
        context.session.commit()
        self.assertIsNot(result['id'], None)

        expected = {}
        expected.update(device_value.__dict__)
        expected.update(
            {
                'id': result['id'],
                'tenant_id': context.tenant_id,
                'project_id': context.tenant_id,
            })
        self.assertEqual(expected, result)
