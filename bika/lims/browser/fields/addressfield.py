from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from plone.i18n.locales.countries import countries
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
import sys
from bika.lims import bikaMessageFactory as _

class AddressField(RecordField):
    """ dedicated address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'address',
        'subfields' : ('address', 'city', 'zip', 'state', 'country'),
        'subfield_labels':{'zip':'Postal code'},
        'subfield_vocabularies' :{'country':'CountryNames'},
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()

    security.declarePublic("CountryNames")
    def CountryNames(self, instance = None):
        if not instance:
            instance = self
        return DisplayList(( [(c[1],c[1]) for c in countries.getCountryListing()] ))

registerField(AddressField,
              title = "Address",
              description = "Used for storing address information",
              )

