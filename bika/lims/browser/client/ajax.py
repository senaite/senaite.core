# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

import plone
from bika.lims.adapters.referencewidgetvocabulary import \
    DefaultReferenceWidgetVocabulary
from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class ReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):
    """Implements IReferenceWidgetVocabulary for Clients
    """

    def __call__(self):
        base_query = json.loads(self.request['base_query'])
        portal_type = base_query.get('portal_type', [])
        if 'Contact' in portal_type:
            base_query['getParentUID'] = [self.context.UID(), ]
            # If ensure_ascii is false, a result may be a unicode instance. This
            # usually happens if the input contains unicode strings or the encoding
            # parameter is used.
            # see: https://github.com/senaite/senaite.core/issues/605
            self.request['base_query'] = json.dumps(base_query, ensure_ascii=False)
        return DefaultReferenceWidgetVocabulary.__call__(self)


class ajaxGetClientInfo(BrowserView):
    """Public exposed getClientInfo to be used by the JSON API
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        wf = getToolByName(self.context, 'portal_workflow')
        ret = {'ClientTitle': self.context.Title(),
               'ClientID': self.context.getClientID(),
               'ClientSysID': self.context.id,
               'ClientUID': self.context.UID(),
               'ContactUIDs': [c.UID() for c in
                               self.context.objectValues('Contact') if
                               wf.getInfoFor(c, 'inactive_state',
                                             '') == 'active']
               }

        return json.dumps(ret)
