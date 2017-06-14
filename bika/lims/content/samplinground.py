# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.content.schema.samplinground import ISamplingRound
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip
from plone.api import user
from plone.dexterity.content import Item
from plone.indexer import indexer
from zope.interface import implements


@indexer(ISamplingRound)
def analysisRequestTemplates(obj):
    return obj.getAnalysisRequestTemplates()


@indexer(ISamplingRound)
def samplingRoundSamplingDate(obj):
    date = obj.sampling_date
    return date.strftime("%Y-%m-%d")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class SamplingRound(Item):
    """
    A Sampling round class.
    - Sampling Rounds are fully fledged LIMS objects which adhere to 
    workflow. They are created with initial status open and when all data are 
    captured they are closed.
    Programmers: Sampling Rounds groups Samples very much like 'Batches' do 
    for ARs
    - The ARs and Samples created per Sampling Round, enter the standard Bika 
    workflow. There is one exception: LIMS-1559 Samples belonging to a 
    Sampling Round that was closed earlier can be disposed of in bulk from 
    the Sampling Round screen, and the date and 'disposer' details capture 
    there. Like other LIMS objects, Sampling Rounds can be cancelled at any 
    given time.
    Programmers: Cancelling is a secondary workflow, like that for cancelling 
    and the Round's original status is maintained, e.g. an open Round can 
    have a cancelled status as well as closed Rounds.
    """
    implements(ISamplingRound)

    @property
    def num_sample_points(self):
        ar_brains = self.getAnalysisRequests()
        sp_num = 0
        for ar_brain in ar_brains:
            ar_samplepoint = ar_brain.getObject().getSamplePoint()
            if ar_samplepoint:
                sp_num += 1
        return sp_num

    @property
    def num_containers(self):
        ar_brains = self.getAnalysisRequests()
        containers = []
        for ar_brain in ar_brains:
            containers += ar_brain.getObject().getContainers()
        return len(containers)

    def getAnalysisRequests(self):
        """Return all the Analysis Request brains linked to the Sampling Round
        """
        # I have to get the catalog in this way because I can't do it with
        # 'self'...
        pc = getToolByName(self, 'portal_catalog')
        contentFilter = {'portal_type': 'AnalysisRequest',
                         'cancellation_state': 'active',
                         'SamplingRoundUID': self.UID()}
        return pc(contentFilter)

    def getAnalysisRequestTemplates(self):
        """This functions builds a list of tuples with the object 
        AnalysisRequestTemplates' uids and names. 
        :returns: A list of tuples where the first value of the tuple is the 
        AnalysisRequestTemplate name and the second one is the 
        AnalysisRequestTemplate UID. --> [( ART.title),(ART.UID),...]
        """
        l = []
        art_uids = self.ar_templates
        # I have to get the catalog in this way because I can't do it with
        # 'self'...
        pc = getToolByName(self, 'uid_catalog')
        for art_uid in art_uids:
            art_obj = pc(UID=art_uid)
            if len(art_obj) != 0:
                l.append((art_obj[0].Title, art_uid))
        return l

    def getDepartmentInfo(self):
        """Returns a dict with the department infomration
        {'uid':'xxxx','id':'xxxx','title':'xxx','url':'xxx'}
        """
        pc = getToolByName(self, 'portal_catalog')
        contentFilter = {'portal_type': 'Department',
                         'UID': self.department}
        departmentlist = pc(contentFilter)
        departmentdict = {'uid': '', 'id': '', 'title': '', 'url': ''}
        if len(departmentlist) == 1:
            department = departmentlist[0].getObject()
            departmentdict = {
                'uid': department.id,
                'id': department.UID(),
                'title': department.title,
                'url': department.absolute_url(),
            }
        else:
            from bika.lims import logger
            error = "Error when looking for department with uid '%s'. "
            logger.exception(error, self.department)
        return departmentdict

    def getSRTemplateInfo(self):
        """Returns a dict with the SRTemplate infomration
        {'uid':'xxxx','id':'xxxx','title':'xxx','url':'xxx'}
        """
        pc = getToolByName(self, 'portal_catalog')
        contentFilter = {'portal_type': 'SRTemplate',
                         'UID': self.sr_template}
        srt = pc(contentFilter)
        srtdict = {'uid': '', 'id': '', 'title': '', 'url': ''}
        if len(srt) == 1:
            template = srt[0].getObject()
            srtdict = {
                'uid': template.id,
                'id': template.UID(),
                'title': template.title,
                'url': template.absolute_url(),
            }
        else:
            from bika.lims import logger
            error = "Error when looking for sr template with uid '%s'. "
            logger.exception(error, self.sr_template)
        return srtdict

    def getClientContact(self):
        """Returns info from the Client contact who coordinates with the lab
        """
        pc = getToolByName(self, 'portal_catalog')
        contentFilter = {'portal_type': 'Contact',
                         'id': self.client_contact}
        cnt = pc(contentFilter)
        cntdict = {'uid': '', 'id': '', 'fullname': '', 'url': ''}
        if len(cnt) == 1:
            cnt = cnt[0].getObject()
            cntdict = {
                'uid': cnt.id,
                'id': cnt.UID(),
                'fullname': cnt.getFullname(),
                'url': cnt.absolute_url(),
            }
        else:
            from bika.lims import logger
            error = "Error when looking for contact with id '%s'. "
            logger.exception(error, self.client_contact)
        return cntdict

    def getClientInChargeAtSamplingTime(self):
        """Returns info from the Client contact who is in charge at sampling 
        time 
        """
        pc = getToolByName(self, 'portal_catalog')
        contentFilter = {'portal_type': 'Contact',
                         'id': self.client_contact_in_charge_at_sampling_time}
        cnt = pc(contentFilter)
        cntdict = {'uid': '', 'id': '', 'fullname': '', 'url': ''}
        if len(cnt) == 1:
            cnt = cnt[0].getObject()
            cntdict = {
                'uid': cnt.id,
                'id': cnt.UID(),
                'fullname': cnt.getFullname(),
                'url': cnt.absolute_url(),
            }
        else:
            from bika.lims import logger
            error = "Error when looking for contact with id '%s'. "
            logger.exception(
                error, self.client_contact_in_charge_at_sampling_time)
        return cntdict

    def hasUserAddEditPermission(self):
        """Checks if the current user has privileges to access to the editing 
        view. From Jira LIMS-1549: - Creation/Edit: Lab manager, Client 
        Contact, Lab Clerk, Client Contact (for Client-specific SRTs)
        :returns: True/False
        """
        mtool = getToolByName(self, 'portal_membership')
        checkPermission = mtool.checkPermission
        # In bika_samplinground_workflow.csv there are defined the
        # ModifyPortalContent statements. There is said that client has
        # ModifyPortalContent permission enabled, so here we have to check if
        #  the client satisfy the condition wrote in the function's description
        if (checkPermission(ModifyPortalContent, self)
            or checkPermission(AddPortalContent, self)) \
                and 'Client' in user.get_current().getRoles():
            # Checking if the current user is a current client's contact
            userID = user.get_current().id
            contact_objs = self.getContacts()
            contact_ids = [obj.getUsername() for obj in contact_objs]
            if userID in contact_ids:
                return True
            else:
                return False
        if checkPermission(ModifyPortalContent, self) or \
                checkPermission(AddPortalContent, self):
            return True

    def workflow_script_cancel(self):
        """When the round is cancelled, all its associated Samples and ARs are 
        cancelled by the system.
        """
        if skip(self, "cancel"):
            return
        self.reindexObject(idxs=["cancellation_state", ])
        # deactivate all analysis requests in this sampling round.
        analysis_requests = self.getAnalysisRequests()
        for ar in analysis_requests:
            ar_obj = ar.getObject()
            workflow = getToolByName(self, 'portal_workflow')
            if workflow.getInfoFor(ar_obj, 'cancellation_state') != 'cancelled':
                doActionFor(ar.getObject(), 'cancel')
                doActionFor(ar.getObject().getSample(), 'cancel')
