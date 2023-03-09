# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.api import label as label_api
from senaite.core.interfaces import ILabel
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class ILabelSchema(model.Schema):
    """Schema interface
    """
    title = schema.TextLine(
        title=u"Title",
        required=False,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    @invariant
    def validate_title(data):
        """Checks if the title is unique
        """
        # https://community.plone.org/t/dexterity-unique-field-validation
        context = getattr(data, "__context__", None)
        if context is not None:
            if context.title == data.title:
                # nothing changed
                return
        labels = label_api.list_labels(inactive=True)
        if data.title in labels:
            raise Invalid(_("Label names must be unique"))


@implementer(ILabel, ILabelSchema, IHideActionsMenu)
class Label(Container):
    """A container for labels
    """
    _catalogs = [SETUP_CATALOG]
