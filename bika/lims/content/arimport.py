from AccessControl import ClassSecurityInfo
import csv
from DateTime.DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import ulocalized_time
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.analysisrequest import schema as ar_schema
from bika.lims.content.sample import schema as sample_schema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARImport, IClient
from bika.lims.utils import tmpID
from bika.lims.vocabularies import CatalogVocabulary
from collective.progressbar.events import InitialiseProgressBar
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import ProgressState
from collective.progressbar.events import UpdateProgressEvent
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import DateColumn
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from zope import event
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from bika.lims.browser.widgets import ReferenceWidget as bReferenceWidget

import sys
import transaction

_p = MessageFactory(u"plone")

OriginalFile = FileField(
    'OriginalFile',
    widget=ComputedWidget(
        visible=False
    ),
)

Filename = StringField(
    'Filename',
    widget=StringWidget(
        label=_('Original Filename'),
        visible=True
    ),
)

NrSamples = StringField(
    'NrSamples',
    widget=StringWidget(
        label=_('Number of samples'),
        visible=True
    ),
)

ClientName = StringField(
    'ClientName',
    searchable=True,
    widget=StringWidget(
        label=_("Client Name"),
    ),
)

ClientID = StringField(
    'ClientID',
    searchable=True,
    widget=StringWidget(
        label=_('Client ID'),
    ),
)

ClientOrderNumber = StringField(
    'ClientOrderNumber',
    searchable=True,
    widget=StringWidget(
        label=_('Client Order Number'),
    ),
)

ClientReference = StringField(
    'ClientReference',
    searchable=True,
    widget=StringWidget(
        label=_('Client Reference'),
    ),
)

Contact = ReferenceField(
    'Contact',
    allowed_types=('Contact',),
    relationship='ARImportContact',
    default_method='getContactUIDForUser',
    referenceClass=HoldingReference,
    vocabulary_display_path_bound=sys.maxint,
    widget=ReferenceWidget(
        label=_('Primary Contact'),
        size=20,
        visible=True,
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='300px',
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Fullname', 'width': '100',
                   'label': _('Name')}],
    ),
)

Batch = ReferenceField(
    'Batch',
    allowed_types=('Batch',),
    relationship='ARImportBatch',
    widget=bReferenceWidget(
        label=_('Batch'),
        visible=True,
        catalog_name='bika_catalog',
        base_query={'review_state': 'open', 'cancellation_state': 'active'},
        showOn=True,
    ),
)

CCContacts = DataGridField(
    'CCContacts',
    allow_insert=False,
    allow_delete=False,
    allow_reorder=False,
    allow_empty_rows=False,
    columns=('CCNamesReport',
             'CCEmailsReport',
             'CCNamesInvoice',
             'CCEmailsInvoice'),
    default=[{'CCNamesReport': [],
              'CCEmailsReport': [],
              'CCNamesInvoice': [],
              'CCEmailsInvoice': []
              }],
    widget=DataGridWidget(
        columns={
            'CCNamesReport': LinesColumn('Report CC Contacts'),
            'CCEmailsReport': LinesColumn('Report CC Emails'),
            'CCNamesInvoice': LinesColumn('Invoice CC Contacts'),
            'CCEmailsInvoice': LinesColumn('Invoice CC Emails')
        }
    )
)

SampleData = DataGridField(
    'SampleData',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('ClientSampleID',
             'SamplingDate',
             'DateSampled',
             'SamplePoint',
             'SampleMatrix',
             'SampleType',  # not a schema field!
             'ContainerType',  # not a schema field!
             'ReportDryMatter',
             'Priority',
             'Analyses',  # not a schema field!
             'Profiles'  # not a schema field!
             ),
    widget=DataGridWidget(
        label=_('Samples'),
        columns={
            'ClientSampleID': Column('Sample ID'),
            'SamplingDate': DateColumn('Sampling Date'),
            'DateSampled': DateColumn('Date Sampled'),
            'SamplePoint': SelectColumn(
                'Sample Point', vocabulary='Vocabulary_SamplePoint'),
            'SampleMatrix': SelectColumn(
                'Sample Matrix', vocabulary='Vocabulary_SampleMatrix'),
            'SampleType': SelectColumn(
                'Sample Type', vocabulary='Vocabulary_SampleType'),
            'ContainerType': SelectColumn(
                'Container', vocabulary='Vocabulary_ContainerType'),
            'ReportDryMatter': CheckboxColumn('Dry'),
            'Priority': SelectColumn(
                'Priority', vocabulary='Vocabulary_Priority'),
            'Analyses': LinesColumn('Analyses'),
            'Profiles': LinesColumn('Profiles'),
        }
    )
)

