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
AddQuery = 'BIKA: Add Query'

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
    'Query': AddQuery,
}

# Very Old permissions:
# ---------------------
ManageBika = 'BIKA: Manage Bika'
ManageClients = 'BIKA: Manage Clients'
ManageOrders = 'BIKA: Manage Orders'
DispatchOrder = 'BIKA: Dispatch Order'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageARImport = 'BIKA: Manage ARImport'
ManageSamples = 'BIKA: Manage Samples'
ManageSuppliers = 'BIKA: Manage Reference Suppliers'
ManageReference = 'BIKA: Manage Reference'
PostInvoiceBatch = 'BIKA: Post Invoice batch'
ManagePricelists = 'BIKA: Manage Pricelists'

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
ViewRetractedAnalyses = 'BIKA: View Retracted Analyses'
CancelAndReinstate = 'BIKA: Cancel and reinstate'

# For adding login credentials to Contacts.
ManageLoginDetails = 'BIKA: Manage Login Details'

Assign = 'BIKA: Assign analyses'
Unassign = 'BIKA: Unassign analyses'


# Edit AR
# -----------------------------------------------------------------------------
# Allows to set values for AR fields in AR view
#
# Only takes effect if:
#   - The AR's 'cancellation_state' is 'active'
#   - The AR's 'review_state' is in: 
#       'sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 
#       'sample_due', 'sample_received', 'to_be_verified', 'attachment_due'
EditAR = 'BIKA: Edit AR'


# Edit Sample Partition
# -----------------------------------------------------------------------------
# Allows to set a Container and/or Preserver for a Sample Partition.
# See AR view: Sample Partitions table and Sample Partitions tab
#
# Only takes effect if:
#   - The Sample's 'cancellation_state' is 'active'
#   - The Sample's 'review_state' is in: 
#       'sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 
#       'sample_due', 'sample_received', 'to_be_verified', 'attachment_due'
EditSamplePartition = 'BIKA: Edit Sample Partition'

# Edit Client
# ----------------------------------------------
# Allows access to 'Edit' and 'Contacts' tabs from Client View 
EditClient = 'BIKA: Edit Client'
