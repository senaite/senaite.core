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

from bika.lims import bikaMessageFactory as _
from referencesamples import ReferenceSamplesView
from senaite.core.i18n import translate


class AddBlankView(ReferenceSamplesView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(AddBlankView, self).__init__(context, request)

        # narrow the base filter down to blank samples
        self.contentFilter["getBlank"] = True

        self.title = translate(_(
            u"listing_add_blank_title",
            default=u"Add Blank Reference"
        ))
