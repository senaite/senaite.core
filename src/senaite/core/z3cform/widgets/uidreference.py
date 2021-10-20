# -*- coding: utf-8 -*-

from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.interfaces import IUIDReferenceWidget
from z3c.form.browser import widget
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@implementer(IUIDReferenceWidget)
class UIDReferenceWidget(TextLinesWidget):
    """Senaite UID reference widget
    """
    klass = u"uidreference-widget"

    def update(self):
        super(UIDReferenceWidget, self).update()
        widget.addFieldClass(self)


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
