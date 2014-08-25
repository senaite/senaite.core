from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _, EditARContact
from bika.lims.utils import t, getUsers
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBatch
from bika.lims.workflow import skip, BatchState, StateFlow, getCurrentState,\
    CancellationState
from bika.lims.browser.widgets import DateTimeWidget
from Products.CMFCore import permissions
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
from bika.lims.permissions import EditBatch
from plone.indexer import indexer
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField
from bika.lims.browser.widgets import RecordsWidget as bikaRecordsWidget
from bika.lims.browser.widgets import ReferenceWidget

#from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

import sys


class InheritedObjectsUIField(RecordsField):

    """XXX bika.lims.RecordsWidget doesn't cater for multiValued fields
    InheritedObjectsUI is a RecordsField because we want the RecordsWidget,
    but the values are stored in ReferenceField 'InheritedObjects'
    """

    def get(self, instance, **kwargs):
        # Return the formatted contents of InheritedObjects field.
        field = instance.Schema()['InheritedObjects']
        value = field.get(instance)
        return [{'Title': x.Title(),
                 'ObjectID': x.id,
                 'Description': x.Description()} for x in value]

    def getRaw(self, instance, **kwargs):
        # Return the formatted contents of InheritedObjects field.
        field = instance.Schema()['InheritedObjects']
        value = field.get(instance)
        return [{'Title': x.Title(),
                 'ObjectID': x.id,
                 'Description': x.Description()} for x in value]

    def set(self, instance, value, **kwargs):
        _field = instance.Schema().getField('InheritedObjects')
        uids = []
        if value:
            bc = getToolByName(instance, 'bika_catalog')
            ids = [x['ObjectID'] for x in value]
            if ids:
                proxies = bc(id=ids)
                if proxies:
                    uids = [x.UID for x in proxies]
        RecordsField.set(self, instance, value)
        return _field.set(instance, uids)


schema = BikaFolderSchema.copy() + Schema((
    StringField(
        'BatchID',
        searchable=True,
        required=False,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible=False,
            label=_("Batch ID"),
        )
    ),
    DateTimeField(
        'BatchDate',
        required=False,
        widget=DateTimeWidget(
            label=_('Date'),
        ),
    ),
    ReferenceField(
        'Client',
        required=0,
        allowed_types=('Client',),
        relationship='BatchClient',
        widget=ReferenceWidget(
            label=_("Client"),
            size=30,
            visible=True,
            base_query={'inactive_state': 'active'},
            showOn=True,
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'ClientID', 'width': '20', 'label': _('Client ID')},
                      {'columnName': 'Title', 'width': '80', 'label': _('Title')}
                     ],
      ),
    ),
    ReferenceField(
        'Contact',
        required=0,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Contact',),
        relationship='BatchContact',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Contact"),
            size=20,
            helper_js=("bika_widgets/referencewidget.js",),
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                     ],
        ),
    ),
    StringField(
        'ClientBatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            label=_("Client Batch ID")
        )
    ),
    DateTimeField(
        'SamplingDate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Sampling Date"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
        ),
    ),
    ReferenceField(
        'SamplePoint',
        required=0,
        allowed_types='SamplePoint',
        relationship='BatchSamplePoint',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Point"),
            description=_("Location where sample was taken"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'SampleType',
        required=0,
        allowed_types='SampleType',
        relationship='BatchSampleType',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Type"),
            description=_("Create a new sample of this type"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'SampleMatrix',
        required=False,
        allowed_types='SampleMatrix',
        relationship='BatchSampleMatrix',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Matrix"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'Specification',
        allowed_types='AnalysisSpec',
        relationship='BatchAnalysisSpec',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Analysis Specification"),
            description=_("Choose default AR specification values"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            colModel=[
                {'columnName': 'contextual_title',
                 'width': '30',
                 'label': _('Title'),
                 'align': 'left'},
                {'columnName': 'SampleTypeTitle',
                 'width': '70',
                 'label': _('SampleType'),
                 'align': 'left'},
                # UID is required in colModel
                {'columnName': 'UID', 'hidden': True},
            ],
            showOn=True,
        ),
    ),
    ReferenceField(
        'Template',
        allowed_types=('ARTemplate',),
        referenceClass=HoldingReference,
        relationship='BatchARTemplate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Template"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'Profile',
        allowed_types=('AnalysisProfile',),
        referenceClass=HoldingReference,
        relationship='BatchAnalysisProfile',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Analysis Profile"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'DefaultContainerType',
        allowed_types = ('ContainerType',),
        relationship = 'AnalysisRequestContainerType',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_('Default Container'),
            description=_('Default container for new sample partitions'),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    StringField(
        'ClientOrderNumber',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_('Client Order Number'),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
        ),
    ),
    StringField(
        'ClientReference',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_('Client Reference'),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
        ),
    ),
    FloatField(
        'ContainerTemperature',
        default_content_type='text/x-web-intelligent',
        default_output_type="text/plain",
        widget=DecimalWidget(
            label=_('Container Temperature'),
            description = _("The temperature of the sample container on arrival"),
        )
    ),
    StringField(
        'ContainerCondition',
        default_content_type='text/x-web-intelligent',
        default_output_type="text/plain",
        widget=StringWidget(
            label=_('Container Condition'),
            description = _("The physical condition of the sample container on arrival"),
        )
    ),
    LinesField(
        'BatchLabels',
        vocabulary="BatchLabelVocabulary",
        accessor="getLabelNames",
        widget=MultiSelectionWidget(
            label=_("Batch labels"),
            format="checkbox",
        )
    ),
    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        )
    ),
    ReferenceField(
        'InheritedObjects',
        required=0,
        multiValued=True,
        allowed_types=('AnalysisRequest'),  # batches are expanded on save
        referenceClass = HoldingReference,
        relationship = 'BatchInheritedObjects',
        widget=ReferenceWidget(
            visible=False,
        ),
    ),
    ReferenceField(
        'Priority',
        allowed_types=('ARPriority',),
        referenceClass=HoldingReference,
        relationship='BatchPriority',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Priority"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            colModel=[
                {'columnName': 'Title', 'width': '30',
                 'label': _('Title'), 'align': 'left'},
                {'columnName': 'Description', 'width': '70',
                 'label': _('Description'), 'align': 'left'},
                {'columnName': 'sortKey', 'hidden': True},
                {'columnName': 'UID', 'hidden': True},
            ],
            sidx='sortKey',
            sord='asc',
            showOn=True,
        ),
    ),
    DateTimeField('DateSampled',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Sampled"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
        ),
    ),
    StringField('Sampler',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        vocabulary='getSamplers',
        widget=SelectionWidget(
            format='select',
            label=_("Sampler"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     },
        ),
    ),
    InheritedObjectsUIField(
        'InheritedObjectsUI',
        required=False,
        type='InheritedObjects',
        subfields=('Title', 'ObjectID', 'Description'),
        subfield_sizes = {'Title': 25,
                          'ObjectID': 25,
                          'Description': 50,
                          },
        subfield_labels = {'Title': _('Title'),
                           'ObjectID': _('Object ID'),
                           'Description': _('Description')
                           },
        widget = bikaRecordsWidget(
            label=_("Inherit From"),
            description=_(
                "Include all analysis requests belonging to the selected objects."),
            innerJoin="<br/>",
            combogrid_options={
                'Title': {
                    'colModel': [
                        {'columnName': 'Title', 'width': '25',
                         'label': _('Title'), 'align': 'left'},
                        {'columnName': 'ObjectID', 'width': '25',
                         'label': _('Object ID'), 'align': 'left'},
                        {'columnName': 'Description', 'width': '50',
                         'label': _('Description'), 'align': 'left'},
                        {'columnName': 'UID', 'hidden': True},
                    ],
                    'url': 'getAnalysisContainers',
                    'showOn': False,
                    'width': '600px'
                },
                'ObjectID': {
                    'colModel': [
                        {'columnName': 'Title', 'width': '25',
                         'label': _('Title'), 'align': 'left'},
                        {'columnName': 'ObjectID', 'width': '25',
                         'label': _('Object ID'), 'align': 'left'},
                        {'columnName': 'Description', 'width': '50',
                         'label': _('Description'), 'align': 'left'},
                        {'columnName': 'UID', 'hidden': True},
                    ],
                    'url': 'getAnalysisContainers',
                    'showOn': False,
                    'width': '600px'
                },
            },
        ),
    ),
)
)


