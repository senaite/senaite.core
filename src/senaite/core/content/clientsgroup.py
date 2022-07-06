# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.interfaces import IClientsGroup
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer


class IClientsGroupSchema(model.Schema):
    """Schema interface for ClientGroup content
    """

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    description = schema.TextLine(
        title=u"Description",
        required=False,
    )

    clients = UIDReferenceField(
        title=_(u"Clients"),
        description=_(
            u"Clients that belong to this group. The assignment of clients to "
            u"groups makes the sharing of existing content amongst clients "
            u"from some group easy",
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


@implementer(IClientsGroup, IClientsGroupSchema, IDeactivable)
class ClientsGroup(Container):
    """ClientsGroup content
    """

    # Catalogs where this type will be catalogued
    _catalogs = ["portal_catalog"]

    security = ClassSecurityInfo()
    exclude_from_nav = True

    @security.private
    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        if raw:
            return schema[fieldname].getRaw
        return schema[fieldname].get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set

    @security.protected(permissions.View)
    def getClients(self, as_objects=True):  # noqa CamelCase
        """Returns the clients assigned to this group
        """
        raw = not as_objects
        accessor = self.accessor("clients")
        return accessor(self, raw=raw)

    @security.protected(permissions.View)
    def getRawClients(self):  # noqa CamelCase
        """Returns the UIDs of the clients assigned to this group
        """
        return self.getClients(as_objects=False)
