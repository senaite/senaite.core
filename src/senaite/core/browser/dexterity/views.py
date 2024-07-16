# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import os
from string import Template

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
from z3c.form.interfaces import INPUT_MODE
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

FORMAT_TPL = Template("""<span class="$css_class">
  $text
</span>
""")


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

    def is_input_mode(self):
        """Check if we are in INPUT mode
        """
        return self.context.mode == INPUT_MODE

    def is_view_mode(self):
        """Checks if we are in view (DISPLAY/HIDDEN) mode
        """
        return not self.is_input_mode()

    def get_prepend_text(self):
        """Get the text/style to prepend to the input field


        Example:

            directives.widget("department_id",
                            before_text_edit="ID",
                            before_css_class_edit="text-secondary",
                            before_text_display="ID:",
                            before_css_class_display="font-weight-bold")
            department_id = schema.TextLine(...)
        """
        mode = self.context.mode
        widget = self.context

        # omit the text in the current mode
        omit = getattr(widget, "before_text_omit_%s" % mode, False)
        if omit:
            return

        # get the append text
        before_text = getattr(widget, "before_text_%s" % mode, None)
        if not before_text:
            before_text = getattr(widget, "before_text", None)

        # get the CSS classes for the append text
        before_css_class = getattr(widget, "before_css_class_%s" % mode, None)
        if not before_css_class:
            before_css_class = getattr(widget, "before_css_class", None)

        return self.format_text(before_text, css_class=before_css_class)

    def get_append_text(self):
        """Get the text/style to append to the input field

        Example:

            directives.widget("department_id",
                              after_text="<i class='fas fa-id-card'></i>",
                              after_css_class="text-primary",
                              after_text_omit_display=True)
            department_id = schema.TextLine(...)
        """
        mode = self.context.mode
        widget = self.context

        # omit the text in the current mode
        omit = getattr(widget, "after_text_omit_%s" % mode, False)
        if omit:
            return

        # get the append text
        after_text = getattr(widget, "after_text_%s" % mode, None)
        if not after_text:
            after_text = getattr(widget, "after_text", None)

        # get the CSS classes for the append text
        after_css_class = getattr(widget, "after_css_class_%s" % mode, None)
        if not after_css_class:
            after_css_class = getattr(widget, "after_css_class", None)

        return self.format_text(after_text, css_class=after_css_class)

    def format_text(self, text, css_class=None):
        """HTML format the text
        """
        if not text:
            return ""
        if css_class is None:
            css_class = ""
        context = {
            "text": text,
            "css_class": css_class,

        }
        return FORMAT_TPL.safe_substitute(context)


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
