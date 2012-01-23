from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "bika.lims"

GLOBALS = globals()

# Very Old permissions:
ManageBika = 'BIKA: Manage Bika'
ManageClients = 'BIKA: Manage Clients'
ManageWorksheets = 'BIKA: Manage Worksheets'
ManageOrders = 'BIKA: Manage Orders'
DispatchOrder = 'BIKA: Dispatch Order'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageARImport = 'BIKA: Manage ARImport'
ManageSample = 'BIKA: Manage Sample'
ManageReferenceSuppliers = 'BIKA: Manage Reference Suppliers'
ManageReference = 'BIKA: Manage Reference'
PostInvoiceBatch = 'BIKA: Post Invoice batch'
ManagePricelists = 'BIKA: Manage Pricelists'
# New or changed permissions:
ReceiveSample = 'BIKA: Receive Sample'
ExpireSample = 'BIKA: Expire Sample'
DisposeSample = 'BIKA: Dispose Sample'
ImportAnalysis = 'BIKA: Import Analysis'
RejectWorksheet = 'BIKA: Reject Worksheet'
Retract = "BIKA: Retract"
Verify = 'BIKA: Verify'
VerifyOwnResults = 'BIKA: Verify own results'
Publish = 'BIKA: Publish'
EditSample = 'BIKA: Edit Sample'
EditAR = 'BIKA: Edit AR'
EditWorksheet = 'BIKA: Edit Worksheet'
ManageResults = 'BIKA: Manage Results'
ResultsNotRequested = 'BIKA: Results not requested'
ManageInvoices = 'BIKA: Manage Invoices'
ViewResults = 'BIKA: View Results'
EditResults = 'BIKA: Edit Results'
CancelAndReinstate = 'BIKA: Cancel and reinstate'

TYPES_TO_VERSION = ('AnalysisService',
                    'Calculation',
                    'SamplePoint',
                    'SampleType',
                    'AnalysisSpec',
                    'WorksheetTemplate',

#                    'Worksheet',
#                    'AnalysisRequest',
#                    'Sample',
#                    'Analysis',
#                    'DuplicateAnalysis',
#                    'ReferenceAnalysis',
                    )

AUTO_VERSION = ('AnalysisService',
                'Calculation',
                'SamplePoint',
                'SampleType',
                'AnalysisSpec',
                'WorksheetTemplate',
                )

BIKA_PERMISSIONS = (
    (ManageBika, ()),
    (ManageClients, ()),
    (ManageWorksheets, ()),
    (ManageOrders, ()),
    (ManageAnalysisRequests, ()),
    (ManageSample, ()),
    (ManageReferenceSuppliers, ()),
    (ManageReference, ()),
    (ManagePricelists, ()),
    (ManageARImport, ()),
    (DispatchOrder, ()),
    (PostInvoiceBatch, ()),
    (ReceiveSample, ()),
    (ExpireSample, ()),
    (DisposeSample, ()),
    (ImportAnalysis, ()),
    (RejectWorksheet, ()),
    (Retract, ()),
    (Verify, ()),
    (VerifyOwnResults, ()),
    (Publish, ()),
    (EditSample, ()),
    (EditAR, ()),
    (EditWorksheet, ()),
    (ManageResults, ()),
    (ResultsNotRequested, ()),
    (ManageInvoices, ()),
    (ViewResults, ()),
    (EditResults, ()),
    (CancelAndReinstate, ()),
)


PUBLICATION_PREFS = DisplayList((
    ('email', _('Email')),
    ('fax', _('Fax')),
    ('file', _('File')),
    ('pdf', _('PDF')),
    ('print', _('Print')),
    ('sms', _('SMS')),
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

CLIENT_TYPES = DisplayList((
    ('corporate', 'Bulk Discount'),
    ('noncorporate', 'Standard Price'),
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
    ('cs', _('Client Sample ID')),
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
