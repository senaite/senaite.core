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
from bika.lims import senaiteMessageFactory as _
from plone.app.z3cform.views import Macros
from plone.app.z3cform.views import RenderWidget
from plone.dexterity.browser.edit import DefaultEditView
from plone.dexterity.browser.view import DefaultView
from senaite.core.interfaces import ISenaiteFormLayer
from z3c.form.interfaces import INPUT_MODE
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

FORMAT_TPL = Template("""<span class="$css">
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
        # allow per mode styling
        if context:
            context.klass = self.get_widget_mode_css(context)

    def get_mode(self):
        """Get the current widget mode

        returns either input, display or hidden
        """
        return self.context.mode

    def is_input_mode(self):
        """Check if we are in INPUT mode
        """
        return self.get_mode() == INPUT_MODE

    def is_view_mode(self):
        """Checks if we are in view (DISPLAY/HIDDEN) mode
        """
        return not self.is_input_mode()

    def get_widget_mode_css(self, widget):
        """Allows mode specific css styling for the widget itself

        Example:

            directives.widget("department_id",
                              widget_css_display="text-danger text-monospace",
                              widget_css_input="text-primary")
            department_id = schema.TextLine(...)
        """
        mode = self.get_mode()

        widget_css = getattr(widget, "widget_css_%s" % mode, None)
        if not widget_css:
            widget_css = getattr(widget, "widget_css", None)

        if not widget_css:
            return widget.klass

        # append the mode specific widget css classes
        current_css = widget.klass.split()
        for cls in widget_css.split():
            if cls not in current_css:
                current_css.append(cls)
        return " ".join(current_css)

    def get_prepend_text(self):
        """Get the text/style to prepend to the input field


        Example:

            directives.widget("department_id",
                              before_text_input="ID",
                              before_css_input="text-secondary",
                              before_text_display="ID:",
                              before_css_display="font-weight-bold")
            department_id = schema.TextLine(...)
        """
        mode = self.get_mode()
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
        before_css = getattr(widget, "before_css_%s" % mode, None)
        if not before_css:
            before_css = getattr(widget, "before_css", None)

        return self.format_text(before_text, css=before_css)

    def get_append_text(self):
        """Get the text/style to append to the input field

        Example:

            directives.widget("department_id",
                              after_text="<i class='fas fa-id-card'></i>",
                              after_css="text-primary",
                              after_text_omit_display=True)
            department_id = schema.TextLine(...)
        """
        mode = self.get_mode()
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
        after_css = getattr(widget, "after_css_%s" % mode, None)
        if not after_css:
            after_css = getattr(widget, "after_css", None)

        return self.format_text(after_text, css=after_css)

    def format_text(self, text, css=None):
        """HTML format the text
        """
        if not text:
            return ""
        if css is None:
            css = ""
        context = {
            "text": text,
            "css": css,

        }
        return FORMAT_TPL.safe_substitute(context)


class SenaiteDefaultView(DefaultView):
    """The default view for Dexterity content.
    This uses a WidgetsView and renders all widgets in display mode.
    """
    tabs_template = ViewPageTemplateFile("templates/tabs.pt")

    def __init__(self, context, request):
        super(SenaiteDefaultView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.enable_form_tabbing = self.get_default_form_tabbing()
        self.default_fieldset_label = _("General")

    def get_default_form_tabbing(self):
        tabbing = self.request.get("enable_form_tabbing", "1")
        if tabbing.lower() in ["0", "no"]:
            return False
        return True

    def render_widget_tabs(self):
        return self.tabs_template()


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
