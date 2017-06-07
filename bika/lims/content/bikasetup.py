# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import registerType
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.bikasetup import schema
from bika.lims.interfaces import IBikaSetup
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.locales import COUNTRIES
from bika.lims.vocabularies import getStickerTemplates as _getStickerTemplates
from plone.app.folder import folder
from zope.interface import implements


class BikaSetup(folder.ATFolder):
    """
    """
    implements(IBikaSetup, IHaveNoBreadCrumbs)

    schema = schema
    security = ClassSecurityInfo()

    def getAttachmentsPermitted(self):
        """Attachments permitted
        """
        if self.getARAttachmentOption() in ['r', 'p'] \
                or self.getAnalysisAttachmentOption() in ['r', 'p']:
            return True
        return False

    def getStickerTemplates(self):
        """Get the sticker templates
        """
        out = [[t['id'], t['title']] for t in _getStickerTemplates()]
        return DisplayList(out)

    def getARAttachmentsPermitted(self):
        """AR attachments permitted
        """
        if self.getARAttachmentOption() == 'n':
            return False
        return True

    def getAnalysisAttachmentsPermitted(self):
        """Analysis attachments permitted
        """
        if self.getAnalysisAttachmentOption() == 'n':
            return False
        return True

    def getAnalysisServices(self):
        """
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + \
                [(o.UID, o.Title) for o in
                 bsc(portal_type='AnalysisService', inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getPrefixFor(self, portal_type):
        """Return the prefix for a portal_type.
           If not found, simply uses the portal_type itself
        """
        prefix = [p for p in self.getPrefixes() if
                  p['portal_type'] == portal_type]
        if prefix:
            return prefix[0]['prefix']
        return portal_type

    def getCountries(self):
        items = [(x['ISO'], x['Country']) for x in COUNTRIES]
        items.sort(lambda z, y: cmp(z[1], y[1]))
        return items

    def isRejectionWorkflowEnabled(self):
        """Return true if the rejection workflow is enabled (its checkbox is 
        set)
        """
        widget = self.getRejectionReasons()
        # widget will be something like:
        # [{'checkbox': u'on',
        #   'textfield-2': u'b',
        #   'textfield-1': u'c',
        #   'textfield-0': u'a'}]
        if len(widget) > 0:
            checkbox = widget[0].get('checkbox', False)
            return True if checkbox == 'on' and len(widget[0]) > 1 else False
        return False

    def _getNumberOfRequiredVerificationsVocabulary(self):
        """
        Returns a DisplayList with the available options for the
        multi-verification list: '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
            multi-verification list
        """
        items = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))


registerType(BikaSetup, PROJECTNAME)
