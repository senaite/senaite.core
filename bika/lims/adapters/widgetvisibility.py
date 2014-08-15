# -*- coding:utf-8 -*-
from Products.CMFCore.WorkflowCore import WorkflowException
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
        self.sort = 100

    def __call__(self, context, mode, field, default):
        """
        We must create an AR and test workflow widget visibility through all states

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD
        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)

        Simple AR creation, no obj_path parameter is required:

        >>> browser.open(portal_url+"/bika_setup/edit")
        >>> browser.follow("Analyses")
        >>> browser.getControl("SamplingWorkflowEnabled").value = True
        >>> browser.getControl('Save').click()

        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "Client=portal_type:Client|id:client-1",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "SamplingDate=2013-09-29",
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        >>> browser.open(portal_url+"/clients/client-1/AP-0001-R01")
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
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 10

    def __call__(self, context, mode, field, default):
        sw_fields = ['Sampler', 'DateSampled']
        state = default if default else 'invisible'
        fieldName = field.getName()
        if fieldName in sw_fields:
            if mode == 'header_table':
                state = 'prominent'
            elif mode == 'view':
                state = 'visible'
        return state


class BatchClientFieldWidgetVisibility(object):
    """This will force the 'Client' field to 'visible' when in Batch context
    """
    implements(IATWidgetVisibility)

    def __init__(self, context):
        self.context = context
        self.sort = 10

    def __call__(self, context, mode, field, default):
        state = default if default else 'visible'
        fieldName = field.getName()
        if fieldName == 'Client' and context.aq_parent.portal_type == 'Batch':
            return 'edit'
        return state
