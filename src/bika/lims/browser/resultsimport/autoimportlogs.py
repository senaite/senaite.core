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

from DateTime.DateTime import DateTime
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from bika.lims.exportimport import instruments
from bika.lims import bikaMessageFactory as _
from bika.lims.catalog import CATALOG_AUTOIMPORTLOGS_LISTING

import traceback
from os import listdir
from os.path import isfile, join


class AutoImportLogsView(BikaListingView):
    """
    To list all logs...
    """
    def __init__(self, context, request):
        super(AutoImportLogsView, self).__init__(context, request)
        self.catalog = CATALOG_AUTOIMPORTLOGS_LISTING
        self.contentFilter = {'portal_type': 'AutoImportLog',
                              'sort_on': 'Created',
                              'sort_order': 'reverse'
                              }
        self.title = self.context.translate(_("Last Auto-Import Logs"))
        self.description = ""
        self.columns = {'ImportTime': {'title': _('Time'),
                                       'sortable': False},
                        'Instrument': {'title': _('Instrument'),
                                       'sortable': False,
                                       'attr': 'getInstrumentTitle',
                                       'replace_url': 'getInstrumentUrl'},
                        'Interface': {'title': _('Interface'),
                                      'sortable': False,
                                      'attr': 'getInterface'},
                        'ImportFile': {'title': _('Imported File'),
                                       'sortable': False,
                                       'attr': 'getImportedFile'},
                        'Results': {'title': _('Results'),
                                    'sortable': False,
                                    'attr': 'getResults'},
                        }
        self.review_states = [
            {'id': 'default',
             'title':  _('All'),
             'contentFilter': {},
             'columns': ['ImportTime',
                         'Instrument',
                         'Interface',
                         'ImportFile',
                         'Results']
             },
        ]

    def folderitem(self, obj, item, index):
        item['ImportTime'] = obj.getLogTime.strftime('%Y-%m-%d H:%M:%S')
        return item
