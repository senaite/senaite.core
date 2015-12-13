import plone, json

from bika.lims.permissions import *

from Acquisition import aq_parent, aq_inner
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction
from bika.lims.subscribers import doActionFor
from bika.lims.utils import isActive
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName

class ClientWorkflowAction(AnalysisRequestWorkflowAction):
    """ This function is called to do the worflow actions
        that apply to objects transitioned directly from Client views

        The main lab 'analysisrequests' and 'samples' views also have
        workflow_action urls bound to this handler.

        The parent AnalysisRequestWorkflowAction handles
        AR and Sample context workflow actions (affecting parts/analyses)

    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        self.context = aq_inner(self.context)
        workflow = getToolByName(self.context, 'portal_workflow')
        bc = getToolByName(self.context, 'bika_catalog')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        translate = self.context.translate
        checkPermission = self.context.portal_membership.checkPermission

        # use came_from to decide which UI action was clicked.
        # "workflow_action" is the action name specified in the
        # portal_workflow transition url.
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            # workflow_action_button is the action name specified in
            # the bika_listing_view table buttons.
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                           self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return

        if action == "sample":
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            transitioned = {'to_be_preserved':[], 'sample_due':[]}
            for obj_uid, obj in objects.items():
                if obj.portal_type == "AnalysisRequest":
                    ar = obj
                    sample = obj.getSample()
                else:
                    sample = obj
                    ar = sample.aq_parent
                # can't transition inactive items
                if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive':
                    continue

                # grab this object's Sampler and DateSampled from the form
                # (if the columns are available and edit controls exist)
                if 'getSampler' in form and 'getDateSampled' in form:
                    try:
                        Sampler = form['getSampler'][0][obj_uid].strip()
                        DateSampled = form['getDateSampled'][0][obj_uid].strip()
                    except KeyError:
                        continue
                    Sampler = Sampler and Sampler or ''
                    DateSampled = DateSampled and DateTime(DateSampled) or ''
                else:
                    continue

                # write them to the sample
                sample.setSampler(Sampler)
                sample.setDateSampled(DateSampled)
                sample.reindexObject()
                ars = sample.getAnalysisRequests()
                # Analyses and AnalysisRequets have calculated fields
                # that are indexed; re-index all these objects.
                for ar in ars:
                    ar.reindexObject()
                    analyses = sample.getAnalyses({'review_state':'to_be_sampled'})
                    for a in analyses:
                        a.getObject().reindexObject()

                # transition the object if both values are present
                if Sampler and DateSampled:
                    workflow.doActionFor(sample, action)
                    new_state = workflow.getInfoFor(sample, 'review_state')
                    doActionFor(ar, action)
                    transitioned[new_state].append(sample.Title())

            message = None
            for state in transitioned:
                tlist = transitioned[state]
                if len(tlist) > 1:
                    if state == 'to_be_preserved':
                        message = _('${items} are waiting for preservation.',
                                    mapping = {'items': ', '.join(tlist)})
                    else:
                        message = _('${items} are waiting to be received.',
                                    mapping = {'items': ', '.join(tlist)})
                    self.context.plone_utils.addPortalMessage(message, 'info')
                elif len(tlist) == 1:
                    if state == 'to_be_preserved':
                        message = _('${item} is waiting for preservation.',
                                    mapping = {'item': ', '.join(tlist)})
                    else:
                        message = _('${item} is waiting to be received.',
                                    mapping = {'item': ', '.join(tlist)})
                    self.context.plone_utils.addPortalMessage(message, 'info')
            if not message:
                message = _('No changes made.')
                self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        elif action == "preserve":
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            transitioned = {}
            not_transitioned = []
            Preserver = str()
            DatePreserved = str()
            for obj_uid, obj in objects.items():
                if obj.portal_type == "AnalysisRequest":
                    ar = obj
                    sample = obj.getSample()
                else:
                    sample = obj
                    ar = sample.aq_parent
                # can't transition inactive items
                if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive':
                    continue
                if not checkPermission(PreserveSample, sample):
                    continue

                # grab this object's Preserver and DatePreserved from the form
                # (if the columns are available and edit controls exist)
                if 'getPreserver' in form and 'getDatePreserved' in form:
                    try:
                        Preserver = form['getPreserver'][0][obj_uid].strip()
                        DatePreserved = form['getDatePreserved'][0][obj_uid].strip()
                    except KeyError:
                        continue
                    Preserver = Preserver and Preserver or ''
                    DatePreserved = DatePreserved and DateTime(DatePreserved) or ''
                else:
                    continue

                for sp in sample.objectValues("SamplePartition"):
                    if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved':
                        sp.setDatePreserved(DatePreserved)
                        sp.setPreserver(Preserver)
                for sp in sample.objectValues("SamplePartition"):
                    if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved':
                        if Preserver and DatePreserved:
                            doActionFor(sp, action)
                            transitioned[sp.aq_parent.Title()] = sp.Title()
                        else:
                            not_transitioned.append(sp)

            if len(transitioned.keys()) > 1:
                message = _('${items}: partitions are waiting to be received.',
                        mapping = {'items': ', '.join(transitioned.keys())})
            else:
                message = _('${item}: ${part} is waiting to be received.',
                        mapping = {'item': ', '.join(transitioned.keys()),
                                   'part': ', '.join(transitioned.values()),})
            self.context.plone_utils.addPortalMessage(message, 'info')

            # And then the sample itself
            if Preserver and DatePreserved and not not_transitioned:
                doActionFor(sample, action)
                #message = _('${item} is waiting to be received.',
                #            mapping = {'item': sample.Title()})
                #message = t(message)
                #self.context.plone_utils.addPortalMessage(message, 'info')

            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        elif action in ('prepublish', 'publish', 'republish'):
            # We pass a list of AR objects to Publish.
            # it returns a list of AR IDs which were actually published.
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            its = []
            for uid, obj in objects.items():
                if isActive(obj):
                    its.append(uid);
            its = ",".join(its)
            q = "/publish?items=" + its
            dest = self.portal_url+"/analysisrequests" + q
            self.request.response.redirect(dest)

        else:
            AnalysisRequestWorkflowAction.__call__(self)
