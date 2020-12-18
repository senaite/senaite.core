# -*- coding: utf-8 -*-

import json

from bika.lims.browser import BrowserView
from bika.lims.decorators import returns_json
from senaite.core.interfaces import IAjaxEditForm
from zope.component import queryMultiAdapter

__doc__ = """
The edit form handler is the server part of `editform.js` JS and must implement
the following two methods:

    def initialized():
        payload = self.get_json()
        return {}

This method is called after the edit form has been loaded on the client side.
The JSON `payload` provides only one key `form`, which contains the serialized
and raw keys/values of the HTML form elements (including ZPublisher
field converters, e.g. `fieldname:boolean:default` etc.).

    def modified():
        payload = self.get_json()
        return {}

This method is called for each field modification. The JSON `payload` provides
the key `form` with the HTML form data as described above. Furthermore, it
provides the keys `name` and `value` with the name and value of the changed
field. The `key` is the fieldname w/o the coverter to match the schema of the
object and the value is converted as follows:

    - checkbox fields: True/False
    - single reference fields: UID
    - multi reference fields: list of UIDs
    - select fields: list of selected values

The return value of both methods is a dictionary with instructions to be done
in the fronted. The following keys are supported:

    hide: []

A list of (schema) field names that should be hidden.

    show: []

A list of (schema) field names that should be visible.

    update: {}

A dictionary of `field name` -> `field option` pairs to update the fields (more
on that later).

    errors: {}

A dictionary of `field name` -> `error message` that highlights the fields as
erroneous and displays the error message below the field.

Note: All error marked fields are flushed in between the updates.

    messages: []

A list of message dictionaries. Each message dictionary consists of a `level`
and `message` mapping.

The level can be one of the following values:

    - alert
    - warning
    - info
    - success

The `message` should be an i18n message factory to be properly translated.


Example:

{
    "hide": ["title"],
    "show": [],
    "update": {
        "ScientificName": False,
        "PointOfCapture": "lab",
        "Department": {
            "selected": [
                {
                    "title": "Clinical Lab",
                    "value": "6f3cb33f10e04ac19b32b8bd47fcd43b",
                }
            ],
            "options": []
        },
        "Calculation": {
            "selected": [
                {
                    "title": "Total Aflatoxins",
                    "value": "69c3999948e94490bf43c7b49694fe2c",
                }
            ],
            "options": [
                {
                    "value": "69c3999948e94490bf43c7b49694fe2c",
                    "title": "Total Aflatoxins",
                }
            ]
        }
    },
    "messages": [
        {"level": "info", "message": _("Changes Saved")}
    ],
    "errors": {
        "description": _("Invalid description"),
    },
}
"""


class FormView(BrowserView):
    """Form View
    """

    @property
    def adapter(self):
        return queryMultiAdapter((self.context, self.request), IAjaxEditForm)

    @returns_json
    def initialized(self):
        data = self.get_json()
        if not data:
            data = {}
        if not self.adapter:
            return {}
        return self.adapter.initialized(data)

    @returns_json
    def modified(self):
        data = self.get_json()
        if not data:
            data = {}
        if not self.adapter:
            return {}
        return self.adapter.modified(data)

    def get_json(self):
        body = self.request.get("BODY", "{}")
        return json.loads(body)
