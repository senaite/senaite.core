# -*- coding: utf-8 -*-

import os

import plone.app.z3cform
import plone.app.z3cform.interfaces
import plone.z3cform.interfaces
import plone.z3cform.templates
import senaite.core.browser.dexterity
import z3c.form.interfaces
from plone.app.z3cform.views import Macros
from plone.app.z3cform.views import RenderWidget
from plone.dexterity.browser.edit import DefaultEditView
from plone.dexterity.browser.view import DefaultView
from senaite.core.interfaces import ISenaiteFormLayer
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


def path(filepart):
    return os.path.join(
        os.path.dirname(senaite.core.browser.dexterity.__file__),
        "templates",
        filepart,
    )


class SenaiteMacros(Macros):
    """Override class for templates/form.pt
    """
    def __init__(self, context, request):
        super(SenaiteMacros, self).__init__(context, request)
        self.context = context
        self.request = request


class SenaiteRenderWidget(RenderWidget):
    index = ViewPageTemplateFile("templates/widget.pt")

    def __init__(self, context, request):
        super(SenaiteRenderWidget, self).__init__(context, request)
        self.context = context
        self.request = request


class SenaiteDefaultView(DefaultView):
    """The default view for Dexterity content.
    This uses a WidgetsView and renders all widgets in display mode.
    """

    def __init__(self, context, request):
        super(SenaiteDefaultView, self).__init__(context, request)
        self.context = context
        self.request = request


class SenaiteDefaultEditView(DefaultEditView):
    """The default edit view for Dexterity content.
    """
    def __init__(self, context, request):
        super(SenaiteDefaultEditView, self).__init__(context, request)
        self.context = context
        self.request = request


# Override the form for the standard full-page form rendering
# Code taken from plone.app.z3cform.views

form_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path("form.pt"),
    form=z3c.form.interfaces.IForm,
    request=ISenaiteFormLayer)
