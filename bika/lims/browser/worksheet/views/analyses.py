# coding=utf-8
from operator import itemgetter
from Products.CMFPlone.i18nl10n import ulocalized_time

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView as BaseView


class AnalysesView(BaseView):
    """ This renders the table for ManageResultsView.
    """
    def __init__(self, context, request):
        BaseView.__init__(self, context, request)
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'portal_type':'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state':'unassigned'}
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.contentFilter = {}
        self.show_select_row = False
        self.show_sort_column = False
        self.allow_edit = True
        self.show_categories = False
        self.expand_all_categories = False

        self.columns = {
            'Pos': {'title': _('Position')},
            'DueDate': {'title': _('Due Date')},
            'Service': {'title': _('Analysis')},
            'getPriority': {'title': _('Priority')},
            'Method': {'title': _('Method')},
            'DetectionLimit': {
                'title': _('DL'),
                'sortable': False,
                'toggle': False},
            'Result': {'title': _('Result'),
                       'input_width': '6',
                       'input_class': 'ajax_calculate numeric',
                       'sortable': False},
            'Uncertainty': {'title': _('+-')},
            'ResultDM': {'title': _('Dry')},
            'retested': {'title': "<img src='++resource++bika.lims.images/retested.png' title='%s'/>" % _('Retested'),
                         'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'Instrument': {'title': _('Instrument')},
            'state_title': {'title': _('State')},
            'Priority': { 'title': _('Priority'), 'index': 'Priority'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [{'id':'submit'},
                             {'id':'verify'},
                             {'id':'retract'},
                             {'id':'unassign'}],
             'columns':['Pos',
                        'Service',
                        'Priority',
                        'Method',
                        'Instrument',
                        'DetectionLimit',
                        'Result',
                        'Uncertainty',
                        'DueDate',
                        'state_title',
                        'Attachments']
             },
        ]

    def folderitems(self):
        self.analyst = self.context.getAnalyst().strip()
        self.instrument = self.context.getInstrument()
        self.contentsMethod = self.context.getFolderContents
        items = BaseView.folderitems(self)
        layout = self.context.getLayout()
        highest_position = 0
        new_items = []
        for x, item in enumerate(items):
            obj = item['obj']
            pos = [slot['position'] for slot in layout if
                   slot['analysis_uid'] == obj.UID()][0]

            # compensate for possible bad data (dbw#104)
            if type(pos) in (list, tuple):
                pos = pos[0]
                if pos == 'new':
                    continue
            pos = int(pos)

            highest_position = max(highest_position, pos)
            items[x]['Pos'] = pos
            items[x]['colspan'] = {'Pos':1}
            service = obj.getService()
            method = service.getMethod()
            items[x]['Service'] = service.Title()
            items[x]['Priority'] = ''
            #items[x]['Method'] = method and method.Title() or ''
            items[x]['class']['Service'] = 'service_title'
            items[x]['Category'] = service.getCategory() and service.getCategory().Title() or ''
            if obj.portal_type == "ReferenceAnalysis":
                items[x]['DueDate'] = self.ulocalized_time(obj.aq_parent.getExpiryDate(), long_format=0)
            else:
                items[x]['DueDate'] = self.ulocalized_time(obj.getDueDate())

            items[x]['Order'] = ''
            instrument = obj.getInstrument()
            #items[x]['Instrument'] = instrument and instrument.Title() or ''

            new_items.append(item)
        items = new_items

        # insert placeholder row items in the gaps
        # This is done badly to compensate for possible bad data (dbw#104)
        empties = []
        used = []
        for slot in layout:
            position = slot['position']
            if type(position) in (list, tuple):
                position = position[0]
                if position == 'new':
                    continue
            position = int(position)
            used.append(position)

        for pos in range(1, highest_position + 1):
            if pos not in used:
                empties.append(pos)
                item = {}
                item.update({
                    'obj': self.context,
                    'id': self.context.id,
                    'uid': self.context.UID(),
                    'title': self.context.Title(),
                    'type_class': 'blank-worksheet-row',
                    'url': self.context.absolute_url(),
                    'relative_url': self.context.absolute_url(),
                    'view_url': self.context.absolute_url(),
                    'path': "/".join(self.context.getPhysicalPath()),
                    'before': {},
                    'after': {},
                    'choices': {},
                    'class': {},
                    'state_class': 'state-empty',
                    'allow_edit': [],
                    'colspan': {'Pos':len(self.columns) + len(self.interim_fields)},
                    'rowspan': {'Pos':1},
                    'Pos': pos,
                    'Service': '',
                    'Attachments': '',
                    'state_title': 's',})
                item['replace'] = {
                    'Pos': "<table width='100%' cellpadding='0' cellspacing='0'>" + \
                            "<tr><td class='pos'>%s</td>" % pos + \
                            "<td align='right'>&nbsp;</td></tr></table>",
                    'select_column': '',
                    }
                items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        try:
            items = sorted(items, key = itemgetter('Pos'))
        except:
            pass

        slot_items = {} # pos:[item_nrs]
        for x in range(len(items)):
            p = items[x]['Pos']
            if p in slot_items:
                slot_items[p].append(x)
            else:
                slot_items[p] = [x, ]
        actual_table_position = -1
        # The first item in items[this position] gets a rowspan for it's
        # "Position" column, which spans all other table rows in this position.
        for pos, pos_items in slot_items.items():
            actual_table_position += 1
            x = pos_items[0]
            if pos in empties:
                continue

            # set Pos column for this row, to have a rowspan
            # Analysis Remarks only allowed for Analysis types
            # Needs to look inside all slot analyses, cause some of them can
            # have remarks entered and can have different analysis statuses
            rowspan = len(pos_items)
            remarksenabled = self.context.bika_setup.getEnableAnalysisRemarks()
            for pos_subitem in pos_items:
                subitem = items[pos_subitem]
                isanalysis = subitem['obj'].portal_type == 'Analysis'
                hasremarks = True if subitem.get('Remarks', '') else False
                remarksedit = remarksenabled and 'Remarks' in subitem.get('allow_edit', [])
                if isanalysis and (hasremarks or remarksedit):
                    rowspan += 1
            items[x]['rowspan'] = {'Pos': rowspan}

            obj = items[x]['obj']
            # fill the rowspan with a little table
            # parent is either an AR, a Worksheet, or a
            # ReferenceSample (analysis parent).
            parent = obj.aq_parent
            if parent.aq_parent.portal_type == "WorksheetFolder":
                # we're a duplicate; get original object's client
                client = obj.getAnalysis().aq_parent.aq_parent
            elif parent.aq_parent.portal_type == "ReferenceSupplier":
                # we're a reference sample; get reference definition
                client = obj.getReferenceDefinition()
            else:
                client = parent.aq_parent
            pos_text = "<table class='worksheet-position' width='100%%' cellpadding='0' cellspacing='0' style='padding-bottom:5px;'><tr>" + \
                       "<td class='pos' rowspan='3'>%s</td>" % pos

            if obj.portal_type == 'ReferenceAnalysis':
                pos_text += "<td class='pos_top'>%s</td>" % obj.getReferenceAnalysesGroupID()
            elif obj.portal_type == 'DuplicateAnalysis' and \
                obj.getAnalysis().portal_type == 'ReferenceAnalysis':
                pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.id)
            elif client:
                pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                    (client.absolute_url(), client.Title())
            else:
                pos_text += "<td class='pos_top'>&nbsp;</td>"

            pos_text += "<td class='pos_top_icons' rowspan='3'>"
            if obj.portal_type == 'DuplicateAnalysis':
                pos_text += "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>" % (_("Duplicate").encode('utf-8'), self.context.absolute_url())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'b':
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/blank.png'></a>" % (parent.absolute_url(), parent.Title())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'c':
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/control.png'></a>" % (parent.absolute_url(), parent.Title())
                pos_text += "<br/>"
            if parent.portal_type == 'AnalysisRequest':
                sample = parent.getSample()
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/sample.png'></a>" % (sample.absolute_url(), sample.Title())
            pos_text += "</td></tr>"

            pos_text += "<tr><td>"
            if parent.portal_type == 'AnalysisRequest':
                pos_text += "<a href='%s'>%s</a>" % (parent.absolute_url(), parent.Title())
            elif parent.portal_type == 'ReferenceSample':
                pos_text += "<a href='%s'>%s</a>" % (parent.absolute_url(), parent.Title())
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += "<a style='white-space:nowrap' href='%s'>%s</a>" % (obj.getAnalysis().aq_parent.absolute_url(), obj.getReferenceAnalysesGroupID())
            elif parent.portal_type == 'Worksheet':
                parent = obj.getAnalysis().aq_parent
                pos_text += "<a href='%s'>(%s)</a>" % (parent.absolute_url(), parent.Title())
            pos_text += "</td></tr>"

            # sampletype
            pos_text += "<tr><td>"
            if obj.portal_type == 'Analysis':
                pos_text += obj.aq_parent.getSample().getSampleType().Title()
            elif obj.portal_type == 'ReferenceAnalysis' or \
                (obj.portal_type == 'DuplicateAnalysis' and \
                 obj.getAnalysis().portal_type == 'ReferenceAnalysis'):
                pos_text += "" #obj.aq_parent.getReferenceDefinition().Title()
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += obj.getAnalysis().aq_parent.getSample().getSampleType().Title()
            pos_text += "</td></tr>"

            # samplingdeviation
            if obj.portal_type == 'Analysis':
                deviation = obj.aq_parent.getSample().getSamplingDeviation()
                if deviation:
                    pos_text += "<tr><td>&nbsp;</td>"
                    pos_text += "<td colspan='2'>"
                    pos_text += deviation.Title()
                    pos_text += "</td></tr>"

##            # barcode
##            barcode = parent.id.replace("-", "")
##            if obj.portal_type == 'DuplicateAnalysis':
##                barcode += "D"
##            pos_text += "<tr><td class='barcode' colspan='3'><div id='barcode_%s'></div>" % barcode + \
##                "<script type='text/javascript'>$('#barcode_%s').barcode('%s', 'code128', {'barHeight':15, addQuietZone:false, showHRI: false })</script>" % (barcode, barcode) + \
##                "</td></tr>"

            pos_text += "</table>"

            items[x]['replace']['Pos'] = pos_text
            items[x]['getPriority'] = '' #Icon get added by adapter

        for k,v in self.columns.items():
            self.columns[k]['sortable'] = False

        return items
