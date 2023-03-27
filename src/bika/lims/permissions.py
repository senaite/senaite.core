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
# Copyright 2018-2021 by it's authors.
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

# flake8:noqa

from zope import deprecation

from senaite.core.permissions import AddAnalysisRequest
from senaite.core.permissions import FieldEditBatch
from senaite.core.permissions import FieldEditClient
from senaite.core.permissions import FieldEditClientOrderNumber
from senaite.core.permissions import FieldEditClientReference
from senaite.core.permissions import FieldEditClientSampleID
from senaite.core.permissions import FieldEditComposite
from senaite.core.permissions import FieldEditContact
from senaite.core.permissions import FieldEditContainer
from senaite.core.permissions import FieldEditDatePreserved
from senaite.core.permissions import FieldEditDateReceived
from senaite.core.permissions import FieldEditDateSampled
from senaite.core.permissions import FieldEditEnvironmentalConditions
from senaite.core.permissions import FieldEditInternalUse
from senaite.core.permissions import FieldEditInvoiceExclude
from senaite.core.permissions import FieldEditMemberDiscount
from senaite.core.permissions import FieldEditPreservation
from senaite.core.permissions import FieldEditPreserver
from senaite.core.permissions import FieldEditPriority
from senaite.core.permissions import FieldEditProfiles
from senaite.core.permissions import FieldEditPublicationSpecifications
from senaite.core.permissions import FieldEditRejectionReasons
from senaite.core.permissions import FieldEditRemarks
from senaite.core.permissions import FieldEditResultsInterpretation
from senaite.core.permissions import FieldEditSampleCondition
from senaite.core.permissions import FieldEditSamplePoint
from senaite.core.permissions import FieldEditSampler
from senaite.core.permissions import FieldEditSampleType
from senaite.core.permissions import FieldEditSamplingDate
from senaite.core.permissions import FieldEditSamplingDeviation
from senaite.core.permissions import FieldEditScheduledSampler
from senaite.core.permissions import FieldEditSpecification
from senaite.core.permissions import FieldEditStorageLocation
from senaite.core.permissions import FieldEditTemplate
from senaite.core.permissions import TransitionCancelAnalysisRequest
from senaite.core.permissions import TransitionCreatePartitions
from senaite.core.permissions import TransitionDetachSamplePartition
from senaite.core.permissions import TransitionDispatchSample
from senaite.core.permissions import TransitionInvalidate
from senaite.core.permissions import TransitionMultiResults
from senaite.core.permissions import TransitionPreserveSample
from senaite.core.permissions import TransitionPublishResults
from senaite.core.permissions import TransitionReceiveSample
from senaite.core.permissions import TransitionReinstateAnalysisRequest
from senaite.core.permissions import TransitionRejectSample
from senaite.core.permissions import TransitionRestoreSample
from senaite.core.permissions import TransitionSampleSample
from senaite.core.permissions import TransitionScheduleSampling

deprecation.deprecated("AddAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditBatch", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditClient", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditClientOrderNumber", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditClientReference", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditClientSampleID", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditComposite", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditContact", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditContainer", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditDatePreserved", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditDateReceived", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditDateSampled", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditEnvironmentalConditions", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditInternalUse", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditInvoiceExclude", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditMemberDiscount", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditPreservation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditPreserver", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditPriority", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditProfiles", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditPublicationSpecifications","Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditRejectionReasons", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditRemarks", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditResultsInterpretation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSampleCondition", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSamplePoint", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSampler", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSampleType", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSamplingDate", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSamplingDeviation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditScheduledSampler", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSpecification", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditStorageLocation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditTemplate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionCancelAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionCreatePartitions", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionDetachSamplePartition", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionDispatchSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionInvalidate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionMultiResults", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionPreserveSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionPublishResults", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReceiveSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReinstateAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRejectSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRestoreSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionSampleSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionScheduleSampling", "Moved to senaite.core.permissions")


# Add Permissions
# ===============
# For "Add" permissions, keep the name of the variable as "Add<portal_type>".
# When the module gets initialized (bika.lims.__init__), the function initialize
# will look through these Add permissions attributes when registering types and
# will automatically associate them with their types.
AddAnalysis = "senaite.core: Add Analysis"
AddAnalysisCategory = "senaite.core: Add AnalysisCategory"
AddAnalysisProfile = "senaite.core: Add AnalysisProfile"
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
AddSampleCondition = "senaite.core: Add SampleCondition"
AddSampleMatrix = "senaite.core: Add SampleMatrix"
AddSamplePoint = "senaite.core: Add SamplePoint"
AddSampleType = "senaite.core: Add SampleType"
AddSamplingDeviation = "senaite.core: Add SamplingDeviation"
AddStorageLocation = "senaite.core: Add StorageLocation"
AddSubGroup = "senaite.core: Add SubGroup"
AddSupplier = "senaite.core: Add Supplier"

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


# Type-specific permissions
# =========================
# Makes "Add Attachment" section from sample context visible
SampleAddAttachment = "senaite.core: Sample: Add Attachment"
# Allows to edit "Type", "Keywords" and "Report Option" from attachments, even
# for those attachment assigned to an analysis
SampleEditAttachment = "senaite.core: Sample: Edit Attachment"
# Displays the "Delete" checkbox
SampleDeleteAttachment = "senaite.core: Sample: Delete Attachment"


# Field Permissions
# =================

# Field permissions (Analysis and alike)
FieldEditAnalysisHidden = "senaite.core: Field: Edit Analysis Hidden"
# Allows the edition of the result from an Analysis, as well as the assignment,
# edition or removal of attachment.
FieldEditAnalysisResult = "senaite.core: Field: Edit Analysis Result"
FieldEditAnalysisRemarks = "senaite.core: Field: Edit Analysis Remarks"
FieldEditAnalysisConditions = "senaite.core: Field: Edit Analysis Conditions"


# Behavioral permissions
# ======================
# TODO Security Review these "behavioral" permissions
AccessJSONAPI = "senaite.core: Access JSON API"
EditFieldResults = "senaite.core: Edit Field Results"
EditResults = "senaite.core: Edit Results"
ManageBika = "senaite.core: Manage Bika"
ManageAnalysisRequests = "senaite.core: Manage Analysis Requests"
ManageInvoices = "senaite.core: Manage Invoices"
ManageLoginDetails = "senaite.core: Manage Login Details"
ManageReference = "senaite.core: Manage Reference"
ViewResults = "senaite.core: View Results"


# View/Action permissions
# =======================
# TODO Security Review these "view/action" permissions
ImportInstrumentResults = "senaite.core: Import Instrument Results"
ViewRetractedAnalyses = "senaite.core: View Retracted Analyses"
ViewLogTab = "senaite.core: View Log Tab"
