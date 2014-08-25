# -*- coding:utf-8 -*-
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.utils import getHiddenAttributesForClass
from types import DictType
from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import IATWidgetVisibility
from zope.interface import implements

_marker = []


class WorkflowAwareWidgetVisibility(object):
    """This adapter allows the schema definition to have different widget visibility
    settings for different workflow states in the primary review_state workflow.

    With this it is possible to write:

        StringField(
            'fieldName',
            widget=StringWidget(
                label=_('field Name'),
                visible = {
                    'edit': 'visible',  # regular AT uses these and they override
                    'view': 'visible',  # everything, without 'edit' you cannot edit
                    'wf_state':    {'edit': 'invisible', 'view': 'visible'  },
                    'other_state': {'edit': 'visible',   'view': 'invisible'},
            }

    The rules about defaults, "hidden", "visible" and "invisible" are the same
    as those from the default Products.Archetypes.Widget.TypesWidget#isVisible

    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 500

    def __call__(self, context, mode, field, default):
        """
        """
        state = default if default else 'visible'
        workflow = getToolByName(self.context, 'portal_workflow')
        try:
            review_state = workflow.getInfoFor(self.context, 'review_state')
        except WorkflowException:
            return state
        vis_dic = field.widget.visible
        if type(vis_dic) is not DictType or review_state not in vis_dic:
            return state
        inner_vis_dic = vis_dic.get(review_state, state)
        if inner_vis_dic is _marker:
            state = state
        if type(inner_vis_dic) is DictType:
            state = inner_vis_dic.get(mode, state)
            state = state
        elif not inner_vis_dic:
            state = 'invisible'
        elif inner_vis_dic < 0:
            state = 'hidden'

        return state


class SamplingWorkflowWidgetVisibility(object):
    """This will force the 'Sampler' and 'DateSampled' widget default to 'visible'.
    We must check the attribute saved on the sample, not the bika_setup value.
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 500

    def __call__(self, context, mode, field, default):
        sw_fields = ['Sampler', 'DateSampled']
        state = default if default else 'invisible'
        fieldName = field.getName()
        if fieldName in sw_fields \
                and hasattr(self.context, 'getSamplingWorkflowEnabled') \
                and self.context.getSamplingWorkflowEnabled():
            if mode == 'header_table':
                state = 'prominent'
            elif mode == 'view':
                state = 'visible'
        return state


class OptionalFieldsWidgetVisibility(object):
    """Remove 'hidden attributes' (fields in registry bika.lims.hiddenattributes).
       fieldName = field.getName()
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 5

    def __call__(self, context, mode, field, default):
        state = default if default else 'visible'
        hiddenattributes = getHiddenAttributesForClass(context.portal_type)
        if field.getName() in hiddenattributes:
            state = "hidden"
        return state
