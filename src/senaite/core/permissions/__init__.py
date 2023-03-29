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

# Sample permissions
from .sample.permissions import AddAnalysisRequest
from .sample.permissions import FieldEditBatch
from .sample.permissions import FieldEditClient
from .sample.permissions import FieldEditClientOrderNumber
from .sample.permissions import FieldEditClientReference
from .sample.permissions import FieldEditClientSampleID
from .sample.permissions import FieldEditComposite
from .sample.permissions import FieldEditContact
from .sample.permissions import FieldEditContainer
from .sample.permissions import FieldEditDatePreserved
from .sample.permissions import FieldEditDateReceived
from .sample.permissions import FieldEditDateSampled
from .sample.permissions import FieldEditEnvironmentalConditions
from .sample.permissions import FieldEditInternalUse
from .sample.permissions import FieldEditInvoiceExclude
from .sample.permissions import FieldEditMemberDiscount
from .sample.permissions import FieldEditPreservation
from .sample.permissions import FieldEditPreserver
from .sample.permissions import FieldEditPriority
from .sample.permissions import FieldEditProfiles
from .sample.permissions import FieldEditPublicationSpecifications
from .sample.permissions import FieldEditRejectionReasons
from .sample.permissions import FieldEditRemarks
from .sample.permissions import FieldEditResultsInterpretation
from .sample.permissions import FieldEditSampleCondition
from .sample.permissions import FieldEditSamplePoint
from .sample.permissions import FieldEditSampler
from .sample.permissions import FieldEditSampleType
from .sample.permissions import FieldEditSamplingDate
from .sample.permissions import FieldEditSamplingDeviation
from .sample.permissions import FieldEditScheduledSampler
from .sample.permissions import FieldEditSpecification
from .sample.permissions import FieldEditStorageLocation
from .sample.permissions import FieldEditTemplate
from .sample.permissions import TransitionCancelAnalysisRequest
from .sample.permissions import TransitionCreatePartitions
from .sample.permissions import TransitionDetachSamplePartition
from .sample.permissions import TransitionDispatchSample
from .sample.permissions import TransitionInvalidate
from .sample.permissions import TransitionMultiResults
from .sample.permissions import TransitionPreserveSample
from .sample.permissions import TransitionPublishResults
from .sample.permissions import TransitionReceiveSample
from .sample.permissions import TransitionReinstateAnalysisRequest
from .sample.permissions import TransitionRejectSample
from .sample.permissions import TransitionRestoreSample
from .sample.permissions import TransitionSampleSample
from .sample.permissions import TransitionScheduleSampling
# Worksheet permissions
from .worksheet.permissions import AddWorksheet
from .worksheet.permissions import AddWorksheetTemplate
from .worksheet.permissions import EditWorksheet
from .worksheet.permissions import ManageWorksheets
from .worksheet.permissions import TransitionRejectWorksheet
from .worksheet.permissions import TransitionRemoveWorksheet
from .worksheet.permissions import WorksheetAddAttachment
