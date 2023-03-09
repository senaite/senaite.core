# -*- coding: utf-8 -*-

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import senaiteMessageFactory as _
from Products.CMFCore import permissions
from senaite.core.browser.widgets import ReferenceWidget
from senaite.core.extender import ExtUIDReferenceField
from senaite.core.interfaces import ICanHaveLabels
from senaite.core.interfaces import ISenaiteCore
from zope.component import adapts
from zope.interface import implements
from senaite.core.catalog import SETUP_CATALOG


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
        ExtUIDReferenceField(
            "ExtLabels",
            allowed_types=("Label",),
            required=False,
            mode="rw",
            schema="Labels",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=ReferenceWidget(
                label=_("Labels"),
                description=_("Attached labels"),
                catalog_name=SETUP_CATALOG,
                base_query={
                    "portal_type": "Label",
                    "is_active": True,
                    "sort_on": "title",
                },
                showOn=True,
                popup_width="400px",
                colModel=[
                    {
                        "columnName": "Title", "width": "100",
                        "label": _("Name"),
                    },
                ],
                ui_item="Title",
                render_own_label=True,
                size=20,
                i18n_domain="senaite.core",
            )),
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
