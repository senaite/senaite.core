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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import bikaMessageFactory as _
from Products.Archetypes.public import DisplayList
from zope.i18n.locales import locales

# Implicit module imports used by others
# XXX Refactor these dependencies to explicit imports!
from bika.lims.utils import t  # noqa
from bika.lims.permissions import *  # noqa

try:
    import collective.indexing
    collective.indexing  # noqa
except ImportError:
    USE_COLLECTIVE_INDEXING = False
else:
    USE_COLLECTIVE_INDEXING = True


PROJECTNAME = "bika.lims"

GLOBALS = globals()

VERSIONABLE_TYPES = ('Calculation',
                     )

# Upper detection limit operand
UDL = ">"

# Lower detection limit operand
LDL = "<"

POINTS_OF_CAPTURE = DisplayList((
    ('field', _('Field Analyses')),
    ('lab', _('Lab Analyses')),
))

SERVICE_POINT_OF_CAPTURE = DisplayList((
    ('field', _('Field')),
    ('lab', _('Lab')),
))

PRESERVATION_CATEGORIES = DisplayList((
    ('field', _('Field Preservation')),
    ('lab', _('Lab Preservation')),
))

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', _('Analysis Services')),
    ('LabProduct', _('Lab Products')),
))

ANALYSIS_TYPES = DisplayList((
    ('a', _('Analysis')),
    ('b', _('Blank')),
    ('c', _('Control')),
    ('d', _('Duplicate')),
))
STD_TYPES = DisplayList((
    ('c', _('Control')),
    ('b', _('Blank')),
))
ATTACHMENT_OPTIONS = DisplayList((
    ('r', _('Required')),
    ('p', _('Permitted')),
    ('n', _('Not Permitted')),
))
ATTACHMENT_REPORT_OPTIONS = DisplayList((
    ('r', _('Render in Report')),
    ('i', _('Ignore in Report')),
))
GENDERS = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ))

ADDRESS_TYPES = DisplayList((
    ('physical', _('Physical address')),
    ('mailing', _('Mailing address')),
    ('billing', _('Billing address')),
    ('shipping', _('Shipping address')),
    ))

QCANALYSIS_TYPES = DisplayList((
    ('b', _('Blank QC analyses')),
    ('c', _('Control QC analyses')),
    ('d', _('Duplicate QC analyses'))
))

WEEKDAYS = DisplayList((
    ('0', _('Monday')),
    ('1', _('Tuesday')),
    ('2', _('Wednesday')),
    ('3', _('Thursday')),
    ('4', _('Friday')),
    ('5', _('Saturday')),
    ('6', _('Sunday')),
))

currencies = locales.getLocale('en').numbers.currencies.values()
currencies.sort(lambda x, y: cmp(x.displayName, y.displayName))

CURRENCIES = DisplayList(
    [(c.type, "%s (%s)" % (c.displayName, c.symbol))
     for c in currencies]
)

VERIFIED_STATES = ('verified', 'published')

DECIMAL_MARKS = DisplayList((
    ('.', _('Dot (.)')),
    (',', _('Comma (,)')),
))
SCINOTATION_OPTIONS = DisplayList((
    ('1', 'aE+b / aE-b'),
    ('2', 'ax10^b / ax10^-b'),
    ('3', 'ax10^b / ax10^-b (with superscript)'),
    ('4', 'a·10^b / a·10^-b'),
    ('5', 'a·10^b / a·10^-b (with superscript)'),
))
WORKSHEET_LAYOUT_OPTIONS = DisplayList((
    ('1', _('Classic')),
    ('2', _('Transposed')),
))
MULTI_VERIFICATION_TYPE = DisplayList((
    ('self_multi_enabled', _('Allow same user to verify multiple times')),
    ('self_multi_not_cons', _('Allow same user to verify multiple times, but not consecutively')),
    ('self_multi_disabled', _('Disable multi-verification for the same user')),
))
PRIORITIES = DisplayList((
    ('1', _('Highest')),
    ('2', _('High')),
    ('3', _('Medium')),
    ('4', _('Low')),
    ('5', _('Lowest')),
))
MIN_OPERATORS = DisplayList((
    ('geq', ">="),
    ('gt', '>')
))
MAX_OPERATORS = DisplayList((
    ('leq', "<="),
    ('lt', '<')
))
