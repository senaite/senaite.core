# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.


class ValidatedData(dict):
    """Validated data wrapper-class
    """

    def __init__(self, data=None, errors=None):
        self['data'] = data or {}
        self['errors'] = errors or {}

    def run(self, *validator_fns):
        result = self
        for fn in validator_fns:
            result = result.merge(fn(result['data']))
        return result

    def merge(self, other):
        self['data'] = dict(self['data'], **other['data'])
        self['errors'] = dict(self['errors'], **other['errors'])
        return self


def success(data):
    return ValidatedData(data=data)


def fail(field_name, error):
    return ValidatedData(errors={field_name: error})


def flatten_dict(d):
    res = {}

    def inner(obj, parent_keys=[]):
        for k, v in obj.items():
            if isinstance(v, dict):
                inner(v, parent_keys + [k])
            else:
                key = frozenset(parent_keys + [k])
                res[key] = v
    inner(d)
    return res
