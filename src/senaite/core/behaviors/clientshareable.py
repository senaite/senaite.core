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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.CMFCore import permissions
from senaite.core.behaviors.utils import get_behavior_schema
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IClientShareable(model.Schema):

    clients = UIDReferenceField(
        title=_(u"Clients"),
        description=_(
            u"Clients with whom this content will be shared across. This "
            u"content will become available on searches to users that belong "
            u"to any of the selected clients. Depending on the roles of those "
            u"users, additional permissions for this content, like edition or "
            u"transitions, might be granted too."
        ),
        allowed_types=("Client", ),
        multi_valued=True,
        required=False,
    )

    directives.widget(
        "clients",
        UIDReferenceWidgetFactory,
        catalog="portal_catalog",
        query={
            "portal_type": "Client",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ],
        limit=15,
    )

    fieldset(
        "clientshareable",
        label=u"Client share",
        fields=["clients"],
    )


@implementer(IBehavior, IClientShareable)
@adapter(IDexterityContent)
class ClientShareable(object):

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context
        self._schema = None

    @property
    def schema(self):
        """Return the schema provided by the underlying behavior
        """
        if self._schema is None:
            self._schema = get_behavior_schema(self.context, IClientShareable)
        return self._schema

    def accessor(self, fieldname):
        """Return the field accessor for the fieldname
        """
        if fieldname in self.schema:
            return self.schema[fieldname].get
        return None

    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        if fieldname in self.schema:
            return self.schema[fieldname].set
        return None

    @security.protected(permissions.View)
    def getClients(self):
        accessor = self.accessor("clients")
        return accessor(self.context)

    @security.protected(permissions.ModifyPortalContent)
    def setClients(self, value):
        mutator = self.mutator("clients")
        mutator(self.context, value)

    clients = property(getClients, setClients)
