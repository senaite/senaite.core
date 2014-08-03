import sys
import time
import transaction
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import ManageBika, PROJECTNAME, ARIMPORT_OPTIONS
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARImport
from bika.lims.permissions import *
from bika.lims.jsonapi import resolve_request_lookup
from bika.lims.workflow import doActionFor
from bika.lims.utils import tmpID
from bika.lims import logger
from collective.progressbar.events import InitialiseProgressBar
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import UpdateProgressEvent
from collective.progressbar.events import ProgressState
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from zope import event
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    StringField('ImportOption',
        widget = SelectionWidget(
            label = _("Import Option"),
            format='select',
        ),
        vocabulary = ARIMPORT_OPTIONS,
    ),
    StringField('FileName',
        searchable = True,
        widget = StringWidget(
            label = _("Filename"),
        ),
    ),
    FileField('OriginalFile',
        searchable = True,
        widget = FileWidget(
            label = _("Original File"),
            visible={'edit': 'invisible',
                     'view': 'visible', 'add': 'invisible'},
        ),
    ),
    StringField('ClientTitle',
        searchable = True,
        widget = StringWidget(
            label = _("Client Name"),
        ),
    ),
    StringField('ClientPhone',
        widget = StringWidget(
            label = _("Client Phone"),
        ),
    ),
    StringField('ClientFax',
        widget = StringWidget(
            label = _("Client Fax"),
        ),
    ),
    StringField('ClientAddress',
        widget = StringWidget(
            label = _("Client Address"),
        ),
    ),
    StringField('ClientCity',
        widget = StringWidget(
            label = _("Client City"),
        ),
    ),
    StringField('ClientID',
        searchable = True,
        widget = StringWidget(
            label = _("Client ID"),
        ),
    ),
    StringField('ContactID',
        widget = StringWidget(
            label = _("Contact ID"),
        ),
    ),
    StringField('ContactName',
        widget = StringWidget(
            label = _("Contact Name"),
        ),
    ),
    ReferenceField('Contact',
        allowed_types = ('Contact',),
        relationship = 'ARImportContact',
        default_method = 'getContactUIDForUser',
        referenceClass = HoldingReference,
        vocabulary_display_path_bound = sys.maxint,
        widget=ReferenceWidget(
            label=_("Contact"),
            size=12,
            helper_js=("bika_widgets/referencewidget.js", "++resource++bika.lims.js/contact.js"),
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible'},
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='300px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '100', 'label': _('Name')},
                     ],
        ),
    ),
    StringField('ClientEmail',
        widget = StringWidget(
            label = _("Client Email"),
        ),
    ),
    StringField('CCContactID',
        widget = StringWidget(
            label = _("CC Contact ID"),
        ),
    ),
    ReferenceField('CCContact',
        allowed_types = ('Contact',),
        relationship = 'ARImportCCContact',
        default_method = 'getCCContactUIDForUser',
        referenceClass = HoldingReference,
        vocabulary_display_path_bound = sys.maxint,
        widget=ReferenceWidget(
            label=_("CCContact"),
            size=12,
            helper_js=("bika_widgets/referencewidget.js", "++resource++bika.lims.js/contact.js"),
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible'},
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='300px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '100', 'label': _('Name')},
                     ],
        ),
    ),
    StringField('CCNamesReport',
        widget = StringWidget(
            label = _("Report Contact Names"),
        ),
    ),
    StringField('CCEmailsReport',
        widget = StringWidget(
            label = _("CC Email - Report"),
        ),
    ),
    StringField('CCEmailsInvoice',
        widget = StringWidget(
            label = _("CC Email - Invoice"),
        ),
    ),
    StringField('OrderID',
        searchable = True,
        widget = StringWidget(
            label = _("Order ID"),
        ),
    ),
    StringField('QuoteID',
        searchable = True,
        widget = StringWidget(
            label = _("QuoteID"),
        ),
    ),
    StringField('SamplePoint',
        searchable = True,
        widget = StringWidget(
            label = _("Sample Point"),
        ),
    ),
    StringField('Temperature',
        widget = StringWidget(
            label = _("Temperature"),
        ),
    ),
    DateTimeField('DateImported',
        required = 1,
        widget = DateTimeWidget(
            label = _("Date Imported"),
            size=12,
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible',
                     'secondary': 'invisible'},
        ),
    ),
    DateTimeField('DateApplied',
        widget = DateTimeWidget(
            label = _("Date Applied"),
            size=12,
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible',
                     'secondary': 'invisible'},
        ),
    ),
    IntegerField('NumberSamples',
        widget = IntegerWidget(
            label = _("Number of samples"),
        ),
    ),
    BooleanField('Status',
        searchable = True,
        widget = StringWidget(
            label = _("Status"),
        ),
    ),
    LinesField('Remarks',
        widget = LinesWidget(
            label = _("Remarks"),
        )
    ),
    LinesField('Analyses',
        widget = LinesWidget(
            label = _("Analyses"),
        )
    ),
    ComputedField('ClientUID',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ReferenceField(
        'Priority',
        allowed_types=('ARPriority',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestPriority',
        mode="rw",
        read_permission=permissions.View,
        write_permission=ManageARPriority,
        widget=ReferenceWidget(
            label=_("Priority"),
            size=10,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'visible',
                     'secondary': 'invisible'},
            catalog_name='bika_setup_catalog',
            base_query={'review_state': 'published'},
            showOn=True,
        ),
    ),
),
)

