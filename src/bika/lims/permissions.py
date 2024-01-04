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
# Copyright 2018-2024 by it's authors.
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

from senaite.core.permissions import *
from zope import deprecation

deprecation.deprecated("AccessJSONAPI", "Moved to senaite.core.permissions")
deprecation.deprecated("AddARTemplate", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysis", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysisCategory", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysisProfile", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysisService", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAnalysisSpec", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAttachment", "Moved to senaite.core.permissions")
deprecation.deprecated("AddAttachmentType", "Moved to senaite.core.permissions")
deprecation.deprecated("AddBatch", "Moved to senaite.core.permissions")
deprecation.deprecated("AddBatchLabel", "Moved to senaite.core.permissions")
deprecation.deprecated("AddCalculation", "Moved to senaite.core.permissions")
deprecation.deprecated("AddClient", "Moved to senaite.core.permissions")
deprecation.deprecated("AddContainer", "Moved to senaite.core.permissions")
deprecation.deprecated("AddContainerType", "Moved to senaite.core.permissions")
deprecation.deprecated("AddDepartment", "Moved to senaite.core.permissions")
deprecation.deprecated("AddIdentifierType", "Moved to senaite.core.permissions")
deprecation.deprecated("AddInstrument", "Moved to senaite.core.permissions")
deprecation.deprecated("AddInstrumentLocation", "Moved to senaite.core.permissions")
deprecation.deprecated("AddInstrumentType", "Moved to senaite.core.permissions")
deprecation.deprecated("AddInvoice", "Moved to senaite.core.permissions")
deprecation.deprecated("AddLabContact", "Moved to senaite.core.permissions")
deprecation.deprecated("AddLabProduct", "Moved to senaite.core.permissions")
deprecation.deprecated("AddManufacturer", "Moved to senaite.core.permissions")
deprecation.deprecated("AddMethod", "Moved to senaite.core.permissions")
deprecation.deprecated("AddMultifile", "Moved to senaite.core.permissions")
deprecation.deprecated("AddPreservation", "Moved to senaite.core.permissions")
deprecation.deprecated("AddPricelist", "Moved to senaite.core.permissions")
deprecation.deprecated("AddReferenceDefinition", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSampleCondition", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSampleMatrix", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSamplePoint", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSampleType", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSamplingDeviation", "Moved to senaite.core.permissions")
deprecation.deprecated("AddStorageLocation", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSubGroup", "Moved to senaite.core.permissions")
deprecation.deprecated("AddSupplier", "Moved to senaite.core.permissions")
deprecation.deprecated("EditFieldResults", "Moved to senaite.core.permissions")
deprecation.deprecated("EditResults", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditAnalysisConditions", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditAnalysisHidden", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditAnalysisRemarks", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditAnalysisResult", "Moved to senaite.core.permissions")
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
deprecation.deprecated("FieldEditSampleType", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSampler", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSamplingDate", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSamplingDeviation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditScheduledSampler", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditSpecification", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditStorageLocation", "Moved to senaite.core.permissions")
deprecation.deprecated("FieldEditTemplate", "Moved to senaite.core.permissions")
deprecation.deprecated("ImportInstrumentResults", "Moved to senaite.core.permissions")
deprecation.deprecated("ManageAnalysisRequests", "Moved to senaite.core.permissions")
deprecation.deprecated("ManageBika", "Moved to senaite.core.permissions")
deprecation.deprecated("ManageInvoices", "Moved to senaite.core.permissions")
deprecation.deprecated("ManageLoginDetails", "Moved to senaite.core.permissions")
deprecation.deprecated("ManageReference", "Moved to senaite.core.permissions")
deprecation.deprecated("SampleAddAttachment", "Moved to senaite.core.permissions")
deprecation.deprecated("SampleDeleteAttachment", "Moved to senaite.core.permissions")
deprecation.deprecated("SampleEditAttachment", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionActivate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionAssignAnalysis", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionCancel", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionCancelAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionClose", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionCreatePartitions", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionDeactivate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionDetachSamplePartition", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionDispatchSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionInvalidate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionMultiResults", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionPreserveSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionPublishResults", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReceiveSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReinstate", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReinstateAnalysisRequest", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRejectSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionReopen", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRestoreSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRetest", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionRetract", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionSampleSample", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionScheduleSampling", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionUnassignAnalysis", "Moved to senaite.core.permissions")
deprecation.deprecated("TransitionVerify", "Moved to senaite.core.permissions")
deprecation.deprecated("ViewLogTab", "Moved to senaite.core.permissions")
deprecation.deprecated("ViewResults", "Moved to senaite.core.permissions")
deprecation.deprecated("ViewRetractedAnalyses", "Moved to senaite.core.permissions")
