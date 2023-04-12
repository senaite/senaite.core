# -*- coding: utf-8 -*-

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import senaiteMessageFactory as _
from Products.CMFCore import permissions
from senaite.core.browser.widgets.queryselect import QuerySelectWidget
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.config.fields import AT_LABEL_FIELD
from senaite.core.extender import ExtLabelField
from senaite.core.interfaces import ICanHaveLabels
from senaite.core.interfaces import ISenaiteCore
from zope.component import adapts
from zope.interface import implements


class LabelSchemaExtender(object):
    """Extend schema fields for labeled contents
    """
    layer = ISenaiteCore
    implements(
        ISchemaExtender,
        IBrowserLayerAwareExtender,
        IOrderableSchemaExtender)
    adapts(ICanHaveLabels)

    fields = [
        # Labels
        ExtLabelField(
            AT_LABEL_FIELD,
            required=False,
            mode="rw",
            schemata="Labels",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=QuerySelectWidget(
                label=_("Labels"),
                description=_("Attached labels"),
                render_own_label=False,
                catalog=SETUP_CATALOG,
                search_index="Title",
                value_key="title",
                search_wildcard=True,
                multi_valued=True,
                allow_user_value=True,
                hide_input_after_select=False,
                i18n_domain="senaite.core",
                query={
                    "portal_type": "Label",
                    "is_active": True,
                    "sort_on": "title",
                },
                columns=[
                    {
                        "name": "Title",
                        "align": "left",
                        "label": _(u"Label"),
                    }, {
                        "name": "Description",
                        "align": "left",
                        "label": _(u"Description"),
                    },
                ],
                limit=5,
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        """Change the order of the extended fields
        """
        return original


class LabelSchemaModifier(object):
    """Rearrange schema fields
    """
    layer = ISenaiteCore
    implements(
        ISchemaModifier,
        IBrowserLayerAwareExtender)
    adapts(ICanHaveLabels)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return schema
