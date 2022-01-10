# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import ISampleContainer
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer


class ISampleContainerSchema(model.Schema):
    """Schema interface
    """

    directives.omitted("title")
    title = schema.TextLine(
        title=u"Title",
        required=False
    )

    directives.omitted("description")
    description = schema.Text(
        title=u"Description",
        required=False
    )

    # Container type reference
    directives.widget(
        "containertype",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_containertype_query",
        display_template="<a href='${url}'>${title}</a>",
        columns="get_default_columns",
        limit=5,
    )
    containertype = UIDReferenceField(
        title=_(u"Container Type"),
        allowed_types=("ContainerType", ),
        multi_valued=False,
        description=_(u"Select the container type"),
        required=False)


@implementer(ISampleContainer, ISampleContainerSchema, IDeactivable)
class SampleContainer(Container):
    """Sample container type
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    def get_containertype_query(self):
        """Return the query for the containertype field
        """
        return {
            "portal_type": "ContainerType",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        }

    def get_default_columns(self):
        """Returns the default columns for the reference dropdown
        """
        return [
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
        ]
