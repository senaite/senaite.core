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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from AccessControl import Unauthorized
from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.browser import BrowserView
from bika.lims.decorators import returns_json
from Products.CMFCore.permissions import ModifyPortalContent
from senaite.core.decorators import readonly_transaction
from senaite.core.interfaces import IAjaxEditForm
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.security.interfaces import IPermission

# Named form adapters of add forms are called like the add view
ADD_FORM_PREFIX = "++add++"

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


def get_permission_title(permission):
    """The title of a permission given by its title or its zope 3 id
    """
    utility = queryUtility(IPermission, name=permission)
    return utility.title if utility else permission


def get_add_permission(portal_type):
    """The permission to add an object of the portal type, or None
    """
    fti = api.get_tool("portal_types").getTypeInfo(portal_type)
    permission = getattr(fti, "add_permission", None)
    return get_permission_title(permission) if permission else None


class FormView(BrowserView):
    """Form View

    NOTE: No persistent operations are allowed!

    The view is registered for every context and visible for whoever may
    view it, so it checks itself whether the user may use the form before
    an adapter is called: an add form needs the add permission of its
    type, any other form `Modify portal content` on the context, unless
    the adapter names a `permission` of its own.
    """

    @property
    def adapter(self):
        name = self.get_form_adapter_name()
        if name is not None:
            # query a named form adapter
            return queryMultiAdapter(
                (self.context, self.request), IAjaxEditForm, name=name)
        return queryMultiAdapter((self.context, self.request), IAjaxEditForm)

    def get_required_permission(self, adapter):
        """The permission the user needs on the context to use the form

        :returns: the title of the permission, or None when there is none
            to check, which refuses the form
        """
        permission = getattr(adapter, "permission", None)
        if permission:
            return get_permission_title(permission)
        name = self.get_form_adapter_name() or ""
        if name.startswith(ADD_FORM_PREFIX):
            return get_add_permission(name[len(ADD_FORM_PREFIX):])
        return ModifyPortalContent

    def check_permission(self, adapter):
        """Refuse a user who may not use the form of the adapter

        :raises Unauthorized: when the user lacks the permission
        """
        permission = self.get_required_permission(adapter)
        if not permission or not check_permission(permission, self.context):
            raise Unauthorized("You are not allowed to use this form")

    def dispatch(self, method):
        """Call the method of the form adapter with the posted data
        """
        adapter = self.adapter
        if not adapter:
            return {}
        self.check_permission(adapter)
        return getattr(adapter, method)(self.get_data() or {})

    @readonly_transaction
    @returns_json
    def initialized(self):
        return self.dispatch("initialized")

    @readonly_transaction
    @returns_json
    def modified(self):
        return self.dispatch("modified")

    @readonly_transaction
    @returns_json
    def added(self):
        return self.dispatch("added")

    @returns_json
    def submit(self):
        return self.dispatch("submit")

    @readonly_transaction
    @returns_json
    def callback(self):
        return self.dispatch("callback")

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
