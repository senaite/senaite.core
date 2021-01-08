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

from bika.lims.catalog import SETUP_CATALOG

from plone.dexterity.content import Item
from plone.supermodel import model

from zope.interface import implementer


class IInterpretationTemplate(model.Schema):
    """Results Interpretation Template content interface
    """
    # The behavior IRichTextBehavior applies to this content type, so it
    # already provides the "text" field that renders the TinyMCE's Wsiwyg
    pass


@implementer(IInterpretationTemplate)
class InterpretationTemplate(Item):
    """Results Interpretation Template content
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]
