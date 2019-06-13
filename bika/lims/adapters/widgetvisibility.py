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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IATWidgetVisibility
from bika.lims.interfaces import IAnalysisRequestSecondary
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import IClient
from bika.lims.utils import getHiddenAttributesForClass
from zope.interface import implements

_marker = []


class SenaiteATWidgetVisibility(object):
    implements(IATWidgetVisibility)

    def __init__(self, context, sort=1000, field_names=None):
        self.context = context
        self.sort = sort
        self.field_names = field_names or list()

    def __call__(self, context, mode, field, default):
        state = default if default else "visible"
        if not field or field.getName() not in self.field_names:
            return state
        return self.isVisible(field, mode, default)

    def isVisible(self, field, mode="view", default="visible"):
        """Returns if the field is visible in a given mode

        Possible returned values are:
        - hidden: Field rendered as a hidden input field
        - invisible: Field not rendered at all
        - visible: Field rendered as a label or editable field depending on the
            mode. E.g. if mode is "edit" and the value returned is "visible",
            the field will be rendered as an input. If the mode is "view", the
            field will be rendered as a span.
        """
        raise NotImplementedError("Must be implemented by subclass")


class ClientFieldVisibility(SenaiteATWidgetVisibility):
    """The Client field is editable by default in ar_add.  This adapter
    will force the Client field to be hidden when it should not be set
    by the user.
    """
    def __init__(self, context):
        super(ClientFieldVisibility, self).__init__(
            context=context, sort=10, field_names=["Client"])

    def isVisible(self, field, mode="view", default="visible"):
        if mode == "add":
            parent = self.context.aq_parent
            if IClient.providedBy(parent):
                # Note we return "hidden" here instead of "invisible": we want
                # the field to be auto-filled and processed on submit
                return "hidden"
            if IBatch.providedBy(parent) and parent.getClient():
                # The Batch has a Client assigned already!
                # Note we can have Batches without a client assigned
                return "hidden"
        elif mode == "edit":
            # This is already managed by wf permission, but is **never** a good
            # idea to allow the user to change the Client from an AR (basically
            # because otherwise, we'd need to move the object from one client
            # folder to another!).
            return "invisible"
        return default


class BatchFieldVisibility(SenaiteATWidgetVisibility):
    """This will force the 'Batch' field to 'hidden' in ar_add when the parent
    context is a Batch.
    """
    def __init__(self, context):
        super(BatchFieldVisibility, self).__init__(
            context=context, sort=10, field_names=["Batch"])

    def isVisible(self, field, mode="view", default="visible"):
        if IBatch.providedBy(self.context.aq_parent):
            return "hidden"
        return default


class PreservationFieldsVisibility(SenaiteATWidgetVisibility):
    """Display/Hide fields related with Preservation Workflow
    """
    def __init__(self, context):
        super(PreservationFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["DatePreserved", "Preserver"])

    def isVisible(self, field, mode="view", default="visible"):
        if not self.context.bika_setup.getSamplePreservationEnabled():
            return "invisible"
        return default


class ScheduledSamplingFieldsVisibility(SenaiteATWidgetVisibility):
    """Display/Hide fields related with ScheduledSampling Workflow
    """
    def __init__(self, context):
        super(ScheduledSamplingFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["ScheduledSamplingSampler", "SamplingRound"])

    def isVisible(self, field, mode="view", default="visible"):
        if not self.context.bika_setup.getScheduleSamplingEnabled():
            return "invisible"
        return default


class SamplingFieldsVisibility(SenaiteATWidgetVisibility):
    """
    This will handle Handling 'DateSampled' and 'SamplingDate' fields'
    visibilities based on Sampling Workflow (SWF)status. We must check the
    attribute saved on the sample, not the bika_setup value though. See the
    internal comments how it enables/disables WidgetVisibility depending on SWF.
    """
    def __init__(self, context):
        super(SamplingFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["Sampler", "DateSampled", "SamplingDate"])

    def isVisible(self, field, mode="view", default="visible"):
        # If object has been already created, get SWF statues from it.
        swf_enabled = False
        if hasattr(self.context, 'getSamplingWorkflowEnabled') and \
                self.context.getSamplingWorkflowEnabled() is not '':
            swf_enabled = self.context.getSamplingWorkflowEnabled()
        else:
            swf_enabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        if mode == "add":
            if field.getName() == "DateSampled":
                field.required = not swf_enabled
                return swf_enabled and "invisible" or "edit"
            elif field.getName() == "SamplingDate":
                field.required = swf_enabled
                return swf_enabled and "edit" or "invisible"
            elif field.getName() == "Sampler":
                return swf_enabled and "edit" or "invisible"

        elif not swf_enabled:
            if field.getName() != "DateSampled":
                return "invisible"

        return default


