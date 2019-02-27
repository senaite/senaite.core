# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""
This file has two parts, the first one contains pseudoconstants to get
permissions titles in other places.

The second part is a function to set up permissions for some general objects.

All the available permissions are defined in permissions.zcml.
Each permission has two attributes: a short ID and a long title. The ID
will be used for zope3-like permissions such as ZCML configuration
files. The long title will be used for zope2-like
permissions such as sm.checkPermission.

In order to avoid typo errors, we will use pseudoconstants instead of
permission string values. these constants are defined in ins this file.

The two files (permissions.py and permissions.zcml) must be kept in sync.

bika.lims.__init__ imports * from this file, so
bika.lims.PermName or bika.lims.permissions.PermName are
both valid.
"""

# Add Permissions
# ===============
# For "Add" permissions, keep the name of the variable as "Add<portal_type>".
# When the module gets initialized (bika.lims.__init__), the function initialize
# will look through these Add permissions attributes when registering types and
# will automatically associate them with their types.
AddAnalysis = 'senaite.core: Add Analysis'
AddAnalysisProfile = 'senaite.core: Add AnalysisProfile'
AddAnalysisRequest = 'senaite.core: Add AnalysisRequest'
AddAnalysisSpec = 'senaite.core: Add AnalysisSpec'
AddAttachment = 'senaite.core: Add Attachment'
AddARTemplate = 'senaite.core: Add ARTemplate'
AddBatch = 'senaite.core: Add Batch'
AddClient = 'senaite.core: Add Client'
AddInvoice = 'senaite.core: Add Invoice'
AddMethod = 'senaite.core: Add Method'
AddMultifile = 'senaite.core: Add Multifile'
AddPricelist = 'senaite.core: Add Pricelist'
AddSupplyOrder = 'senaite.core: Add SupplyOrder'
AddSampleMatrix = 'senaite.core: Add SampleMatrix'
AddSamplePoint = 'senaite.core: Add SamplePoint'
AddSamplingDeviation = 'senaite.core: Add SamplingDeviation'
AddSamplingRound = 'senaite.core: Add SamplingRound'
AddSRTemplate = 'senaite.core: Add SRTemplate'
AddSubGroup = 'senaite.core: Add Sub-group'

# Transition permissions
# ======================
TransitionDeactivate = "senaite.core: Transition: Deactivate"
TransitionActivate = "senaite.core: Transition: Activate"
TransitionCancel = "senaite.core: Transition: Cancel"
TransitionReinstate = "senaite.core: Transition: Reinstate"
TransitionClose = 'senaite.core: Transition: Close'
TransitionReopen = 'senaite.core: Transition: Reopen'

# Transition permissions (Analysis and alike)
TransitionRetract = "senaite.core: Transition: Retract"
TransitionVerify = "senaite.core: Transition: Verify"
TransitionAssignAnalysis = 'senaite.core: Transition: Assign Analysis'
TransitionUnassignAnalysis = 'senaite.core: Transition: Unassign Analysis'

# Transition permissions (Analysis Request)
TransitionCancelAnalysisRequest = "senaite.core: Transition: Cancel Analysis Request"
TransitionReinstateAnalysisRequest = "senaite.core: Transition: Reinstate Analysis Request"
TransitionInvalidate = "senaite.core: Transition Invalidate"
TransitionPreserveSample = "senaite.core: Transition: Preserve Sample"
TransitionPublishResults = "senaite.core: Transition: Publish Results"
TransitionReceiveSample = "senaite.core: Transition: Receive Sample"
TransitionRejectSample = "senaite.core: Transition: Reject Sample"
TransitionSampleSample = "senaite.core: Transition: Sample Sample"
TransitionScheduleSampling = "senaite.core: Transition: Schedule Sampling"

# Transition permissions (Supply Order)
TransitionDispatchOrder = 'senaite.core: Transition: Dispatch Order'

# Transition permissions (Sampling Round)
TransitionCloseSamplingRound = 'senaite.core: Transition: Close Sampling Round'
TransitionReopenSamplingRound = 'senaite.core: Transition: Reopen Sampling Round'

# Transition permissions (Worksheet)
TransitionRejectWorksheet = 'senaite.core: Transition: Reject Worksheet'


# Field Permissions
# =================
# Field permissions (Analysis Request)
FieldEditBatch = "senaite.core: Field: Edit Batch"
FieldEditClient = "senaite.core: Field: Edit Client"
FieldEditClientOrderNumber = "senaite.core: Field: Edit Client Order Number"
FieldEditClientReference = "senaite.core: Field: Edit Client Reference"
FieldEditClientSampleID = "senaite.core: Field: Edit Client Sample ID"
FieldEditComposite = "senaite.core: Field: Edit Composite"
FieldEditContact = "senaite.core: Field: Edit Contact"
FieldEditContainer = "senaite.core: Field: Edit Container"
FieldEditDatePreserved = "senaite.core: Field: Edit Date Preserved"
FieldEditDateReceived = "senaite.core: Field: Edit Date Received"
FieldEditDateSampled = "senaite.core: Field: Edit Date Sampled"
FieldEditEnvironmentalConditions = "senaite.core: Field: Edit Environmental Conditions"
FieldEditInvoiceExclude = "senaite.core: Field: Edit Invoice Exclude"
FieldEditMemberDiscount = "senaite.core: Field: Edit Member Discount"
FieldEditPreservation = "senaite.core: Field: Edit Preservation"
FieldEditPreserver = "senaite.core: Field: Edit Preserver"
FieldEditPriority = "senaite.core: Field: Edit Priority"
FieldEditProfiles = "senaite.core: Field: Edit Profiles"
FieldEditPublicationSpecifications = "senaite.core: Field: Edit Publication Specification"
FieldEditRejectionReasons = "senaite.core: Field: Edit Rejection Reasons"
FieldEditResultsInterpretation = "senaite.core: Field: Edit Results Interpretation"
FieldEditSampleCondition = "senaite.core: Field: Edit Sample Condition"
FieldEditSamplePoint = "senaite.core: Field: Edit Sample Point"
FieldEditSampleType = "senaite.core: Field: Edit Sample Type"
FieldEditSampler = "senaite.core: Field: Edit Sampler"
FieldEditSamplingDate = "senaite.core: Field: Edit Sampling Date"
FieldEditSamplingDeviation = "senaite.core: Field: Edit Sampling Deviation"
FieldEditSamplingRound = "senaite.core: Field: Edit Sampling Round"
FieldEditScheduledSampler = "senaite.core: Field: Edit Scheduled Sampler"
FieldEditSpecification = "senaite.core: Field: Edit Specification"
FieldEditStorageLocation = "senaite.core: Field: Edit Storage Location"
FieldEditTemplate = "senaite.core: Field: Edit Template"

# Field permissions (Analysis and alike)
FieldEditAnalysisHidden = "senaite.core: Field: Edit Analysis Hidden"
FieldEditAnalysisResult = "senaite.core: Field: Edit Analysis Result"
FieldEditAnalysisRemarks = "senaite.core: Field: Edit Analysis Remarks"


# Behavioral permissions
# ======================
# TODO Security Review these "behavioral" permissions
AccessJSONAPI = 'BIKA: Access JSON API'
EditFieldResults = 'BIKA: Edit Field Results'
EditResults = 'BIKA: Edit Results'
EditWorksheet = 'BIKA: Edit Worksheet'
ManageBika = 'BIKA: Manage Bika'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageARImport = 'BIKA: Manage ARImport'
ManageInvoices = 'BIKA: Manage Invoices'
ManageLoginDetails = 'BIKA: Manage Login Details'
ManageReference = 'BIKA: Manage Reference'
ManageWorksheets = 'BIKA: Manage Worksheets'
ViewResults = 'BIKA: View Results'


# View/Action permissions
# =======================
# TODO Security Review these "view/action" permissions
ImportInstrumentResults = "BIKA: Import Instrument Results"
ViewRetractedAnalyses = 'BIKA: View Retracted Analyses'
ViewLogTab = 'BIKA: View Log Tab'
