# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from types import DictType

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.interfaces import IATWidgetVisibility
from bika.lims.interfaces import IBatch, IClient
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
        """
        raise NotImplementedError("Must be implemented by subclass")


class ClientFieldWidgetVisibility(object):
    """The Client field is editable by default in ar_add.  This adapter
    will force the Client field to be hidden when it should not be set
    by the user.
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 10

    def __call__(self, context, mode, field, default):
        state = default if default else 'hidden'
        fieldName = field.getName()
        if fieldName != 'Client':
            return state
        parent = self.context.aq_parent

        if IBatch.providedBy(parent):
            if parent.getClient():
                return 'hidden'

        if IClient.providedBy(parent):
            return 'hidden'

        return state

# TODO Is this necessary - Is still possible to add ARs inside a Batch folder?
class BatchARAdd_BatchFieldWidgetVisibility(object):
    """This will force the 'Batch' field to 'hidden' in ar_add when the parent
    context is a Batch.
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 10

    def __call__(self, context, mode, field, default):
        state = default if default else 'visible'
        fieldName = field.getName()
        if fieldName == 'Batch' and context.aq_parent.portal_type == 'Batch':
            return 'hidden'
        return state



class PreservationFieldsVisibility(SenaiteATWidgetVisibility):
    """Display/Hide fields related with Preservation Workflow
    """
    def __init__(self, context):
        super(PreservationFieldsVisibility, self).__init__(
            context=context, sort=10,
            field_names=["DatePreserved", "Preservation", "Preserver"])

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
        sw_enabled = False
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
            context=context, sort=-1, field_names=[field_names,]
        )

    def isVisible(self, field, mode="view", default="visible"):
        return "invisible"


class AccountancyFieldsVisibility(SenaiteATWidgetVisibility):
    """Display/Hide fields related with Accountancy (Discount, prices, invoice)
    """
    def __init__(self, context):
        super(AccountancyFieldsVisibility, self).__init__(
            context=context, sort=3,
            field_names=["BulkDiscount", "MemberDiscountApplies",
                         "InvoiceExclude", "MemberDiscount"]
        )

    def isVisible(self, field, mode="view", default="visible"):
        if not self.context.bika_setup.getShowPrices():
            return "invisible"
        return default


class DateReceivedFieldVisibility(SenaiteATWidgetVisibility):
    """DateReceived is editable in sample context, only if all related analyses
    are not yet submitted.
    """
    def __init__(self, context):
        super(DateReceivedFieldVisibility, self).__init__(
            context=context, sort=3, field_names=["DateReceived"])

    def isVisible(self, field, mode="view", default="visible"):
        """Returns whether the field is visible in a given mode
        """
        if mode != "edit":
            return default
        if not hasattr(self.context, "isOpen"):
            logger.warn("Object {}  does not have 'isOpen' method defined".
                        format(self.context.__class__.__name__))
            return default
        return self.context.isOpen() and "visible" or "invisible"
