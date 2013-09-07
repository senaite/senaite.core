"""	All permissions are defined here.
    They are also defined in permissions.zcml.
    The two files must be kept in sync.

    bika.lims.__init__ imports * from this file, so
    bika.lims.PermName or bika.lims.permissions.PermName are
    both valid.

"""
from Products.CMFCore.permissions import AddPortalContent

# Add Permissions:
# ----------------
AddAnalysis = 'BIKA: Add Analysis'
AddAnalysisProfile = 'BIKA: Add AnalysisProfile'
AddAnalysisRequest = 'BIKA: Add Analysis Request'
AddAnalysisSpec = 'BIKA: Add AnalysisSpec'
AddARTemplate = 'BIKA: Add ARTemplate'
AddBatch = 'BIKA: Add Batch'
AddClient = 'BIKA: Add Client'
AddClientFolder = 'BIKA: Add ClientFolder'
AddMethod = 'BIKA: Add Method'
AddSample = 'BIKA: Add Sample'
AddSampleMatrix = 'BIKA: Add SampleMatrix'
AddSamplePartition = 'BIKA: Add SamplePartition'
AddSamplePoint = 'BIKA: Add SamplePoint'
AddSamplingDeviation = 'BIKA: Add SamplingDeviation'

# Default Archetypes Add Permission
ADD_CONTENT_PERMISSION = AddPortalContent

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'ARAnalysisSpec': AddAnalysisSpec,
    'AnalysisProfile': AddAnalysisProfile,
    'Analysis': AddAnalysis,
    'AnalysisRequest': AddAnalysisRequest,
    'Batch': AddBatch,
    'Client': AddClient,
    'Method': AddMethod,
    'Sample': AddSample,
    'SampleMatrix': AddSampleMatrix,
    'SamplePartition': AddSamplePartition,
    'SamplingDeviation': AddSamplingDeviation,
}

# Very Old permissions:
# ---------------------
ManageBika = 'BIKA: Manage Bika'
ManageOrders = 'BIKA: Manage Orders'
DispatchOrder = 'BIKA: Dispatch Order'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageARImport = 'BIKA: Manage ARImport'
ManageSamples = 'BIKA: Manage Samples'
ManageSuppliers = 'BIKA: Manage Reference Suppliers'
ManageReference = 'BIKA: Manage Reference'
PostInvoiceBatch = 'BIKA: Post Invoice batch'
ManagePricelists = 'BIKA: Manage Pricelists'

# This allows to edit all client fields, and perform admin tasks on Clients.
ManageClients = 'BIKA: Manage Clients'

# this is for creating and transitioning worksheets
ManageWorksheets = 'BIKA: Manage Worksheets'
# this is for adding/editing/exporting analyses on worksheets
EditWorksheet = 'BIKA: Edit Worksheet'
RejectWorksheet = 'BIKA: Reject Worksheet'

ImportInstrumentResults = "BIKA: Import Instrument Results"

# New or changed permissions:
# ---------------------------
SampleSample = 'BIKA: Sample Sample'
PreserveSample = 'BIKA: Preserve Sample'
ReceiveSample = 'BIKA: Receive Sample'
ExpireSample = 'BIKA: Expire Sample'
DisposeSample = 'BIKA: Dispose Sample'
ImportAnalysis = 'BIKA: Import Analysis'
Retract = "BIKA: Retract"
Verify = 'BIKA: Verify'
VerifyOwnResults = 'BIKA: Verify own results'
Publish = 'BIKA: Publish'
EditSample = 'BIKA: Edit Sample'
EditAR = 'BIKA: Edit AR'
ResultsNotRequested = 'BIKA: Results not requested'
ManageInvoices = 'BIKA: Manage Invoices'
ViewResults = 'BIKA: View Results'
EditResults = 'BIKA: Edit Results'
EditFieldResults = 'BIKA: Edit Field Results'
CancelAndReinstate = 'BIKA: Cancel and reinstate'

# For adding login credentials to Contacts.
ManageLoginDetails = 'BIKA: Manage Login Details'