schema['title'].required = False
schema['title'].widget.visible = True
schema['title'].widget.description = _("If no Title value is entered, the Batch ID will be used.")
schema['description'].required = False
schema['description'].widget.visible = True

# schema.moveField('ClientBatchID', before='description')
# schema.moveField('BatchID', before='description')
# schema.moveField('title', before='description')
# schema.moveField('Client', after='title')


class Batch(ATFolder):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Batch ID if title is not defined """
        titlefield = self.Schema().getField('title')
        if titlefield.widget.visible:
            return safe_unicode(self.title).encode('utf-8')
        else:
            return safe_unicode(self.id).encode('utf-8')

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getClientTitle(self):
        client = self.getClient()
        if client:
            return client.Title()
        return ""

    def getContactTitle(self):
        return ""

    def getProfileTitle(self):
        return ""

    def getAnalysisCategory(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getCategoryTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysisService(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getServiceTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    security.declarePublic('getBatchID')

    def getBatchID(self):
        return self.getId()

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type='BatchLabel',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequests(self):
        """ Return all the Analysis Requests linked to the Batch
        """
        return self.getBackReferences("AnalysisRequestBatch")

    def isOpen(self):
        """ Returns true if the Batch is in 'open' state
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.open \
            and canstatus == CancellationState.active

    def getLabelNames(self):
        uc = getToolByName(self, 'uid_catalog')
        uids = [uid for uid in self.Schema().getField('BatchLabels').get(self)]
        labels = [label.getObject().title for label in uc(UID=uids)]
        return labels

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user.  Copied from content/client.py
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type='Contact',
               getUsername=user_id)
        if len(r) == 1:
            return r[0].UID

    def workflow_guard_open(self):
        """ Permitted if current review_state is 'closed' or 'cancelled'
            The open transition is already controlled by 'Bika: Reopen Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific-needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.closed \
            and canstatus == CancellationState.active

    def workflow_guard_close(self):
        """ Permitted if current review_state is 'open'.
            The close transition is already controlled by 'Bika: Close Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.open \
            and canstatus == CancellationState.active

    def getSamplers(self):
        return getUsers(self, ['LabManager', 'Sampler'])


registerType(Batch, PROJECTNAME)


@indexer(IBatch)
def BatchDate(instance):
    return instance.Schema().getField('BatchDate').get(instance)
