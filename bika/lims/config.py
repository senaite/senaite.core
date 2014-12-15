# -*- coding: utf-8 -*-

from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import *
from zope.i18n.locales import locales

PROJECTNAME = "bika.lims"

GLOBALS = globals()

VERSIONABLE_TYPES = ('AnalysisService',
                     'Calculation',
                     'SamplePoint',
                     'StorageLocation',
                     'SampleType',
                     'AnalysisSpec',
                     'WorksheetTemplate',
                     )

PUBLICATION_PREFS = DisplayList((
    ('email', _('Email')),
    ('pdf', _('PDF')),
# https://github.com/bikalabs/Bika-LIMS/issues/713
#    ('fax', _('Fax')),
#    ('file', _('File')),
#    ('print', _('Print')),
#    ('sms', _('SMS')),
))

POINTS_OF_CAPTURE = DisplayList((
    ('field', _('Field Analyses')),
    ('lab', _('Lab Analyses')),
))

SERVICE_POINT_OF_CAPTURE = DisplayList((
    ('field', _('Field')),
    ('lab', _('Lab')),
))

PRESERVATION_CATEGORIES = DisplayList((
    ('field', _('Field Preservation')),
    ('lab', _('Lab Preservation')),
))

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', _('Analysis Services')),
    ('LabProduct', _('Lab Products')),
))

ANALYSIS_TYPES = DisplayList((
    ('a', _('Analysis')),
    ('b', _('Blank')),
    ('c', _('Control')),
    ('d', _('Duplicate')),
))
STD_TYPES = DisplayList((
    ('c', _('Control')),
    ('b', _('Blank')),
))
ATTACHMENT_OPTIONS = DisplayList((
    ('r', _('Required')),
    ('p', _('Permitted')),
    ('n', _('Not Permitted')),
))
DEFAULT_AR_SPECS = DisplayList((
    ('ar_specs', _('Analysis Request Specifications')),
    ('lab_sampletype_specs', _('Sample Type Specifications (Lab)')),
    ('client_sampletype_specs', _('Sample Type Specifications (Client)')),
))
ARIMPORT_OPTIONS = DisplayList((
    ('c', _('Classic')),
    ('p', _('Profiles')),
#    ('s', _('Special')),
))
EMAIL_SUBJECT_OPTIONS = DisplayList((
    ('ar', _('Analysis Request ID')),
    ('co', _('Order ID')),
    ('cr', _('Client Reference')),
    ('cs', _('Client SID')),
))

GENDERS = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ))

ADDRESS_TYPES = DisplayList((
    ('physical', _('Physical address')),
    ('mailing', _('Mailing address')),
    ('billing', _('Billing address')),
    ('shipping', _('Shipping address')),
    ))

QCANALYSIS_TYPES = DisplayList((
    ('b', _('Blank QC analyses')),
    ('c', _('Control QC analyses')),
    ('d', _('Duplicate QC analyses'))
))

currencies = locales.getLocale('en').numbers.currencies.values()
currencies.sort(lambda x,y:cmp(x.displayName, y.displayName))

CURRENCIES = DisplayList(
    [(c.type, "%s (%s)" % (c.displayName, c.symbol))
     for c in currencies]
)

VERIFIED_STATES = ('verified', 'published')

DECIMAL_MARKS = DisplayList((
    ('.', _('Dot (.)')),
    (',', _('Comma (,)')),
))
SCINOTATION_OPTIONS = DisplayList((
    ('1', 'aE+b / aE-b'),
    ('2', 'ax10^b / ax10^-b'),
    ('3', 'ax10^b / ax10^-b (with superscript)'),
    ('4', 'a·10^b / a·10^-b'),
    ('5', 'a·10^b / a·10^-b (with superscript)'),
))
