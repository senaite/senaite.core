# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.organisation import schema
from plone.app.folder.folder import ATFolder


class Organisation(ATFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(CMFCorePermissions.View, 'getSchema')

    def getSchema(self):
        return self.schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        field = self.getField('Name')
        field = field and field.get(self) or ''
        return safe_unicode(field).encode('utf-8')

    def setTitle(self, value, **kwargs):
        return self.setName(value, **kwargs)

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress', 'BillingAddress']

    def getPrintAddress(self):
        postal = self.getPostalAddress()
        physical = self.getPhysicalAddress()
        billing = self.getBillingAddress()

        use_address = None
        if postal.get('city', False):
            use_address = postal
        elif physical.get('city', False):
            use_address = physical
        elif billing.get('city', False):
            use_address = billing

        address_lines = []
        if use_address:
            if use_address['address']:
                address_lines.append(use_address['address'])
            city_line = ''
            if use_address['city']:
                city_line += use_address['city'] + ' '
            if use_address['zip']:
                city_line += use_address['zip'] + ' '
            if city_line:
                address_lines.append(city_line)

            statecountry_line = ''
            if use_address['state']:
                statecountry_line += use_address['state'] + ', '
            if use_address['country']:
                statecountry_line += use_address['country']
            if statecountry_line:
                address_lines.append(statecountry_line)

        return address_lines


registerType(Organisation, PROJECTNAME)