class RegistryHiddenFieldsVisibility(SenaiteATWidgetVisibility):
    """Do not display fields declared in bika.lims.hiddenattributes registry key
    """
    def __init__(self, context):
        field_names = getHiddenAttributesForClass(context.portal_type)
        super(RegistryHiddenFieldsVisibility, self).__init__(
            context=context, sort=-1, field_names=[field_names,])

    def isVisible(self, field, mode="view", default="visible"):
        return "invisible"


class AccountancyFieldsVisibility(SenaiteATWidgetVisibility):
    """Display/Hide fields related with Accountancy (Discount, prices, invoice)
    """
    def __init__(self, context):
        super(AccountancyFieldsVisibility, self).__init__(
            context=context, sort=3,
            field_names=["BulkDiscount", "MemberDiscountApplies",
                         "InvoiceExclude", "MemberDiscount"])

    def isVisible(self, field, mode="view", default="visible"):
        if not self.context.bika_setup.getShowPrices():
            return "invisible"
        return default


class DateReceivedFieldVisibility(SenaiteATWidgetVisibility):
    """DateReceived is editable in sample context, only if all related analyses
    are not yet submitted and if not a secondary sample.
    """
    def __init__(self, context):
        super(DateReceivedFieldVisibility, self).__init__(
            context=context, sort=3, field_names=["DateReceived"])

    def isVisible(self, field, mode="view", default="visible"):
        """Returns whether the field is visible in a given mode
        """
        if mode != "edit":
            return default

        # If this is a Secondary Analysis Request, this field is not editable
        if IAnalysisRequestSecondary.providedBy(self.context):
            return "invisible"

        return self.context.isOpen() and "visible" or "invisible"


class SecondaryDateSampledFieldVisibility(SenaiteATWidgetVisibility):
    """DateSampled is editable in sample unless secondary sample
    """
    def __init__(self, context):
        super(SecondaryDateSampledFieldVisibility, self).__init__(
            context=context, sort=3, field_names=["DateSampled"])

    def isVisible(self, field, mode="view", default="visible"):
        """Returns whether the field is visible in a given mode
        """
        if mode != "edit":
            return default

        # If this is a Secondary Analysis Request, this field is not editable
        if IAnalysisRequestSecondary.providedBy(self.context):
            return "invisible"
        return default


class PrimaryAnalysisRequestFieldVisibility(SenaiteATWidgetVisibility):
    """PrimarySample field is not visible unless the current Sample is a
    Secondary Sample. And even in such case, the field cannot be edited
    """
    def __init__(self, context):
        super(PrimaryAnalysisRequestFieldVisibility, self).__init__(
            context=context, sort=3, field_names=["PrimaryAnalysisRequest"])

    def isVisible(self, field, mode="view", default="visible"):
        """Returns whether the field is visible in a given mode
        """
        if mode == "add":
            return default

        if not IAnalysisRequestSecondary.providedBy(self.context):
            # If not a secondary Analysis Request, don't render the field
            return "hidden"

        # No mather if the mode is edit or view, display it always as readonly
        if mode == "edit":
            return "invisible"

        return default


class InternalUseFieldVisibility(SenaiteATWidgetVisibility):
    """InternalUse field must only be visible to lab personnel
    """
    def __init__(self, context):
        super(InternalUseFieldVisibility, self).__init__(
            context=context, sort=3, field_names=["InternalUse"])

    def isVisible(self, field, mode="view", default="visible"):
        """Returns whether the field is visible in a given mode
        """
        return api.get_current_client() and "invisible" or default
