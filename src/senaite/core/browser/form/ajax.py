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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims.browser import BrowserView
from bika.lims.decorators import returns_json
from senaite.core.decorators import readonly_transaction
from senaite.core.interfaces import IAjaxEditForm
from zope.component import queryMultiAdapter

__doc__ = """
The edit form handler is the server part of `editform.js` JS and must implement
the following two methods:

    def initialized():
        payload = self.get_data()
        return {}

This method is called after the edit form has been loaded on the client side.
The JSON `payload` provides only one key `form`, which contains the serialized
and raw keys/values of the HTML form elements (including ZPublisher
field converters, e.g. `fieldname:boolean:default` etc.).

    def modified():
        payload = self.get_data()
        return {}

This method is called on each field modification. The JSON `payload` provides
the key `form` with the HTML form data as described above.

Furthermore, it provides the keys `name` and `value` with the name and value of
the changed field. The `key` is the fieldname w/o the coverter to match the
schema of the object and the value is converted as follows:

    - checkbox fields: True/False
    - single reference fields: UID
    - multi reference fields: list of UIDs
    - select fields: list of selected values

The return value of both methods is a dictionary with instructions to be done
in the fronted.

The following keys are supported in the returned dictionary:

    hide: [
        {"name": "title"},
        {"name": "description"},
    ]

A list of field records containing at least the `name` of the field.

    show: [
        {"name": "title"},
        {"name": "description"},
    ]

A list of field records containing at least the `name` of the field.

    readonly: [
        {"name": "title"},
        {"name": "description"},
    ]

A list of field records containing at least the `name` of the field.

    update: [
        {"name": "title", value="My Title"},
        {"name": "description", "value": "My Description"},
        {"name": "Department", "value": {
            "selected": ["6f3cb33f10e04ac19b32b8bd47fcd43b"],
            "options": [
                {
                    "title": "Clinical Lab",
                    "value": "6f3cb33f10e04ac19b32b8bd47fcd43b",
                }
            ]
        }
    ]

A list of records containing at least the `name` and the `value` of the fields
to update.

    errors: [
        {"name": "title", error="Invalid characters detected"},
    ]

A list of records containing at least the `name` and the `error` of the fields
that should be displayed as erroneous.

Note: Form submission is disabled when fields are marked as erroneous!

    notifications: [
        {"title": "Heads Up", message": "Notifications are awesome!"},
    ]

A list of records containing at least the `title` and the `message` of the
notifications messages to display.

    messages: [
        {"message": "Changes Saved", level="info"},
    ]

A list of records containing at least the `message` and the `level` of the
status messages to display.

The level can be one of the following values:

    - info
    - success
    - warning
    - dangrous
    - success

The `message` should be an i18n message factory and are translated with
`jsi18n` in JS.
"""


class FormView(BrowserView):
    """Form View

    NOTE: No persistent operations are allowed!
    """

    @property
    def adapter(self):
        name = self.get_form_adapter_name()
        if name is not None:
            # query a named form adapter
            return queryMultiAdapter(
                (self.context, self.request), IAjaxEditForm, name=name)
        return queryMultiAdapter((self.context, self.request), IAjaxEditForm)

    @readonly_transaction
    @returns_json
    def initialized(self):
        data = self.get_data()
        if not data:
            data = {}
        if not self.adapter:
            return {}
        return self.adapter.initialized(data)

    @readonly_transaction
    @returns_json
    def modified(self):
        data = self.get_data()
        if not data:
            data = {}
        if not self.adapter:
            return {}
        return self.adapter.modified(data)

    @returns_json
    def submit(self):
        data = self.get_data()
        if not data:
            data = {}
        if not self.adapter:
            return {}
        return self.adapter.submit(data)

    def get_data(self):
        body = self.request.get("BODY")
        if body:
            return json.loads(body)
        form = self.request.form
        if form:
            return {"form": form}
        return {}

    def get_form_adapter_name(self):
        """Returns the form adapter name for the query
        """
        data = self.get_data()
        form = data.get("form", {})
        return form.get("form_adapter_name")
