# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from decimal import Decimal
from operator import methodcaller

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.analysisrequest import schema
from bika.lims.interfaces import IAnalysisRequest, ISamplePrepWorkflow
from bika.lims.permissions import Verify as VerifyPermission, ManageInvoices
from bika.lims.utils import dicts_to_dict, getUsers
from bika.lims.utils import user_email
from bika.lims.utils import user_fullname
from bika.lims.workflow import getTransitionDate
from bika.lims.workflow import getTransitionUsers
from bika.lims.workflow.analysisrequest import events
from bika.lims.workflow.analysisrequest import guards
from plone.api.user import has_permission
from zope.interface import implements

schema['title'].required = False

schema['id'].widget.visible = {
    'edit': 'invisible',
    'view': 'invisible',
}

schema['title'].widget.visible = {
    'edit': 'invisible',
    'view': 'invisible',
}

schema.moveField('Client', before='Contact')
schema.moveField('ResultsInterpretation', pos='bottom')
schema.moveField('ResultsInterpretationDepts', pos='bottom')


class AnalysisRequest(BaseFolder):
    implements(IAnalysisRequest, ISamplePrepWorkflow)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the Request ID as title """
        return self.getId()

    def sortable_title(self):
        """Some lists expects this index
        """
        return self.getId()

    def Description(self):
        """ Return searchable data as Description """
        descr = " ".join((self.getId(), self.aq_parent.Title()))
        return safe_unicode(descr).encode('utf-8')

    @deprecated('[1703] Use getId() instead')
    def getRequestID(self):
        """Another way to return the object ID. It is used as a column and 
        index.
        :returns: The object ID
        :rtype: str
        """
        return self.getId()

    @deprecated('[1703] Use setId(new_id) instad')
    def setRequestID(self, new_id):
        """Delegates to setId() function
        :param new_id: The new id to define
        """
        self.setId(new_id)

    def getClient(self):
        if self.aq_parent.portal_type == 'Client':
            return self.aq_parent
        if self.aq_parent.portal_type == 'Batch':
            return self.aq_parent.getClient()
        return ''

    def getClientPath(self):
        return "/".join(self.aq_parent.getPhysicalPath())

    def getProfilesTitle(self):
        return [profile.Title() for profile in self.getProfiles()]

    def setPublicationSpecification(self, value):
        """Never contains a value; this field is here for the UI." \
        """
        return value

    def getAnalysisService(self):
        proxies = self.getAnalyses(full_objects=False)
        value = set()
        for proxy in proxies:
            value.add(proxy.Title)
        return list(value)

    def getAnalysts(self):
        proxies = self.getAnalyses(full_objects=True)
        value = []
        for proxy in proxies:
            val = proxy.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    def getDistrict(self):
        client = self.aq_parent
        return client.getDistrict()

    def getProvince(self):
        client = self.aq_parent
        return client.getProvince()

    def getBatch(self):
        # The parent type may be "Batch" during ar_add.
        # This function fills the hidden field in ar_add.pt
        if self.aq_parent.portal_type == 'Batch':
            return self.aq_parent
        else:
            return self.Schema()['Batch'].get(self)

    def getDefaultMemberDiscount(self):
        """ compute default member discount if it applies """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                settings = self.bika_setup
                return settings.getMemberDiscount()
            else:
                return "0.00"

    security.declareProtected(View, 'getResponsible')

    def _getAnalysesNum(self):
        """ Return the amount of analyses verified/total in the current AR """
        verified = 0
        total = 0
        for analysis in self.getAnalyses():
            review_state = analysis.review_state
            if review_state in ['verified', 'published']:
                verified += 1
            if review_state not in 'retracted':
                total += 1
        return verified, total

    def getResponsible(self):
        """ Return all manager info of responsible departments """
        managers = {}
        for department in self.getDepartments():
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if manager_id not in managers:
                managers[manager_id] = {}
                managers[manager_id]['salutation'] = safe_unicode(
                    manager.getSalutation())
                managers[manager_id]['name'] = safe_unicode(
                    manager.getFullname())
                managers[manager_id]['email'] = safe_unicode(
                    manager.getEmailAddress())
                managers[manager_id]['phone'] = safe_unicode(
                    manager.getBusinessPhone())
                managers[manager_id]['job_title'] = safe_unicode(
                    manager.getJobTitle())
                if manager.getSignature():
                    managers[manager_id]['signature'] = \
                        '{}/Signature'.format(manager.absolute_url())
                else:
                    managers[manager_id]['signature'] = False
                managers[manager_id]['departments'] = ''
            mngr_dept = managers[manager_id]['departments']
            if mngr_dept:
                mngr_dept += ', '
            mngr_dept += safe_unicode(department.Title())
            managers[manager_id]['departments'] = mngr_dept
        mngr_keys = managers.keys()
        mngr_info = {'ids': mngr_keys, 'dict': managers}

        return mngr_info

    security.declareProtected(View, 'getResponsible')

    def getManagers(self):
        """ Return all managers of responsible departments """
        manager_ids = []
        manager_list = []
        for department in self.getDepartments():
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if manager_id not in manager_ids:
                manager_ids.append(manager_id)
                manager_list.append(manager)
        return manager_list

    security.declareProtected(View, 'getLate')

    def getLate(self):
        """ return True if any analyses are late """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        resultdate = 0
        if review_state in ['to_be_sampled', 'to_be_preserved',
                            'sample_due', 'published']:
            return False

        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                continue
            # This situation can be met during analysis request creation
            calculation = analysis.getCalculation()
            if not calculation or (
                        calculation and not calculation.getDependentServices()):
                resultdate = analysis.getResultCaptureDate()
            duedate = analysis.getDueDate()
            # noinspection PyCallingNonCallable
            if (resultdate and resultdate > duedate) \
                    or (not resultdate and DateTime() > duedate):
                return True
        return False

    def getPrinted(self):
        """ returns "0", "1" or "2" to indicate Printed state.
            0 -> Never printed.
            1 -> Printed after last publish
            2 -> Printed but republished afterwards.
        """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        if review_state not in ['published']:
            return "0"
        reports = self.objectValues('ARReport')
        report_list = sorted(reports, key=methodcaller('getDatePublished'))
        if not report_list:
            return "0"
        last_report = report_list[-1]
        if last_report.getDatePrinted():
            return "1"
        else:
            for report in report_list:
                if report.getDatePrinted():
                    return "2"
        return "0"

    def printLastReport(self):
        """Setting Printed Time of the last report, so its Printed value 
        will be 1
        """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        if review_state not in ['published']:
            return
        reports = self.objectValues('ARReport')
        reports = sorted(reports, key=methodcaller('getDatePublished'))
        if reports:
            lastreport = reports[-1]
            if lastreport and not lastreport.getDatePrinted():
                lastreport.setDatePrinted(DateTime())
                self.reindexObject(idxs=['getPrinted'])

    security.declareProtected(View, 'getBillableItems')

    def getBillableItems(self):
        """The main purpose of this function is to obtain the analysis services
        and profiles from the analysis request
        whose prices are needed to quote the analysis request.
        If an analysis belongs to a profile, this analysis will only be
        included in the analyses list if the profile
        has disabled "Use Analysis Profile Price".
        :returns: a tuple of two lists. The first one only contains analysis
        services not belonging to a profile
                 with active "Use Analysis Profile Price".
                 The second list contains the profiles with activated "Use
                 Analysis Profile Price".
        """
        workflow = getToolByName(self, 'portal_workflow')
        # REMEMBER: Analysis != Analysis services
        analyses = []
        analysis_profiles = []
        to_be_billed = []
        # Getting all analysis request analyses
        # Getting all analysis request analyses
        ar_analyses = self.getAnalyses(cancellation_state='active',
                                       full_objects=True)
        for analysis in ar_analyses:
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state not in ('not_requested', 'retracted'):
                analyses.append(analysis)
        # Getting analysis request profiles
        for profile in self.getProfiles():
            # Getting the analysis profiles which has "Use Analysis Profile
            # Price" enabled
            if profile.getUseAnalysisProfilePrice():
                analysis_profiles.append(profile)
            else:
                # we only need the analysis service keywords from these profiles
                to_be_billed += [service.getKeyword() for service in
                                 profile.getService()]
        # So far we have three arrays:
        #   - analyses: has all analyses (even if they are included inside a
        # profile or not)
        #   - analysis_profiles: has the profiles with "Use Analysis Profile
        # Price" enabled
        #   - to_be_quoted: has analysis services keywords from analysis
        # profiles with "Use Analysis Profile Price"
        #     disabled
        # If a profile has its own price, we don't need their analises'
        # prices, so we have to quit all
        # analysis belonging to that profile. But if another profile has the
        # same analysis service but has
        # "Use Analysis Profile Price" disabled, the service must be included
        #  as billable.
        for profile in analysis_profiles:
            for analysis_service in profile.getService():
                for analysis in analyses:
                    if analysis_service.getKeyword() == analysis.getKeyword() \
                            and analysis.getKeyword() not in to_be_billed:
                        analyses.remove(analysis)
        return analyses, analysis_profiles

    def getServicesAndProfiles(self):
        """This function gets all analysis services and all profiles and removes
        the services belonging to a profile.
        :returns: a tuple of three lists, where the first list contains the
        analyses and the second list the profiles.
                 The third contains the analyses objects used by the profiles.
        """
        # Getting requested analyses
        workflow = getToolByName(self, 'portal_workflow')
        analyses = []
        # profile_analyses contains the profile's analyses (analysis !=
        # service") objects to obtain
        # the correct price later
        profile_analyses = []
        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                analyses.append(analysis)
        # Getting all profiles
        analysis_profiles = self.getProfiles() if len(
            self.getProfiles()) > 0 else []
        # Cleaning services included in profiles
        for profile in analysis_profiles:
            for analysis_service in profile.getService():
                for analysis in analyses:
                    if analysis_service.getKeyword() == analysis.getKeyword():
                        analyses.remove(analysis)
                        profile_analyses.append(analysis)
        return analyses, analysis_profiles, profile_analyses

    security.declareProtected(View, 'getSubtotal')

    def getSubtotal(self):
        """ Compute Subtotal (without member discount and without vat)
        """
        analyses, a_profiles = self.getBillableItems()
        return sum(
            [Decimal(obj.getPrice()) for obj in analyses] +
            [Decimal(obj.getAnalysisProfilePrice()) for obj in a_profiles]
        )

    security.declareProtected(View, 'getSubtotalVATAmount')

    def getSubtotalVATAmount(self):
        """ Compute VAT amount without member discount"""
        analyses, a_profiles = self.getBillableItems()
        if len(analyses) > 0 or len(a_profiles) > 0:
            return sum(
                [Decimal(o.getVATAmount()) for o in analyses] +
                [Decimal(o.getVATAmount()) for o in a_profiles]
            )
        return 0

    security.declareProtected(View, 'getSubtotalTotalPrice')

    def getSubtotalTotalPrice(self):
        """ Compute the price with VAT but no member discount"""
        return self.getSubtotal() + self.getSubtotalVATAmount()

    security.declareProtected(View, 'getDiscountAmount')

    def getDiscountAmount(self):
        """It computes and returns the analysis service's discount amount
        without VAT
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal(self.getSubtotal() * discount / 100)
        else:
            return 0

    def getVATAmount(self):
        """It computes the VAT amount from (subtotal-discount.)*VAT/100,
        but each analysis has its
        own VAT!
        :returns: the analysis request VAT amount with the discount
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        VATAmount = self.getSubtotalVATAmount()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal((1 - discount / 100) * VATAmount)
        else:
            return VATAmount

    security.declareProtected(View, 'getTotalPrice')

    def getTotalPrice(self):
        """It gets the discounted price from analyses and profiles to obtain the
        total value with the VAT
        and the discount applied
        :returns: the analysis request's total price including the VATs and
        discounts
        """
        price = (self.getSubtotal() - self.getDiscountAmount() +
                 self.getVATAmount())
        return price

    getTotal = getTotalPrice

    security.declareProtected(ManageInvoices, 'issueInvoice')

    # noinspection PyUnusedLocal
    def issueInvoice(self, REQUEST=None, RESPONSE=None):
        """ issue invoice
        """
        # check for an adhoc invoice batch for this month
        # noinspection PyCallingNonCallable
        now = DateTime()
        batch_month = now.strftime('%b %Y')
        batch_title = '%s - %s' % (batch_month, 'ad hoc')
        invoice_batch = None
        for b_proxy in self.portal_catalog(portal_type='InvoiceBatch',
                                           Title=batch_title):
            invoice_batch = b_proxy.getObject()
        if not invoice_batch:
            # noinspection PyCallingNonCallable
            first_day = DateTime(now.year(), now.month(), 1)
            start_of_month = first_day.earliestTime()
            last_day = first_day + 31
            # noinspection PyUnresolvedReferences
            while last_day.month() != now.month():
                last_day -= 1
            # noinspection PyUnresolvedReferences
            end_of_month = last_day.latestTime()

            invoices = self.invoices
            batch_id = invoices.generateUniqueId('InvoiceBatch')
            invoice_batch = _createObjectByType("InvoiceBatch", invoices,
                                                batch_id)
            invoice_batch.edit(
                title=batch_title,
                BatchStartDate=start_of_month,
                BatchEndDate=end_of_month,
            )
            invoice_batch.processForm()

        client_uid = self.getClientUID()
        # Get the created invoice
        invoice = invoice_batch.createInvoice(client_uid, [self, ])
        invoice.setAnalysisRequest(self)
        # Set the created invoice in the schema
        self.Schema()['Invoice'].set(self, invoice)

    security.declarePublic('printInvoice')

    # noinspection PyUnusedLocal
    def printInvoice(self, REQUEST=None, RESPONSE=None):
        """ print invoice
        """
        invoice = self.getInvoice()
        invoice_url = invoice.absolute_url()
        RESPONSE.redirect('{}/invoice_print'.format(invoice_url))

    def addARAttachment(self, REQUEST=None, RESPONSE=None):
        """ Add the file as an attachment
        """
        workflow = getToolByName(self, 'portal_workflow')

        this_file = self.REQUEST.form['AttachmentFile_file']
        if 'Analysis' in self.REQUEST.form:
            analysis_uid = self.REQUEST.form['Analysis']
        else:
            analysis_uid = None

        attachmentid = self.generateUniqueId('Attachment')
        attachment = _createObjectByType("Attachment", self.aq_parent,
                                         attachmentid)
        attachment.edit(
            AttachmentFile=this_file,
            AttachmentType=self.REQUEST.form.get('AttachmentType', ''),
            AttachmentKeys=self.REQUEST.form['AttachmentKeys'])
        attachment.processForm()
        attachment.reindexObject()

        if analysis_uid:
            tool = getToolByName(self, REFERENCE_CATALOG)
            analysis = tool.lookupObject(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            if workflow.getInfoFor(analysis,
                                   'review_state') == 'attachment_due':
                workflow.doActionFor(analysis, 'attach')
        else:
            others = self.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.setAttachment(attachments)

        if REQUEST['HTTP_REFERER'].endswith('manage_results'):
            RESPONSE.redirect('{}/manage_results'.format(self.absolute_url()))
        else:
            RESPONSE.redirect(self.absolute_url())

    def delARAttachment(self, REQUEST=None, RESPONSE=None):
        """ delete the attachment """
        tool = getToolByName(self, REFERENCE_CATALOG)
        if 'Attachment' in self.REQUEST.form:
            attachment_uid = self.REQUEST.form['Attachment']
            attachment = tool.lookupObject(attachment_uid)
            parent_r = attachment.getRequest()
            parent_a = attachment.getAnalysis()

            parent = parent_a if parent_a else parent_r
            others = parent.getAttachment()
            attachments = []
            for other in others:
                if not other.UID() == attachment_uid:
                    attachments.append(other.UID())
            parent.setAttachment(attachments)
            client = attachment.aq_parent
            ids = [attachment.getId(), ]
            BaseFolder.manage_delObjects(client, ids, REQUEST)

        RESPONSE.redirect(self.REQUEST.get_header('referer'))

    security.declarePublic('getVerifier')

    def getVerifier(self):
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')

        verifier = None
        # noinspection PyBroadException
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:
            return 'access denied'

        if not review_history:
            return 'no history'
        for items in review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        mt = getToolByName(self, 'portal_membership')
        user = mt.getAuthenticatedMember()
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type='Contact',
               getUsername=user_id)
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        # noinspection PyCallingNonCallable
        return DateTime()

    def getQCAnalyses(self, qctype=None, review_state=None):
        """ return the QC analyses performed in the worksheet in which, at
            least, one sample of this AR is present.
            Depending on qctype value, returns the analyses of:
            - 'b': all Blank Reference Samples used in related worksheet/s
            - 'c': all Control Reference Samples used in related worksheet/s
            - 'd': duplicates only for samples contained in this AR
            If qctype==None, returns all type of qc analyses mentioned above
        """
        qcanalyses = []
        suids = []
        ans = self.getAnalyses()
        wf = getToolByName(self, 'portal_workflow')
        for an in ans:
            an = an.getObject()
            if an.getServiceUID() not in suids:
                suids.append(an.getServiceUID())

        def valid_dup(wan):
            if wan.portal_type == 'ReferenceAnalysis':
                return False
            an_state = wf.getInfoFor(wan, 'review_state')
            return \
                wan.portal_type == 'DuplicateAnalysis' \
                and wan.getRequestID() == self.id \
                and (review_state is None or an_state in review_state)

        def valid_ref(wan):
            if wan.portal_type != 'ReferenceAnalysis':
                return False
            an_state = wf.getInfoFor(wan, 'review_state')
            an_reftype = wan.getReferenceType()
            return wan.getServiceUID() in suids and \
                wan not in qcanalyses and \
                (qctype is None or an_reftype == qctype) and \
                (review_state is None or an_state in review_state)

        for an in ans:
            an = an.getObject()
            br = an.getBackReferences('WorksheetAnalysis')
            if len(br) > 0:
                ws = br[0]
                was = ws.getAnalyses()
                for wa in was:
                    if valid_dup(wa):
                        qcanalyses.append(wa)
                    elif valid_ref(wa):
                        qcanalyses.append(wa)

        return qcanalyses

    def isInvalid(self):
        """ return if the Analysis Request has been invalidated
        """
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(self, 'review_state') == 'invalid'

    def getLastChild(self):
        """ return the last child Request due to invalidation
        """
        child = self.getChildAnalysisRequest()
        while child and child.getChildAnalysisRequest():
            child = child.getChildAnalysisRequest()
        return child

    def getRequestedAnalyses(self):
        """It returns all requested analyses, even if they belong to an analysis
        profile or not.
        """
        #
        # title=Get requested analyses
        #
        result = []
        cats = {}
        workflow = getToolByName(self, 'portal_workflow')
        for analysis in self.getAnalyses(full_objects=True):
            review_state = workflow.getInfoFor(analysis, 'review_state')
            if review_state == 'not_requested':
                continue
            category_name = analysis.getCategoryTitle()
            if category_name not in cats:
                cats[category_name] = {}
            cats[category_name][analysis.Title()] = analysis
        cat_keys = sorted(cats.keys(), key=methodcaller('lower'))
        for cat_key in cat_keys:
            analyses = cats[cat_key]
            analysis_keys = sorted(analyses.keys(),
                                   key=methodcaller('lower'))
            for analysis_key in analysis_keys:
                result.append(analyses[analysis_key])
        return result

    def getSamplingRoundUID(self):
        """Obtains the sampling round UID
        :returns: a UID
        """
        if self.getSamplingRound():
            return self.getSamplingRound().UID()
        else:
            return ''

    def setResultsRange(self, value=None):
        """Sets the spec values for this AR.
        1 - Client specs where (spec.Title) matches (ar.SampleType.Title)
        2 - Lab specs where (spec.Title) matches (ar.SampleType.Title)
        3 - Take override values from instance.Specification
        4 - Take override values from the form (passed here as parameter
        'value').

        The underlying field value is a list of dictionaries.

        The value parameter may be a list of dictionaries, or a dictionary (of
        dictionaries).  In the last case, the keys are irrelevant, but in both
        cases the specs must contain, at minimum, the "keyword", "min", "max",
        and "error" fields.

        Value will be stored in ResultsRange field as list of dictionaries
        """
        rr = {}
        sample = self.getSample()
        if not sample:
            # portal_factory
            return []
        stt = self.getSample().getSampleType().Title()
        bsc = getToolByName(self, 'bika_setup_catalog')
        # 1 or 2: rr = Client specs where (spec.Title) matches (
        # ar.SampleType.Title)
        for folder in self.aq_parent, self.bika_setup.bika_analysisspecs:
            proxies = bsc(portal_type='AnalysisSpec',
                          getSampleTypeTitle=stt,
                          ClientUID=folder.UID())
            if proxies:
                rr = dicts_to_dict(proxies[0].getObject().getResultsRange(),
                                   'keyword')
                break
        # 3: rr += override values from instance.Specification
        ar_spec = self.getSpecification()
        if ar_spec:
            ar_spec_rr = ar_spec.getResultsRange()
            rr.update(dicts_to_dict(ar_spec_rr, 'keyword'))
        # 4: rr += override values from the form (value=dict key=service_uid)
        if value:
            if type(value) in (list, tuple):
                value = dicts_to_dict(value, "keyword")
            elif type(value) == dict:
                value = dicts_to_dict(value.values(), "keyword")
            rr.update(value)
        return self.Schema()['ResultsRange'].set(self, rr.values())

    # Then a string of fields which are defined on the AR, but need to be set
    # and read from the sample

    security.declarePublic('setSamplingDate')

    def setSamplingDate(self, value):
        """Sets the specified sampling date from the sample.
        :value: a date as a date object.
        """
        sample = self.getSample()
        if sample and value:
            sample.setSamplingDate(value)
            self.Schema()['DateSampled'].set(self, value)
        elif not sample:
            logger.warning(
                "setSamplingDate has failed for Analysis Request %s because "
                "it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setSamplingDate has failed for Analysis Request %s because "
                "'value' doesn't have a value'." % self.id)

    security.declarePublic('getSamplingDate')

    def getSamplingDate(self):
        """Gets the specified sampling date from the sample.
        """
        sample = self.getSample()
        if sample:
            return sample.getSamplingDate()
        else:
            return ''

    security.declarePublic('setSampler')

    def setSampler(self, value):
        """Sets the sampler to the sample.
        :value: a user id.
        """
        sample = self.getSample()
        if sample and value:
            sample.setSampler(value)
            self.Schema()['Sampler'].set(self, value)
        elif not sample:
            logger.warning(
                "setSampler has failed for Analysis Request %s because "
                "it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setSampler has failed for Analysis Request %s because "
                "'value' doesn't have a value'." % self.id)

    security.declarePublic('getSampler')

    def getSampler(self):
        """Returns the sampler (as a user id) from the sample
        """
        sample = self.getSample()
        if sample:
            return sample.getSampler()
        else:
            return ''

    security.declarePublic('setDateSampled')

    def setDateSampled(self, value):
        """sets the date when the sample has been sampled.
        :value: the time value
        """
        sample = self.getSample()
        if sample and value:
            sample.setDateSampled(value)
            self.Schema()['DateSampled'].set(self, value)
        elif not sample:
            logger.warning(
                "setDateSampled has failed for Analysis Request %s because "
                "it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setDateSampled has failed for Analysis Request %s because "
                "'value' doesn't have a value'." % self.id)

    security.declarePublic('getDateSampled')

    def getDateSampled(self):
        """Returns the date when the sample has been sampled.
        """
        sample = self.getSample()
        if sample:
            return sample.getDateSampled()
        else:
            return ''

    security.declarePublic('getDatePublished')

    def getDatePublished(self):
        """Returns the transition date from the Analysis Request object
        """
        return getTransitionDate(self, 'publish', not_as_string=True)

    security.declarePublic('setSamplePoint')

    def setSamplePoint(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSamplePoint(value)
            self.Schema()['SamplePoint'].set(self, value)
        elif not sample:
            logger.warning(
                "setSamplePoint has failed for Analysis Request %s because "
                "it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setSamplePoint has failed for Analysis Request %s because "
                "'value' doesn't have a value'." % self.id)

    security.declarePublic('getSamplepoint')

    def getSamplePoint(self):
        sample = self.getSample()
        if sample:
            return sample.getSamplePoint()
        else:
            return ''

    security.declarePublic('setSampleType')

    def setSampleType(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSampleType(value)
            self.Schema()['SampleType'].set(self, value)
        elif not sample:
            logger.warning(
                "setSampleType has failed for Analysis Request %s because "
                "it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setSampleType has failed for Analysis Request %s because "
                "'value' doesn't have a value'." % self.id)

    security.declarePublic('getSampleType')

    def getSampleType(self):
        sample = self.getSample()
        if sample:
            return sample.getSampleType()

    security.declarePublic('setClientReference')

    def setClientReference(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setClientReference(value)
        self.Schema()['ClientReference'].set(self, value)

    security.declarePublic('getClientReference')

    def getClientReference(self):
        sample = self.getSample()
        if sample:
            return sample.getClientReference()
        return self.Schema().getField('ClientReference').get(self)

    security.declarePublic('setClientSampleID')

    def setClientSampleID(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setClientSampleID(value)
        self.Schema()['ClientSampleID'].set(self, value)

    security.declarePublic('getClientSampleID')

    def getClientSampleID(self):
        sample = self.getSample()
        if sample:
            return sample.getClientSampleID()
        return self.Schema().getField('ClientSampleID').get(self)

    security.declarePublic('setSamplingDeviation')

    def setSamplingDeviation(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSamplingDeviation(value)
            self.Schema()['SamplingDeviation'].set(self, value)
        elif not sample:
            logger.warning(
                "setSamplingDeviation has failed for Analysis Request %s "
                "because it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setSamplingDeviation has failed for Analysis Request %s "
                "because 'value' doesn't have a value'." % self.id)

    security.declarePublic('getSamplingDeviation')

    def getSamplingDeviation(self):
        """It works as a metacolumn.
        """
        sample = self.getSample()
        if sample:
            return sample.getSamplingDeviation()

    security.declarePublic('getSamplingDeviationTitle')

    def getSamplingDeviationTitle(self):
        """It works as a metacolumn.
        """
        sd = self.getSamplingDeviation()
        if sd:
            return sd.Title()

    security.declarePublic('getHazardous')

    def getHazardous(self):
        """It works as a metacolumn.
        """
        sample_type = self.getSampleType()
        if sample_type:
            return sample_type.getHazardous()

    security.declarePublic('getContactURL')

    def getContactURL(self):
        """It works as a metacolumn.
        """
        contact = self.getContact()
        if contact:
            return contact.absolute_url_path()

    security.declarePublic('getSamplingWorkflowEnabled')

    def getSamplingWorkflowEnabled(self):
        """It works as a metacolumn.
        """
        sample = self.getSample()
        if sample:
            return sample.getSamplingWorkflowEnabled()

    security.declarePublic('setSampleCondition')

    def setSampleCondition(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSampleCondition(value)
        self.Schema()['SampleCondition'].set(self, value)

    security.declarePublic('getSampleCondition')

    def getSampleCondition(self):
        sample = self.getSample()
        if sample:
            return sample.getSampleCondition()
        return self.Schema().getField('SampleCondition').get(self)

    security.declarePublic('setEnvironmentalConditions')

    def setEnvironmentalConditions(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setEnvironmentalConditions(value)
        self.Schema()['EnvironmentalConditions'].set(self, value)

    security.declarePublic('getEnvironmentalConditions')

    def getEnvironmentalConditions(self):
        sample = self.getSample()
        if sample:
            return sample.getEnvironmentalConditions()
        return self.Schema().getField('EnvironmentalConditions').get(self)

    security.declarePublic('setComposite')

    def setComposite(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setComposite(value)
        self.Schema()['Composite'].set(self, value)

    security.declarePublic('getComposite')

    def getComposite(self):
        sample = self.getSample()
        if sample:
            return sample.getComposite()
        return self.Schema().getField('Composite').get(self)

    security.declarePublic('setStorageLocation')

    def setStorageLocation(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setStorageLocation(value)
            self.Schema()['StorageLocation'].set(self, value)
        elif not sample:
            logger.warning(
                "setStorageLocation has failed for Analysis Request %s because"
                " it hasn't got a sample." % self.id)
        else:
            logger.warning(
                "setStorageLocation has failed for Analysis Request %s because"
                " 'value' doesn't have a value'." % self.id)

    security.declarePublic('getStorageLocation')

    def getStorageLocation(self):
        sample = self.getSample()
        if sample:
            return sample.getStorageLocation()
        else:
            return ''

    security.declarePublic('setAdHoc')

    def setAdHoc(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setAdHoc(value)
        self.Schema()['AdHoc'].set(self, value)

    security.declarePublic('getAdHoc')

    def getAdHoc(self):
        sample = self.getSample()
        if sample:
            return sample.getAdHoc()
        return self.Schema().getField('AdHoc').get(self)

    security.declarePublic('setScheduledSamplingSampler')

    def setScheduledSamplingSampler(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setScheduledSamplingSampler(value)
        self.Schema()['ScheduledSamplingSampler'].set(self, value)

    security.declarePublic('getScheduledSamplingSampler')

    def getScheduledSamplingSampler(self):
        sample = self.getSample()
        if sample:
            return sample.getScheduledSamplingSampler()
        return self.Schema() \
            .getField('ScheduledSamplingSampler').get(self)

    def getSamplers(self):
        return getUsers(self, ['LabManager', 'Sampler'])

    def getPreparationWorkflows(self):
        """Return a list of sample preparation workflows.  These are identified
        by scanning all workflow IDs for those beginning with "sampleprep".
        """
        wf = self.portal_workflow
        ids = wf.getWorkflowIds()
        sampleprep_ids = [wid for wid in ids if wid.startswith('sampleprep')]
        prep_workflows = [['', ''], ]
        for workflow_id in sampleprep_ids:
            workflow = wf.getWorkflowById(workflow_id)
            prep_workflows.append([workflow_id, workflow.title])
        return DisplayList(prep_workflows)

    def getDepartments(self):
        """Returns a list of the departments assigned to the Analyses
        from this Analysis Request
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        dept_uids = [b.getDepartmentUID for b in self.getAnalyses()]
        brains = bsc(portal_type='Department', UID=dept_uids)
        depts = [b.getObject() for b in brains]
        return list(set(depts))

    def getDepartmentUIDs(self):
        """Return a list of the UIDs of departments assigned to the Analyses
        from this Analysis Request.
        """
        return [dept.UID() for dept in self.getDepartments()]

    def getResultsInterpretationByDepartment(self, department=None):
        """ Returns the results interpretation for this Analysis Request
            and department. If department not set, returns the results
            interpretation tagged as 'General'.

            Returns a dict with the following keys:
            {'uid': <department_uid> or 'general',
             'richtext': <text/plain>}
        """
        uid = department.UID() if department else 'general'
        rows = self.Schema()['ResultsInterpretationDepts'].get(self)
        row = [row for row in rows if row.get('uid') == uid]
        if len(row) > 0:
            row = row[0]
        elif uid == 'general' \
                and hasattr(self, 'getResultsInterpretation') \
                and self.getResultsInterpretation():
            row = {'uid': uid, 'richtext': self.getResultsInterpretation()}
        else:
            row = {'uid': uid, 'richtext': ''}
        return row

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            analysis requests:
            1. looks for settings in AR's ARTemplate. If found, returns
                the settings for the AnalysisService set in the Template
            2. If no settings found, looks in AR's ARProfile. If found,
                returns the settings for the AnalysisService from the
                AR Profile. Otherwise, returns a one entry dictionary
                with only the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings()
                if s.get('uid', '') == uid]

        # Created by using an ARTemplate?
        if not sets and self.getTemplate():
            adv = self.getTemplate().getAnalysisServiceSettings(uid)
            sets = [adv] if 'hidden' in adv else []

        # Created by using an AR Profile?
        if not sets and self.getProfiles():
            adv = []
            adv += [profile.getAnalysisServiceSettings(uid) for profile in
                    self.getProfiles()]
            sets = adv if 'hidden' in adv[0] else []

        return sets[0] if sets else {'uid': uid}

    def getPartitions(self):
        """This functions returns the partitions from the analysis request's
        analyses.
        :returns: a list with the full partition objects
        """
        analyses = self.getRequestedAnalyses()
        partitions = []
        for analysis in analyses:
            if analysis.getSamplePartition() not in partitions:
                partitions.append(analysis.getSamplePartition())
        return partitions

    def getContainers(self):
        """This functions returns the containers from the analysis request's
        analyses
        :returns: a list with the full partition objects
        """
        partitions = self.getPartitions()
        containers = []
        for partition in partitions:
            if partition.getContainer():
                containers.append(partition.getContainer())
        return containers

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this request, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                request or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('{} is not valid'.format(uid))
        return sets.get('hidden', False)

    def getRejecter(self):
        """If the Analysis Request has been rejected, returns the user who 
        did the
        rejection. If it was not rejected or the current user has not enough
        privileges to access to this information, returns None.
        """
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')
        # noinspection PyBroadException
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:
            return None
        for items in review_history:
            action = items.get('action')
            if action != 'reject':
                continue
            actor = items.get('actor')
            return mtool.getMemberById(actor)
        return None

    def getReceivedBy(self):
        """Returns the User who received the analysis request.
        :returns: the user id
        """
        user = getTransitionUsers(self, 'receive', last_user=True)
        return user[0] if user else ''

    def getDateVerified(self):
        """Returns the date of verification as a DateTime object.
        """
        return getTransitionDate(self, 'verify', not_as_string=True)

    def _getCreatorFullName(self):
        """Returns the full name of this analysis request's creator.
        """
        return user_fullname(self, self.Creator())

    def _getCreatorEmail(self):
        """Returns the email of this analysis request's creator.
        """
        return user_email(self, self.Creator())

    def _getSamplerFullName(self):
        """Returns the full name's defined sampler.
        """
        return user_fullname(self, self.getSampler())

    def _getSamplerEmail(self):
        """Returns the email of this analysis request's sampler.
        """
        return user_email(self, self.Creator())

    # TODO Workflow, AnalysisRequest Move to guards.verify?
    def isVerifiable(self):
        """Checks it the current Analysis Request can be verified. This is, 
        its not a cancelled Analysis Request and all the analyses that 
        contains are verifiable too. Note that verifying an Analysis Request 
        is in fact, the same as verifying all the analyses that contains. 
        Therefore, the 'verified' state of an Analysis Request shouldn't be a 
        'real' state, rather a kind-of computed state, based on the statuses 
        of the analyses it contains. This is why this function checks if the 
        analyses contained are verifiable, cause otherwise, the Analysis 
        Request will never be able to reach a 'verified' state.

        :returns: True or False
        """
        # Check if the analysis request is active
        workflow = getToolByName(self, "portal_workflow")
        objstate = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if objstate == "cancelled":
            return False

        # Check if the analysis request state is to_be_verified
        review_state = workflow.getInfoFor(self, "review_state")
        if review_state == 'to_be_verified':
            # This means that all the analyses from this analysis request have
            # already been transitioned to a 'verified' state, and so the
            # analysis request itself
            return True
        else:
            # Check if the analyses contained in this analysis request are
            # verifiable. Only check those analyses not cancelled and that
            # are not in a kind-of already verified state
            canbeverified = True
            omit = ['published', 'retracted', 'rejected', 'verified']
            for a in self.getAnalyses(full_objects=True):
                st = workflow.getInfoFor(a, 'cancellation_state', 'active')
                if st == 'cancelled':
                    continue
                st = workflow.getInfoFor(a, 'review_state')
                if st in omit:
                    continue
                # Can the analysis be verified?
                if not a.isVerifiable(self):
                    canbeverified = False
                    break
            return canbeverified

    def getObjectWorkflowStates(self):
        """This method is used as a metacolumn. Returns a dictionary with the 
        workflow id as key and workflow state as value.

        :returns: {'review_state':'active',...}
        """
        workflow = getToolByName(self, 'portal_workflow')
        states = {}
        for w in workflow.getWorkflowsFor(self):
            state = w._getWorkflowStateOf(self).id
            states[w.state_var] = state
        return states

    # TODO Workflow, AnalysisRequest Move to guards.verify?
    def isUserAllowedToVerify(self, member):
        """Checks if the specified user has enough privileges to verify the 
        current AR. Apart from the roles, this function also checks if the 
        current user has enough privileges to verify all the analyses 
        contained in this Analysis Request. Note that this function only 
        returns if the user can verify the analysis request according to 
        his/her privileges and the analyses contained (see isVerifiable 
        function)

        :member: user to be tested
        :returns: true or false
        """
        # Check if the user has "Bika: Verify" privileges
        username = member.getUserName()
        allowed = has_permission(VerifyPermission, username=username)
        if not allowed:
            return False
        # Check if the user is allowed to verify all the contained analyses
        # TODO-performance: gettin all analysis each time this function is
        # called
        notallowed = [a for a in self.getAnalyses(full_objects=True)
                      if not a.isUserAllowedToVerify(member)]
        return not notallowed

    @deprecated('[1705] Use guards.to_be_preserved from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_to_be_preserved(self):
        return guards.to_be_preserved(self)

    @deprecated('[1705] Use guards.verify from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_verify_transition(self):
        return guards.verify(self)

    @deprecated('[1705] Use guards.unassign from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_unassign_transition(self):
        return guards.unassign(self)

    @deprecated('[1705] Use guards.assign from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_assign_transition(self):
        return guards.assign(self)

    @deprecated('[1705] Use guards.receive from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_receive_transition(self):
        return guards.receive(self)

    @deprecated('[1705] Use guards.sample_prep from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_sample_prep_transition(self):
        return guards.sample_prep(self)

    @deprecated('[1705] Use guards.sample_prep_complete from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_sample_prep_complete_transition(self):
        return guards.sample_prep_complete(self)

    @deprecated('[1705] Use guards.schedule_sampling from '
                'bika.lims.workflow.analysisrequest')
    @security.public
    def guard_schedule_sampling_transition(self):
        return guards.schedule_sampling(self)

    @deprecated('[1705] Use events.after_no_sampling_workflow from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_no_sampling_workflow(self):
        events.after_no_sampling_workflow(self)

    @deprecated('[1705] Use events.after_sampling_workflow from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_sampling_workflow(self):
        events.after_sampling_workflow(self)

    @deprecated('[1705] Use events.after_sample from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_sample(self):
        events.after_sample(self)

    @deprecated('[1705] Use events.after_receive from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_receive(self):
        events.after_receive(self)

    @deprecated('[1705] Use events.after_preserve from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_preserve(self):
        events.after_preserve(self)

    @deprecated('[1705] Use events.after_attach from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_attach(self):
        events.after_attach(self)

    @deprecated('[1705] Use events.after_verify from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_verify(self):
        events.after_verify(self)

    @deprecated('[1705] Use events.after_publish from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_publish(self):
        events.after_publish(self)

    @deprecated('[1705] Use events.after_reinstate from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_reinstate(self):
        events.after_reinstate(self)

    @deprecated('[1705] Use events.after_cancel from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_cancel(self):
        events.after_cancel(self)

    @deprecated('[1705] Use events.after_schedule_sampling from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_schedule_sampling(self):
        events.after_schedule_sampling(self)

    @deprecated('[1705] Use events.after_reject from '
                'bika.lims.workflow.anaysisrequest')
    @security.public
    def workflow_script_reject(self):
        events.after_reject(self)

    def SearchableText(self):
        """Override searchable text logic based on the requirements.

        This method constructs a text blob which contains all full-text
        searchable text for this content item.
        https://docs.plone.org/develop/plone/searching_and_indexing/indexing
        .html#full-text-searching
        """

        # Speed up string concatenation ops by using a buffer
        entries = []

        # plain text fields we index from ourself,
        # a list of accessor methods of the class
        plain_text_fields = ("getId",)

        def read(getter):
            """Call a class accessor method to give a value for certain
            Archetypes field.
            """
            # noinspection PyBroadException
            # XXX @pau bare except
            try:
                val = getter()
            except:
                message = \
                    "Error getting the accessor parameter in SearchableText " \
                    "from the Analysis Request Object {}".format(self.getId())
                logger.error(message)
                val = ""

            if val is None:
                val = ""

            return val

        # Concatenate plain text fields as they are
        for f in plain_text_fields:
            accessor = getattr(self, f)
            value = read(accessor)
            entries.append(value)

        # Plone accessor methods assume utf-8
        def convertToUTF8(text):
            if type(text) == unicode:
                return text.encode("utf-8")
            return text

        entries = [convertToUTF8(entry) for entry in entries]

        # Concatenate all strings to one text blob
        return " ".join(entries)


registerType(AnalysisRequest, PROJECTNAME)
