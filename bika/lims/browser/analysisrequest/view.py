from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.analyses import QCAnalysesView
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.browser.sample import SamplePartitionsView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

import plone

class AnalysisRequestViewView(BrowserView):

    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")
    messages = []

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.messages = []

    def __call__(self):
        ar = self.context
        workflow = getToolByName(self.context, 'portal_workflow')
        # Contacts get expanded for view
        contact = self.context.getContact()
        contacts = []
        for cc in self.context.getCCContact():
            contacts.append(cc)
        if contact in contacts:
            contacts.remove(contact)
        ccemails = []
        for cc in contacts:
            ccemails.append("%s &lt;<a href='mailto:%s'>%s</a>&gt;"
                % (cc.Title(), cc.getEmailAddress(), cc.getEmailAddress()))
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
        self.header_table = HeaderTableView(self.context, self.request)
        # Create Partitions View for this ARs sample
        p = SamplePartitionsView(self.context.getSample(), self.request)
        p.show_column_toggles = False
        self.parts = p.contents_table()
        # Create Field and Lab Analyses tables
        self.tables = {}
        for poc in POINTS_OF_CAPTURE:
            if self.context.getAnalyses(getPointOfCapture=poc):
                t = self.createAnalysesView(ar,
                                 self.request,
                                 getPointOfCapture=poc,
                                 show_categories=self.context.bika_setup.getCategoriseAnalysisServices())
                t.allow_edit = True
                t.form_id = "%s_analyses" % poc
                t.review_states[0]['transitions'] = [{'id': 'submit'},
                                                     {'id': 'retract'},
                                                     {'id': 'verify'}]
                t.show_workflow_action_buttons = True
                t.show_select_column = True
                if getSecurityManager().checkPermission(EditFieldResults, self.context) \
                   and poc == 'field':
                    t.review_states[0]['columns'].remove('DueDate')
                self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()
        # Un-captured field analyses may cause confusion
        if ar.getAnalyses(getPointOfCapture='field',
                          review_state=['sampled', 'sample_due']):
            message = _("There are field analyses without submitted results.")
            self.addMessage(message, 'info')
        # Create QC Analyses View for this AR
        show_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        qcview = self.createQCAnalyesView(ar,
                                self.request,
                                show_categories=show_cats)
        qcview.allow_edit = False
        qcview.show_select_column = False
        qcview.show_workflow_action_buttons = False
        qcview.form_id = "%s_qcanalyses"
        qcview.review_states[0]['transitions'] = [{'id': 'submit'},
                                                  {'id': 'retract'},
                                                  {'id': 'verify'}]
        self.qctable = qcview.contents_table()
        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            message = _('These results have been withdrawn and are '
                        'listed here for trace-ability purposes. Please follow '
                        'the link to the retest')
            if childar:
                message = (message + " %s.") % childar.getRequestID()
            else:
                message = message + "."
            self.addMessage(message, 'warning')
        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request %s.') % par.getRequestID()
            self.addMessage(message, 'info')
        self.renderMessages()
        return self.template()

    def addMessage(self, message, msgtype='info'):
        self.messages.append({'message': message, 'msgtype': msgtype})

    def renderMessages(self):
        for message in self.messages:
            self.context.plone_utils.addPortalMessage(
                message['message'], message['msgtype'])

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)

    def createQCAnalyesView(self, context, request, **kwargs):
        return QCAnalysesView(context, request, **kwargs)

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

    def getMemberDiscountApplies(self):
        client = self.context.portal_type == 'Client' and self.context or self.context.aq_parent
        return client and client.portal_type == 'Client' and client.getMemberDiscountApplies() or False

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

    def samplingdeviations(self):
        """ SamplingDeviation vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject())
               for sd in bsc(portal_type='SamplingDeviation',
                             inactive_state='active')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    def sampleconditions(self):
        """ SampleConditions vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject())
               for sd in bsc(portal_type='SampleConditions',
                             inactive_state='active')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    def containertypes(self):
        """ DefaultContainerType vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(o.getObject().Title(), o.getObject())
               for o in bsc(portal_type='ContainerType')]
        res.sort(lambda x, y: cmp(x[0], y[0]))
        return res

    def SelectedServices(self):
        """ return information about services currently selected in the
            context AR.
            [[PointOfCapture, category uid, service uid],
             [PointOfCapture, category uid, service uid], ...]
        """
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        res = []
        for analysis in bac(portal_type="Analysis",
                           getRequestID=self.context.RequestID):
            analysis = analysis.getObject()
            service = analysis.getService()
            res.append([service.getPointOfCapture(),
                        service.getCategoryUID(),
                        service.UID()])
        return res

    def getRestrictedCategories(self):
        if self.context.portal_type == 'Client':
            return self.context.getRestrictedCategories()
        return []

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

    def getDefaultCategories(self):
        if self.context.portal_type == 'Client':
            return self.context.getDefaultCategories()
        return []

    def DefaultCategories(self):
        """ Used in AR add context, to return list of UIDs for
        automatically-expanded categories.
        """
        cats = self.getDefaultCategories()
        return [cat.UID() for cat in cats]

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

    def getAnalysisProfileTitle(self):
        """Grab the context's current AnalysisProfile Title if any
        """
        return self.context.getProfile() and \
               self.context.getProfile().Title() or ''

    def getARTemplateTitle(self):
        """Grab the context's current ARTemplate Title if any
        """
        return self.context.getTemplate() and \
               self.context.getTemplate().Title() or ''

    def get_requested_analyses(self):
        #
        # title=Get requested analyses
        #
        result = []
        cats = {}
        for analysis in self.context.getAnalyses(full_objects=True):
            if analysis.review_state == 'not_requested':
                continue
            service = analysis.getService()
            category_name = service.getCategoryTitle()
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

    def get_analyses_not_requested(self):
        #
        # title=Get analyses which have not been requested by the client
        #

        result = []
        for analysis in self.context.getAnalyses():
            if analysis.review_state == 'not_requested':
                result.append(analysis)
        return result

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

    def get_custom_fields(self):
        """ Returns a dictionary with custom fields to be rendered after
            header_table with this structure:
            {<fieldid>:{title:<title>, value:<html>}
        """
        custom = {}
        ar = self.context
        workflow = getToolByName(self.context, 'portal_workflow')
        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            anchor = childar and ("<a href='%s'>%s</a>" % (childar.absolute_url(), childar.getRequestID())) or None
            if anchor:
                custom['ChildAR'] = {
                    'title': t(_("AR for retested results")),
                    'value': anchor
                }
        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            anchor = "<a href='%s'>%s</a>" % (par.absolute_url(), par.getRequestID())
            custom['ParentAR'] = {
                'title': t(_("Invalid AR retested")),
                'value': anchor
            }
        return custom

    def getPriorityIcon(self):
        priority = self.context.getPriority()
        if priority:
            icon = priority.getBigIcon()
            if icon:
                return '/'.join(icon.getPhysicalPath())
