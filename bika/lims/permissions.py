# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore import permissions
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFEditions.Permissions import ApplyVersionControl
from Products.CMFEditions.Permissions import SaveNewVersion

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

# SENAITE CORE Permissions
# ========================

# Generic Transition permissions
# ----------------------
TransitionActivate="senaite.core: Transition: Activate"
TransitionDeactivate="senaite.core: Transition: Deactivate"
TransitionReinstate="senaite.core: Transition: Reinstate"
TransitionCancel="senaite.core: Transition: Cancel"



# AR Permissions
# --------------

# Field Permissions
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

# Transition Permissions
TransitionInvalidate = "senaite.core: Transition Invalidate"
TransitionPreserveSample = "senaite.core: Transition: Preserve Sample"
TransitionPublishResults = "senaite.core: Transition: Publish Results"
TransitionReceiveSample = "senaite.core: Transition: Receive Sample"
TransitionRejectSample = "senaite.core: Transition: Reject Sample"
TransitionRetract = "senaite.core: Transition: Retract"
TransitionSampleSample = "senaite.core: Transition: Sample Sample"
TransitionScheduleSampling = "senaite.core: Transition: Schedule Sampling"


# Analysis Permissions
# --------------
# Field Permissions
FieldEditAnalysisHidden = "senaite.core: Field: Edit Analysis Hidden"
FieldEditAnalysisResult = "senaite.core: Field: Edit Analysis Result"
FieldEditAnalysisRemarks = "senaite.core: Field: Edit Analysis Remarks"

# Transition Permissions
TransitionVerify = "senaite.core: Transition: Verify"


# Add Permissions:
# ----------------
AddAnalysis = 'senaite.core: Add Analysis'
AddAnalysisProfile = 'senaite.core: Add AnalysisProfile'
AddAnalysisRequest = 'senaite.core: Add Analysis Request'
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
AddSample = 'senaite.core: Add Sample'
AddSampleMatrix = 'senaite.core: Add SampleMatrix'
AddSamplePoint = 'senaite.core: Add SamplePoint'
AddSamplingDeviation = 'senaite.core: Add SamplingDeviation'
AddSamplingRound = 'senaite.core: Add SamplingRound'
AddSRTemplate = 'senaite.core: Add SRTemplate'
AddSubGroup = 'senaite.core: Add Sub-group'

# Default Archetypes Add Permission
ADD_CONTENT_PERMISSION = permissions.AddPortalContent

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'ARAnalysisSpec': AddAnalysisSpec, 'AnalysisProfile': AddAnalysisProfile,
    'Analysis': AddAnalysis, 'AnalysisRequest': AddAnalysisRequest,
    'Attachment': AddAttachment, 'Batch': AddBatch, 'Client': AddClient,
    'Invoice': AddInvoice, 'Method': AddMethod, 'Multifile': AddMultifile,
    'SupplyOrder': AddSupplyOrder,
    'SampleMatrix': AddSampleMatrix,
    'SamplingDeviation': AddSamplingDeviation,
    'SamplingRound': AddSamplingRound, 'SubGroup': AddSubGroup, }


# Very Old permissions:
# ---------------------
ManageBika = 'BIKA: Manage Bika'
DispatchOrder = 'BIKA: Dispatch Order'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageReference = 'BIKA: Manage Reference'


# this is for creating and transitioning worksheets
ManageWorksheets = 'BIKA: Manage Worksheets'
# this is for adding/editing/exporting analyses on worksheets
EditWorksheet = 'BIKA: Edit Worksheet'
RejectWorksheet = 'BIKA: Reject Worksheet'

ImportInstrumentResults = "BIKA: Import Instrument Results"

AccessJSONAPI = 'BIKA: Access JSON API'

# New or changed permissions:
# ---------------------------
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

ViewLogTab = 'BIKA: View Log Tab'


# Batch-specific permissions
# ----------------------------------------------
CloseBatch = 'BIKA: Close Batch'
ReopenBatch = 'BIKA: Reopen Batch'

