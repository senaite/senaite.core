""" Fiastar
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
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
import json
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
        (they are not always the same; think of multiple duplicates of the same
        analysis.)
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

def Import(context,request):
    """ Read FIAStar analysis results
    """

    template = "fiastar_import.pt"

    csvfile = request.form['file']

    bac = getToolByName(context, 'bika_analysis_catalog')
    uc = getToolByName(context, 'uid_catalog')
    bsc = getToolByName(context, 'bika_setup_catalog')
    workflow = getToolByName(context, 'portal_workflow')

    updateable_states = ['sample_received', 'assigned', 'not_requested']
    now = DateTime().strftime('%Y%m%d-%H%M')

    res = {'errors': [],
           'log': [],}

    options = {'dilute_factor' : 1,
               'F SO2' : 'FSO2',
               'T SO2' : 'TSO2'}
    for k,v in options.items():
        if k in request:
            options[k] = request.get(k)
        else:
            options[k] = v

    # kw_map to lookup Fiastar parameter -> service keyword and vice versa
    kw_map = {}
    for param in ['F SO2', 'T SO2']:
        service = bsc(getKeyword = options[param])
        if not service:
            msg = _('Service keyword ${keyword} not found',
                    mapping = {'keyword': options[param], })
            res['errors'].append(context.translate(msg))
            continue
        service = service[0].getObject()
        kw_map[param] = service
        kw_map[service.getKeyword()] = param

    # all errors at this point are fatal ones
    if res['errors']:
        return json.dumps(res)

    rows = []
    batch_headers = None
    fia1 = False
    fia2 = False
    # place all valid rows into list of dict by CSV row title
    for row in csvfile.readlines():
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
        if fia1:
            row['Peak Mean'] = 0
            row['Peak St dev'] = 0
            row['Concentration Mean'] = 0
            row['Concentration St dev'] = 0
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
            msg = _('Analysis parent UID ${parent_uid} not found',
                    mapping = {'parent_uid': row['Sample name'], })
            res['errors'].append(context.translate(msg))
            continue
        parent = parent[0].getObject()

        c_uid = row['Sample type']
        container = uc(UID = c_uid)
        if len(container) == 0:
            msg = _('Analysis container UID ${parent_uid} not found',
                    mapping = {'container_uid': row['Sample type'], })
            res['errors'].append(context.translate(msg))
            continue
        container = container[0].getObject()

        # Duplicates.
        if p_uid != c_uid:
            dups = [d.getObject() for d in
                    bac(portal_type='DuplicateAnalysis',
                       path={'query': "/".join(container.getPhysicalPath()),
                             'level': 0,})]
            # The analyses should exist already
            # or no results will be imported.
            analysis = None
            for dup in dups:
                if dup.getAnalysis().aq_parent == p_uid and \
                   dup.getKeyword() in (options['F SO2'], options['T SO2']):
                    analysis = dup
            if not analysis:
                msg = _('Duplicate analysis for slot ${slot} not found',
                        mapping = {'slot': row['Cup'], })
                res['errors'].append(context.translate(msg))
                continue
            row['analysis'] = analysis
        else:
            analyses = parent.objectIds()
            if keyword in analyses:
                # analysis exists for this parameter.
                analysis = parent.get(keyword)
                row['analysis'] = analysis
            else:
                # analysis does not exist;
                # create new analysis and set 'results_not_requested' state
                parent.invokeFactory(type_name="Analysis", id = keyword)
                analysis = parent[keyword]
                analysis.edit(Service = service,
                              InterimFields = interim_fields,
                              MaxTimeAllowed = service.getMaxTimeAllowed())
                changeWorkflowState(analysis,
                                    'not_requested',
                                    comments="FOSS FIAStar")

                analysis.unmarkCreationFlag()
                zope.event.notify(ObjectInitializedEvent(analysis))
                row['analysis'] = analysis

        as_state = workflow.getInfoFor(analysis, 'review_state', '')
        if (as_state not in updateable_states):
            msg = _('Analysis ${service} at slot ${slot} in state ${state} - not updated',
                    mapping = {'service': service.Title(),
                               'slot': row['Cup'],
                               'state': as_state,})
            res['errors'].append(context.translate(msg))
            continue
        if analysis.getResult():
            msg = _('Analysis ${service} at slot ${slot} has a result - not updated',
                    mapping = {'service': service.Title(),
                               'slot': row['Cup'], })
            res['errors'].append(context.translate(msg))
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
             'value': row['Concentration'],
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
             'value': row['Deviation'],
             'unit':''},
            ]
        )

        msg = _('Analysis ${service} at slot ${slot}: OK',
                mapping = {'service': service.Title(),
                           'slot': row['Cup'], })
        res['log'].append(context.translate(msg))

    return json.dumps(res)
