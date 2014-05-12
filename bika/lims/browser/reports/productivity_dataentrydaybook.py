from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/productivity.pt")
    template = ViewPageTemplateFile("templates/productivity_dataentrydaybook.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):

        parms = []
        titles = []

        # Apply filters
        self.contentFilter = {'portal_type': 'AnalysisRequest'}
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateCreated',
                                                    _('Date Created'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        # Query the catalog and store results in a dictionary
        ars = self.bika_catalog(self.contentFilter)
        if not ars:
            message = _("No Analysis Requests matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = {}
        footlines = {}
        totalcreatedcount = len(ars)
        totalreceivedcount = 0
        totalpublishedcount = 0
        totalanlcount = 0
        totalreceptionlag = 0
        totalpublicationlag = 0

        for ar in ars:
            ar = ar.getObject()
            datecreated = ar.created()
            datereceived = ar.getDateReceived()
            datepublished = ar.getDatePublished()
            receptionlag = 0
            publicationlag = 0
            anlcount = len(ar.getAnalyses())

            dataline = {
                "AnalysisRequestID": ar.getRequestID(),
                "DateCreated": self.ulocalized_time(datecreated),
                "DateReceived": self.ulocalized_time(datereceived),
                "DatePublished": self.ulocalized_time(datepublished),
                "ReceptionLag": receptionlag,
                "PublicationLag": publicationlag,
                "TotalLag": receptionlag + publicationlag,
                "BatchID": ar.getBatch().getId() if ar.getBatch() else '',
                "SampleID": ar.getSample().Title(),
                "SampleType": ar.getSampleTypeTitle(),
                "NumAnalyses": anlcount,
                "ClientID": ar.aq_parent.id,
                "Creator": ar.Creator(),
                "Remarks": ar.getRemarks()
            }

            datalines[ar.getRequestID()] = dataline

            totalreceivedcount += ar.getDateReceived() and 1 or 0
            totalpublishedcount += ar.getDatePublished() and 1 or 0
            totalanlcount += anlcount
            totalreceptionlag += receptionlag
            totalpublicationlag += publicationlag

        # Footer total data
        totalreceivedcreated_ratio = float(totalreceivedcount) / float(
            totalcreatedcount)
        totalpublishedcreated_ratio = float(totalpublishedcount) / float(
            totalcreatedcount)
        totalpublishedreceived_ratio = totalreceivedcount and float(
            totalpublishedcount) / float(totalreceivedcount) or 0

        footline = {'Created': totalcreatedcount,
                    'Received': totalreceivedcount,
                    'Published': totalpublishedcount,
                    'ReceivedCreatedRatio': totalreceivedcreated_ratio,
                    'ReceivedCreatedRatioPercentage': ('{0:.0f}'.format(
                        totalreceivedcreated_ratio * 100)) + "%",
                    'PublishedCreatedRatio': totalpublishedcreated_ratio,
                    'PublishedCreatedRatioPercentage': ('{0:.0f}'.format(
                        totalpublishedcreated_ratio * 100)) + "%",
                    'PublishedReceivedRatio': totalpublishedreceived_ratio,
                    'PublishedReceivedRatioPercentage': ('{0:.0f}'.format(
                        totalpublishedreceived_ratio * 100)) + "%",
                    'AvgReceptionLag': (
                    '{0:.1f}'.format(totalreceptionlag / totalcreatedcount)),
                    'AvgPublicationLag': (
                    '{0:.1f}'.format(totalpublicationlag / totalcreatedcount)),
                    'AvgTotalLag': ('{0:.1f}'.format((
                                                     totalreceptionlag + totalpublicationlag) / totalcreatedcount)),
                    'NumAnalyses': totalanlcount
        }

        footlines['Total'] = footline

        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'footlines': footlines}

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                "AnalysisRequestID",
                "DateCreated",
                "DateReceived",
                "DatePublished",
                "ReceptionLag",
                "PublicationLag",
                "TotalLag",
                "BatchID",
                "SampleID",
                "SampleType",
                "NumAnalyses",
                "ClientID",
                "Creator",
                "Remarks",
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for ar_id, row in datalines.items():
                dw.writerow({
                    "AnalysisRequestID": row["AnalysisRequestID"],
                    "DateCreated": row["DateCreated"],
                    "DateReceived": row["DateReceived"],
                    "DatePublished": row["DatePublished"],
                    "ReceptionLag": row["ReceptionLag"],
                    "PublicationLag": row["PublicationLag"],
                    "TotalLag": row["TotalLag"],
                    "BatchID": row["BatchID"],
                    "SampleID": row["SampleID"],
                    "SampleType": row["SampleType"],
                    "NumAnalyses": row["NumAnalyses"],
                    "ClientID": row["ClientID"],
                    "Creator": row["Creator"],
                    "Remarks": row["Remarks"],
                })
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"dataentrydaybook_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': _('Data entry day book'),
                    'report_data': self.template()}
