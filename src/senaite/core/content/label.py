# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ILabel
from senaite.core.schema import UIDReferenceField
from zope import schema
from zope.interface import implementer


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

    directives.omitted("labeled")
    labeled = UIDReferenceField(
        title=_(u"Labeled objects"),
        multi_valued=True,
        description=_(u"Objects that are marked with this label"),
        required=False,
    )

    category = schema.TextLine(
        title=u"Category",
        required=False,
    )


@implementer(ILabel, ILabelSchema, IHideActionsMenu)
class Label(Container):
    """A container for labels
    """
    _catalogs = [SETUP_CATALOG]

    def getCategory(self):
        """Return the label category
        """
        accessor = self.accessor("category")
        return accessor(self)

    def setCategory(self, value):
        """Set the label category
        """
        mutator = self.mutator("category")
        return mutator(self, api.safe_unicode(value))

    def getCategoryTitle(self):
        """Leverage existing metadata
        """
        return self.getCategory()
