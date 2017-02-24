# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime.DateTime import DateTime
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from bika.lims.exportimport import instruments
from bika.lims import bikaMessageFactory as _

import traceback
from os import listdir
from os.path import isfile, join


class AutoImportLogsView(BikaListingView):
    """
    To list all logs...
    """
    def __init__(self, context, request):
        super(AutoImportLogsView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'AutoImportLog',
                              'sort_on': 'Created',
                              'sort_order': 'reverse'
                              }
        self.title = self.context.translate(_("Last Auto-Import Logs"))
        self.description = ""
        self.columns = {'ImportTime': {'title': _('Time'),
                                       'sortable': False},
                        'Instrument': {'title': _('Instrument'),
                                       'sortable': False},
                        'Interface': {'title': _('Interface'),
                                      'sortable': False,
                                      'attr': 'getInterface'},
                        'ImportFile': {'title': _('Imported File'),
                                       'sortable': False,
                                       'attr': 'getImportedFile'},
                        'Results': {'title': _('Results'),
                                    'sortable': False},
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
        item['ImportTime'] = obj.getLogTime().strftime('%Y-%m-%d  \
                                                            %H:%M:%S')

        item['Instrument'] = ''
        instrument = obj.getInstrument()
        if instrument:
            item['Instrument'] = instrument.Title()
            item['replace']['Instrument'] = "<a href='%s'>%s</a>" % \
                (instrument.absolute_url(), instrument.Title())
        results = ''.join(obj.getResults())
        summ = results[:80]+'...' if len(results) > 80 else results
        item['Results'] = summ
        return item
