# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.analysisprofile import schema
from bika.lims.interfaces import IAnalysisProfile
from zope.interface import implements


class AnalysisProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisProfile)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getClientUID(self):
        return self.aq_parent.UID()

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            profile, returns a dictionary with the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings()
                if s.get('uid', '') == uid]
        return sets[0] if sets else {'uid': uid}

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this profile, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                profile or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('%s is not valid' % uid)
        return sets.get('hidden', False)

    def getVATAmount(self):
        """ Compute AnalysisProfileVATAmount
        """
        price, vat = self.getAnalysisProfilePrice(), \
                     self.getAnalysisProfileVAT()
        return float(price) * float(vat) / 100

    def getTotalPrice(self):
        """
        Computes the final price using the VATAmount and the subtotal price
        """
        price, vat = self.getAnalysisProfilePrice(), self.getVATAmount()
        return float(price) + float(vat)


registerType(AnalysisProfile, PROJECTNAME)
