from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Registry import registerField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, INSTRUMENT_EXPORTS, PROJECTNAME
from bika.lims.config import AddAndRemoveAnalyses, ManageResults
from Products.ATExtensions.ateapi import RecordsField
from zope.interface import implements
from bika.lims.interfaces import IWorksheet
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('WorksheetTemplate',
        allowed_types = ('WorksheetTemplate',),
        relationship = 'WorksheetAnalysisTemplate',
    ),
    RecordsField('Layout',
        required = 1,
        subfields = ('position', 'type', 'container_uid', 'analysis_uid'),
        subfield_types = {'position':'int'},
    ),
    # all layout info lives in Layout; Analyses is used for back references.
    ReferenceField('Analyses',
        required = 1,
        multiValued = 1,
        allowed_types = ('Analysis',),
        relationship = 'WorksheetAnalysis',
    ),
    StringField('Analyst',
    ),
    TextField('Notes',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _('Notes')
        ),
    ),
),
)

IdField = schema['id']
IdField.required = 0
IdField.widget.visible = False
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Worksheet(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    implements(IWorksheet)
    archetype_name = 'Worksheet'
    schema = schema

    def Title(self):
        return self.id

    def getFolderContents(self, contentFilter):
        # The bika_listing machine passes contentFilter to all
        # contentsMethod methods.  We ignore it.
        return list(self.getAnalyses())

    security.declareProtected(AddAndRemoveAnalyses, 'addAnalysis')
    def addAnalysis(self, analysis, position=None):
        """- add the analysis to self.Analyses().
           - try to add the analysis parent in the worksheet layout according
             to the worksheet's template, if possible.
        """
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, 'reference_catalog')

        analysis_uid = analysis.UID()
        parent_uid = analysis.aq_parent.UID()
        analyses = self.getAnalyses()
        layout = self.getLayout()
        wst = self.getWorksheetTemplate()
        wstlayout = wst and wst.getLayout() or []

        # adding analyses to cancelled worksheet reinstates it
        if wf.getInfoFor(self, 'cancellation_state', '') == 'cancelled':
            wf.doActionFor(self, 'reinstate')

        # check if this analysis is already in the layout
        if analysis_uid in [l['analysis_uid'] for l in layout]:
            return

        self.setAnalyses(analyses + [analysis,])

        # if not, get first available position in max(layout)
        # if not, get next position after max(layout)

        # if our parent has a position, use that one.
        if analysis.aq_parent.UID() in [slot['container_uid'] for slot in layout if \
                                        slot['type'] == 'a']:
            position = [slot['position'] for slot in layout if \
                        slot['container_uid'] == analysis.aq_parent.UID()][0]
        else:
            if not position:
                position = max([int(slot['position']) for slot in layout])+1
                if wst:
                    used_positions = [slot['position'] for slot in layout]
                    available_positions = [row['pos'] for row in wstlayout \
                                           if row['pos'] not in used_positions and \
                                              row['type'] == 'a'] or [position,]
                    position = available_positions[0]
        self.setLayout(layout + [{'position': position,
                                  'type': 'a',
                                  'container_uid': parent_uid,
                                  'analysis_uid': analysis.UID()},])

    security.declareProtected(AddAndRemoveAnalyses, 'removeAnalysis')
    def removeAnalysis(self, analysis):
        """ delete an analyses from the worksheet and un-assign it
        """
        Analyses = self.getAnalyses()
        Analyses.remove(analysis)
        self.setAnalyses(Analyses)

        # perhaps it's entire slot is now removed.
        parents = {}
        for A in Analyses:
            parent_uid = A.aq_parent.UID()
            if parent_uid in parents:
                parents[parent_uid]['analyses'].append(A)
            else:
                parents[parent_uid] = {'parent':A.aq_parent, 'analyses': [A,]}
        Layout = self.getLayout()
        for slot in self.getLayout():
            if not slot['container_uid'] in parents:
                Layout.remove(slot)
        self.setLayout(Layout)

    def addReferences(self, position, reference, service_uids):
        """ Add reference analyses to reference, and add to worksheet layout
        """
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, 'reference_catalog')
        analyses = self.getAnalyses()
        layout = self.getLayout()
        wst = self.getWorksheetTemplate()
        wstlayout = wst and wst.getLayout() or []
        ref_type = reference.getBlank() and 'b' or 'c'
        ref_uid = reference.UID()

        # adding analyses to cancelled worksheet reinstates it
        if wf.getInfoFor(self, 'cancellation_state', '') == 'cancelled':
            wf.doActionFor(self, 'reinstate')

        if position == 'new':
            highest_existing_position = len(wstlayout)
            for pos in [int(slot['position']) for slot in layout]:
                if pos > highest_existing_position:
                    highest_existing_position = pos
            position = highest_existing_position + 1

        # find out which services already have analyses in this slot
        slot_analyses = [slot['analysis_uid'] for slot in layout if \
                                    slot['container_uid'] == ref_uid]
        existing_services_in_pos = []
        if [slot['container_uid'] for slot in layout if slot['container_uid'] == reference.UID()]:
            for analysis in analyses:
                if analysis.aq_parent.UID() == reference.UID():
                    existing_services_in_pos.append(analysis.getService().UID())

        for service_uid in service_uids:
            if service_uid in existing_services_in_pos:
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis = rc.lookupObject(ref_uid)
            self.setLayout(
                self.getLayout() + [{'position' : position,
                                     'type':ref_type,
                                     'container_uid' : reference.UID(),
                                     'analysis_uid': ref_analysis.UID()}])
            self.setAnalyses(
                self.getAnalyses() + [ref_analysis,])


    security.declareProtected(AddAndRemoveAnalyses, 'addDuplicateAnalyses')
    def addDuplicateAnalyses(self, src_slot, dest_slot):
        """ add duplicate analyses to worksheet
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        wf = getToolByName(self, 'portal_workflow')

        analyses = self.getAnalyses()
        layout = self.getLayout()
        wst = self.getWorksheetTemplate()
        wstlayout = wst and wst.getLayout() or []

        src_ar = [slot['container_uid'] for slot in layout if \
                  slot['position'] == src_slot]
        if src_ar:
            src_ar = src_ar[0]

        # check/overwrite/set dest_slot
        if src_ar in [slot['container_uid'] for slot in layout if \
                      slot['type'] == 'd']:
            dest_slot = [slot['position'] for slot in layout if \
                         slot['container_uid'] == src_ar and \
                         slot['type'] == 'd'][0]
        else:
            if not dest_slot or dest_slot == 'new':
                highest_existing_position = len(wstlayout)
                for pos in [int(slot['position']) for slot in layout]:
                    if pos > highest_existing_position:
                        highest_existing_position = pos
                dest_slot = highest_existing_position + 1

        src_analyses = [rc.lookupObject(slot['analysis_uid']) \
                        for slot in layout if \
                        slot['position'] == src_slot]
        dest_analyses = [rc.lookupObject(slot['analysis_uid']).getAnalysis().UID() \
                        for slot in layout if \
                        slot['position'] == dest_slot]

        for analysis in src_analyses:
            if analysis.UID() in dest_analyses:
                continue
            service = analysis.getService()
            keyword = service.getKeyword()
            duplicate_id = self.generateUniqueId('DuplicateAnalysis')
            self.invokeFactory('DuplicateAnalysis', id = duplicate_id)
            duplicate = self[duplicate_id]
            duplicate.setAnalysis(analysis)
            duplicate.processForm()
            wf.doActionFor(duplicate, 'assign')
            self.setLayout(
                self.getLayout() + [{'position':dest_slot,
                                     'type':'d',
                                     'container_uid':analysis.aq_parent.UID(),
                                     'analysis_uid': duplicate.UID()},]
            )
            self.setAnalyses(self.getAnalyses() + [duplicate,])

    def getInstrumentExports(self):
        """ return the possible instrument export formats """
        return INSTRUMENT_EXPORTS

    def instrument_export_form(self, REQUEST, RESPONSE):
        """ Redirect to the instrument export form template """
        RESPONSE.redirect('%s/instrument_export' % self.absolute_url())

    def exportAnalyses(self, REQUEST = None, RESPONSE = None):
        """ Export analyses from this worksheet """
        import bika.lims.InstrumentExport as InstrumentExport
        instrument = REQUEST.form['getInstrument']
        try:
            func = getattr(InstrumentExport, "%s_export" % instrument)
        except:
            return
        func(self, REQUEST, RESPONSE)
        return

    security.declarePublic('getPosAnalyses')
    def getPosAnalyses(self, pos):
        """ return the analyses in a particular position
        """
        try:
            this_pos = int(pos)
        except:
            return []
        rc = getToolByName(self, REFERENCE_CATALOG)
        analyses = []
        for item in self.getLayout():
            if item['pos'] == this_pos:
                analysis = rc.lookupObject(item['uid'])
                analyses.append(analysis)
        return analyses

    security.declarePublic('searchAnalyses')
    def searchAnalyses(self, REQUEST, RESPONSE):
        """ return search form - analyses action stays active because we
            set 'template_id'
        """
        return self.worksheet_search_analysis(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'manage_results')

    security.declareProtected(AddAndRemoveAnalyses, 'assignNumberedAnalyses')
    def assignNumberedAnalyses(self, analyses):
        """ assign selected analyses to worksheet
            Analyses = [(pos, uid),]
        """
        for pos_uid in analyses:
            pos = pos_uid[0]
            uid = pos_uid[1]
            self._assignAnalyses([uid, ])
            self._addToSequence('a', pos, [uid, ])

        message = self.translate('message_analyses_assigned', default = 'Analyses assigned', domain = 'bika')
        utils = getToolByName(self, 'plone_utils')
        utils.addPortalMessage(message, type = u'info')

    security.declareProtected(AddAndRemoveAnalyses, 'assignUnnumberedAnalyses')
    def assignUnnumberedAnalyses(self, REQUEST = None, RESPONSE = None, Analyses = []):
        """ assign selected analyses to worksheet
            Analyses = [uid,]
        """
        analysis_seq = []
        if Analyses:
            self._assignAnalyses(Analyses)
            for analysis in Analyses:
                analysis_seq.append(analysis)
            self._addToSequence('a', 0, analysis_seq)

            message = self.translate('message_analyses_assigned', default = 'Analyses assigned', domain = 'bika')
            utils = getToolByName(self, 'plone_utils')
            utils.addPortalMessage(message, type = u'info')
        if REQUEST:
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    def addWSAttachment(self, REQUEST = None, RESPONSE = None):
        """ Add the file as an attachment
        """
        this_file = self.REQUEST.form['AttachmentFile_file']
        if self.REQUEST.form.has_key('Analysis'):
            analysis_uid = self.REQUEST.form['Analysis']
        else:
            analysis_uid = None
        if self.REQUEST.form.has_key('Service'):
            service_uid = self.REQUEST.form['Service']
        else:
            service_uid = None

        tool = getToolByName(self, REFERENCE_CATALOG)
        if analysis_uid:
            analysis = tool.lookupObject(analysis_uid)
            attachmentid = self.generateUniqueId('Attachment')
            client = analysis.aq_parent.aq_parent
            client.invokeFactory(id = attachmentid, type_name = "Attachment")
            attachment = client._getOb(attachmentid)
            attachment.edit(
                AttachmentFile = this_file,
                AttachmentType = self.REQUEST.form['AttachmentType'],
                AttachmentKeys = self.REQUEST.form['AttachmentKeys'])
            attachment.processForm()
            attachment.reindexObject()

            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)

        if service_uid:
            wf_tool = self.portal_workflow
            for analysis in self.getAnalyses():
##            getServiceUID = service_uid,
##                                             review_state = ('assigned', 'to_be_verified')):
                attachmentid = self.generateUniqueId('Attachment')
                client = analysis.aq_parent.aq_parent
                client.invokeFactory(id = attachmentid, type_name = "Attachment")
                attachment = client._getOb(attachmentid)
                attachment.edit(
                    AttachmentFile = this_file,
                    AttachmentType = self.REQUEST.form['AttachmentType'],
                    AttachmentKeys = self.REQUEST.form['AttachmentKeys'])
                attachment.processForm()
                attachment.reindexObject()

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)

        if RESPONSE:
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    def getAllAnalyses(self, contentFilter = None):
        """ get all the analyses of different types linked to this WS
            contentFilter is supplied by BikaListingView, and ignored.
        """

        analyses = []
        for analysis in self.getAnalyses():
            analyses.append(analysis)

        for analysis in self.getReferenceAnalyses():
            analyses.append(analysis)

        for analysis in self.objectValues('DuplicateAnalysis'):
            analyses.append(analysis)

        return analyses

    security.declarePublic('getReferencePositions')
    def getReferencePositions(self, type, reference_uid):
        """ get the current reference positions and analyses
        """

        seq = {}
        positions = {}

        for item in self.getLayout():
            seq[item['uid']] = item['pos']
        services = ''
        for analysis in self.getReferenceAnalyses():
            if (analysis.getReferenceType() == type) & \
               (analysis.getReferenceSampleUID() == reference_uid):
                pos = seq[analysis.UID()]
                if not positions.has_key(pos):
                    positions[pos] = {}
                    services = analysis.getServiceUID()
                else:
                    services = services + ';' + analysis.getServiceUID()
                positions[pos] = services


        return positions

    security.declarePublic('getARServices')
    def getARServices(self, ar_id):
        """ get the current AR services
        """
        dup_pos = 0

        seq = {}
        for item in self.getLayout():
            seq[item['uid']] = item['pos']

        services = []
        for analysis in self.getAnalyses():
            if (analysis.getRequestID() == ar_id):
                services.append(analysis.getService())

        duplicates = []
        for dup in self.objectValues('DuplicateAnalysis'):
            if (dup.getRequest().getRequestID() == ar_id):
                dup_pos = seq[dup.UID()]
                duplicates.append(dup.getServiceUID())

        results = {'services': services,
                   'dup_uids': duplicates,
                   'pos': dup_pos
                   }

        return results

    security.declarePublic('getAnalysisRequests')
    def getAnalysisRequests(self):
        """ get the ars associated with this worksheet
        """
        ars = {}

        for analysis in self.getAnalyses():
            if not ars.has_key(analysis.getRequestID()):
                ars[analysis.getRequestID()] = analysis.aq_parent

        ar_ids = ars.keys()
        ar_ids.sort()
        results = []
        for ar_id in ar_ids:
            results.append(ars[ar_id])
        return results

    security.declarePublic('getWorksheetServices')
    def getWorksheetServices(self):
        """ get list of analysis services present on this worksheet
        """
        services = []
        for analysis in self.getAnalyses():
            service = analysis.getService()
            if service not in services:
                services.append(service)
        return services

    security.declareProtected(AddAndRemoveAnalyses, 'resequenceWorksheet')
    def resequenceWorksheet(self, REQUEST = None, RESPONSE = None):
        """  Reset the sequence of analyses in the worksheet """
        """ sequence is [{'pos': , 'type': , 'uid', 'key'},] """
        old_seq = self.getLayout()
        new_dict = {}
        new_seq = []
        other_dict = {}
        for seq in old_seq:
            if seq['key'] == '':
                if not other_dict.has_key(seq['pos']):
                    other_dict[seq['pos']] = []
                other_dict[seq['pos']].append(seq)
                continue
            if not new_dict.has_key(seq['key']):
                new_dict[seq['key']] = []
            analyses = new_dict[seq['key']]
            analyses.append(seq)
            new_dict[seq['key']] = analyses
        new_keys = new_dict.keys()
        new_keys.sort()

        rc = getToolByName(self, REFERENCE_CATALOG)
        seqno = 1
        for key in new_keys:
            analyses = {}
            if len(new_dict[key]) == 1:
                new_dict[key][0]['pos'] = seqno
                new_seq.append(new_dict[key][0])
            else:
                for item in new_dict[key]:
                    item['pos'] = seqno
                    analysis = rc.lookupObject(item['uid'])
                    service = analysis.Title()
                    analyses[service] = item
                a_keys = analyses.keys()
                a_keys.sort()
                for a_key in a_keys:
                    new_seq.append(analyses[a_key])
            seqno += 1
        other_keys = other_dict.keys()
        other_keys.sort()
        for other_key in other_keys:
            for item in other_dict[other_key]:
                item['pos'] = seqno
                new_seq.append(item)
            seqno += 1

        self.setLayout(new_seq)
        RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    def _addToSequence(self, type, position, analyses):
        """ Layout is [{'uid': , 'type': , 'pos', 'key'},] """
        """ analyses [uids,]       """
        ws_seq = self.getLayout()
        rc = getToolByName(self, REFERENCE_CATALOG)

        if position == 0:
            used_pos = []
            key_dict = {}
            for seq in ws_seq:
                used_pos.append(seq['pos'])
                key_dict[seq['key']] = seq['pos']

            used_pos.sort()
            first_available = 1

        for analysis in analyses:
            if type == 'a':
                analysis_obj = rc.lookupObject(analysis)
                keyvalue = analysis_obj.getRequestID()
            else:
                keyvalue = ''
            if position == 0:
                new_pos = None
                if type == 'a':
                    if key_dict.has_key(keyvalue):
                        new_pos = key_dict[keyvalue]
                if not new_pos:
                    empty_found = False
                    new_pos = first_available
                    while not empty_found:
                        if new_pos in used_pos:
                            new_pos = new_pos + 1
                        else:
                            empty_found = True
                            first_available = new_pos + 1
                    used_pos.append(new_pos)
                    used_pos.sort()
                    if type == 'a':
                        key_dict[keyvalue] = new_pos
                    else:
                        position = new_pos
            else:
                new_pos = position

            element = {'uid': analysis,
                       'type': type,
                       'pos': new_pos,
                       'key': keyvalue}
            ws_seq.append(element)

        self.setLayout(ws_seq)

    def _removeFromSequence(self, analyses):
        """ analyses is [analysis.UID] """
        ws_seq = self.getLayout()

        new_seq = []
        for pos in ws_seq:
            if pos['uid'] not in analyses:
                new_seq.append(pos)

        self.setLayout(new_seq)

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(Worksheet, PROJECTNAME)
