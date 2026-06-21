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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from cgi import escape as html_escape

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from senaite.core.api import label as label_api


class LabelColorViewlet(ViewletBase):
    """Restyles the Label view's `<h1>` heading to look like the
    colored chip it represents.

    Renders nothing visible — only an inline `<style>` block that
    targets `.documentFirstHeading` and paints it with the Label's
    own color. We do not insert a duplicate chip element so the
    heading remains a single, semantically correct `<h1>`.
    """
    index = ViewPageTemplateFile("templates/label_color.pt")

    def color(self):
        value = getattr(self.context, "color", u"") or u""
        return value if label_api.is_safe_color(value) else u""

    def chip_style(self):
        return label_api.chip_style(self.color())

    def title_escaped(self):
        # kept for backwards compat; no longer used by the template
        return html_escape(self.context.title or u"")
