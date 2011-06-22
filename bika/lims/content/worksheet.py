from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
#from Products.CMFPlone import transaction_note
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, INSTRUMENT_EXPORTS, PROJECTNAME
from bika.lims.config import AssignAnalyses, DeleteAnalyses, \
    SubmitResults, ManageWorksheets, ManageBika
from Products.ATExtensions.ateapi import RecordsField
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from zope.interface import implements
from bika.lims.interfaces import IWorksheet,IHaveNoByline
from bika.lims.browser.fields import WorksheetAnalysesField

schema = BikaSchema.copy() + Schema((
    StringField('Number',
        index = 'FieldIndex',
        required = 1,
        searchable = 1,
        default_method = 'getNextWorksheetNumber',
        widget = StringWidget(
            label = 'Worksheet number',
            label_msgid = 'label_worksheetnumber',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ComputedField('Owner',
        expression = 'context.getOwnerUserID()',
        widget = ComputedWidget(
            label = 'Owner',
            label_msgid = 'label_owner',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Analyses',
        multiValued = 1,
        allowed_types = ('Analysis',),
        relationship = 'WorksheetAnalysis',
        widget = ReferenceWidget(
            label = 'Analyses',
            label_msgid = 'label_analyses',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ReferenceField('StandardAnalyses',
        multiValued = 1,
        allowed_types = ('StandardAnalysis',),
        relationship = 'WorksheetStandardAnalysis',
        widget = ReferenceWidget(
            label = 'StandardAnalyses',
            label_msgid = 'label_standardanalyses',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    ReferenceField('LinkedWorksheet',
        multiValued = 1,
        allowed_types = ('Worksheet',),
        relationship = 'WorksheetWorksheet',
        widget = ReferenceWidget(
            label = 'Worksheet',
            label_msgid = 'label_worksheet',
            i18n_domain = I18N_DOMAIN,
            visible = False,
        ),
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes'
        ),
    ),
    # The physical sequence of the analyses in the tray 
    WorksheetAnalysesField('WorksheetLayout',
    ),
    # The lab personnel who performed the analysis
    StringField('Analyser',
        vocabulary = 'getAnalysersDisplayList',
    ),

    IntegerField('MaxPositions',
        widget = IntegerWidget(
            label = "Maximum Positions Allowed",
            label_msgid = 'label_max_positions',
            description = 'Maximum positions allowed on ' \
                        'the worksheet',
            description_msgid = 'help_max_positions',
        ),
    ),
    ComputedField('Status',
        expression = 'context.getWorkflowState()',
        widget = ComputedWidget(
            visible = False,
        )
    ),
),
)

IdField = schema['id']
IdField.required = 0
IdField.widget.visible = False
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Worksheet(BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    implements(IWorksheet, IHaveNoByline)
    archetype_name = 'Worksheet'
    schema = schema

    def Title(self):
        """ Return the Number as title """
        return self.getNumber()

    security.declareProtected(View, 'getOwnerUserID')
    def getOwnerUserID(self):
        """ Return the owner's user id """
        owner_tuple = self.getOwnerTuple()
        return owner_tuple[1]

    def getNextWorksheetNumber(self):
        """ return the next worksheet number """
        return self.getId()

    security.declareProtected(View, 'getWorkflowState')
    def getWorkflowState(self):
        """ compute our own workflow state """
        wf_tool = getToolByName(self, 'portal_workflow')
        return wf_tool.getInfoFor(self, 'review_state', '')

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
        for item in self.getWorksheetLayout():
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
            template_id = 'worksheet_analyses')


    security.declareProtected(AssignAnalyses, 'assignNumberedAnalyses')
    def assignNumberedAnalyses(self, REQUEST = None, RESPONSE = None, Analyses = []):
        """ assign selected analyses to worksheet
            Analyses = [(pos, uid),]
        """
        analyses = []
        analysis_seq = []
        if Analyses:
            for pos_uid in Analyses:
                pos = pos_uid[0]
                uid = pos_uid[1]
                self._assignAnalyses([uid, ])
                self._addToSequence('a', pos, [uid, ])

            message = self.translate('message_analyses_assigned', default = 'Analyses assigned', domain = 'bika')
            utils = getToolByName(self, 'plone_utils')
            utils.addPortalMessage(message, type = u'info')
        if REQUEST:
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    security.declareProtected(AssignAnalyses, 'assignUnnumberedAnalyses')
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
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    def _assignAnalyses(self, Analyses = []):
        """ assign selected analyses to worksheet
        """
        self._delegating_workflow_action = 1

        if Analyses:
            wf_tool = getToolByName(self, 'portal_workflow')
            rc = getToolByName(self, REFERENCE_CATALOG)
            assigned = []
            for uid in Analyses:
                analysis = rc.lookupObject(uid)
                # can only assign to worksheet if state == 'sample_received'
                if wf_tool.getInfoFor(
                    analysis, 'review_state', '') != 'sample_received':
                    continue
                wf_tool.doActionFor(analysis, 'assign')
                analysis.reindexObject()
 #               transaction_note('Changed status of %s at %s' % (
#                    analysis.title_or_id(), analysis.absolute_url()))
                assigned.append(uid)

            assigned = assigned + self.getAnalyses()

            self.setAnalyses(assigned)


        del self._delegating_workflow_action

    security.declareProtected(DeleteAnalyses, 'deleteAnalyses')
    def deleteAnalyses(self, REQUEST, RESPONSE, Analyses = []):
        """ delete analyses from the worksheet and set their state back to
            'sample_received'
            Analyses = [uid,]
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        real_analyses = []
        real_uids = []
        dup_ids = []
        std_uids = []
        std_analyses = []
        for uid in Analyses:
            analysis = rc.lookupObject(uid)
            if analysis.portal_type == 'Analysis':
                real_analyses.append(analysis)
                real_uids.append(uid)
            elif analysis.portal_type == 'DuplicateAnalysis':
                dup_ids.append(analysis.getId())
            elif analysis.portal_type == 'StandardAnalysis':
                std_analyses.append(analysis)
                std_uids.append(uid)

        self._delegating_workflow_action = 1

        if real_analyses:
            wf_tool = getToolByName(self, 'portal_workflow')
            for analysis in real_analyses:
                analysis._assigned_to_worksheet = False
                wf_tool.doActionFor(analysis, 'retract')
 #               transaction_note('Changed status of %s at %s' % (
#                    analysis.title_or_id(), analysis.absolute_url()))

            uids = []
            for a in self.getAnalyses():
                if a.UID() not in real_uids:
                    uids.append(a.UID())
            self.setAnalyses(uids)

        if dup_ids:
            self.manage_delObjects(dup_ids)

        """ Leave analysis on Standard Sample? AVS 
        if std_analyses:
            for std_analysis in std_analyses:
                standard_sample = std_analysis.aq_parent
                standard_sample.manage_delObjects(std_analysis.getId())

        
        """
        if std_uids:
            wf_tool = getToolByName(self, 'portal_workflow')
            for std_analysis in std_analyses:
                review_state = wf_tool.getInfoFor(
                    std_analysis, 'review_state', '')
                if review_state != 'assigned':
                    wf_tool.doActionFor(std_analysis, 'retract')
                wf_tool.doActionFor(std_analysis, 'unassign')
 #               transaction_note('Changed status of %s at %s' % (
#                    std_analysis.title_or_id(), std_analysis.absolute_url()))
            uids = []
            for a in self.getStandardAnalyses():
                if a.UID() not in std_uids:
                    uids.append(a.UID())
            self.setStandardAnalyses(uids)

        self._removeFromSequence(Analyses)
        del self._delegating_workflow_action

        RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

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
                if not analysis.getServiceUID() == service_uid:
                    continue
                review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
                if not review_state in ['assigned', 'to_be_verified']:
                    continue
                attachmentid = self.generateUniqueId('Attachment')
                client = analysis.aq_parent.aq_parent
                client.invokeFactory(id = attachmentid, type_name = "Attachment")
                attachment = client._getOb(attachmentid)
                attachment.edit(
                    AttachmentFile = this_file,
                    AttachmentType = self.REQUEST.form['AttachmentType'],
                    AttachmentKeys = self.REQUEST.form['AttachmentKeys'])
                attachment.reindexObject()

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)

        if RESPONSE:
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    security.declareProtected(SubmitResults, 'submitResults')
    def submitResults(self, analyser = None, results = {}, Notes = None, REQUEST = None, RESPONSE = None):
        """ Submit results, interim results and Analyser
        """
        self.setNotes(Notes)
        wf_tool = self.portal_workflow
        review_state = wf_tool.getInfoFor(
                self, 'review_state', '')
        if review_state != 'open':
            return

        rc = getToolByName(self, REFERENCE_CATALOG)
        states = {}

        if analyser:
            if analyser.strip() == '':
                analyser = None
            self.setAnalyser(analyser)

        worksheet_seq = []

        dm_ars = []
        dm_ar_ids = []
        for key, value in self.REQUEST.form.items():
            if key.startswith('results'):
                UID = key.split('.')[-1]
                analysis = rc.lookupObject(UID)
                if analysis.getCalcType() == 'dep':
                    continue
                # check for no interim state change
                analysis_review_state = wf_tool.getInfoFor(
                        analysis, 'review_state', '')
                if analysis_review_state not in ['assigned']:
                    continue
                result = value.get('Result')
                if result:
                    if result.strip() == '':
                        result = None
                else:
                    result = None

                retested = value.get('Retested')

                uncertainty = None
                service = analysis.getService()

                if result:
                    precision = service.getPrecision()
                    if precision:
                        result = self.get_precise_result(result, precision)
                    uncertainty = self.get_uncertainty(result, service)

                titrationvolume = value.get('TitrationVolume')
                if titrationvolume:
                    if titrationvolume.strip() == '':
                        titrationvolume = None
                else:
                    titrationvolume = None

                titrationfactor = value.get('TitrationFactor')
                if titrationfactor:
                    if titrationfactor.strip() == '':
                        titrationfactor = None
                else:
                    titrationfactor = None

                grossmass = value.get('GrossMass')
                if grossmass:
                    if grossmass.strip() == '':
                        grossmass = None
                else:
                    grossmass = None

                netmass = value.get('NetMass')
                if netmass:
                    if netmass.strip() == '':
                        netmass = None
                else:
                    netmass = None

                vesselmass = value.get('VesselMass')
                if vesselmass:
                    if vesselmass.strip() == '':
                        vesselmass = None
                else:
                    vesselmass = None

                samplemass = value.get('SampleMass')
                if samplemass:
                    if samplemass.strip() == '':
                        samplemass = None
                else:
                    samplemass = None

                analysis.setTitrationVolume(titrationvolume)
                analysis.setTitrationFactor(titrationfactor)
                analysis.setGrossMass(grossmass)
                analysis.setNetMass(netmass)
                analysis.setVesselMass(vesselmass)
                analysis.setSampleMass(samplemass)

                analysis.edit(
                    Result = result,
                    Retested = retested,
                    Uncertainty = uncertainty,
                    Unit = service.getUnit()
                )

                """ calculate dependant results """
                if analysis.portal_type == 'Analysis':
                    if analysis._affects_other_analysis:
                        self.get_dependant_results(analysis)
                    if analysis.aq_parent.getReportDryMatter():
                        if analysis.aq_parent.getId() not in dm_ar_ids:
                            dm_ars.append(analysis.aq_parent)
                            dm_ar_ids.append(analysis.aq_parent.getId())

                """ AVS omit renumbering
                seq = int(value.get('Pos'))
                key = value.get('Key')
                type = value.get('Type')
                sequence = {}
                sequence['pos'] = seq
                sequence['type'] = type
                sequence['uid'] = analysis.UID()
                sequence['key'] = key
                worksheet_seq.append(sequence)
                """

        for ar in dm_ars:
            ar.setDryMatterResults()

        # self.setWorksheetLayout(worksheet_seq)

        if RESPONSE:
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    security.declarePublic('addBlankAnalysis')
    def addBlankAnalysis(self, REQUEST, RESPONSE):
        """ Add a blank analysis to the first available entry
        """

        return self.worksheet_add_blank(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'worksheet_analyses')

    def getAllAnalyses(self):
        """ get all the analyses of different types linked to this WS """

        analyses = []
        for analysis in self.getAnalyses():
            analyses.append(analysis)

        for analysis in self.getStandardAnalyses():
            analyses.append(analysis)

        for analysis in self.objectValues('DuplicateAnalysis'):
            analyses.append(analysis)

        for analysis in self.objectValues('RejectAnalysis'):
            analyses.append(analysis)

        return analyses

    security.declarePublic('getStandardPositions')
    def getStandardPositions(self, type, standard_uid):
        """ get the current standard positions and analyses
        """

        seq = {}
        positions = {}

        for item in self.getWorksheetLayout():
            seq[item['uid']] = item['pos']
        services = ''
        for analysis in self.getStandardAnalyses():
            if (analysis.getStandardType() == type) & \
               (analysis.getStandardSampleUID() == standard_uid):
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
        for item in self.getWorksheetLayout():
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

    security.declarePublic('addDuplicateAnalysis')
    def addDuplicateAnalysis(self, REQUEST, RESPONSE):
        """ Add a duplicate analysis to the first available entry
        """
        return self.worksheet_add_duplicate(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'worksheet_analyses')

    security.declareProtected(AssignAnalyses, 'assignDuplicate')
    def assignDuplicate(self, AR = None, Position = None, Service = [], REQUEST = None, RESPONSE = None):
        """ assign selected analyses to worksheet
        """
        if not AR or not Position or not Service:
            message = self.translate('message_no_dup_assigned', default = 'No duplicate analysis assigned', domain = 'bika')
        else:
            rc = getToolByName(self, REFERENCE_CATALOG)
            ar = rc.lookupObject(AR)
            duplicates = []
            for service_uid in Service:
                service = rc.lookupObject(service_uid)
                service_id = service.getId()
                analysis = ar[service_id]
                duplicate_id = self.generateUniqueId('DuplicateAnalysis')
                self.invokeFactory(id = duplicate_id, type_name = 'DuplicateAnalysis')
                duplicate = self._getOb(duplicate_id)
                duplicate.edit(
                    Request = ar,
                    Service = service,
                    Unit = analysis.getUnit(),
                    Uncertainty = analysis.getUncertainty(),
                    CalcType = analysis.getCalcType(),
                    ServiceUID = service.UID(),
                    WorksheetUID = self.UID()
                )
                duplicate.reindexObject()
                duplicates.append(duplicate.UID())

            self._addToSequence('d', int(Position), duplicates)

            message = self.translate('message_dups_assigned', default = 'Duplicate analyses assigned', domain = 'bika')

        utils = getToolByName(self, 'plone_utils')
        utils.addPortalMessage(message, type = u'info')

        if REQUEST:
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    security.declarePublic('addControlAnalysis')
    def addControlAnalysis(self, REQUEST, RESPONSE):
        """ Add a standard analysis to the first available entry
        """
        return self.worksheet_add_control(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'worksheet_analyses')

    security.declareProtected(AssignAnalyses, 'assignStandard')
    def assignStandard(self, Standard = None, Position = None, Type = None, Service = [], REQUEST = None, RESPONSE = None):
        """ assign selected standard analyses to worksheet
            Standard=uid, Position=number or 'new', Service=[uids]
        """

        if not Standard or not Position or not Service:
            if Type == 'b':
                message = self.translate('message_no_blank_assigned', default = 'No blank analysis assigned', domain = 'bika')
            else:
                message = self.translate('message_no_standard_assigned', default = 'No standard analysis assigned', domain = 'bika')
        else:
            rc = getToolByName(self, REFERENCE_CATALOG)
            assigned = []
            standard = rc.lookupObject(Standard)
            for service_uid in Service:
                sa_uid = standard.addStandardAnalysis(service_uid, Type)
                assigned.append(sa_uid)

            self._addToSequence(Type, int(Position), assigned)
            assigned = assigned + self.getStandardAnalyses()
            self.setStandardAnalyses(assigned)

            if Type == 'b':
                message = self.translate('message_blank_assigned', default = 'Blank analysis has been assigned', domain = 'bika')
            else:
                message = self.translate('message_control_assigned', default = 'Control analysis has been assigned', domain = 'bika')

        utils = getToolByName(self, 'plone_utils')
        utils.addPortalMessage(message, type = u'info')

        if REQUEST:
            RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    security.declareProtected(ManageWorksheets, 'resequenceWorksheet')
    def resequenceWorksheet(self, REQUEST = None, RESPONSE = None):
        """  Reset the sequence of analyses in the worksheet """
        """ sequence is [{'pos': , 'type': , 'uid', 'key'},] """
        old_seq = self.getWorksheetLayout()
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

        self.setWorksheetLayout(new_seq)
        RESPONSE.redirect('%s/worksheet_analyses' % self.absolute_url())

    def _addToSequence(self, type, position, analyses):
        """ WorksheetLayout is [{'uid': , 'type': , 'pos', 'key'},] """
        """ analyses [uids,]       """
        ws_seq = self.getWorksheetLayout()
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

        self.setWorksheetLayout(ws_seq)

    def _removeFromSequence(self, analyses):
        """ analyses is [analysis.UID] """
        ws_seq = self.getWorksheetLayout()

        new_seq = []
        for pos in ws_seq:
            if pos['uid'] not in analyses:
                new_seq.append(pos)

        self.setWorksheetLayout(new_seq)


    def manage_beforeDelete(self, item, container):
        """ retract all analyses before deleting worksheet """
        self._delegating_workflow_action = 1
        wf_tool = self.portal_workflow
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state == 'assigned':
                wf_tool.doActionFor(analysis, 'retract')
            analysis._assigned_to_worksheet = False

        for std_analysis in self.getStandardAnalyses():
            review_state = wf_tool.getInfoFor(
                std_analysis, 'review_state', '')
            if review_state != 'assigned':
                wf_tool.doActionFor(std_analysis, 'retract')
            wf_tool.doActionFor(std_analysis, 'unassign')

        """ AVS - leave standard analyses on Standard Sample?
        std_samples = []
        std_analyses = {}
        for std_analysis in self.getStandardAnalyses():
            parent_uid = std_analysis.aq_parent.UID()
            if not std_analyses.has_key(parent_uid):
                std_samples.append(std_analysis.aq_parent)
                std_analyses[parent_uid] = []

            std_analyses[parent_uid].append(std_analysis.getID())

        for std_sample in std_samples:
            std_sample.manage_delObjects(std_analyses[std_sample.getId()])
        """

        del_ids = [dup.getId() for dup in self.objectValues('DuplicateAnalysis')]
        self.manage_delObjects(del_ids)


        del_ids = [rej.getId() for rej in self.objectValues('RejectAnalysis')]
        self.manage_delObjects(del_ids)

        BaseFolder.manage_beforeDelete(self, item, container)
        del self._delegating_workflow_action


    def workflow_script_submit(self, state_info):
        """ submit sample """

        if getattr(self, '_escalating_workflow_action', None):
            return

        self._delegating_workflow_action = 1
        wf_tool = self.portal_workflow
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if review_state == 'assigned':
                wf_tool.doActionFor(analysis, 'submit')
                analysis.reindexObject()


        del self._delegating_workflow_action

        for std_analysis in self.getStandardAnalyses():
            review_state = wf_tool.getInfoFor(
                std_analysis, 'review_state', '')
            if review_state == 'assigned':
                wf_tool.doActionFor(std_analysis, 'submit')
                std_analysis.reindexObject()

        duplicates = self.objectValues('DuplicateAnalysis')
        for duplicate in duplicates:
            review_state = wf_tool.getInfoFor(
                duplicate, 'review_state', '')
            if review_state == 'assigned':
                wf_tool.doActionFor(duplicate, 'submit')
                duplicate.reindexObject()


    def workflow_script_verify(self, state_info):
        """ verify sample """
        if getattr(self, '_escalating_workflow_action', None):
            return

        self._delegating_workflow_action = 1
        wf_tool = self.portal_workflow
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if review_state == 'to_be_verified':
                wf_tool.doActionFor(analysis, 'verify')
                analysis.reindexObject()
        del self._delegating_workflow_action

        for std_analysis in self.getStandardAnalyses():
            review_state = wf_tool.getInfoFor(
                std_analysis, 'review_state', '')
            if review_state == 'to_be_verified':
                wf_tool.doActionFor(std_analysis, 'verify')
                std_analysis.reindexObject()

        duplicates = self.objectValues('DuplicateAnalysis')
        for duplicate in duplicates:
            review_state = wf_tool.getInfoFor(
                duplicate, 'review_state', '')
            if review_state == 'to_be_verified':
                wf_tool.doActionFor(duplicate, 'verify')
                duplicate.reindexObject()


    def workflow_script_reject(self, state_info):
        """ reject sample  """
        """
            copy real analyses to RejectAnalysis, with link to real
            create a new worksheet, with the original analyses, and new
            duplicates and standards to match the rejected
            worksheet.
        """
        utils = getToolByName(self, 'plone_utils')
        # create a new worksheet
        if getattr(self, '_escalating_workflow_action', None):
            return

        self._delegating_workflow_action = 1

        wf_tool = self.portal_workflow
        seq = self.getWorksheetLayout()
        new_dict = {}
        for item in seq:
            new_dict[item['uid']] = item['pos']
        sequence = []
        new_sequence = []

        # analyses
        analyses = self.getAnalyses()
        new_ws_analyses = []
        old_ws_analyses = []
        for analysis in analyses:
            position = new_dict[analysis.UID()]
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state in ['published', 'verified']:
                old_ws_analyses.append(analysis.UID())
                sequence.append({'pos': position,
                                 'type':'a',
                                 'uid':analysis.UID(),
                                 'key':analysis.getRequestID()})
            else:
                new_ws_analyses.append(analysis.UID())
                reject_id = self.generateUniqueId('RejectAnalysis')
                self.invokeFactory(id = reject_id, type_name = 'RejectAnalysis')
                reject = self._getOb(reject_id)
                reject.edit(
                    Service = analysis.getService(),
                    Request = analysis.aq_parent,
                    Unit = analysis.getUnit(),
                    Result = analysis.getResult(),
                    Retested = analysis.getRetested(),
                    Uncertainty = analysis.getUncertainty(),
                    CalcType = analysis.getCalcType(),
                    InterimCalcs = analysis.getInterimCalcs(),
                )
                reject.reindexObject()
                analysis.edit(
                    Result = None,
                    Retested = True,
                    InterimCalcs = None,
                )
                analysis.reindexObject()
                keyvalue = analysis.getRequestID()
                new_sequence.append({'pos': position,
                                     'type':'a',
                                     'uid':analysis.UID(),
                                     'key':keyvalue})
                sequence.append({'pos': position,
                                 'type':'r',
                                 'uid':reject.UID(),
                                 'key':''})

        self.setAnalyses(old_ws_analyses)

        self._delegating_workflow_action = 1
        worksheets = self.aq_parent
        new_ws_id = worksheets.generateUniqueId('Worksheet')
        worksheets.invokeFactory(id = new_ws_id, type_name = 'Worksheet')
        new_ws = worksheets[new_ws_id]
        new_ws.edit(
            Number = new_ws_id,
            Notes = self.getNotes(),
            Analyses = new_ws_analyses,
            LinkedWorksheet = self.UID()
        )

        current_links = self.getLinkedWorksheet()
        new_links = []
        new_links.append(new_ws.UID())
        for link in current_links:
            new_links.append(link.UID())
        self.setLinkedWorksheet(new_links)

        # Standard analyses
        assigned = []
        std_analyses = self.getStandardAnalyses()
        for std_analysis in std_analyses:
            service_uid = std_analysis.getService().UID()
            standard = std_analysis.aq_parent
            standard_type = std_analysis.getStandardType()
            new_std_uid = standard.addStandardAnalysis(service_uid, standard_type)
            assigned.append(new_std_uid)
            position = new_dict[std_analysis.UID()]
            sequence.append({'pos': position,
                             'type':standard_type,
                             'uid':std_analysis.UID(),
                             'key':''})
            new_sequence.append({'pos': position,
                                 'type':standard_type,
                                 'uid':new_std_uid,
                                 'key':''})

            wf_tool.doActionFor(std_analysis, 'reject')
            std_analysis.reindexObject()
            new_ws.setStandardAnalyses(assigned)

        # duplicates
        duplicates = self.objectValues('DuplicateAnalysis')
        for duplicate in duplicates:
            ar = duplicate.getRequest()
            service = duplicate.getService()
            duplicate_id = new_ws.generateUniqueId('DuplicateAnalysis')
            new_ws.invokeFactory(id = duplicate_id, type_name = 'DuplicateAnalysis')
            new_duplicate = new_ws._getOb(duplicate_id)
            new_duplicate.edit(
                Request = ar,
                Service = service,
                Unit = duplicate.getUnit(),
                CalcType = duplicate.getCalcType(),
            )
            new_duplicate.reindexObject()
            position = new_dict[duplicate.UID()]
            sequence.append({'pos': position,
                             'type':'d',
                             'uid':duplicate.UID(),
                             'key':''})
            new_sequence.append({'pos': position,
                                 'type':'d',
                                 'uid':new_duplicate.UID(),
                                 'key':''})

            wf_tool.doActionFor(duplicate, 'reject')
            duplicate.reindexObject()

        new_ws.setWorksheetLayout(new_sequence)
        self.setWorksheetLayout(sequence)

        for analysis in new_ws.getAnalyses():
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state == 'to_be_verified':
                wf_tool.doActionFor(analysis, 'retract')
                analysis.reindexObject()

#        transaction_note('New worksheet created: %s' % (new_ws_id))
        message = self.translate('message_new_worksheet', default = 'New worksheet ${ws} has been created', mapping = {'ws': new_ws_id}, domain = 'bika')
        utils.addPortalMessage(message, type = u'info')

        del self._delegating_workflow_action

    def workflow_script_retract(self, state_info):
        """ retract sample """
        if getattr(self, '_escalating_workflow_action', None):
            return

        self._delegating_workflow_action = 1
        wf_tool = self.portal_workflow
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(
                analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if review_state in ('to_be_verified', 'verified'):
                wf_tool.doActionFor(analysis, 'retract')
                analysis.reindexObject()
        del self._delegating_workflow_action

        for std_analysis in self.getStandardAnalyses():
            review_state = wf_tool.getInfoFor(
                std_analysis, 'review_state', '')
            if review_state in ('to_be_verified', 'verified'):
                wf_tool.doActionFor(std_analysis, 'retract')
                std_analysis.setDateVerified(None)
                std_analysis.reindexObject()

        duplicates = self.objectValues('DuplicateAnalysis')
        for duplicate in duplicates:
            review_state = wf_tool.getInfoFor(
                duplicate, 'review_state', '')
            if review_state in ('to_be_verified', 'verified'):
                wf_tool.doActionFor(duplicate, 'retract')
                duplicate.setDateVerified(None)
                duplicate.reindexObject()



    def _escalateWorkflowAction(self):
        """ if all analyses have transitioned to next state then our
            state must change too
        """
        if getattr(self, '_delegating_workflow_action', None):
            return

        self._escalating_workflow_action = 1
        wf_tool = self.portal_workflow
        analyses_states = {}
        for analysis in self.getAllAnalyses():
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            analyses_states[review_state] = 1

        # build a state to transition map
        transitions = wf_tool.getTransitionsFor(self)
        wf = wf_tool.getWorkflowById('bika_worksheet_workflow')
        # make a map of transitions
        transition_map = {}
        for t in transitions:
            transition = wf.transitions.get(t['id'])
            transition_map[transition.new_state_id] = transition.id

        state_map = {'assigned': 'open', 'published': 'verified'}
        worksheet_state = wf_tool.getInfoFor(self, 'review_state', '')
        # change the Worksheet to the lowest possible state
        for state_id in ('assigned', 'to_be_verified', 'verified',
                         'published'):
            if analyses_states.has_key(state_id):
                state_id = state_map.get(state_id, state_id)
                if worksheet_state == state_id:
                    break
                elif transition_map.has_key(state_id):
                    wf_tool.doActionFor(self,
                        transition_map.get(state_id))
                    break

        del self._escalating_workflow_action

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    # Present the labmanagers and labtechnicans as options for analyser
    # set the first entry to blank to force selection
    security.declarePublic('getAnalysersDisplayList')
    def getAnalysersDisplayList(self):
        mtool = getToolByName(self, 'portal_membership')
        analysers = {}
        pairs = [(' ', ' '), ]
        analysers = mtool.searchForMembers(roles = ['LabManager', 'LabTechnician'])
        for member in analysers:
            uid = member.getId()
            fullname = member.getProperty('fullname')
            if fullname is None:
                fullname = uid
            pairs.append((uid, fullname))
        return DisplayList(pairs)

    # find the name of the person who performed the analysis
    security.declarePublic('getAnalyserName')
    def getAnalyserName(self):
        uid = self.getAnalyser()
        if uid is None:
            return ' '
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getMemberById(uid)
        if member is None:
            return uid
        else:
            fullname = member.getProperty('fullname')
        if fullname is None:
            return uid
        return fullname

registerType(Worksheet, PROJECTNAME)
