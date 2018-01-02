# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.utils import t
from bika.lims.permissions import *
from bika.lims.utils import to_unicode
from Products.ZCTextIndex.ParseTree import ParseError
import json
import plone


class ajaxGetSampleTypeInfo(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uid = self.request.get('UID', '')
        title = self.request.get('Title', '')
        ret = {
               'UID': '',
               'Title': '',
               'Prefix': '',
               'Hazardous': '',
               'SampleMatrixUID': '',
               'SampleMatrixTitle': '',
               'MinimumVolume':  '',
               'ContainerTypeUID': '',
               'ContainerTypeTitle': '',
               'SamplePoints': ('',),
               'StorageLocations': ('',),
               }
        proxies = None
        if uid:
            try:
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                proxies = bsc(UID=uid)
            except ParseError:
                pass
        elif title:
            try:
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                proxies = bsc(portal_type='SampleType', title=to_unicode(title))
            except ParseError:
                pass

        if proxies and len(proxies) == 1:
            st = proxies[0].getObject();
            ret = {
               'UID': st.UID(),
               'Title': st.Title(),
               'Prefix': st.getPrefix(),
               'Hazardous': st.getHazardous(),
               'SampleMatrixUID': st.getSampleMatrix() and \
                                  st.getSampleMatrix().UID() or '',
               'SampleMatrixTitle': st.getSampleMatrix() and \
                                  st.getSampleMatrix().Title() or '',
               'MinimumVolume':  st.getMinimumVolume(),
               'ContainerTypeUID': st.getContainerType() and \
                                   st.getContainerType().UID() or '',
               'ContainerTypeTitle': st.getContainerType() and \
                                     st.getContainerType().Title() or '',
               'SamplePoints': dict((sp.UID(),sp.Title()) for sp in st.getSamplePoints()),
               'StorageLocations': dict((sp.UID(),sp.Title()) for sp in st.getStorageLocations()),
               }

        return json.dumps(ret)
