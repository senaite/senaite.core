# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
AddAnalysis = "senaite.core: Add Analysis"
AddAnalysisCategory = "senaite.core: Add AnalysisCategory"
AddAnalysisProfile = "senaite.core: Add AnalysisProfile"
AddAnalysisRequest = "senaite.core: Add AnalysisRequest"
AddAnalysisService = "senaite.core: Add AnalysisService"
AddAnalysisSpec = "senaite.core: Add AnalysisSpec"
AddARTemplate = "senaite.core: Add ARTemplate"
AddAttachment = "senaite.core: Add Attachment"
AddAttachmentType = "senaite.core: Add AttachmentType"
AddBatch = "senaite.core: Add Batch"
AddBatchLabel = "senaite.core: Add BatchLabel"
AddCalculation = "senaite.core: Add Calculation"
AddClient = "senaite.core: Add Client"
AddContainer = "senaite.core: Add Container"
AddContainerType = "senaite.core: Add ContainerType"
AddDepartment = "senaite.core: Add Department"
AddIdentifierType = "senaite.core: Add IdentifierType"
AddInstrument = "senaite.core: Add Instrument"
AddInstrumentLocation = "senaite.core: Add InstrumentLocation"
AddInstrumentType = "senaite.core: Add InstrumentType"
AddInvoice = "senaite.core: Add Invoice"
AddLabContact = "senaite.core: Add LabContact"
AddLabProduct = "senaite.core: Add LabProduct"
AddManufacturer = "senaite.core: Add Manufacturer"
AddMethod = "senaite.core: Add Method"
AddMultifile = "senaite.core: Add Multifile"
AddPreservation = "senaite.core: Add Preservation"
AddPricelist = "senaite.core: Add Pricelist"
AddReferenceDefinition = "senaite.core: Add ReferenceDefinition"
AddReflexRule = "senaite.core: Add ReflexRule"
AddSampleCondition = "senaite.core: Add SampleCondition"
AddSampleMatrix = "senaite.core: Add SampleMatrix"
AddSamplePoint = "senaite.core: Add SamplePoint"
AddSampleType = "senaite.core: Add SampleType"
AddSamplingDeviation = "senaite.core: Add SamplingDeviation"
AddStorageLocation = "senaite.core: Add StorageLocation"
AddSubGroup = "senaite.core: Add SubGroup"
AddSupplier = "senaite.core: Add Supplier"
AddSupplyOrder = "senaite.core: Add SupplyOrder"
AddWorksheetTemplate = "senaite.core: Add WorksheetTemplate"

# Transition permissions
# ======================
TransitionDeactivate = "senaite.core: Transition: Deactivate"
TransitionActivate = "senaite.core: Transition: Activate"
TransitionCancel = "senaite.core: Transition: Cancel"
TransitionReinstate = "senaite.core: Transition: Reinstate"
TransitionClose = "senaite.core: Transition: Close"
TransitionReopen = "senaite.core: Transition: Reopen"

# Transition permissions (Analysis and alike)
TransitionRetest = "senaite.core: Transition: Retest"
TransitionRetract = "senaite.core: Transition: Retract"
TransitionVerify = "senaite.core: Transition: Verify"
TransitionAssignAnalysis = "senaite.core: Transition: Assign Analysis"
TransitionUnassignAnalysis = "senaite.core: Transition: Unassign Analysis"

# Transition permissions (Analysis Request)
TransitionCancelAnalysisRequest = "senaite.core: Transition: Cancel Analysis Request"
TransitionDetachSamplePartition = "senaite.core: Transition: Detach Sample Partition"
TransitionReinstateAnalysisRequest = "senaite.core: Transition: Reinstate Analysis Request"
TransitionInvalidate = "senaite.core: Transition Invalidate"
TransitionPreserveSample = "senaite.core: Transition: Preserve Sample"
TransitionPublishResults = "senaite.core: Transition: Publish Results"
TransitionReceiveSample = "senaite.core: Transition: Receive Sample"
TransitionRejectSample = "senaite.core: Transition: Reject Sample"
TransitionSampleSample = "senaite.core: Transition: Sample Sample"
TransitionScheduleSampling = "senaite.core: Transition: Schedule Sampling"

# Transition permissions (Supply Order)
TransitionDispatchOrder = "senaite.core: Transition: Dispatch Order"

# Transition permissions (Worksheet)
TransitionRejectWorksheet = "senaite.core: Transition: Reject Worksheet"
TransitionRemoveWorksheet = "senaite.core: Transition: Remove Worksheet"


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
FieldEditInternalUse = "senaite.core: Field: Edit Internal Use"
FieldEditInvoiceExclude = "senaite.core: Field: Edit Invoice Exclude"
FieldEditMemberDiscount = "senaite.core: Field: Edit Member Discount"
FieldEditPreservation = "senaite.core: Field: Edit Preservation"
FieldEditPreserver = "senaite.core: Field: Edit Preserver"
FieldEditPriority = "senaite.core: Field: Edit Priority"
FieldEditProfiles = "senaite.core: Field: Edit Profiles"
FieldEditPublicationSpecifications = "senaite.core: Field: Edit Publication Specification"
FieldEditRejectionReasons = "senaite.core: Field: Edit Rejection Reasons"
FieldEditRemarks = "senaite.core: Field: Edit Remarks"
FieldEditResultsInterpretation = "senaite.core: Field: Edit Results Interpretation"
FieldEditSampleCondition = "senaite.core: Field: Edit Sample Condition"
FieldEditSamplePoint = "senaite.core: Field: Edit Sample Point"
FieldEditSampleType = "senaite.core: Field: Edit Sample Type"
FieldEditSampler = "senaite.core: Field: Edit Sampler"
FieldEditSamplingDate = "senaite.core: Field: Edit Sampling Date"
FieldEditSamplingDeviation = "senaite.core: Field: Edit Sampling Deviation"
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
AccessJSONAPI = "senaite.core: Access JSON API"
EditFieldResults = "senaite.core: Edit Field Results"
EditResults = "senaite.core: Edit Results"
EditWorksheet = "senaite.core: Edit Worksheet"
ManageBika = "senaite.core: Manage Bika"
ManageAnalysisRequests = "senaite.core: Manage Analysis Requests"
ManageInvoices = "senaite.core: Manage Invoices"
ManageLoginDetails = "senaite.core: Manage Login Details"
ManageReference = "senaite.core: Manage Reference"
ManageWorksheets = "senaite.core: Manage Worksheets"
ViewResults = "senaite.core: View Results"


# View/Action permissions
# =======================
# TODO Security Review these "view/action" permissions
ImportInstrumentResults = "senaite.core: Import Instrument Results"
ViewRetractedAnalyses = "senaite.core: View Retracted Analyses"
ViewLogTab = "senaite.core: View Log Tab"
