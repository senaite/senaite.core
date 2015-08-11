from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from calendar import monthrange
from DateTime import DateTime
import datetime

class DashboardView(BrowserView):
    template = ViewPageTemplateFile("templates/dashboard.pt")

    def __call__(self):
        self.icon = self.portal_url + "/++resource++bika.lims.images/chevron_big.png"

        # By default, weekly
        self.periodicity = self.request.get('p', 'w')
        if (self.periodicity == 'd'):
            # Daily
            self.date_from = DateTime()
            self.date_to = DateTime() + 1
        elif (self.periodicity == 'm'):
            # Monthly
            today = datetime.date.today()
            self.date_from = DateTime(today.year, today.month, 1)
            self.date_to = DateTime(today.year, today.month, monthrange(today.year, today.month)[1], 23, 59, 59)
        elif (self.periodicity == 'q'):
            # Quarterly
            today = datetime.date.today()
            m = (((today.month-1)/3)*3)+1
            self.date_from = DateTime(today.year, m, 1)
            self.date_to = DateTime(today.year, m+2, monthrange(today.year, m+2)[1], 23, 59, 59)
        elif (self.periodicity == 'b'):
            # Biannual
            today = datetime.date.today()
            m = (((today.month-1)/6)*6)+1
            self.date_from = DateTime(today.year, m, 1)
            self.date_to = DateTime(today.year, m+5, monthrange(today.year, m+5)[1], 23, 59, 59)
        elif (self.periodicity == 'y'):
            # Yearly
            today = datetime.date.today()
            self.date_from = DateTime(today.year, 1, 1)
            self.date_to = DateTime(today.year, 12, 31, 23, 59, 59)
        else:
            # weekly
            today = datetime.date.today()
            year, weeknum, dow = today.isocalendar()
            self.date_from = DateTime() - dow
            self.date_to = self.date_from + 7

        self.date_range = {'query': (self.date_from, self.date_to), 'range': 'min:max'}
        self.below_date = {'query': (DateTime('1990-01-01 00:00:00'), self.date_from - 1), 'range':'min:max'}

        return self.template()

    def get_sections(self):

        sections = [self.get_analysisrequests_section(),
                    self.get_worksheets_section()]

        return sections

    def get_analysisrequests_section(self):
        out = []

        # Analysis Requests
        active_rs = ['to_be_sampled',
                     'to_be_preserved',
                     'sample_due',
                     'sample_received',
                     'assigned',
                     'to_be_verified',
                     'attachment_due',
                     'verified']
        bc = getToolByName(self.context, "bika_catalog")
        ars = bc(portal_type="AnalysisRequest",
                 created=self.date_range,
                 cancellation_state=['active',])

        # Create a barchart with the number for ARs created per period


        numars = len(ars)
        numars += len(bc(portal_type="AnalysisRequest",
                        review_state=active_rs,
                        cancellation_state=['active',],
                        created=self.below_date))

        # Analysis Requests awaiting to be sampled
        review_state = ['to_be_sampled',]
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be sampled")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests to be sampled'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=to_be_sampled'})

        # Analysis Requests awaiting to be preserved
        review_state = ['to_be_preserved',]
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be preserved")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests to be preserved'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=to_be_preserved'})

        # Analysis Requests awaiting for reception
        review_state = ['sample_due',]
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Reception pending")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests to be received'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=sample_due'})

        # Analysis Requests under way
        review_state = ['attachment_due', 'sample_received', 'assigned']
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Results pending")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests with results pending'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=sample_received'})

        # Analysis Requests to be verified
        review_state = ['to_be_verified',]
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be verified")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests to be verified'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=to_be_verified'})

        # Analysis Requests to be published
        review_state = ['verified',]
        ars = len(bc(portal_type="AnalysisRequest",
                     review_state=review_state,
                     cancellation_state=['active',]))
        ratio = (float(ars)/float(numars))*100 if ars > 0 and numars > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be published")
        out.append({'type':         'simple-panel',
                    'name':         _('Analysis Requests to be published'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ars,
                    'total':        numars,
                    'legend':       _('of') + " " + str(numars) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/analysisrequests?analysisrequests_review_state=verified'})

        return {'id': 'analysisrequests',
                'title': _('Analysis Requests'),
                'panels': out}

    def get_worksheets_section(self):
        out = []
        bc = getToolByName(self.context, "bika_catalog")
        active_ws = ['open', 'to_be_verified', 'attachment_due']
        numws = len(bc(portal_type="Worksheet",
                       created=self.date_range))

        numws += len(bc(portal_type="Worksheet",
                        review_state=active_ws,
                        created=self.below_date))

        # Open worksheets
        review_state = ['open', 'attachment_due']
        ws = len(bc(portal_type="Worksheet",
                    review_state=review_state))
        ratio = (float(ws)/float(numws))*100 if ws > 0 and numws > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("Results pending")
        out.append({'type':         'simple-panel',
                    'name':         _('Results pending'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ws,
                    'total':        numws,
                    'legend':       _('of') + " " + str(numws) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/worksheets?list_review_state=open'})

        # Worksheets to be verified
        review_state = ['to_be_verified', ]
        ws = len(bc(portal_type="Worksheet",
                    review_state=review_state))
        ratio = (float(ws)/float(numws))*100 if ws > 0 and numws > 0 else 0
        ratio = str("%%.%sf" % 1) % ratio
        msg = _("To be verified")
        out.append({'type':         'simple-panel',
                    'name':         _('To be verified'),
                    'class':        'informative',
                    'description':  msg,
                    'number':       ws,
                    'total':        numws,
                    'legend':       _('of') + " " + str(numws) + ' (' + ratio +'%)',
                    'link':         self.portal_url + '/worksheets?list_review_state=to_be_verified'})

        return {'id': 'worksheets',
                'title': _('Worksheets'),
                'panels': out}
