from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
#from Products.CMFPlone import transaction_note
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
    StringField('Analyser',
        vocabulary = 'getAnalysersDisplayList',
    ),
    ReferenceField('Analyses',
        required = 1,
        multiValued = 1,
        allowed_types = ('Analysis',),
        relationship = 'WorksheetAnalysis',
    ),
    RecordsField('Layout',
        required = 1,
        subfields = ('position', 'container_uid')
    ),
    TextField('Notes'),
    IntegerField('MaxPositions'),
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
        return self.getAnalyses()

    def assignAnalysis(analysis):
        # - add the analysis to self.Analyses()
        # - try to add the analysis parent in the worksheet layout according to
        #   the worksheet's template, if possible.

        self.setAnalyses(self.getAnalyses() + [analysis,])

        # if our parent object is already in the worksheet layout we're done.
        parent_uid = analysis.aq_parent.UID()
        if parent_uid in [l[1] for l in self.getLayout()]:
            return
        wst = self.getWorksheetTemplate()
        wstlayout = wst.getLayout()
        if analysis.portal_type == 'Analysis':
            analysis_type = 'a'
        elif analysis.portal_type == 'DuplicateAnalysis':
            analysis_type = 'd'
        elif analysis.portal_type == 'ReferenceAnalysis':
            if analysis.getBlank():
                analysis_type = 'b'
            else:
                analysis_type = 'c'
        else:
            raise WorkflowException, _("Invalid Analysis Type")
        wslayout = self.getLayout()
        position = len(wslayout) + 1
        if wst:
            used_positions = [slot['position'] for slot in wslayout]
            available_positions = [row['pos'] for row in wstlayout \
                                   if row['pos'] not in used_positions and \
                                      row['type'] == analysis_type]
            if available_positions:
                position = available_positions[0]
        self.setLayout(layout + [{'position': position,
                                'container_uid': parent_uid},])

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

    def _assignAnalyses(self, Analyses = []):
        """ assign selected analyses to worksheet
        """
        if Analyses:
            workflow = getToolByName(self, 'portal_workflow')
            rc = getToolByName(self, REFERENCE_CATALOG)
            assigned = []
            for uid in Analyses:
                analysis = rc.lookupObject(uid)
                workflow.doActionFor(analysis, 'assign')
                assigned.append(uid)

            self.setAnalyses(self.getAnalyses() + assigned)

    security.declareProtected(AddAndRemoveAnalyses, 'deleteAnalyses')
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
            elif analysis.portal_type == 'ReferenceAnalysis':
                std_analyses.append(analysis)
                std_uids.append(uid)


        if real_analyses:
            wf_tool = getToolByName(self, 'portal_workflow')
            for analysis in real_analyses:
                analysis._assigned_to_worksheet = False
                wf_tool.doActionFor(analysis, 'retract')

            uids = []
            for a in self.getAnalyses():
                if a.UID() not in real_uids:
                    uids.append(a.UID())
            self.setAnalyses(uids)

        if dup_ids:
            self.manage_delObjects(dup_ids)

        """ Leave analysis on Reference Sample? AVS
        if std_analyses:
            for std_analysis in std_analyses:
                reference_sample = std_analysis.aq_parent
                reference_sample.manage_delObjects(std_analysis.getId())
        """
        if std_uids:
            wf_tool = getToolByName(self, 'portal_workflow')
            for std_analysis in std_analyses:
                review_state = wf_tool.getInfoFor(
                    std_analysis, 'review_state', '')
                if review_state != 'assigned':
                    wf_tool.doActionFor(std_analysis, 'retract')
                wf_tool.doActionFor(std_analysis, 'unassign')
            uids = []
            for a in self.getReferenceAnalyses():
                if a.UID() not in std_uids:
                    uids.append(a.UID())
            self.setReferenceAnalyses(uids)

        self._removeFromSequence(Analyses)

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
            for analysis in self.getAnalyses(getServiceUID = service_uid,
                                             review_state = ('assigned', 'to_be_verified')):
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

    security.declareProtected(ManageResults, 'submitResults')
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
                        result = "%%.%df" % precision % result
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

        # self.setLayout(worksheet_seq)

        if RESPONSE:
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    security.declarePublic('addBlankAnalysis')
    def addBlankAnalysis(self, REQUEST, RESPONSE):
        """ Add a blank analysis to the first available entry
        """

        return self.worksheet_add_blank(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'manage_results')

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

        for analysis in self.objectValues('RejectAnalysis'):
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

    security.declarePublic('addDuplicateAnalysis')
    def addDuplicateAnalysis(self, REQUEST, RESPONSE):
        """ Add a duplicate analysis to the first available entry
        """
        return self.worksheet_add_duplicate(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'manage_results')

    security.declareProtected(AddAndRemoveAnalyses, 'assignDuplicate')
    def assignDuplicate(self, AR = None, Position = None, Service = [], REQUEST = None, RESPONSE = None):
        """ assign selected analyses to worksheet
        """
        if not AR or not Position or not Service:
            message = self.translate('message_no_dup_assigned',
                                     default = 'No duplicate analysis assigned',
                                     domain = 'bika')
        else:
            rc = getToolByName(self, REFERENCE_CATALOG)
            wf = getToolByName(self, 'portal_workflow')

            ar = rc.lookupObject(AR)
            duplicates = []
            for service_uid in Service:
                service = rc.lookupObject(service_uid)
                service_id = service.getKeyword()
                analysis = ar[service_id]
                duplicate_id = self.generateUniqueId('DuplicateAnalysis')
                self.invokeFactory('DuplicateAnalysis', id = duplicate_id)
                duplicate = self[duplicate_id]
                duplicate.setAnalysis(analysis)
                duplicate.processForm()
                wf.doActionFor(duplicate, 'assign')
                duplicates.append(duplicate.UID())

            self._addToSequence('d', int(Position), duplicates)

            message = self.translate('message_dups_assigned',
                                     default = 'Duplicate analyses assigned',
                                     domain = 'bika')

        self.plone_utils.addPortalMessage(message)

        if REQUEST:
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    security.declarePublic('addControlAnalysis')
    def addControlAnalysis(self, REQUEST, RESPONSE):
        """ Add a reference analysis to the first available entry
        """
        return self.worksheet_add_control(
            REQUEST = REQUEST, RESPONSE = RESPONSE,
            template_id = 'manage_results')

    security.declareProtected(AddAndRemoveAnalyses, 'assignReference')
    def assignReference(self, Reference = None, Position = None, Type = None, Service = [], REQUEST = None, RESPONSE = None):
        """ assign selected reference analyses to worksheet
            Reference=uid, Position=number or 'new', Service=[uids]
        """

        if not Reference or not Position or not Service:
            if Type == 'b':
                addPortalMessage(_('No blank analysis assigned'))
            else:
                addPortalMessage(_('No reference analysis assigned'))
        else:
            rc = getToolByName(self, REFERENCE_CATALOG)
            assigned = []
            reference = rc.lookupObject(Reference)
            for service_uid in Service:
                ref_uid = reference.addReferenceAnalysis(service_uid, Type)
                assigned.append(ref_uid)

            self._addToSequence(Type, int(Position), assigned)
            assigned = assigned + self.getReferenceAnalyses()
            self.setReferenceAnalyses(assigned)

            if Type == 'b':
                message = self.translate('message_blank_assigned', default = 'Blank analysis has been assigned', domain = 'bika')
            else:
                message = self.translate('message_control_assigned', default = 'Control analysis has been assigned', domain = 'bika')

        utils = getToolByName(self, 'plone_utils')
        utils.addPortalMessage(message, type = u'info')

        if REQUEST:
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())

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

    # Present the LabManagers and labtechnicans as options for analyser
    # set the first entry to blank to force selection
    security.declarePublic('getAnalysersDisplayList')
    def getAnalysersDisplayList(self):
        mtool = getToolByName(self, 'portal_membership')
        analysers = {}
        pairs = [(' ', ' '), ]
        analysers = mtool.searchForMembers(roles = ['LabManager', 'Analyst'])
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
