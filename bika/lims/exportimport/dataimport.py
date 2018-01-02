# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.content.instrument import getDataInterfaces
from bika.lims.exportimport import instruments
from bika.lims.exportimport.load_setup_data import LoadSetupData
from bika.lims.interfaces import ISetupDataSetList
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from pkg_resources import *
from zope.component import getAdapters
import json

import plone


class SetupDataSetList:

    implements(ISetupDataSetList)

    def __init__(self, context):
        self.context = context

    def __call__(self, projectname="bika.lims"):
        datasets = []
        for f in resource_listdir(projectname, 'setupdata'):
            fn = f+".xlsx"
            try:
                if fn in resource_listdir(projectname, 'setupdata/%s' % f):
                    datasets.append({"projectname": projectname, "dataset": f})
            except OSError:
                pass
        return datasets


class ImportView(BrowserView):

    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("import.pt")

    def __init__(self, context, request):
        super(ImportView, self).__init__(context, request)

        self.icon = ""
        self.title = self.context.translate(_("Import"))
        self.description = self.context.translate(_("Select a data interface"))

        request.set('disable_border', 1)

    def getDataInterfaces(self):
        return getDataInterfaces(self.context)

    def getSetupDatas(self):
        datasets = []
        adapters = getAdapters((self.context, ), ISetupDataSetList)
        for name, adapter in adapters:
            datasets.extend(adapter())
        return datasets

    def getProjectName(self):
        adapters = getAdapters((self.context, ), ISetupDataSetList)
        productnames = [name for name, adapter in adapters]
        if len(productnames) == 1:
            productnames[0] = 'bika.lims'
        return productnames[len(productnames) - 1]

    def __call__(self):
        if 'submitted' in self.request:
            if 'setupfile' in self.request.form or \
               'setupexisting' in self.request.form:
                lsd = LoadSetupData(self.context, self.request)
                return lsd()
            else:
                exim = instruments.getExim(self.request['exim'])
                if not exim:
                    er_mes = "Importer not found for: %s" % self.request['exim']
                    results = {'errors': [er_mes], 'log': '', 'warns': ''}
                    return json.dumps(results)
                else:
                    return exim.Import(self.context, self.request)
        else:
            return self.template()

    def getInstruments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '...Choose an Instrument...')] + [(o.UID, o.Title) for o in
                               bsc(portal_type = 'Instrument',
                                   inactive_state = 'active')]
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))

class ajaxGetImportTemplate(BrowserView):

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        exim = self.request.get('exim').replace(".", "/")
        # If a specific template for this instrument doesn't exist yet,
        # use the default template for instrument results file import located
        # at bika/lims/exportimport/instruments/instrument.pt
        import os.path
        instrpath = os.path.join("exportimport", "instruments")
        templates_dir = resource_filename("bika.lims", instrpath)
        fname = "%s/%s_import.pt" % (templates_dir, exim)
        if os.path.isfile(fname):
            return ViewPageTemplateFile("instruments/%s_import.pt" % exim)(self)
        else:
            return ViewPageTemplateFile("instruments/instrument.pt")(self)

    def getAnalysisServicesDisplayList(self):
        ''' Returns a Display List with the active Analysis Services
            available. The value is the keyword and the title is the
            text to be displayed.
        '''
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.getObject().Keyword, o.Title) for o in
                                bsc(portal_type = 'AnalysisService',
                                   inactive_state = 'active')]
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))


class ajaxGetImportInterfaces(BrowserView):
    """ Returns a json list with the interfaces assigned to the instrument
        with the following structure:
        [{'id': <interface_id>,
          'title': <interface_title>
        ]
    """
    def __call__(self):
        interfaces = []
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(interfaces)

        from bika.lims.exportimport import instruments
        bsc = getToolByName(self, 'bika_setup_catalog')
        instrument=bsc(portal_type='Instrument',
                       UID=self.request.get('instrument_uid', ''),
                       inactive_state='active',)
        if instrument and len(instrument) == 1:
            instrument = instrument[0].getObject()
            for i in instrument.getImportDataInterface():
                if i:
                    exim = instruments.getExim(i)
                    interface = {'id': i, 'title': exim.title}
                    interfaces.append(interface)
        return json.dumps(interfaces)
