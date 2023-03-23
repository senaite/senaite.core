# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.CMFCore import permissions
from senaite.core.api import label as label_api
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import ICanHaveLabels
from senaite.core.z3cform.widgets.queryselect import QuerySelectWidgetFactory
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class ILabelSchema(model.Schema):
    """Behavior with schema fields to allow to add/remove labels
    """
    fieldset(
        "labels",
        label=u"Labels",
        fields=["ext_labels"])

    directives.widget(
        "ext_labels",
        QuerySelectWidgetFactory,
        catalog=SETUP_CATALOG,
        search_index="Title",
        value_key="title",
        search_wildcard=True,
        multi_valued=True,
        allow_user_value=True,
        hide_input_after_select=False,
        query={
            "portal_type": "Label",
            "is_active": True,
            "sort_on": "title",
        },
        columns=[
            {
                "name": "title",
                "width": "100",
                "align": "left",
                "label": _(u"Label"),
            },
        ],
        display_template="<a href='${url}'>${title}</a>",
        limit=5,
    )
    ext_labels = schema.List(
        title=_(u"label_ext_labels", default=u"Labels"),
        description=_(u"description_ext_labels", default=u"Attached labels"),
        value_type=schema.TextLine(title=u"Label"),
        required=False,
    )


@implementer(ILabelSchema)
@adapter(ICanHaveLabels)
class LabelSchema(object):
    """Factory that provides the extended label fields
    """
    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context

    @security.protected(permissions.View)
    def get_labels(self):
        return label_api.get_obj_labels(self.context)

    @security.protected(permissions.ModifyPortalContent)
    def set_labels(self, value):
        labels = label_api.to_labels(value)
        return label_api.set_obj_labels(self.context, labels)

    ext_labels = property(get_labels, set_labels)