schema['title'].required = False

class ARImport(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements (IARImport)
    _at_rename_after_creation = True

    #def Title(self):
    #    """ Return the id as title """
    #    return safe_unicode(self.getId()).encode('utf-8')

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)


    # workflow methods
    #
    def workflow_script_submit(self):
        """ submit arimport batch """
        if self.getImportOption() == 'p':
            self._submit_arimport_p()
        else:
            self._submit_arimport_c()
        transaction.commit()
        #TODO time.sleep(2)
        self.REQUEST.response.write(
            '<script>document.location.href="%s"</script>' % (
                self.absolute_url()))

    def _submit_arimport_c(self):
        """ load the classic import layout """

        ars = []
        samples = []
        valid_batch = True
        client = self.aq_parent
        contact_obj = None
        cc_contact_obj = None

        # validate contact
        for contact in client.objectValues('Contact'):
            if contact.getUsername() == self.getContactID():
                contact_obj = contact
            if self.getCCContactID() == None:
                if contact_obj != None:
                    break
            else:
                if contact.getUsername() == self.getCCContactID():
                    cc_contact_obj = contact
                    if contact_obj != None:
                        break

        if contact_obj == None:
            valid_batch = False

        # get Keyword to ServiceId Map
        services = {}
        for service in self.bika_setup_catalog(
                portal_type = 'AnalysisService'):
            obj = service.getObject()
            keyword = obj.getKeyword()
            if keyword:
                services[keyword] = '%s:%s' % (obj.UID(), obj.getPrice())

        samplepoints = self.bika_setup_catalog(
            portal_type = 'SamplePoint',
            Title = self.getSamplePoint())
        if not samplepoints:
            valid_batch = False

        aritems = self.objectValues('ARImportItem')
        request = self.REQUEST
        title = 'Submitting AR Import'
        bar = ProgressBar(
                self, request, title, description='')
        event.notify(InitialiseProgressBar(bar))

        SamplingWorkflowEnabled = \
            self.bika_setup.getSamplingWorkflowEnabled()
        row_count = 0
        item_count =len(aritems)
        prefix = 'Sample'
        for aritem in aritems:
            row_count += 1
            # set up analyses
            analyses = []
            for analysis in aritem.getAnalyses(full_objects=True):
                if services.has_key(analysis):
                    analyses.append(services[analysis])
                else:
                    valid_batch = False

            sampletypes = self.portal_catalog(
                portal_type = 'SampleType',
                sortable_title = aritem.getSampleType().lower(),
                )
            if not sampletypes:
                valid_batch = False
                return
            sampletypeuid = sampletypes[0].getObject().UID()

            samplematrices = self.bika_setup_catalog(
                portal_type = 'SampleMatrix',
                sortable_title = aritem.getSampleMatrix().lower(),
                )
            if not samplematrices:
                valid_batch = False
                return
            samplematrixuid = samplematrices[0].getObject().UID()

            if aritem.getSampleDate():
                date_items = aritem.getSampleDate().split('/')
                sample_date = DateTime(
                    int(date_items[2]), int(date_items[1]), int(date_items[0]))
            else:
                sample_date = None

            sample_id = '%s-%s' % (prefix, tmpID())
            sample = _createObjectByType("Sample", client, sample_id)
            sample.unmarkCreationFlag()
            sample.edit(
                SampleID = sample_id,
                ClientReference = aritem.getClientRef(),
                ClientSampleID = aritem.getClientSid(),
                SampleType = aritem.getSampleType(),
                DateSampled = sample_date,
                SamplingDate = sample_date,
                DateReceived = DateTime(),
                )
            sample._renameAfterCreation()
            #sp_id = client.invokeFactory('SamplePoint', id=tmpID())
            #sp = client[sp_id]
            #sp.edit(title=self.getSamplePoint())
            sample.setSamplePoint(self.getSamplePoint())
            sample.setSampleID(sample.getId())
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()
            sample_uid = sample.UID()
            samples.append(sample_id)
            aritem.setSample(sample_uid)

            priorities = self.bika_setup_catalog(
                portal_type = 'ARPriority',
                sortable_title = aritem.Priority.lower(),
                )
            if len(priorities) < 1:
                logger.warning(
                    'Invalid Priority: validation should have prevented this')

            #Create AR
            ar_id = tmpID()
            ar = _createObjectByType("AnalysisRequest", client, ar_id)
            if aritem.getReportDryMatter().lower() == 'y':
                report_dry_matter = True
            else:
                report_dry_matter = False
            ar.unmarkCreationFlag()
            ar.edit(
                RequestID = ar_id,
                Contact = self.getContact(),
                CCContact = self.getCCContact(),
                CCEmails = self.getCCEmailsInvoice(),
                ClientOrderNumber = self.getOrderID(),
                ReportDryMatter = report_dry_matter,
                Analyses = analyses,
                Priority = priorities[0].getObject(),
                )
            ar.setSample(sample_uid)
            sample = ar.getSample()
            ar.setSampleType(sampletypeuid)
            ar.setSampleMatrix(samplematrixuid)
            ar_uid = ar.UID()
            aritem.setAnalysisRequest(ar_uid)
            ars.append(ar_id)
            ar._renameAfterCreation()

            self._add_services_to_ar(ar, analyses)

            progress_index = float(row_count)/float(item_count)*100.0
            progress = ProgressState(request, progress_index)
            event.notify(UpdateProgressEvent(progress))
            #TODO REmove for production - just to look pretty
            #time.sleep(1)
        self.setDateApplied(DateTime())
        self.reindexObject()

    def _submit_arimport_p(self):
        """ load the profiles import layout """

        ars = []
        samples = []
        valid_batch = False
        client = self.aq_parent
        contact_obj = None
        cc_contact_obj = None

        # validate contact
        for contact in client.objectValues('Contact'):
            if contact.getUsername() == self.getContactID():
                contact_obj = contact
            if self.getCCContactID() == None:
                if contact_obj != None:
                    break
            else:
                if contact.getUsername() == self.getCCContactID():
                    cc_contact_obj = contact
                    if contact_obj != None:
                        break

        if contact_obj == None:
            valid_batch = False

        # get Keyword to ServiceId Map
        services = {}
        service_uids = {}

        for service in self.bika_setup_catalog(
                portal_type = 'AnalysisService'):
            obj = service.getObject()
            keyword = obj.getKeyword()
            if keyword:
                services[keyword] = '%s:%s' % (obj.UID(), obj.getPrice())
            service_uids[obj.UID()] = '%s:%s' % (obj.UID(), obj.getPrice())

        samplepoints = self.bika_setup_catalog(
            portal_type = 'SamplePoint',
            Title = self.getSamplePoint())
        if not samplepoints:
            valid_batch = False

        profiles = {}
        aritems = self.objectValues('ARImportItem')

        request = self.REQUEST
        title = 'Submitting AR Import'
        bar = ProgressBar(
                self, request, title, description='')
        event.notify(InitialiseProgressBar(bar))

        row_count = 0
        item_count = len(aritems)
        prefix = 'Sample'
        for aritem in aritems:
            # set up analyses
            ar_profile = None
            analyses = []
            row_count += 1

            for profilekey in aritem.getAnalysisProfile():
                this_profile = None
                if not profiles.has_key(profilekey):
                    profiles[profilekey] = []
                    # there is no profilekey index
                    l_prox = self._findProfileKey(profilekey)
                    if l_prox:
                        profiles[profilekey] = \
                                [s.UID() for s in l_prox.getService()]
                        this_profile = l_prox
                    else:
                        #TODO This will not find it!!
                        # there is no profilekey index
                        c_prox = self.bika_setup_catalog(
                                    portal_type = 'AnalysisProfile',
                                    getClientUID = client.UID(),
                                    getProfileKey = profilekey)
                        if c_prox:
                            obj = c_prox[0].getObject()
                            profiles[profilekey] = \
                                    [s.UID() for s in obj.getService()]
                            this_profile = obj

                if ar_profile is None:
                    ar_profile = obj
                else:
                    ar_profile = None
                profile = profiles[profilekey]
                for analysis in profile:
                    if not service_uids.has_key(analysis):
                        service = tool.lookupObject(analysis)
                        keyword = service.getKeyword()
                        service_uids[obj.UID()] = '%s:%s' % (obj.UID(), obj.getPrice())
                        if keyword:
                            services[keyword] = '%s:%s' % (obj.UID(), obj.getPrice())

                    if service_uids.has_key(analysis):
                        if not service_uids[analysis] in analyses:
                            analyses.append(service_uids[analysis])
                    else:
                        valid_batch = False

            for analysis in aritem.getAnalyses(full_objects=True):
                if not services.has_key(analysis):
                    for service in self.bika_setup_catalog(
                            portal_type = 'AnalysisService',
                            getKeyword = analysis):
                        obj = service.getObject()
                        services[analysis] = '%s:%s' % (obj.UID(), obj.getPrice())
                        service_uids[obj.UID()] = '%s:%s' % (obj.UID(), obj.getPrice())

                if services.has_key(analysis):
                    analyses.append(services[analysis])
                else:
                    valid_batch = False

            sampletypes = self.portal_catalog(
                portal_type = 'SampleType',
                sortable_title = aritem.getSampleType().lower(),
                )
            if not sampletypes:
                valid_batch = False
                return
            sampletypeuid = sampletypes[0].getObject().UID()

            samplematrices = self.bika_setup_catalog(
                portal_type = 'SampleMatrix',
                sortable_title = aritem.getSampleMatrix().lower(),
                )
            if not samplematrices:
                valid_batch = False
                return
            samplematrixuid = samplematrices[0].getObject().UID()

            if aritem.getSampleDate():
                date_items = aritem.getSampleDate().split('/')
                sample_date = DateTime(
                    int(date_items[2]), int(date_items[0]), int(date_items[1]))
            else:
                sample_date = None

            sample_id = '%s-%s' % (prefix, tmpID())
            sample = _createObjectByType("Sample", client, sample_id)
            sample.unmarkCreationFlag()
            sample.edit(
                SampleID = sample_id,
                ClientReference = aritem.getClientRef(),
                ClientSampleID = aritem.getClientSid(),
                SampleType = aritem.getSampleType(),
                SampleMatrix = aritem.getSampleMatrix(),
                DateSampled = sample_date,
                SamplingDate = sample_date,
                DateReceived = DateTime(),
                Remarks = aritem.getClientRemarks(),
                )
            sample._renameAfterCreation()
            sample.setSamplePoint(self.getSamplePoint())
            sample.setSampleID(sample.getId())
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()
            sample_uid = sample.UID()
            samples.append(sample_id)
            aritem.setSample(sample_uid)

            priorities = self.bika_setup_catalog(
                portal_type = 'ARPriority',
                sortable_title = aritem.Priority.lower(),
                )
            if len(priorities) < 1:
                logger.warning(
                    'Invalid Priority: validation should have prevented this')
                priority = ''
            else:
                priority = priorities[0].getObject()

            ar_id = tmpID()
            ar = _createObjectByType("AnalysisRequest", client, ar_id)
            report_dry_matter = False

            ar.unmarkCreationFlag()
            ar.edit(
                RequestID = ar_id,
                Contact = self.getContact(),
                CCContact = self.getCCContact(),
                CCEmails = self.getCCEmailsInvoice(),
                ClientOrderNumber = self.getOrderID(),
                ReportDryMatter = report_dry_matter,
                Profile = ar_profile,
                Analyses = analyses,
                Remarks = aritem.getClientRemarks(),
                Priority = priority,
                )
            ar.setSample(sample_uid)
            sample = ar.getSample()
            ar.setSampleType(sampletypeuid)
            ar.setSampleMatrix(samplematrixuid)
            ar_uid = ar.UID()
            aritem.setAnalysisRequest(ar_uid)
            ars.append(ar_id)
            ar._renameAfterCreation()
            progress_index = float(row_count)/float(item_count)*100.0
            progress = ProgressState(request, progress_index)
            event.notify(UpdateProgressEvent(progress))
            self._add_services_to_ar(ar, analyses)

        self.setDateApplied(DateTime())
        self.reindexObject()


    def _add_services_to_ar(self, ar, analyses):
        #Add Services
        service_uids = [i.split(':')[0] for i in analyses]
        new_analyses = ar.setAnalyses(service_uids)
        ar.setRequestID(ar.getId())
        ar.reindexObject()
        event.notify(ObjectInitializedEvent(ar))
        ar.at_post_create_script()

        SamplingWorkflowEnabled = \
            self.bika_setup.getSamplingWorkflowEnabled()
        wftool = getToolByName(self, 'portal_workflow')

        # Create sample partitions
        parts = [{'services': [],
                 'container':[],
                 'preservation':'',
                 'separate':False}]
        sample = ar.getSample()
        parts_and_services = {}
        for _i in range(len(parts)):
            p = parts[_i]
            part_prefix = sample.getId() + "-P"
            if '%s%s' % (part_prefix, _i + 1) in sample.objectIds():
                parts[_i]['object'] = sample['%s%s' % (part_prefix, _i + 1)]
                parts_and_services['%s%s' % (part_prefix, _i + 1)] = \
                        p['services']
            else:
                part = _createObjectByType("SamplePartition", sample, tmpID())
                parts[_i]['object'] = part
                container = None
                preservation = p['preservation']
                parts[_i]['prepreserved'] = False
                part.unmarkCreationFlag()
                part.edit(
                    Container=container,
                    Preservation=preservation,
                )
                part._renameAfterCreation()
                if SamplingWorkflowEnabled:
                    wftool.doActionFor(part, 'sampling_workflow')
                else:
                    wftool.doActionFor(part, 'no_sampling_workflow')
                parts_and_services[part.id] = p['services']

        if SamplingWorkflowEnabled:
            wftool.doActionFor(ar, 'sampling_workflow')
        else:
            wftool.doActionFor(ar, 'no_sampling_workflow')

        # Add analyses to sample partitions
        # XXX jsonapi create AR: right now, all new analyses are linked to the first samplepartition
        if new_analyses:
            analyses = list(part.getAnalyses())
            analyses.extend(new_analyses)
            part.edit(
                Analyses=analyses,
            )
            for analysis in new_analyses:
                analysis.setSamplePartition(part)

        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not SamplingWorkflowEnabled:
            to_be_preserved = []
            sample_due = []
            lowest_state = 'sample_due'
            for p in sample.objectValues('SamplePartition'):
                if p.getPreservation():
                    lowest_state = 'to_be_preserved'
                    to_be_preserved.append(p)
                else:
                    sample_due.append(p)
            for p in to_be_preserved:
                doActionFor(p, 'to_be_preserved')
            for p in sample_due:
                doActionFor(p, 'sample_due')
            doActionFor(sample, lowest_state)
            for analysis in ar.objectValues('Analysis'):
                doActionFor(analysis, lowest_state)
            doActionFor(ar, lowest_state)

        # receive secondary AR
        #TODO if request.get('Sample_id', ''):
        #    doActionFor(ar, 'sampled')
        #    doActionFor(ar, 'sample_due')
        #    not_receive = ['to_be_sampled', 'sample_due', 'sampled',
        #                   'to_be_preserved']
        #    sample_state = wftool.getInfoFor(sample, 'review_state')
        #    if sample_state not in not_receive:
        #        doActionFor(ar, 'receive')
        #    for analysis in ar.getAnalyses(full_objects=1):
        #        doActionFor(analysis, 'sampled')
        #        doActionFor(analysis, 'sample_due')
        #        if sample_state not in not_receive:
        #            doActionFor(analysis, 'receive')

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('getCCContactUIDForUser')
    def getCCContactUIDForUser(self):
        """ get the UID of the cc contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID


    def validateIt(self):
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        client = self.aq_parent
        batch_remarks = []
        valid_batch = True
        uid = self.UID()
        batches = pc({
                    'portal_type': 'ARImport',
                    'path': {'query': '/'.join(client.getPhysicalPath())},
                    })
        for brain in batches:
            if brain.UID == uid:
                continue
            batch = brain.getObject()
            if batch.getOrderID() != self.getOrderID():
                continue
            if batch.getStatus():
                # then a previous valid batch exists
                batch_remarks.append(
                    '\n' + 'Duplicate order %s' % self.getOrderID())
                valid_batch = False
                break

        # validate client
        if self.getClientID() != client.getClientID():
            batch_remarks.append(
                '\n' + 'Client ID should be %s' %client.getClientID())
            valid_batch = False

        # validate contact
        contact_found = False
        cc_contact_found = False

        if self.getContact():
            contact_found = True
        else:
            contactid = self.getContactID()
            for contact in client.objectValues('Contact'):
                if contact.getUsername() == contactid:
                    self.edit(Contact=contact)
                    contact_found = True
                    #break

        if self.getCCContact():
            cc_contact_found = True
        else:
            if self.getCCContactID():
                cccontact_uname = self.getCCContactID()
                for contact in client.objectValues('Contact'):
                    if contact.getUsername() == cccontact_uname:
                        self.edit(CCContact=contact)
                        cc_contact_found = True
                        break

        cccontact_uname = self.getCCContactID()

        if not contact_found:
            batch_remarks.append('\n' + 'Contact invalid')
            valid_batch = False
        if cccontact_uname != None and \
           cccontact_uname != '':
            if not cc_contact_found:
                batch_remarks.append('\n' + 'CC contact invalid')
                valid_batch = False

        # validate sample point
        samplepoint = self.getSamplePoint()
        if samplepoint != None:
            points = pc(portal_type='SamplePoint',
                Title=samplepoint)

        sampletypes = \
            [p.Title for p in pc(portal_type="SampleType")]
        samplematrices = \
            [p.Title for p in bsc(portal_type="SampleMatrix")]
        containertypes = \
            [p.Title for p in bsc(portal_type="ContainerType")]
        service_keys = []
        dependant_services = {}

        services = bsc(portal_type = "AnalysisService",
                       inactive_state = 'active')
        for brain in services:
            service = brain.getObject()
            service_keys.append(service.getKeyword())
            calc = service.getCalculation()
            if calc:
                dependencies = calc.getDependentServices()
                if dependencies:
                    dependant_services[service.getKeyword()] = dependencies
        aritems = self.objectValues('ARImportItem')
        for aritem in aritems:
            item_remarks = []
            valid_item = True
            #validate sample type
            if aritem.getSampleType() not in sampletypes:
                batch_remarks.append('\n%s: Sample type %s invalid' %(
                    aritem.getSampleName(), aritem.getSampleType()))
                item_remarks.append(
                    '\nSample type %s invalid' %(aritem.getSampleType()))
                valid_item = False
            if aritem.getSampleMatrix() not in samplematrices:
                batch_remarks.append('\n%s: Sample Matrix %s invalid' %(
                    aritem.getSampleName(), aritem.getSampleMatrix()))
                item_remarks.append(
                    '\nSample Matrix %s invalid' %(aritem.getSampleMatrix()))
                valid_item = False
            #validate container type
            if aritem.getContainerType() not in containertypes:
                batch_remarks.append(
                    '\n%s: Container type %s invalid' %(
                        aritem.getSampleName(), aritem.getContainerType()))
                item_remarks.append(
                    '\nContainer type %s invalid' %(aritem.getContainerType()))
                valid_item = False
            #validate Sample Date
            try:
                date_items = aritem.getSampleDate().split('/')
                test_date = DateTime(int(date_items[2]), int(date_items[1]), int(date_items[0]))
            except:
                valid_item = False
                batch_remarks.append('\n' + '%s: Sample date %s invalid' %(aritem.getSampleName(), aritem.getSampleDate()))
                item_remarks.append('\n' + 'Sample date %s invalid' %(aritem.getSampleDate()))

            #validate Priority
            invalid_priority = False
            try:
                priorities = self.bika_setup_catalog(
                    portal_type = 'ARPriority',
                    sortable_title = aritem.Priority.lower(),
                    )
                if len(priorities) < 1:
                    invalid_priority = True
            except:
                invalid_priority = True

            if invalid_priority:
                valid_item = False
                batch_remarks.append('\n' + '%s: Priority %s invalid' % (
                    aritem.getSampleName(), aritem.Priority))
                item_remarks.append('\n' + 'Priority %s invalid' % (
                    aritem.Priority))

            #Validate option specific fields
            if self.getImportOption() == 'c':
                analyses = aritem.getAnalyses()
                for analysis in analyses:
                    if analysis not in service_keys:
                        batch_remarks.append('\n' + '%s: Analysis %s invalid' %(aritem.getSampleName(), analysis))
                        item_remarks.append('\n' + 'Analysis %s invalid' %(analysis))
                        valid_item = False
                    # validate analysis dependancies
                    reqd_analyses = []
                    if dependant_services.has_key(analysis):
                        reqd_analyses = \
                            [s.getKeyword() for s in dependant_services[analysis]]
                    reqd_titles = ''
                    for reqd in reqd_analyses:
                        if (reqd not in analyses):
                            if reqd_titles != '':
                                reqd_titles += ', '
                            reqd_titles += reqd
                    if reqd_titles != '':
                        valid_item = False
                        batch_remarks.append('\n' + '%s: %s needs %s' \
                            %(aritem.getSampleName(), analysis, reqd_titles))
                        item_remarks.append('\n' + '%s needs %s' \
                            %(analysis, reqd_titles))

                # validate analysisrequest dependancies
                if aritem.getReportDryMatter().lower() == 'y':
                    required = self.get_analysisrequest_dependancies('DryMatter')
                    reqd_analyses = required['keys']
                    reqd_titles = ''
                    for reqd in reqd_analyses:
                        if reqd not in analyses:
                            if reqd_titles != '':
                                reqd_titles += ', '
                            reqd_titles += reqd

                    if reqd_titles != '':
                        valid_item = False
                        batch_remarks.append('\n' + '%s: Report as Dry Matter needs %s' \
                            %(aritem.getSampleName(), reqd_titles))
                        item_remarks.append('\n' + 'Report as Dry Matter needs %s' \
                            %(reqd_titles))
            elif self.getImportOption() == 'p':
                analyses = aritem.getAnalysisProfile()
                if len(analyses) == 0:
                    valid_item = False
                    item_remarks.append('\n%s: No Profile provided' \
                        % aritem.getSampleName())
                    batch_remarks.append('\n%s: No Profile provided' \
                        % aritem.getSampleName())
                elif len(analyses) > 1:
                    valid_item = False
                    item_remarks.append('\n%s: Only one Profile allowed' \
                        % aritem.getSampleName())
                    batch_remarks.append('\n%s: Only one Profile allowed' \
                        % aritem.getSampleName())
                else:
                    if not self._findProfileKey(analyses[0]):
                        valid_item = False
                        item_remarks.append('\n%s: unknown Profile %s' \
                            % (aritem.getSampleName(), analyses[0]))
                        batch_remarks.append('\n%s: unknown Profile %s' \
                            % (aritem.getSampleName(), analyses[0]))

            aritem.setRemarks(item_remarks)
            #print item_remarks
            if not valid_item:
                valid_batch = False
        if self.getNumberSamples() != len(aritems):
            valid_batch = False
            batch_remarks.append('\nNumber of samples specified (%s) does no match number listed (%s)' % (self.getNumberSamples(), len(aritems)))
        self.edit(
            Remarks=batch_remarks,
            Status=valid_batch)

        #print batch_remarks
        return valid_batch

    def _findProfileKey(self, key):
        profiles = self.bika_setup_catalog(
                portal_type = 'AnalysisProfile')
        found = False
        for brain in profiles:
            if brain.getObject().getProfileKey() == key:
                return brain.getObject()

atapi.registerType(ARImport, PROJECTNAME)