Errors = LinesField(
    'Errors',
    widget=LinesWidget(
        label=_('Errors'),
        rows=10,
    )
)

schema = BikaSchema.copy() + Schema((
    OriginalFile,
    Filename,
    NrSamples,
    ClientName,
    ClientID,
    ClientOrderNumber,
    ClientReference,
    Contact,
    CCContacts,
    Batch,
    SampleData,
    Errors,
))

schema['title'].validators = ()
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class ARImport(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IARImport)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def guard_validate_transition(self):
        """We may only attempt validation if file data has been uploaded.
        """
        data = self.getOriginalFile()
        if data and len(data):
            return True

    def workflow_before_validate(self):
        """This function transposes values from the provided file into the
        ARImport object's fields, and checks for invalid values.

        If errors are found:
            - Validation transition is aborted.
            - Errors are stored on object and displayed to user.

        """
        # Re-set the errors on this ARImport each time validation is attempted.
        # When errors are detected they are immediately appended to this field.
        self.setErrors([])

        self.validate_headers()
        self.validate_samples()

        if self.getErrors():
            addStatusMessage(self.REQUEST, _p('Validation errors.'), 'error')
            transaction.commit()
            self.REQUEST.response.write(
                '<script>document.location.href="%s/edit"</script>' % (
                    self.absolute_url()))
        self.REQUEST.response.write(
            '<script>document.location.href="%s/view"</script>' % (
                self.absolute_url()))

    def at_post_edit_script(self):
        workflow = getToolByName(self, 'portal_workflow')
        trans_ids = [t['id'] for t in workflow.getTransitionsFor(self)]
        if 'validate' in trans_ids:
            workflow.doActionFor(self, 'validate')

    def workflow_script_import(self):
        """Create objects from valid ARImport
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        workflow = getToolByName(self, 'portal_workflow')
        client = self.aq_parent

        title = _('Submitting AR Import')
        description = _('Creating and initialising objects')
        bar = ProgressBar(self, self.REQUEST, title, description)
        notify(InitialiseProgressBar(bar))

        profiles = [x.getObject() for x in bsc(portal_type='AnalysisProfile')]

        gridrows = self.schema['SampleData'].get(self)
        row_cnt = 0
        for therow in gridrows:
            row = therow.copy()
            row_cnt += 1
            # Create Sample
            sample = _createObjectByType('Sample', client, tmpID())
            sample.unmarkCreationFlag()
            # First convert all row values into something the field can take
            sample.edit(**row)
            sample._renameAfterCreation()
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()
            swe = self.bika_setup.getSamplingWorkflowEnabled()
            if swe:
                workflow.doActionFor(sample, 'sampling_workflow')
            else:
                workflow.doActionFor(sample, 'no_sampling_workflow')
            part = _createObjectByType('SamplePartition', sample, 'part-1')
            part.unmarkCreationFlag()
            if swe:
                workflow.doActionFor(part, 'sampling_workflow')
            else:
                workflow.doActionFor(part, 'no_sampling_workflow')
            # Container is special... it could be a containertype.
            container = self.get_row_container(row)
            if container:
                if container.portal_type == 'ContainerType':
                    containers = container.getContainers()
                # XXX And so we must calculate the best container for this partition
                part.edit(Container=containers[0])

            # Profiles are titles, profile keys, or UIDS: convert them to UIDs.
            newprofiles = []
            for title in row['Profiles']:
                objects = [x for x in profiles
                           if title in (x.getProfileKey(), x.UID(), x.Title())]
                for obj in objects:
                    newprofiles.append(obj.UID())
            row['Profiles'] = newprofiles

            # BBB in bika.lims < 3.1.9, only one profile is permitted
            # on an AR.  The services are all added, but only first selected
            # profile name is stored.
            row['Profile'] = newprofiles[0] if newprofiles else None

            # Same for analyses
            newanalyses = set(self.get_row_services(row) +
                              self.get_row_profile_services(row))
            row['Analyses'] = []
            # get batch
            batch = self.schema['Batch'].get(self)
            if batch:
                row['Batch'] = batch
            # Add AR fields from schema into this row's data
            row['ClientReference'] = self.getClientReference()
            row['ClientOrderNumber'] = self.getClientOrderNumber()
            row['Contact'] = self.getContact()
            # Create AR
            ar = _createObjectByType("AnalysisRequest", client, tmpID())
            ar.setSample(sample)
            ar.unmarkCreationFlag()
            ar.edit(**row)
            ar._renameAfterCreation()
            for analysis in ar.getAnalyses(full_objects=True):
                analysis.setSamplePartition(part)
            ar.at_post_create_script()
            if swe:
                workflow.doActionFor(ar, 'sampling_workflow')
            else:
                workflow.doActionFor(ar, 'no_sampling_workflow')
            ar.setAnalyses(list(newanalyses))
            progress_index = float(row_cnt) / len(gridrows) * 100
            progress = ProgressState(self.REQUEST, progress_index)
            notify(UpdateProgressEvent(progress))
        # document has been written to, and redirect() fails here
        self.REQUEST.response.write(
            '<script>document.location.href="%s"</script>' % (
                self.absolute_url()))

    def get_header_values(self):
        """Scrape the "Header" values from the original input file
        """
        lines = self.getOriginalFile().data.splitlines()
        reader = csv.reader(lines)
        header_fields = header_data = []
        for row in reader:
            if not any(row):
                continue
            if row[0].strip().lower() == 'header':
                header_fields = [x.strip() for x in row][1:]
                continue
            if row[0].strip().lower() == 'header data':
                header_data = [x.strip() for x in row][1:]
                break
        if not (header_data or header_fields):
            return None
        if not (header_data and header_fields):
            self.error("File is missing header row or header data")
            return None
        # inject us out of here
        values = dict(zip(header_fields, header_data))
        # blank cell from sheet will probably make it in here:
        if '' in values:
            del (values[''])
        return values

    def save_header_data(self):
        """Save values from the file's header row into their schema fields.
        """
        client = self.aq_parent

        headers = self.get_header_values()
        if not headers:
            return False

        # Plain header fields that can be set into plain schema fields:
        for h, f in [
            ('File name', 'Filename'),
            ('No of Samples', 'NrSamples'),
            ('Client name', 'ClientName'),
            ('Client ID', 'ClientID'),
            ('Client Order Number', 'ClientOrderNumber'),
            ('Client Reference', 'ClientReference')
        ]:
            v = headers.get(h, None)
            if v:
                field = self.schema[f]
                field.set(self, v)
            del (headers[h])

        # Primary Contact
        v = headers.get('Contact', None)
        contacts = [x for x in client.objectValues('Contact')]
        contact = [c for c in contacts if c.Title() == v]
        if contact:
            self.schema['Contact'].set(self, contact)
        else:
            self.error("Specified contact '%s' does not exist; using '%s'"%
                       (v, contacts[0].Title()))
            self.schema['Contact'].set(self, contacts[0])
        del (headers['Contact'])

        # CCContacts
        field_value = {
            'CCNamesReport': '',
            'CCEmailsReport': '',
            'CCNamesInvoice': '',
            'CCEmailsInvoice': ''
        }
        for h, f in [
            # csv header name      DataGrid Column ID
            ('CC Names - Report', 'CCNamesReport'),
            ('CC Emails - Report', 'CCEmailsReport'),
            ('CC Names - Invoice', 'CCNamesInvoice'),
            ('CC Emails - Invoice', 'CCEmailsInvoice'),
        ]:
            if h in headers:
                values = [x.strip() for x in headers.get(h, '').split(",")]
                field_value[f] = values if values else ''
                del (headers[h])
        self.schema['CCContacts'].set(self, [field_value])

        if headers:
            unexpected = ','.join(headers.keys())
            self.error("Unexpected header fields: %s" % unexpected)

    def get_sample_values(self):
        """Read the rows specifying Samples and return a dictionary with
        related data.

        keys are:
            headers - row with "Samples" in column 0.  These headers are
               used as dictionary keys in the rows below.
            prices - Row with "Analysis Price" in column 0.
            total_analyses - Row with "Total analyses" in colmn 0
            price_totals - Row with "Total price excl Tax" in column 0
            samples - All other sample rows.

        """
        res = {'samples': []}
        lines = self.getOriginalFile().data.splitlines()
        reader = csv.reader(lines)
        next_rows_are_sample_rows = False
        for row in reader:
            if not any(row):
                continue
            if next_rows_are_sample_rows:
                vals = [x.strip() for x in row]
                if not any(vals):
                    continue
                res['samples'].append(zip(res['headers'], vals))
            elif row[0].strip().lower() == 'samples':
                res['headers'] = [x.strip() for x in row]
            elif row[0].strip().lower() == 'analysis price':
                res['prices'] = \
                    zip(res['headers'], [x.strip() for x in row])
            elif row[0].strip().lower() == 'total analyses':
                res['total_analyses'] = \
                    zip(res['headers'], [x.strip() for x in row])
            elif row[0].strip().lower() == 'total price excl tax':
                res['price_totals'] = \
                    zip(res['headers'], [x.strip() for x in row])
                next_rows_are_sample_rows = True
        return res

    def save_sample_data(self):
        """Save values from the file's header row into the DataGrid columns
        after doing some very basic validation
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        keywords = self.bika_setup_catalog.uniqueValuesFor('getKeyword')
        profiles = []
        for p in bsc(portal_type='AnalysisProfile'):
            p = p.getObject()
            profiles.append(p.Title())
            profiles.append(p.getProfileKey())

        sample_data = self.get_sample_values()
        if not sample_data:
            return False

        # columns that we expect, but do not find, are listed here.
        # we report on them only once, after looping through sample rows.
        missing = set()

        # This contains all sample header rows that were not handled
        # by this code
        unexpected = set()

        # Save other errors here instead of sticking them directly into
        # the field, so that they show up after MISSING and before EXPECTED
        errors = []

        # This will be the new sample-data field value, when we are done.
        grid_rows = []

        row_nr = 0
        for row in sample_data['samples']:
            row = dict(row)
            row_nr += 1

            # sid is just for referring the user back to row X in their
            # in put spreadsheet
            gridrow = {'sid': row['Samples']}
            del (row['Samples'])

            # We'll use this later to verify the number against selections
            if 'Total number of Analyses or Profiles' in row:
                nr_an = row['Total number of Analyses or Profiles']
                del (row['Total number of Analyses or Profiles'])
            else:
                nr_an = 0
            try:
                nr_an = int(nr_an)
            except ValueError:
                nr_an = 0

            # TODO this is ignored and is probably meant to serve some purpose.
            del (row['Price excl Tax'])

            # ContainerType - not part of sample or AR schema
            if 'ContainerType' in row:
                title = row['ContainerType']
                if title:
                    obj = self.lookup(('ContainerType',),
                                      Title=row['ContainerType'])
                    if obj:
                        gridrow['ContainerType'] = obj[0].UID
                del (row['ContainerType'])

            if 'SampleMatrix' in row:
                # SampleMatrix - not part of sample or AR schema
                title = row['SampleMatrix']
                if title:
                    obj = self.lookup(('SampleMatrix',),
                                      Title=row['SampleMatrix'])
                    if obj:
                        gridrow['SampleMatrix'] = obj[0].UID
                del (row['SampleMatrix'])

            # match against sample schema
            for k, v in row.items():
                if k in ['Analyses', 'Profiles']:
                    continue
                if k in sample_schema:
                    del (row[k])
                    if v:
                        try:
                            value = self.munge_field_value(
                                sample_schema, row_nr, k, v)
                            gridrow[k] = value
                        except ValueError as e:
                            errors.append(e.message)

            # match against ar schema
            for k, v in row.items():
                if k in ['Analyses', 'Profiles']:
                    continue
                if k in ar_schema:
                    del (row[k])
                    if v:
                        try:
                            value = self.munge_field_value(
                                ar_schema, row_nr, k, v)
                            gridrow[k] = value
                        except ValueError as e:
                            errors.append(e.message)

            # Count and remove Keywords and Profiles from the list
            gridrow['Analyses'] = []
            for k, v in row.items():
                if k in keywords:
                    del (row[k])
                    if str(v).strip().lower() not in ('', '0', 'false'):
                        gridrow['Analyses'].append(k)
            gridrow['Profiles'] = []
            for k, v in row.items():
                if k in profiles:
                    del (row[k])
                    if str(v).strip().lower() not in ('', '0', 'false'):
                        gridrow['Profiles'].append(k)
            if len(gridrow['Analyses']) + len(gridrow['Profiles']) != nr_an:
                errors.append(
                    "Row %s: Number of analyses does not match provided value" %
                    row_nr)

            grid_rows.append(gridrow)

        self.setSampleData(grid_rows)

        if missing:
            self.error("SAMPLES: Missing expected fields: %s" %
                       ','.join(missing))

        for thing in errors:
            self.error(thing)

        if unexpected:
            self.error("Unexpected header fields: %s" %
                       ','.join(unexpected))

    def get_batch_header_values(self):
        """Scrape the "Batch Header" values from the original input file
        """
        lines = self.getOriginalFile().data.splitlines()
        reader = csv.reader(lines)
        batch_headers = batch_data = []
        for row in reader:
            if not any(row):
                continue
            if row[0].strip().lower() == 'batch header':
                batch_headers = [x.strip() for x in row][1:]
                continue
            if row[0].strip().lower() == 'batch data':
                batch_data = [x.strip() for x in row][1:]
                break
        if not (batch_data or batch_headers):
            return None
        if not (batch_data and batch_headers):
            self.error("Missing batch headers or data")
            return None
        # Inject us out of here
        values = dict(zip(batch_headers, batch_data))
        return values

    def create_or_reference_batch(self):
        """Save reference to batch, if existing batch specified
        Create new batch, if possible with specified values
        """
        client = self.aq_parent
        batch_headers = self.get_batch_header_values()
        if not batch_headers:
            return False
        # if the Batch's Title is specified and exists, no further
        # action is required. We will just set the Batch field to
        # use the existing object.
        batch_title = batch_headers.get('title', False)
        if batch_title:
            existing_batch = [x for x in client.objectValues('Batch')
                              if x.title == batch_title]
            if existing_batch:
                self.setBatch(existing_batch[0])
                return existing_batch[0]
        # If the batch title is specified but does not exist,
        # we will attempt to create the bach now.
        if 'title' in batch_headers:
            if 'id' in batch_headers:
                del (batch_headers['id'])
            if '' in batch_headers:
                del (batch_headers[''])
            batch = _createObjectByType('Batch', client, tmpID())
            batch.processForm()
            batch.edit(**batch_headers)
            self.setBatch(batch)

    def munge_field_value(self, schema, row_nr, fieldname, value):
        """Convert a spreadsheet value into a field value that fits in
        the corresponding schema field.
        - boolean: All values are true except '', 'false', or '0'.
        - reference: The title of an object in field.allowed_types;
            returns a UID or list of UIDs
        - datetime: returns a string value from ulocalized_time

        Tho this is only used during "Saving" of csv data into schema fields,
        it will flag 'validation' errors, as this is the only chance we will
        get to complain about these field values.

        """
        field = schema[fieldname]
        if field.type == 'boolean':
            value = str(value).strip().lower()
            value = '' if value in ['0', 'no', 'false', 'none'] else '1'
            return value
        if field.type == 'reference':
            value = str(value).strip()
            brains = self.lookup(field.allowed_types, Title=value)
            if not brains:
                brains = self.lookup(field.allowed_types, UID=value)
            if not brains:
                raise ValueError('Row %s: value is invalid (%s=%s)' % (
                    row_nr, fieldname, value))
            if field.multiValued:
                return [b.UID for b in brains] if brains else []
            else:
                return brains[0].UID if brains else None
        if field.type == 'datetime':
            try:
                value = DateTime(value)
                return ulocalized_time(
                    value, long_format=True, time_only=False, context=self)
            except:
                raise ValueError('Row %s: value is invalid (%s=%s)' % (
                    row_nr, fieldname, value))
        return str(value)

    def validate_headers(self):
        """Validate headers fields from schema
        """

        pc = getToolByName(self, 'portal_catalog')
        pu = getToolByName(self, "plone_utils")

        client = self.aq_parent

        # Verify Client Name
        if self.getClientName() != client.Title():
            self.error("%s: value is invalid (%s)." % (
                'Client name', self.getClientName()))

        # Verify Client ID
        if self.getClientID() != client.getClientID():
            self.error("%s: value is invalid (%s)." % (
                'Client ID', self.getClientID()))

        existing_arimports = pc(portal_type='ARImport',
                                review_state=['valid', 'imported'])
        # Verify Client Order Number
        for arimport in existing_arimports:
            if arimport.UID == self.UID() \
                    or not arimport.getClientOrderNumber():
                continue
            arimport = arimport.getObject()

            if arimport.getClientOrderNumber() == self.getClientOrderNumber():
                self.error('%s: already used by existing ARImport.' %
                           'ClientOrderNumber')
                break

        # Verify Client Reference
        for arimport in existing_arimports:
            if arimport.UID == self.UID() \
                    or not arimport.getClientReference():
                continue
            arimport = arimport.getObject()
            if arimport.getClientReference() == self.getClientReference():
                self.error('%s: already used by existing ARImport.' %
                           'ClientReference')
                break

        # getCCContacts has no value if object is not complete (eg during test)
        if self.getCCContacts():
            cc_contacts = self.getCCContacts()[0]
            contacts = [x for x in client.objectValues('Contact')]
            contact_names = [c.Title() for c in contacts]
            # validate Contact existence in this Client
            for k in ['CCNamesReport', 'CCNamesInvoice']:
                for val in cc_contacts[k]:
                    if val and val not in contact_names:
                        self.error('%s: value is invalid (%s)' % (k, val))
        else:
            cc_contacts = {'CCNamesReport': [],
                           'CCEmailsReport': [],
                           'CCNamesInvoice': [],
                           'CCEmailsInvoice': []
                           }
            # validate Contact existence in this Client
            for k in ['CCEmailsReport', 'CCEmailsInvoice']:
                for val in cc_contacts.get(k, []):
                    if val and not pu.validateSingleNormalizedEmailAddress(val):
                        self.error('%s: value is invalid (%s)' % (k, val))

    def validate_samples(self):
        """Scan through the SampleData values and make sure
        that each one is correct
        """

        bsc = getToolByName(self, 'bika_setup_catalog')
        keywords = bsc.uniqueValuesFor('getKeyword')
        profiles = []
        for p in bsc(portal_type='AnalysisProfile'):
            p = p.getObject()
            profiles.append(p.Title())
            profiles.append(p.getProfileKey())

        row_nr = 0
        for gridrow in self.getSampleData():
            row_nr += 1

            # validate against sample and ar schemas
            for k, v in gridrow.items():
                if k in ['Analysis', 'Profiles']:
                    break
                if k in sample_schema:
                    try:
                        self.validate_against_schema(
                            sample_schema, row_nr, k, v)
                        continue
                    except ValueError as e:
                        self.error(e.message)
                        break
                if k in ar_schema:
                    try:
                        self.validate_against_schema(
                            ar_schema, row_nr, k, v)
                    except ValueError as e:
                        self.error(e.message)

            an_cnt = 0
            for v in gridrow['Analyses']:
                if v and v not in keywords:
                    self.error("Row %s: value is invalid (%s=%s)" %
                               ('Analysis keyword', row_nr, v))
                else:
                    an_cnt += 1
            for v in gridrow['Profiles']:
                if v and v not in profiles:
                    self.error("Row %s: value is invalid (%s=%s)" %
                               ('Profile Title', row_nr, v))
                else:
                    an_cnt += 1
            if not an_cnt:
                self.error("Row %s: No valid analyses or profiles" % row_nr)

    def validate_against_schema(self, schema, row_nr, fieldname, value):
        """
        """
        field = schema[fieldname]
        if field.type == 'boolean':
            value = str(value).strip().lower()
            return value
        if field.type == 'reference':
            value = str(value).strip()
            if field.required and not value:
                raise ValueError("Row %s: %s field requires a value" % (
                    row_nr, fieldname))
            if not value:
                return value
            brains = self.lookup(field.allowed_types, UID=value)
            if not brains:
                raise ValueError("Row %s: value is invalid (%s=%s)" % (
                    row_nr, fieldname, value))
            if field.multiValued:
                return [b.UID for b in brains] if brains else []
            else:
                return brains[0].UID if brains else None
        if field.type == 'datetime':
            try:
                ulocalized_time(DateTime(value), long_format=True,
                                time_only=False, context=self)
            except:
                raise ValueError('Row %s: value is invalid (%s=%s)' % (
                    row_nr, fieldname, value))
        return value

    def lookup(self, allowed_types, **kwargs):
        """Lookup an object of type (allowed_types).  kwargs is sent
        directly to the catalog.
        """
        at = getToolByName(self, 'archetype_tool')
        for portal_type in allowed_types:
            catalog = at.catalog_map.get(portal_type, [None])[0]
            catalog = getToolByName(self, catalog)
            kwargs['portal_type'] = portal_type
            brains = catalog(**kwargs)
            if brains:
                return brains

    def get_row_services(self, row):
        """Return a list of services which are referenced in Analyses.
        values may be UID, Title or Keyword.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        services = set()
        for val in row.get('Analyses', []):
            brains = bsc(portal_type='AnalysisService', getKeyword=val)
            if not brains:
                brains = bsc(portal_type='AnalysisService', title=val)
            if not brains:
                brains = bsc(portal_type='AnalysisService', UID=val)
            if brains:
                services.add(brains[0].UID)
            else:
                self.error("Invalid analysis specified: %s" % val)
        return list(services)

    def get_row_profile_services(self, row):
        """Return a list of services which are referenced in profiles
        values may be UID, Title or ProfileKey.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        services = set()
        profiles = [x.getObject() for x in bsc(portal_type='AnalysisProfile')]
        for val in row.get('Profiles', []):
            objects = [x for x in profiles
                       if val in (x.getProfileKey(), x.UID(), x.Title())]
            if objects:
                for service in objects[0].getService():
                    services.add(service.UID())
            else:
                self.error("Invalid profile specified: %s" % val)
        return list(services)

    def get_row_container(self, row):
        """Return a sample container
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        val = row.get('Container', False)
        if val:
            brains = bsc(portal_type='Container', UID=row['Container'])
            if brains:
                brains[0].getObject()
            brains = bsc(portal_type='ContainerType', UID=row['Container'])
            if brains:
                # XXX Cheating.  The calculation of capacity vs. volume  is not done.
                return brains[0].getObject()
        return None

    def get_row_profiles(self, row):
        bsc = getToolByName(self, 'bika_setup_catalog')
        profiles = []
        for profile_title in row.get('Profiles', []):
            profile = bsc(portal_type='AnalysisProfile', title=profile_title)
            profiles.append(profile)
        return profiles

    def Vocabulary_SamplePoint(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        folders = [self.bika_setup.bika_samplepoints]
        if IClient.providedBy(self.aq_parent):
            folders.append(self.aq_parent)
        return vocabulary(allow_blank=True, portal_type='SamplePoint')

    def Vocabulary_SampleMatrix(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='SampleMatrix')

    def Vocabulary_SampleType(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        folders = [self.bika_setup.bika_sampletypes]
        if IClient.providedBy(self.aq_parent):
            folders.append(self.aq_parent)
        return vocabulary(allow_blank=True, portal_type='SampleType')

    def Vocabulary_ContainerType(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='ContainerType')

    def Vocabulary_Priority(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='ARPriority')

    def error(self, msg):
        errors = list(self.getErrors())
        errors.append(msg)
        self.setErrors(errors)


atapi.registerType(ARImport, PROJECTNAME)
