""" Fiastar
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from cStringIO import StringIO
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import csv
import plone
import zope

title = 'FIAStar'

class Export(BrowserView):
    """ Writes workseet analyses to a CSV file that FIAStar can read.
        Sends the CSV file to the response.
        # only works for analyses who's parent is AR, Worksheet or Ref Sample.
    """

    def __call__(self, analyses):
        tray = 1
        now = DateTime().strftime('%Y%m%d-%H%M')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        instrument = self.context.getInstrument()
        norm = getUtility(IIDNormalizer).normalize
        filename  = '%s-%s.csv'%(self.context.getId(),
                                 norm(instrument.getDataInterface()))
        listname  = '%s_%s_%s' %(self.context.getId(),
                                 norm(instrument.Title()), now)
        options = {'dilute_factor' : 1,
                   'F SO2' : 'FSO2',
                   'T SO2' : 'TSO2'}
        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        # kw_map to lookup Fiastar parameter -> service keyword and vice versa
        kw_map = {}
        for param in ['F SO2', 'T SO2']:
            service = bsc(getKeyword = options[param])
            if not service:
                log.append('ERROR: Could not find service for %s' % param)
                continue
            service = service[0].getObject()
            kw_map[param] = service
            kw_map[service.getKeyword()] = param

        # for looking up "cup" number (= slot) of analyses
        analysis_to_slot = {}
        for s in self.context.getLayout():
            analysis_to_slot[s['analysis_uid']] = int(s['position'])

        # split into FSO2 and TSO2 batches
        batches = {}
        for analysis in analyses:
            kw = analysis.getService().getKeyword()
            if kw not in kw_map:
                logger.info("%s (slot %s): keyword %s not present in options" % \
                            (analysis.getService().Title(),
                             analysis_to_slot[analysis.UID()],
                             kw))
                continue
            param = kw_map[kw]
            if not param in batches:
                batches[param] = []
            batches[param].append(analysis)

        if not batches:
            message = _("fiastar_no_analyses_found",
                        default="No analyses were found for FIAStar export.")
            message = self.context.translate(message)
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # write rows
        rows = []
        for param, analyses in batches.items():
            # create batch header row
            header = [listname, param]
            rows.append(header)
            for analysis in analyses:
                cup = analysis_to_slot[analysis.UID()]
                detail = [tray,
                          cup,
                          analysis.UID(),
                          analysis.getId(),
                          options['dilute_factor'],
                          ""]
                rows.append(detail)

        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=';')
        assert(writer)
        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length',len(result))
        #setHeader('Content-Type', 'application/x-download')
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)

class Import(BrowserView):
    """ Read FIAStar analysis results
    """

    def __call__(self, csvfile):

        pc = getToolByName(self.context, 'portal_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        wf_tool = getToolByName(self.context, 'portal_workflow')

        updateable_states = ['sample_received', 'assigned']
        now = DateTime().strftime('%Y%m%d-%H%M')
        instrument = self.context.getInstrument()

        options = {'dilute_factor' : 1,
                   'F SO2' : 'FSO2',
                   'T SO2' : 'TSO2'}
        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        # kw_map to lookup Fiastar parameter -> service keyword and vice versa
        kw_map = {}
        for param in ['F SO2', 'T SO2']:
            service = bsc(getKeyword = options[param])
            if not service:
                log.append('ERROR: Could not find service for %s' % param)
                continue
            service = service[0].getObject()
            kw_map[param] = service
            kw_map[service.getKeyword()] = param

        analyses = []
        batch_headers = None
        fia1 = False
        fia2 = False
        # place all valid rows into 'analyses' list of dict
        for row in open(csvfile).readlines():
            if not row: continue
            row = row.split(';')
            # a new batch starts
            if row[0] == 'List name':
                fia1 = False
                fia2 = False
                if row[13] == 'Concentration':
                    fia1 = True
                elif row[15] == 'Concentration':
                    row[13] = 'Peak Mean'
                    row[14] = 'Peak St dev'
                    row[16] = 'Concentration Mean'
                    row[17] = 'Concentration St dev'
                    fia2 = True
                fields = row
                continue
            row = dict(zip(fields, row))
            if row['Parameter'] == 'sample' or not row['Concentration']:
                continue
            analyses.append(row)

        log = []
        for row in samples:
            param = row['Parameter']
            service = kw_map[param]
            keyword = service.getKeyword()

            analysis = uc(UID = row['Sample name'])

            if len(analysis) == 0:
                log.append('ERROR: no analysis %s' % row['Sample name'])
                continue
            analysis = analysis[0].getObject()
            as_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if (as_state not in updateable_states):
                log.append('ERROR: Analysis %s in %s status '
                           '- not updated' % (service.Title(), as_state))
                continue
            if analysis.getResult():
                log.append('ERROR: Analysis %s has a result '
                           '- not updated' % service.Title())
                continue

            analysis.setInterimFields(
                [
                {'keyword':'dilution_factor',
                 'title': 'Dilution Factor',
                 'value': row['Dilution'],
                 'unit':''},
                {'keyword':'injection',
                 'title': 'Injection',
                 'value': row['Injection'],
                 'unit':''},
                {'keyword':'peak',
                 'title': 'Peak Height/Area',
                 'value': row['Peak Height/Area'],
                 'unit':''},
                {'keyword':'peak_mean',
                 'title': 'Peak Mean',
                 'value': row.get('Peak Mean', '0'),
                 'unit':''},
                {'keyword':'peak_st_dev',
                 'title': 'Peak St dev',
                 'value': row.get('Peak St dev', '0'),
                 'unit':''},
                {'keyword':'concentration',
                 'title': 'Concentration',
                 'value': row['concentration'],
                 'unit':''},
                {'keyword':'concentration_mean',
                 'title': 'Concentration Mean',
                 'value': row['Concentration Mean'],
                 'unit':''},
                {'keyword':'concentration_st_dev',
                 'title': 'Concentration St dev',
                 'value': row['Concentration St dev'],
                 'unit':''},
                {'keyword':'deviation',
                 'title': 'Deviation',
                 'value': row['deviation'],
                 'unit':''},
                ]
            )

        return '\n'.join(log)
