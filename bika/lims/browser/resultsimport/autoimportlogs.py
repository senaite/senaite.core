# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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

    def folderitems(self, full_objects=False, classic=False):
        return BikaListingView.folderitems(self, full_objects=False,
                                           classic=False)

    def folderitem(self, obj, item, index):
        item['ImportTime'] = obj.getLogTime.strftime('%Y-%m-%d  \
                                                            %H:%M:%S')
        return item
