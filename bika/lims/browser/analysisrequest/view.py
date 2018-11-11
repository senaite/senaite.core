# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from functools import wraps

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.analyses import QCAnalysesView
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import EditFieldResults
from bika.lims.permissions import EditResults
from bika.lims.utils import check_permission
from bika.lims.utils import isActive
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from bika.lims.workflow import wasTransitionPerformed
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.decorators import timeit


def XXX_REMOVEME(func):
    @wraps(func)
    def decorator(self, *args, **kwargs):
        logger.warn("~~~~~~~ XXX REMOVEME marked method called: {}.{}".format(
            self.__class__.__name__, func.func_name))
        return func(self, *args, **kwargs)
    return decorator


class AnalysisRequestViewView(BrowserView):
    """Main AR View
    """
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")
    messages = []

    def __init__(self, context, request):
        self.init__ = super(AnalysisRequestViewView, self).__init__(context,
                                                                    request)
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/analysisrequest_big.png",
        )
        self.messages = []

    @timeit()
    def __call__(self):
        if "transition" in self.request.form:
            doActionFor(self.context, self.request.form["transition"])

        # If the analysis request has been received and hasn't been yet
        # verified yet, redirect the user to manage_results view, but only if
        # the user has privileges to Edit(Field)Results, cause otherwise she/he
        # will receive an InsufficientPrivileges error!
        if (self.request.PATH_TRANSLATED.endswith(self.context.id) and
            self.can_edit_results() and self.can_edit_field_results() and
           self.is_received() and not self.is_verified()):

            # Redirect to manage results view if not cancelled
            if not self.is_cancelled():
                manage_results_url = "{}/{}".format(
                    self.context.absolute_url(),
                    "manage_results")
                self.request.response.redirect(manage_results_url)
                return

        # Contacts get expanded for view
        contact = self.context.getContact()
        contacts = []
        for cc in self.context.getCCContact():
            contacts.append(cc)
        if contact in contacts:
            contacts.remove(contact)
        ccemails = []
        for cc in contacts:
            email = cc.getEmailAddress()
            ccemails.append("%s &lt;<a href='mailto:%s'>%s</a>&gt;" %
                            (cc.Title(), email, email))
        # CC Emails become mailto links
        emails = self.context.getCCEmails()
        if isinstance(emails, str):
            emails = emails and [emails, ] or []
        cc_emails = []
        cc_hrefs = []
        for cc in emails:
            cc_emails.append(cc)
            cc_hrefs.append("<a href='mailto:%s'>%s</a>" % (cc, cc))

        # render header table
        self.header_table = HeaderTableView(self.context, self.request)()

        # Create the ResultsInterpretation by department view
        from resultsinterpretation import ARResultsInterpretationView
        self.riview = ARResultsInterpretationView(self.context, self.request)

        # If a general retracted is done, rise a waring
        if api.get_workflow_status_of(self.context) == "sample_received":
            allstatus = list()
            for analysis in self.context.getAnalyses():
                status = api.get_workflow_status_of(analysis)
                if status not in ["retracted", "to_be_verified", "verified"]:
                    allstatus = []
                    break
                else:
                    allstatus.append(status)
            if len(allstatus) > 0:
                message = "General Retract Done.  Submit this AR manually."
                self.addMessage(message, "warning")

        self.renderMessages()
        return self.template()

    def render_analyses_table(self, table="lab"):
        """Render Analyses Table
        """
        view_name = "table_{}_analyses".format(table)
        view = api.get_view(
            view_name, context=self.context, request=self.request)
        view.update()
        view.before_render()
        return view.ajax_contents_table()

    def get_points_of_capture(self):
        """Get the registered points of capture
        """
        return POINTS_OF_CAPTURE.keys()

    def get_poc_title(self, poc):
        """Return the title of the point of capture
        """
        return POINTS_OF_CAPTURE.getValue(poc)

    def can_edit_results(self):
        """Checks if the current user has the permission "EditResults"
        """
        return check_permission(EditResults, self.context)

    def can_edit_field_results(self):
        """Checks if the current user has the permission "EditFieldResults"
        """
        return check_permission(EditFieldResults, self.context)

    def is_received(self):
        """Checks if the AR is received
        """
        return wasTransitionPerformed(self.context, "receive")

    def is_verified(self):
        """Checks if the AR is verified
        """
        return wasTransitionPerformed(self.context, "verify")

    def is_cancelled(self):
        """Checks if the AR is cancelled
        """
        return api.get_cancellation_status(self.context) == "cancelled"

    def is_hazardous(self):
        """Checks if the AR is hazardous
        """
        sample = self.context.getSample()
        sample_type = sample.getSampleType()
        return sample_type.getHazardous()

    def is_retest(self):
        """Checks if the AR is a retest
        """
        return self.context.getRetest()

    def exclude_invoice(self):
        """True if the invoice should be excluded
        """

    def show_categories(self):
        """Check the setup if analysis services should be categorized
        """
        setup = api.get_setup()
        return setup.getCategoriseAnalysisServices()

    def addMessage(self, message, msgtype='info'):
        self.messages.append({'message': message, 'msgtype': msgtype})

    def renderMessages(self):
        for message in self.messages:
            self.context.plone_utils.addPortalMessage(
                message['message'], message['msgtype'])

    @XXX_REMOVEME
    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)

    @XXX_REMOVEME
    def createQCAnalyesView(self, context, request, **kwargs):
        return QCAnalysesView(context, request, **kwargs)

    @XXX_REMOVEME
    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    @XXX_REMOVEME
    def now(self):
        return DateTime()

    @XXX_REMOVEME
    def analysisprofiles(self):
        """ Return applicable client and Lab AnalysisProfile records
        """
        res = []
        profiles = []
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for profile in client.objectValues("AnalysisProfile"):
            if isActive(profile):
                profiles.append((profile.Title(), profile))
        profiles.sort(lambda x, y: cmp(x[0], y[0]))
        res += profiles
        profiles = []
        for profile in self.context.bika_setup.bika_analysisprofiles.objectValues("AnalysisProfile"):
            if isActive(profile):
                lab = t(_('Lab'))
                title = to_utf8(profile.Title())
                profiles.append(("%s: %s" % (lab, title), profile))
        profiles.sort(lambda x, y: cmp(x[0], y[0]))
        res += profiles
        return res

    @XXX_REMOVEME
    def artemplates(self):
        """ Return applicable client and Lab ARTemplate records
        """
        res = []
        templates = []
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for template in client.objectValues("ARTemplate"):
            if isActive(template):
                templates.append((template.Title(), template))
        templates.sort(lambda x, y: cmp(x[0], y[0]))
        res += templates
        templates = []
        for template in self.context.bika_setup.bika_artemplates.objectValues("ARTemplate"):
            if isActive(template):
                lab = t(_('Lab'))
                title = to_utf8(template.Title())
                templates.append(("%s: %s" % (lab, title), template))
        templates.sort(lambda x, y: cmp(x[0], y[0]))
        res += templates
        return res

    @XXX_REMOVEME
    def samplingdeviations(self):
        """ SamplingDeviation vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject())
               for sd in bsc(portal_type='SamplingDeviation',
                             inactive_state='active')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    @XXX_REMOVEME
    def sampleconditions(self):
        """ SampleConditions vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject())
               for sd in bsc(portal_type='SampleConditions',
                             inactive_state='active')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    @XXX_REMOVEME
    def containertypes(self):
        """ DefaultContainerType vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(o.getObject().Title(), o.getObject())
               for o in bsc(portal_type='ContainerType')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    @XXX_REMOVEME
    def SelectedServices(self):
        """ return information about services currently selected in the
            context AR.
            [[PointOfCapture, category uid, service uid],
             [PointOfCapture, category uid, service uid], ...]
        """
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        res = []
        for analysis in bac(portal_type="Analysis",
                            getRequestUID=self.context.UID()):
            analysis = analysis.getObject()
            res.append([analysis.getPointOfCapture(),
                        analysis.getCategoryUID(),
                        analysis.getServiceUID()])
        return res

    @XXX_REMOVEME
    def getRestrictedCategories(self):
        # we are in portal_factory AR context right now
        parent = self.context.aq_parent
        if hasattr(parent, "getRestrictedCategories"):
            return parent.getRestrictedCategories()
        return []

    @XXX_REMOVEME
    def Categories(self):
        """ Dictionary keys: poc
            Dictionary values: (Category UID,category Title)
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        cats = {}
        restricted = [u.UID() for u in self.getRestrictedCategories()]
        for service in bsc(portal_type="AnalysisService",
                           inactive_state='active'):
            cat = (service.getCategoryUID, service.getCategoryTitle)
            if restricted and cat[0] not in restricted:
                continue
            poc = service.getPointOfCapture
            if poc not in cats:
                cats[poc] = []
            if cat not in cats[poc]:
                cats[poc].append(cat)
        return cats

    @XXX_REMOVEME
    def getDefaultCategories(self):
        # we are in portal_factory AR context right now
        parent = self.context.aq_parent
        if hasattr(parent, "getDefaultCategories"):
            return parent.getDefaultCategories()
        return []

    @XXX_REMOVEME
    def DefaultCategories(self):
        """ Used in AR add context, to return list of UIDs for
        automatically-expanded categories.
        """
        cats = self.getDefaultCategories()
        return [cat.UID() for cat in cats]

    @XXX_REMOVEME
    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember()
        member_groups = [pg.getGroupById(group.id).getGroupName()
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    @XXX_REMOVEME
    def getARTemplateTitle(self):
        """Grab the context's current ARTemplate Title if any
        """
        return self.context.getTemplate() and \
               self.context.getTemplate().Title() or ''

    @XXX_REMOVEME
    def get_requested_analyses(self):
        #
        # title=Get requested analyses
        #
        result = []
        cats = {}
        for analysis in self.context.getAnalyses(full_objects=True):
            if analysis.review_state == 'not_requested':
                continue
            category_name = analysis.getCategoryTitle()
            if not category_name in cats:
                cats[category_name] = {}
            cats[category_name][analysis.Title()] = analysis
        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        for cat_key in cat_keys:
            analyses = cats[cat_key]
            analysis_keys = analyses.keys()
            analysis_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
            for analysis_key in analysis_keys:
                result.append(analyses[analysis_key])
        return result

    @XXX_REMOVEME
    def get_analyses_not_requested(self):
        #
        # title=Get analyses which have not been requested by the client
        #

        result = []
        for analysis in self.context.getAnalyses():
            if analysis.review_state == 'not_requested':
                result.append(analysis)
        return result

    @XXX_REMOVEME
    def get_analysisrequest_verifier(self, analysisrequest):
        """Get the name of the member who last verified this AR
        """
        wtool = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        verifier = None
        try:
            review_history = wtool.getInfoFor(analysisrequest, 'review_history')
        except:
            return 'access denied'
        review_history = [review for review in review_history if review.get('action', '')]
        if not review_history:
            return 'no history'
        for items in review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            if not member:
                verifier = actor
                continue
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier
