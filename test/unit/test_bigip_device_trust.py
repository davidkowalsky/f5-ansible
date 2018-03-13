# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import sys

from nose.plugins.skip import SkipTest
if sys.version_info < (2, 7):
    raise SkipTest("F5 Ansible modules require Python >= 2.7")

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import Mock
from ansible.compat.tests.mock import patch
from ansible.module_utils.basic import AnsibleModule

try:
    from library.bigip_device_trust import Parameters
    from library.bigip_device_trust import ModuleManager
    from library.bigip_device_trust import ArgumentSpec
    from library.bigip_device_trust import HAS_F5SDK
    from library.bigip_device_trust import HAS_NETADDR
    from library.module_utils.network.f5.common import F5ModuleError
    from library.module_utils.network.f5.common import iControlUnexpectedHTTPError
    from test.unit.modules.utils import set_module_args
except ImportError:
    try:
        from ansible.modules.network.f5.bigip_device_trust import Parameters
        from ansible.modules.network.f5.bigip_device_trust import ModuleManager
        from ansible.modules.network.f5.bigip_device_trust import ArgumentSpec
        from ansible.modules.network.f5.bigip_device_trust import HAS_F5SDK
        from ansible.modules.network.f5.bigip_device_trust import HAS_NETADDR
        from ansible.module_utils.network.f5.common import F5ModuleError
        from ansible.module_utils.network.f5.common import iControlUnexpectedHTTPError
        from units.modules.utils import set_module_args
    except ImportError:
        raise SkipTest("F5 Ansible modules require the f5-sdk Python library")

    from ansible.modules.network.f5.bigip_device_trust import HAS_NETADDR
    if not HAS_NETADDR:
        raise SkipTest("F5 Ansible modules require the netaddr Python library")

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            peer_server='10.10.10.10',
            peer_hostname='foo.bar.baz',
            peer_user='admin',
            peer_password='secret'
        )

        p = Parameters(params=args)
        assert p.peer_server == '10.10.10.10'
        assert p.peer_hostname == 'foo.bar.baz'
        assert p.peer_user == 'admin'
        assert p.peer_password == 'secret'

    def test_module_parameters_with_peer_type(self):
        args = dict(
            peer_server='10.10.10.10',
            peer_hostname='foo.bar.baz',
            peer_user='admin',
            peer_password='secret',
            type='peer'
        )

        p = Parameters(params=args)
        assert p.peer_server == '10.10.10.10'
        assert p.peer_hostname == 'foo.bar.baz'
        assert p.peer_user == 'admin'
        assert p.peer_password == 'secret'
        assert p.type is True

    def test_module_parameters_with_subordinate_type(self):
        args = dict(
            peer_server='10.10.10.10',
            peer_hostname='foo.bar.baz',
            peer_user='admin',
            peer_password='secret',
            type='subordinate'
        )

        p = Parameters(params=args)
        assert p.peer_server == '10.10.10.10'
        assert p.peer_hostname == 'foo.bar.baz'
        assert p.peer_user == 'admin'
        assert p.peer_password == 'secret'
        assert p.type is False

    def test_hyphenated_peer_hostname(self):
        args = dict(
            peer_hostname='hn---hyphen____underscore.hmatsuda.local',
        )

        p = Parameters(params=args)
        assert p.peer_hostname == 'hn---hyphen____underscore.hmatsuda.local'

    def test_numbered_peer_hostname(self):
        args = dict(
            peer_hostname='BIG-IP_12x_ans2.example.local',
        )

        p = Parameters(params=args)
        assert p.peer_hostname == 'BIG-IP_12x_ans2.example.local'


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create_device_trust(self, *args):
        set_module_args(dict(
            peer_server='10.10.10.10',
            peer_hostname='foo.bar.baz',
            peer_user='admin',
            peer_password='secret',
            server='localhost',
            password='password',
            user='admin'
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods in the specific type of manager
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=False)
        mm.create_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True

    def test_create_device_trust_idempotent(self, *args):
        set_module_args(dict(
            peer_server='10.10.10.10',
            peer_hostname='foo.bar.baz',
            peer_user='admin',
            peer_password='secret',
            server='localhost',
            password='password',
            user='admin'
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods in the specific type of manager
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is False
