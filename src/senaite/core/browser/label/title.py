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

from Products.Five.browser import BrowserView
from senaite.core.api import label as label_api


class LabelTitleView(BrowserView):
    """Override of `@@title` for Label content.

    Plone's `main_template.pt` renders the page heading via
    `<h1 tal:replace="structure context/@@title" />`. Overriding the
    view for `ILabel` lets us emit the heading already styled as a
    colored chip — same look as the row chips and the chip grid in
    the manage-labels modal — without resorting to a CSS-injection
    viewlet or a body-class selector.
    """

    def __call__(self):
        title = self.context.title or u""
        color = getattr(self.context, "color", u"") or u""
        style = label_api.chip_style(color)
        style_attr = u' style="{}"'.format(style) if style else u""
        return (
            u'<h1 class="documentFirstHeading">'
            u'<span class="sample-label sample-label--lg"{style}>'
            u'<span class="sample-label-text">{title}</span>'
            u'</span>'
            u'</h1>'
        ).format(style=style_attr, title=html_escape(title))
