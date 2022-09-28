#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """"""

EXAMPLES = """"""

RETURN = """"""
import re

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible_collections.junipernetworks.junos.plugins.module_utils.network.junos.junos import (
    junos_argument_spec,
    get_connection,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import NetworkConfig, dumps
from ansible.utils.display import Display

display = Display()

USE_PERSISTENT_CONNECTION = True


def load_config(module, config, commit=False):
    conn = get_connection(module)
    try:
        resp = conn.edit_config(to_list(config) + ["top"], commit)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

    diff = resp.get("diff", "")
    return to_text(diff, errors="surrogate_then_replace").strip()

def get_commands_from_src(module):
    candidate = NetworkConfig(indent=1)
    if module.params['src']:
        candidate.loadfp(module.params['src'])
    return candidate

def main():
    """main entry point for module execution"""
    argument_spec = dict(
        src = dict(type="path"),
        save = dict(type='bool', default=False))


    argument_spec.update(junos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    warnings = []
    result = {"changed": False, "warnings": warnings}

    candidate = get_commands_from_src(module)
    configobjs = candidate.items
    if configobjs:
        commands = dumps(configobjs, 'commands')
        commands = commands.split('\n')
    display.warning(commands)
    result["commands"] = commands

    if commands:
        commit = not module.check_mode
        diff = load_config(module, commands, commit=commit)
        if diff:
            if module._diff:
                result["diff"] = {"prepared": diff}
            result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()
