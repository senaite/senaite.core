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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

# flake8:noqa

from .analysis.permissions import *
from .sample.permissions import *
from .worksheet.permissions import *

# Add Permissions
# ===============
# For "Add" permissions, keep the name of the variable as "Add<portal_type>".
# When the module gets initialized (bika.lims.__init__), the function initialize
# will look through these Add permissions attributes when registering types and
# will automatically associate them with their types.
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


# Behavioral permissions
# ======================
# TODO Security Review these "behavioral" permissions
AccessJSONAPI = "senaite.core: Access JSON API"
EditFieldResults = "senaite.core: Edit Field Results"
EditResults = "senaite.core: Edit Results"
ManageBika = "senaite.core: Manage Bika"
ManageSenaite = "senaite.core: Manage Bika"
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