# Sampling Round permissions
# --------------------------
CloseSamplingRound = 'BIKA: Close SamplingRound'
ReopenSamplingRound = 'BIKA: Reopen SamplingRound'

# Manage AR Imports
# ----------------------------------------------
ManageARImport = 'BIKA: Manage ARImport'


def setup_permissions(portal):
    """
    This function sets permissions for some general objects (or
    folders) during Bika installation process.
    Those objects are:
    the general Portal, bika_setup, laboratory, clients folder, contacts,
    batches, worksheets folder, etc

    :param portal: the site object
    :return: None
    """
    # @formatter:off
    # Root permissions
    mp = portal.manage_permission

    mp(AccessJSONAPI, ['Manager', 'LabManager'], 0)

    mp(AddAnalysis, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler'], 1)
    mp(AddAnalysisProfile, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddAnalysisRequest, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddAnalysisSpec, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddARTemplate, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddAttachment, ['Manager', 'LabManager', 'Owner' 'Analyst', 'LabClerk', 'Sampler', 'Client'], 0)
    mp(AddBatch, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddClient, ['Manager', 'Owner', 'LabManager'], 1)
    mp(AddInvoice, ['Manager', 'LabManager'], 1)
    mp(AddMethod, ['Manager', 'LabManager'], 1)
    mp(AddMultifile, ['Manager', 'LabManager', 'LabClerk'], 1)
    mp(AddPricelist, ['Manager', 'Owner', 'LabManager'], 1)
    mp(AddSample, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler'], 1)
    mp(AddSampleMatrix, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSamplePoint, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSamplingDeviation, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    mp(AddSRTemplate, ['Manager', 'Owner', 'LabManager'], 0)
    mp(AddSubGroup, ['Manager', 'LabManager', 'LabClerk'], 0)

    mp(permissions.AddPortalContent, ['Manager', 'Owner', 'LabManager'], 1)
    mp(permissions.FTPAccess, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
    mp(permissions.ManageUsers, ['Manager', 'LabManager', ], 1)

    mp(ApplyVersionControl, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(SaveNewVersion, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(AccessPreviousVersions, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)

    mp(DispatchOrder, ['Manager', 'LabManager', 'LabClerk'], 1)
    mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector', 'SamplingCoordinator'], 1)
    mp(ManageBika, ['Manager', 'LabManager'], 1)
    mp(ManageLoginDetails, ['Manager', 'LabManager'], 1)
    mp(ManageReference, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
    mp(ManageWorksheets, ['Manager', 'LabManager'], 1)

    mp(CancelAndReinstate, ['Manager', 'LabManager'], 0)
    mp(ViewRetractedAnalyses, ['Manager', 'LabManager', 'LabClerk', 'Analyst', ], 0)
    mp(EditWorksheet, ['Manager', 'LabManager', 'Analyst'], 1)
    mp(ManageInvoices, ['Manager', 'LabManager', 'Owner'], 1)
    mp(ViewResults, ['Manager', 'LabManager', 'Analyst', 'Sampler', 'RegulatoryInspector', 'SamplingCoordinator'], 1)
    mp(EditResults, ['Manager', 'LabManager', 'Analyst'], 1)
    mp(EditFieldResults, ['Manager', 'LabManager', 'Sampler'], 1)
    mp('Access contents information', ['Authenticated'], 1)

    mp(ImportInstrumentResults, ['Manager', 'LabManager', 'Analyst'], 1)

    mp(ViewLogTab, ['Manager', 'LabManager'], 1)


    # /reports folder permissions
    mp = portal.reports.manage_permission
    mp('ATContentTypes: Add Image', ['Manager', 'Labmanager', 'LabClerk', 'Member', ], 0)
    mp('ATContentTypes: Add File', ['Manager', 'Labmanager', 'LabClerk', 'Member', ], 0)
    portal.reports.reindexObject()
