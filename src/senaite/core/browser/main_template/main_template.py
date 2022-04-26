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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFPlone.browser.main_template import MainTemplate as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MainTemplate(Base):
    """SENAITE Main Template
    """
    main_template_name = "templates/main_template.pt"

    def __init__(self, context, request):
        super(MainTemplate, self).__init__(context, request)

    @property
    def macros(self):
        # Reinstanciating the templatefile is a workaround for
        # https://github.com/plone/Products.CMFPlone/issues/2666
        # Without this a inifite recusion in a template
        # (i.e. a template that calls its own view)
        # kills the instance instead of raising a RecursionError.
        return ViewPageTemplateFile(self.template_name).macros
