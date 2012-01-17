""" Fiastar
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.event import ObjectInitializedEvent
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import changeWorkflowState
from bika.lims import logger
from cStringIO import StringIO
from operator import itemgetter
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import csv
import plone
import zope
import zope.event

title = 'FIAStar'

class Export(BrowserView):
    """ Writes workseet analyses to a CSV file that FIAStar can read.
        Sends the CSV file to the response.
        Requests "TSO2 & F SO2" for all requests.
        uses analysis' PARENT UID as 'Sample name' col.
        uses analysis' CONTAINER UID as 'Sample type' col.
        (this is not always the same thing as the 'container_uid'
         specified in ws.getLayout())
    """

    def __call__(self, analyses):
        tray = 1
        now = DateTime().strftime('%Y%m%d-%H%M')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        instrument = self.context.getInstrument()
        norm = getUtility(IIDNormalizer).normalize
        filename  = '%s-%s.csv'%(self.context.getId(),
                                 norm(instrument.getDataInterface()))
        listname  = '%s_%s_%s' %(self.context.getId(),
                                 norm(instrument.Title()), now)
        options = {'dilute_factor' : 1,
                   'method': 'F SO2 & T SO2'}
        for k,v in instrument.getDataInterfaceOptions():
            options[k] = v

        # for looking up "cup" number (= slot) of ARs
        parent_to_slot = {}
        layout = self.context.getLayout()
        for x in range(len(layout)):
            a_uid = layout[x]['analysis_uid']
            p_uid = uc(UID=a_uid)[0].getObject().aq_parent.UID()
            layout[x]['parent_uid'] = p_uid
            if not p_uid in parent_to_slot.keys():
                parent_to_slot[p_uid] = int(layout[x]['position'])

        # write rows, one per PARENT
        header = [listname, options['method']]
        rows = []
        rows.append(header)
        tmprows = []
        ARs_exported = []
        for x in range(len(layout)):
            # create batch header row
            c_uid = layout[x]['container_uid']
            p_uid = layout[x]['parent_uid']
            if p_uid in ARs_exported:
                continue
            cup = parent_to_slot[p_uid]
            tmprows.append([tray,
                            cup,
                            p_uid,
                            c_uid,
                            options['dilute_factor'],
                            ""])
            ARs_exported.append(p_uid)
        tmprows.sort(lambda a,b:cmp(a[1], b[1]))
        rows += tmprows

        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=';')
        assert(writer)
        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Length',len(result))
        setheader('Content-Type', 'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.request.RESPONSE.write(result)

class Import(BrowserView):
    """ Read FIAStar analysis results
    """

    template = "fiastar_import.pt"

    def __call__(self):

        if 'submitted' not in self.request:
            return self.template()

        csvfile = self.request.form['csvfile']

        pc = getToolByName(self.context, 'portal_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        uc = getToolByName(self.context, 'uid_catalog')
        wf_tool = getToolByName(self.context, 'portal_workflow')

        updateable_states = ['sample_received', 'assigned', 'not_requested']
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

        rows = []
        batch_headers = None
        fia1 = False
        fia2 = False
        # place all valid rows into list of dict by CSV row title
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
            rows.append(row)

        log = []
        for row in rows:
            param = row['Parameter']
            service = kw_map[param]
            keyword = service.getKeyword()
            calc = service.getCalculation()
            interim_fields = calc and calc.getInterimFields() or []

            p_uid = row['Sample name']
            parent = uc(UID = p_uid)
            if len(parent) == 0:
                log.append('ERROR: no analysis parent %s' % row['Sample name'])
                continue
            parent = parent[0].getObject()

            c_uid = row['Sample type']
            container = uc(UID = c_uid)
            if len(container) == 0:
                log.append('ERROR: no analysis container %s' % row['Sample name'])
                continue
            container = container[0].getObject()

            # Duplicates.
            if c_uid == self.context.UID():
                # The analyses should exist already
                # or no results will be imported.
                analysis = None
                for dup in self.context.objectValues():
                    if dup.aq_parent == p_uid and \
                       dup.getKeyword() in (options['F SO2'], options['T SO2']):
                        analysis = dup
                if not analysis:
                    log.append('ERROR: no duplicate analysis found for slot %s' % row['Cup'])
                    continue
                row['analysis'] = analysis
            else:
                analyses = parent.objectIds()
                if keyword in analyses:
                    # analysis exists for this parameter.
                    row['analysis'] = parent.get(keyword)
                else:
                    # analysis does not exist;
                    # create new analysis and set 'results_not_requested' state
                    parent.invokeFactory(type_name="Analysis", id = keyword)
                    analysis = parent[keyword]
                    analysis.edit(Service = service,
                                  InterimFields = interim_fields,
                                  MaxTimeAllowed = service.getMaxTimeAllowed())
                    msg = parent.translate("FOSS FIAStar")
                    changeWorkflowState(analysis, 'not_requested', comments=msg)

                    analysis.unmarkCreationFlag()
                    zope.event.notify(ObjectInitializedEvent(analysis))
                    row['analysis'] = analysis

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
