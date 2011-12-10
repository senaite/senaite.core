""" Fiastar
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from cStringIO import StringIO
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import csv
import plone
import zope

title = 'FIAStar'

class Export(BrowserView):
    """ Writes analyses to a CSV file that FIAStar can read.
        Sends the CSV file to the response.
        # only works for analyses who's parent is AR, Worksheet or Ref Sample.
    """

    def __call__(self, analyses):
        now = DateTime().strftime('%Y%m%d-%H%M')
        instrument = self.context.getInstrument()
        options = {'delimiter' : ';',
                   'parameter' : 'F SO2 & T SO2',
                   'dilute_factor' : 1,
                   'F SO2' : 'FSO2',
                   'T SO2' : 'TSO2'}
        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        norm = getUtility(IIDNormalizer).normalize
        filename  = '%s-%s.csv'%(self.context.getId(), norm(instrument.getDataInterface()))
        listname  = '%s_%s_%s' %(self.context.getId(), norm(instrument.Title()), now)

        tray = 1
        cup = 0

        rows = []
        # create header row
        header = [listname, options['parameter']]
        rows.append(header)

        parents = {}
        # create detail rows
        for analysis in analyses:
            if analysis.portal_type in ('Analysis', 'DuplicateAnalysis'):
                _id = analysis.getRequestID()
                if not parents.has_key(_id):
                    parent = analysis.aq_parent
                    sample = parent.getSample()
                    parents[_id] = {'title': sample.getSampleType().Title(),
                                    'notes': parent.getNotes()}
            else:
                _id = analysis.aq_parent.getId()
                if not parents.has_key(_id):
                    sample = analysis.aq_parent
                    parents[_id] = {'title': sample.Title(),
                                    'notes': sample.getNotes()}

        ar_ids = parents.keys()
        ar_ids.sort()

        for ar_id in ar_ids:
            cup += 1
            detail = [tray,
                      cup,
                      ar_id,
                      parents[ar_id]['title'],
                      options['dilute_factor'],
                      parents[ar_id]['notes'], ]
            rows.append(detail)

        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=options['delimiter'])
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
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        wf_tool = getToolByName(self.context, 'portal_workflow')

        updateable_states = ['received', 'assigned']
        now = DateTime().strftime('%Y%m%d-%H%M')
        instrument = self.context.getInstrument()

        options = {'delimiter' : ';',
                   'parameter' : 'F SO2 & T SO2',
                   'dilute_factor' : 1,
                   'F SO2' : 'FSO2',
                   'T SO2' : 'TSO2'}

        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        samples = []
        batch_headers = None
        fia1 = False
        fia2 = False
        for row in open(csvfile).readlines():
            if not row: continue
            in_data = row[0].split(';')
            # a new batch starts
            if in_data[0] == 'List name':
                fia1 = False
                fia2 = False
                if in_data[13] == 'Concentration':
                    fia1 = True
                elif in_data[15] == 'Concentration':
                    fia2 = True
                continue

            list_name = row[0]
            date = row[1]
            time = row[2]
            sample_id = row[5]
            dilution_factor = row[7]
            parameter = row[9]
            injection = row[11]
            peak = row[12]
            if fia1:
                peak_mean = 0
                peak_st_dev = 0
                concentration = row[13]
                concentration_mean = 0
                concentration_st_dev = 0
                deviation = row[14]
            else:
                peak_mean = row[13]
                peak_st_dev = row[14]
                concentration = row[15]
                concentration_mean = row[16]
                concentration_st_dev = row[17]
                deviation = row[18]

            if parameter == 'sample' or \
               not concentration:
                continue

            samples.append({
                'sample_id' : sample_id,
                'parameter': parameter,
                'dilution_factor': dilution_factor,
                'injection': injection,
                'peak': peak,
                'peak_mean': peak_mean,
                'peak_st_dev': peak_st_dev,
                'concentration': concentration,
                'concentration_mean': concentration_mean,
                'concentration_st_dev': concentration_st_dev,
                'deviation': deviation})

        # kw_map to lookup Fiastar paramter -> service keyword
        kw_map = {}
        for param in ['F SO2', 'T SO2']:
            service = bsc(getKeyword = options[param])
            if not service:
                log.append('ERROR: Could not find service for %s' % param)
                continue
            kw_map[param] = service[0].getObject()

        log = []
        for row in samples:
            log.append(' ')
            log.append('%s' % row['sample_id'])

            service = kw_map[options[row['parameter']]]
            keyword = service.getKeyword()

            ar = pc(id = row['sample_id'])
            if len(ar) == 0:
                log.append('ERROR: Could not find AR %s' % row['sample_id'])
                continue
            ar_state = ar[0].review_state
            if (ar_state not in updateable_states):
                log.append('ERROR: AR State is %s - not updated' % ar_state)
                continue
            ar = ar[0].getObject()
            ar_service_ids = ar.objectIds("Analysis")

            if keyword in ar_service_ids:
                analysis = ar._getOb(keyword)
                as_state = wf_tool.getInfoFor(analysis, 'review_state', '')
                if (as_state not in updateable_states):
                    log.append('ERROR: Analysis %s in %s status '
                               '- not updated' % (service.Title(), as_state))
                    continue
                if analysis.getResult():
                    log.append('ERROR: Analysis %s has a result '
                               '- not updated' % service.Title())
                    continue

            else:
                # create the analysis and set its status to 'not requested'
                ar.invokeFactory(type_name='Analysis',
                                 id = keyword)
                analysis = ar[keyword]
                discount = ar.getMemberDiscount()
                if ar.getMemberDiscountApplies():
                    price = service.getDiscountedPrice()
                    totalprice = service.getTotalDiscountedPrice()
                else:
                    price = service.getPrice()
                    totalprice = service.getTotalPrice()

                analysis.edit(
                    Service=service,
                    Price=price,
                    Discount=discount,
                    VAT=service.getVAT(),
                    TotalPrice=totalprice,
                )
##                self.REQUEST.set('suppress_escalation', 1)
##                wf_tool.doActionFor(analysis, 'import')
##                del self.REQUEST.other['suppress_escalation']
                log.append('INFO: No analysis %s, adding one.' % keyword)

            analysis.setInterimFields(
                [
                {'keyword':'dilution_factor', 'title': 'Dilution Factor', 'value': row['dilution_factor'], 'unit':''},
                {'keyword':'injection', 'title': 'Injection', 'value': row['injection'], 'unit':''},
                {'keyword':'peak', 'title': 'Peak Height/Area', 'value': row['peak'], 'unit':''},
                {'keyword':'peak_mean', 'title': 'Peak Mean', 'value': row['peak_mean'], 'unit':''},
                {'keyword':'peak_st_dev', 'title': 'Peak St Dev', 'value': row['peak_st_dev'], 'unit':''},
                {'keyword':'concentration', 'title': 'Concentration', 'value': row['concentration'], 'unit':''},
                {'keyword':'concentration_mean', 'title': 'Concentration Mean', 'value': row['concentration_mean'], 'unit':''},
                {'keyword':'concentration_st_dev', 'title': 'Concentration St Dev', 'value': row['concentration_st_dev'], 'unit':''},
                {'keyword':'deviation', 'title': 'Deviation', 'value': row['deviation'], 'unit':''},
                ]
            )

        return '\n'.join(log)
