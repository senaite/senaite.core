# -*- coding: utf-8 -*-
#
# Vendored from collective.z3cform.datagridfield 1.5.3.
# See senaite/core/z3cform/datagridfield/__init__.py for details.
"""

    Taken from
    http://pydoc.net/jyu.formwidget.object/1.0b7/jyu.formwidget.object.autoform

    Adds subform support for plone.autoform.

"""
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IAutoExtensibleForm
from z3c.form import action
from z3c.form import form
from z3c.form.error import MultipleErrorViewSnippet
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IMultipleErrors
from z3c.form.interfaces import IObjectWidget
from z3c.form.interfaces import ISubForm
from z3c.form.interfaces import ISubformFactory
from zope.component import adapter
from zope.i18nmessageid import Message
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISubForm)
class AutoExtensibleSubForm(AutoExtensibleForm, form.BaseForm):

    @property
    def schema(self):
        return self.__parent__.field.schema

    def updateActions(self):
        self.actions = action.Actions(self.__parent__, self.request, None)

    def refreshActions(self):
        pass

    def updateFields(self):
        self.updateFieldsFromSchemata()
        super(AutoExtensibleSubForm, self).updateFields()


@adapter(
    Interface,   # widget value
    IFormLayer,  # request
    Interface,   # widget context
    IAutoExtensibleForm,  # form
    IObjectWidget,  # widget
    Interface,   # field
    Interface    # field.schema
)
@implementer(ISubformFactory)
class AutoExtensibleSubformAdapter(object):
    factory = AutoExtensibleSubForm


# XXX: The following controversial and may have side effects.
# Its only purpose is to hide redundant error messages. Every
# error within a subform seem to be rendered both for
# the subform and for the individual field.

@adapter(IMultipleErrors, None, None, None, IAutoExtensibleForm, None)
class MultipleErrorViewSnippetWithMessage(MultipleErrorViewSnippet):
    def render(self):
        return Message(u"There were some errors.", domain="z3c.form")
