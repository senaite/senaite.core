import sys
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import ManageBika, PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('ImportOption',
        widget = StringWidget(
            label = _("Import Option"),
        ),
    ),
    StringField('FileName',
        searchable = True,
        widget = StringWidget(
            label = _("Filename"),
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
    StringField('CCContactID',
        widget = StringWidget(
            label = _("Contact ID"),
        ),
    ),
    ReferenceField('Contact',
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'ARImportContact',
    ),
    StringField('ClientEmail',
        widget = StringWidget(
            label = _("Client Email"),
        ),
    ),
    ReferenceField('CCContact',
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'ARImportCCContact',
    ),
    StringField('CCEmails',
        widget = StringWidget(
            label = _("CC Emails"),
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
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Date"),
        ),
    ),
    DateTimeField('DateApplied',
        widget = DateTimeWidget(
            label = _("Date"),
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
),
)

schema['title'].required = False

class ARImport(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the id as title """
        return self.getId()


    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


    # workflow methods
    #
    def workflow_script_submit(self, state_info):
        """ submit arimport batch """
        if self.getImportOption() == 's':
            self.submit_arimport_s()
        else:
            self.submit_arimport_c()

    def submit_arimport_c(self):
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
        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request submission">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Completed">')

        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(aritems))

        row_count = 0
        next_id = self.generateUniqueId('Sample', batch_size = len(aritems))
        (prefix, next_num) = next_id.split('-')
        next_num = int(next_num)
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
                sortable_title = aritem.getSampleType())
            if not sampletypes:
                valid_batch = False
            if aritem.getSampleDate():
                date_items = aritem.getSampleDate().split('/')
                sample_date = DateTime(int(date_items[2]), int(date_items[1]), int(date_items[0]))
            else:
                sample_date = None
            sample_id = '%s-%s' % (prefix, (str(next_num)).zfill(5))
            next_num += 1
            client.invokeFactory(id = sample_id, type_name = 'Sample')
            sample = client[sample_id]
            sample.edit(
                SampleID = sample_id,
                ClientReference = aritem.getClientRef(),
                ClientSampleID = aritem.getClientSid(),
                SampleType = aritem.getSampleType(),
                SamplePoint = aritem.getSamplePoint(),
                DateSampled = sample_date,
                DateReceived = DateTime(),
                )
            sample.processForm()
            sample_uid = sample.UID()
            samples.append(sample_id)
            aritem.setSample(sample_uid)

            ar_id = self.generateARUniqueId('AnalysisRequest', sample_id, 1)
            client.invokeFactory(id = ar_id, type_name = 'AnalysisRequest')
            ar = client[ar_id]
            if aritem.getReportDryMatter().lower() == 'y':
                report_dry_matter = True
            else:
                report_dry_matter = False
            ar.edit(
                RequestID = ar_id,
                Contact = self.getContact(),
                CCContact = self.getCCContact(),
                CCEmails = self.getCCEmails(),
                ClientOrderNumber = self.getOrderID(),
                ReportDryMatter = report_dry_matter,
                Sample = sample_uid,
                Analyses = analyses
                )
            ar.processForm()
            ar_uid = ar.UID()
            aritem.setAnalysisRequest(ar_uid)
            ars.append(ar_id)
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)
        self.setDateApplied(DateTime())
        self.reindexObject()
        REQUEST.RESPONSE.write('<script>document.location.href="%s?portal_status_message=%s%%20submitted"</script>' % (self.absolute_url(), self.getId()))

    def submit_arimport_s(self):
        """ load the special (benchmark) import layout """

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
                valid_batch = True
                break

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
        sampletypes = []

        profiles = {}

        aritems = self.objectValues('ARImportItem')

        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request submission">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Completed">')
        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(aritems))

        row_count = 0
        next_id = self.generateUniqueId('Sample', batch_size = len(aritems))
        (prefix, next_num) = next_id.split('-')
        next_num = int(next_num)
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
                    l_prox = self.bika_setup_catalog(portal_type = 'AnalysisProfile',
                                    getProfileKey = profilekey)
                    if l_prox:
                        p = l_prox[0].getObject()
                        profiles[profilekey] = [s.UID() for s in p.getService()]
                        this_profile = p
                    else:
                        # there is no profilekey index
                        c_prox = self.bika_setup_catalog(portal_type = 'AnalysisProfile',
                                    getClientUID = client.UID(),
                                    getProfileKey = profilekey)
                        if c_prox:
                            p = c_prox[0].getObject()
                            profiles[profilekey] = [s.UID() for s in p.getService()]
                            this_profile = p

                if ar_profile is None:
                    ar_profile = p
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

            sampletype = aritem.getSampleType()
            if not sampletype in sampletypes:
                for s in self.bika_setup_catalog(portal_type = 'SampleType',
                                Title = sampletype):
                    sampletypes.append(s.Title)


            if not sampletype in sampletypes:
                valid_batch = False

            if aritem.getSampleDate():
                date_items = aritem.getSampleDate().split('/')
                sample_date = DateTime(int(date_items[2]), int(date_items[0]), int(date_items[1]))
            else:
                sample_date = None
            sample_id = '%s-%s' % (prefix, (str(next_num)).zfill(5))
            client.invokeFactory(id = sample_id, type_name = 'Sample')
            next_num += 1
            sample = client[sample_id]
            sample.edit(
                SampleID = sample_id,
                ClientReference = aritem.getClientRef(),
                ClientSampleID = aritem.getClientSid(),
                SampleType = sampletype,
                DateSampled = sample_date,
                DateReceived = DateTime(),
                Remarks = aritem.getClientRemarks(),
                )
            sample.processForm()
            sample_uid = sample.UID()
            aritem.setSample(sample_uid)

            ar_id = self.generateARUniqueId('AnalysisRequest', sample_id, 1)
            client.invokeFactory(id = ar_id, type_name = 'AnalysisRequest')
            ar = client[ar_id]
            report_dry_matter = False

            ar.edit(
                RequestID = ar_id,
                Contact = self.getContact(),
                CCEmails = self.getCCEmails(),
                ReportDryMatter = report_dry_matter,
                Sample = sample_uid,
                Profile = ar_profile,
                ClientOrderNumber = self.getOrderID(),
                Remarks = aritem.getClientRemarks(),
                Analyses = analyses,
                )
            ar.processForm()
            ar_uid = ar.UID()
            aritem.setAnalysisRequest(ar_uid)
            ars.append(ar_id)
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)

        self.setDateApplied(DateTime())
        self.reindexObject()
        REQUEST.RESPONSE.write('<script>document.location.href="%s?portal_status_message=%s%%20submitted"</script>' % (self.absolute_url(), self.getId()))


atapi.registerType(ARImport, PROJECTNAME)
