from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "bika"
SKINS_DIR = 'skins'

GLOBALS = globals()

ManageBika = 'BIKA: Manage bika'
ManageClients = 'BIKA: Manage Clients'
ManageWorksheets = 'BIKA: Manage Worksheets'
ManageOrders = 'BIKA: Manage Orders'
ManageAnalysisRequest = 'BIKA: Manage AnalysisRequest'
ManageSample = 'BIKA: Manage Sample'
ManageStandardSuppliers = 'BIKA: Manage Standard Suppliers'
ManageStandard = 'BIKA: Manage Standard'
ManageInvoices = 'BIKA: Manage Invoices'
ManagePricelists = 'BIKA: Manage Pricelists'
ViewMethods = 'BIKA: View Methods'
EditAnalyses = 'BIKA: Edit analyses'
ViewResults = 'BIKA: View Results'
ManageARImport = 'BIKA: Manage ARImport'

# Workflow permissions
ReceiveSample = 'BIKA: Receive sample'
SubmitSample = 'BIKA: Submit sample'
VerifySample = 'BIKA: Verify sample'
PublishSample = 'BIKA: Publish sample'
RetractSample = 'BIKA: Retract sample'
ImportSample = 'BIKA: Import sample'

SubmitWorksheet = 'BIKA: Submit Worksheet'
VerifyWorksheet = 'BIKA: Verify Worksheet'
RetractWorksheet = 'BIKA: Retract Worksheet'

DispatchOrder = 'BIKA: Dispatch Order'

PostInvoiceBatch = 'BIKA: Post Invoice batch'

# Worksheet permissions
AssignAnalyses = 'BIKA: Assign analyses'
DeleteAnalyses = 'BIKA: Delete analyses'
SubmitResults = 'BIKA: Submit results'

BIKA_PERMISSIONS = (
    (ManageBika, ()),
    (ManageClients, ()),
    (ManageWorksheets, ()),
    (ManageOrders, ()),
    (ManageAnalysisRequest, ()),
    (ManageSample, ()),
    (ManageStandardSuppliers, ()),
    (ManageStandard, ()),
    (EditAnalyses, ()),
    (ViewResults, ()),
    (ViewMethods, ()),
    (ReceiveSample, ()),
    (SubmitSample, ()),
    (VerifySample, ()),
    (PublishSample, ()),
    (RetractSample, ()),
    (ImportSample, ()),
    (ManageARImport, ()),
    (SubmitWorksheet, ()),
    (VerifyWorksheet, ()),
    (RetractWorksheet, ()),
    (DispatchOrder, ()),
    (DeleteAnalyses, ()),
    (SubmitResults, ()),
)

PUBLICATION_PREFS = DisplayList((
    ('email', 'Email'),
    ('fax', 'Fax'),
    ('file', 'File'),
    ('pdf', 'PDF'),
    ('print', 'Print'),
    ('sms', 'SMS'),
))

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', 'Analysis services'),
    ('LabProduct', 'Lab products'),
))

CLIENT_TYPES = DisplayList((
    ('corporate', 'Corporate'),
    ('noncorporate', 'Non Corporate'),
))

ANALYSIS_TYPES = DisplayList((
    ('a', 'Analysis'),
    ('b', 'Blank'),
    ('c', 'Control'),
    ('d', 'Duplicate'),
))
STD_TYPES = DisplayList((
    ('c', 'Control'),
    ('b', 'Blank'),
))
ATTACHMENT_OPTIONS = DisplayList((
    ('r', 'Required'),
    ('p', 'Permitted'),
    ('n', 'Not Permitted'),
))
ARIMPORT_OPTIONS = DisplayList((
    ('c', 'Classic'),
    ('p', 'Profiles'),
    ('s', 'Special'),
))
EMAIL_SUBJECT_OPTIONS = DisplayList((
    ('ar', 'Analysis Request ID'),
    ('co', 'Order ID'),
    ('cr', 'Client Reference'),
    ('cs', 'Client Sample ID'),
))
INSTRUMENT_EXPORTS = DisplayList((
    ('instrument1', 'Instrument 1'),
    ('instrument2', 'Instrument 2'),
    ('instrument3', 'Instrument 3'),
))

INSTRUMENT_IMPORTS = DisplayList((
    ('instrument1', 'Instrument 1'),
    ('instrument2', 'Instrument 2'),
    ('instrument3', 'Instrument 3'),
))

I18N_DOMAIN = 'bika'

