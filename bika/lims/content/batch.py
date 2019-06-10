# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget as bikaRecordsWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import IClient
from plone.app.folder.folder import ATFolder
from plone.indexer import indexer
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements


@indexer(IBatch)
def BatchDate(instance):
    return instance.Schema().getField('BatchDate').get(instance)


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
        required=False,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            # XXX This field can never hold a user value, because it is
            #     invisible (see custom getBatchID getter method)
            # => we should remove that field
            visible=False,
            label=_("Batch ID"),
        )
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
            base_query={'review_state': 'active'},
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'Title', 'width': '60', 'label': _('Title')},
                {'columnName': 'ClientID', 'width': '20', 'label': _('Client ID')}
            ],
        ),
    ),

    StringField(
        'ClientBatchID',
        required=0,
        widget=StringWidget(
            label=_("Client Batch ID")
        )
    ),

    DateTimeField(
        'BatchDate',
        required=False,
        widget=DateTimeWidget(
            label=_('Date'),
        ),
    ),

    LinesField(
        'BatchLabels',
        vocabulary="BatchLabelVocabulary",
        accessor="getLabelNames",
        widget=MultiSelectionWidget(
            label=_("Batch Labels"),
            format="checkbox",
        )
    ),

    RemarksField(
        'Remarks',
        searchable=True,
        widget=RemarksWidget(
            label=_('Remarks'),
        )
    ),

    ReferenceField(
        'InheritedObjects',
        required=0,
        multiValued=True,
        allowed_types=('AnalysisRequest'),  # batches are expanded on save
        referenceClass=HoldingReference,
        relationship='BatchInheritedObjects',
        widget=ReferenceWidget(
            visible=False,
        ),
    ),

    InheritedObjectsUIField(
        'InheritedObjectsUI',
        required=False,
        type='InheritedObjects',
        subfields=('Title', 'ObjectID', 'Description'),
        subfield_sizes={
            'Title': 25,
            'ObjectID': 25,
            'Description': 50,
        },

        subfield_labels={
            'Title': _('Title'),
            'ObjectID': _('Object ID'),
            'Description': _('Description')
        },

        widget=bikaRecordsWidget(
            label=_("Inherit From"),
            description=_(
                "Include all samples belonging to the selected objects."),
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
))

# Remove implicit `uniquefieldvalidator` coming from `BikaFolderSchema`
schema['title'].validators = ()
schema['title'].widget.description = _("If no value is entered, the Batch ID"
                                       " will be auto-generated.")
schema['title'].required = False
schema['title'].widget.visible = True
schema['title'].widget.description = _("If no Title value is entered,"
                                       " the Batch ID will be used.")
schema['description'].required = False
schema['description'].widget.visible = True

schema.moveField('ClientBatchID', before='description')
schema.moveField('BatchID', before='description')
schema.moveField('title', before='description')
schema.moveField('Client', after='title')


class Batch(ATFolder):
    """A Batch combines multiple ARs into a logical unit
    """
    implements(IBatch, ICancellable)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the Batch ID if title is not defined
        """
        titlefield = self.Schema().getField('title')
        if titlefield.widget.visible:
            return safe_unicode(self.title).encode('utf-8')
        else:
            return safe_unicode(self.id).encode('utf-8')

    @deprecated("This method will be removed in senaite.core 1.2.0")
    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getClient(self):
        """Retrieves the Client for which the current Batch is attached to
           Tries to retrieve the Client from the Schema property, but if not
           found, searches for linked ARs and retrieve the Client from the
           first one. If the Batch has no client, returns None.
        """
        client = self.Schema().getField('Client').get(self)
        if client:
            return client
        client = self.aq_parent
        if IClient.providedBy(client):
            return client

    def getClientTitle(self):
        client = self.getClient()
        if client:
            return client.Title()
        return ""

    def getClientUID(self):
        """This index is required on batches so that batch listings can be
        filtered by client
        """
        client = self.getClient()
        if client:
            return client.UID()

    def getContactTitle(self):
        return ""

    def getProfilesTitle(self):
        return ""

    def getAnalysisService(self):
        analyses = set()
        for ar in self.getAnalysisRequests():
            for an in ar.getAnalyses():
                analyses.add(an)
        value = []
        for analysis in analyses:
            val = analysis.Title
            if val not in value:
                value.append(val)
        return list(value)

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

    @deprecated("Please use getId instead")
    def getBatchID(self):
        # NOTE This method is a custom getter of the invisible field "BatchID".
        #      Therefore, it is unlikely that it returns anything else than `getId`.
        if self.BatchID:
            return self.BatchID
        if self.checkCreationFlag():
            return self.BatchID
        return self.getId()

    def BatchLabelVocabulary(self):
        """Return all batch labels as a display list
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type='BatchLabel',
                     is_active=True,
                     sort_on='sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequestsBrains(self, **kwargs):
        """Return all the Analysis Requests brains linked to the Batch
        kargs are passed directly to the catalog.
        """
        kwargs['getBatchUID'] = self.UID()
        catalog = getToolByName(self, CATALOG_ANALYSIS_REQUEST_LISTING)
        brains = catalog(kwargs)
        return brains

    def getAnalysisRequests(self, **kwargs):
        """Return all the Analysis Requests objects linked to the Batch kargs
        are passed directly to the catalog.
        """
        brains = self.getAnalysisRequestsBrains(**kwargs)
        return [b.getObject() for b in brains]

    def isOpen(self):
        """Returns true if the Batch is in 'open' state
        """
        return api.get_workflow_status_of(self) not in ["cancelled", "closed"]

    def getLabelNames(self):
        uc = getToolByName(self, 'uid_catalog')
        uids = [uid for uid in self.Schema().getField('BatchLabels').get(self)]
        labels = [label.getObject().title for label in uc(UID=uids)]
        return labels


registerType(Batch, PROJECTNAME)
