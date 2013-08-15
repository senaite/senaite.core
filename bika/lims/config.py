from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import *
from zope.i18n.locales import locales

PROJECTNAME = "bika.lims"

GLOBALS = globals()

VERSIONABLE_TYPES = ('AnalysisService',
                     'Calculation',
                     'SamplePoint',
                     'SampleType',
                     'AnalysisSpec',
                     'WorksheetTemplate',
                     )

PUBLICATION_PREFS = DisplayList((
    ('email', _('Email')),
#    ('fax', _('Fax')),
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
ARIMPORT_OPTIONS = DisplayList((
    ('c', _('Classic')),
    ('p', _('Profiles')),
    ('s', _('Special')),
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

currencies = locales.getLocale('en').numbers.currencies.values()
currencies.sort(lambda x,y:cmp(x.displayName, y.displayName))

CURRENCIES = DisplayList(
    [(c.type, "%s (%s)" % (c.displayName, c.symbol))
     for c in currencies]
)
