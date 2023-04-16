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
from senaite.core.permissions import *

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
