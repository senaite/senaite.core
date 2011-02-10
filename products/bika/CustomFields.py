from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.bika.config import COUNTRY_NAMES
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
import sys

validation.register(
    RegexValidator('isNumber', r'^([+-])?[0-9 ]+$', title = 'XXX',
                    description = 'XXX', errmsg = 'is not a valid number.')
)

class AnalysisSpecField(RecordsField):
    """a list of in-range analysis result specifications """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'analysisspec',
        'subfields' : ('service', 'min', 'max', 'error'),
        'required_subfields' : ('service', 'min', 'max', 'error'),
        'subfield_labels':{'service': 'Analysis Service',
                           'min': 'Min',
                           'max': 'Max',
                           'error': '% Error'},
        })
    security = ClassSecurityInfo()

registerField(AnalysisSpecField,
              title = "Analysis Result Specification",
              description = "Used for storing analysis results specifications",
              )

class StandardResultField(RecordsField):
    """a list of standard sample results """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'standardresult',
        'subfields' : ('service', 'result', 'min', 'max'),
        'required_subfields' : ('service'),
        'subfield_labels':{'service': 'Analysis Service',
                           'result': 'Result',
                           'min': 'Min',
                           'max': 'Max'},
        })
    security = ClassSecurityInfo()

registerField(StandardResultField,
              title = "Standard Results",
              description = "Used for storing standard results",
              )

class TemplatePositionField(RecordsField):
    """a list of worksheet template rows """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'templateposition',
        'subfields' : ('pos', 'type', 'sub'),
        'required_subfields' : ('pos', 'type'),
        'subfield_labels':{'pos': 'Position',
                           'type': 'Type',
                           'sub': 'Subtype'},
        })
    security = ClassSecurityInfo()

registerField(TemplatePositionField,
              title = "Template Position",
              description = "Used for storing worksheet layout",
              )

class WorksheetAnalysesField(RecordsField):
    """a list of worksheet analyses """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'worksheetanalyses',
        'subfields' : ('uid', 'type', 'pos', 'key'),
        'subfield_types' : {'pos':'int'},
        'required_subfields' : ('uid', 'type', 'pos', 'key'),
        'subfield_labels':{'uid': 'UID',
                           'type': 'Type',
                           'pos': 'Position',
                           'key': 'Key value'},
        })
    security = ClassSecurityInfo()

registerField(WorksheetAnalysesField,
              title = "Worksheet Analyses",
              description = "Used for storing worksheet analyses",
              )


# XXX some provision for default country for this lims
#  probably from bika_settings/laboratory

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
        return COUNTRY_NAMES


registerField(AddressField,
              title = "Address",
              description = "Used for storing address information",
              )

