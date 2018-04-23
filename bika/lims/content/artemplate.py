# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""
    AnalysisRequests often use the same configurations.
    ARTemplate includes all AR fields, including preset AnalysisProfile
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.ATExtensions.field.records import RecordsField
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.interfaces import IARTemplate
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.browser.widgets import ARTemplatePartitionsWidget
from bika.lims.browser.widgets import ARTemplateAnalysesWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
    ## SamplePoint and SampleType references are managed with
    ## accessors and mutators below to get/set a string value
    ## (the Title of the object), but still store a normal Reference.
    ## Form autocomplete widgets can then work with the Titles.
    ReferenceField('SamplePoint',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SamplePoint',),
        relationship = 'ARTemplateSamplePoint',
        referenceClass = HoldingReference,
        accessor = 'getSamplePoint',
        edit_accessor = 'getSamplePoint',
        mutator = 'setSamplePoint',
        widget=ReferenceWidget(
            label = _("Sample Point"),
            description = _("Location where sample was taken"),
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible',
                     'secondary': 'invisible'},
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ComputedField(
        "SamplePointUID",
        expression="context.Schema()['SamplePoint'].get(context) and context.Schema()['SamplePoint'].get(context).UID() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ReferenceField('SampleType',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'ARTemplateSampleType',
        referenceClass = HoldingReference,
        accessor = 'getSampleType',
        edit_accessor = 'getSampleType',
        mutator = 'setSampleType',
        widget=ReferenceWidget(
            label = _("Sample Type"),
            description = _("Create a new sample of this type"),
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible',
                     'secondary': 'invisible'},
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ComputedField(
        "SampleTypeUID",
        expression="context.Schema()['SampleType'].get(context) and context.Schema()['SampleType'].get(context).UID() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    BooleanField('Composite',
        default=False,
        widget=BooleanWidget(
            label=_("Composite"),
            description=_("It's a composite sample"),
        ),
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _("Remarks"),
            append_only = True,
        ),
    ),
    RecordsField('Partitions',
        schemata = 'Sample Partitions',
        required = 0,
        type = 'artemplate_parts',
        subfields = ('part_id',
                     'Container',
                     'Preservation',
                     'container_uid',
                     'preservation_uid'),
        subfield_labels = {'part_id': _('Partition'),
                           'Container': _('Container'),
                           'Preservation': _('Preservation')},
        subfield_sizes = {'part_id': 15,
                           'Container': 35,
                           'Preservation': 35},
        subfield_hidden = {'preservation_uid': True,
                           'container_uid': True},
        default = [{'part_id':'part-1',
                    'Container':'',
                    'Preservation':'',
                    'container_uid':'',
                    'preservation_uid':''}],
        widget=ARTemplatePartitionsWidget(
            label = _("Sample Partitions"),
            description = _("Configure the sample partitions and preservations " + \
                            "for this template. Assign analyses to the different " + \
                            "partitions on the template's Analyses tab"),
            combogrid_options={
                'Container': {
                    'colModel': [
                        {'columnName':'container_uid', 'hidden':True},
                        {'columnName':'Container', 'width':'30', 'label':_('Container')},
                        {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                    'url': 'getcontainers',
                    'showOn': True,
                    'width': '550px'
                },
                'Preservation': {
                    'colModel': [
                        {'columnName':'preservation_uid', 'hidden':True},
                        {'columnName':'Preservation', 'width':'30', 'label':_('Preservation')},
                        {'columnName':'Description', 'width':'70', 'label':_('Description')}],
                    'url': 'getpreservations',
                    'showOn': True,
                    'width': '550px'
                },
            },
         ),
    ),
    ReferenceField('AnalysisProfile',
        schemata = 'Analyses',
        required = 0,
        multiValued = 0,
        allowed_types = ('AnalysisProfile',),
        relationship = 'ARTemplateAnalysisProfile',
        widget=ReferenceWidget(
            label = _("Analysis Profile"),
            description =_("The Analysis Profile selection for this template"),
            visible={'edit': 'visible', 'view': 'visible', 'add': 'visible',
                     'secondary': 'invisible'},
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    RecordsField('Analyses',
        schemata = 'Analyses',
        required = 0,
        type = 'analyses',
        subfields = ('service_uid', 'partition'),
        subfield_labels = {'service_uid': _('Title'),
                           'partition': _('Partition')},
        default = [],
        widget = ARTemplateAnalysesWidget(
            label = _("Analyses"),
            description=_("Select analyses to include in this template"),
        )
    ),
    # Custom settings for the assigned analysis services
    # https://jira.bikalabs.com/browse/LIMS-1324
    # Fields:
    #   - uid: Analysis Service UID
    #   - hidden: True/False. Hide/Display in results reports
    RecordsField('AnalysisServicesSettings',
         required=0,
         subfields=('uid', 'hidden',),
         widget=ComputedWidget(visible=False),
    ),
),
)

schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()

class ARTemplate(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IARTemplate)

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('AnalysisProfiles')
    def AnalysisProfiles(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for p in bsc(portal_type='AnalysisProfile',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            p = p.getObject()
            title = p.Title()
            items.append((p.UID(), title))
        items = [['','']] + list(items)
        return DisplayList(items)

    def getClientUID(self):
        """This populates the getClientUID catalog
        If the parent is the system bika_artemplates folder,
        then that folder's UID must be returned in this index.
        """
        return self.aq_parent.UID()
        return ''

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            template, returns a dictionary with the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings() \
                if s.get('uid','') == uid]
        return sets[0] if sets else {'uid': uid}

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this template, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                template or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('%s is not valid' % uid)
        return sets.get('hidden', False)


    def remove_service(self, service):
        """Removes the service passed in from the services offered by the
        current Template. If the Analysis Service passed in is not assigned to
        this Analysis Template, returns False.
        :param service: the service to be removed from this AR Template
        :type service: AnalysisService
        :return: True if the AnalysisService has been removed successfully
        """
        uid = api.get_uid(service)

        # Remove the service from the referenced services
        services = self.getAnalyses()
        num_services = len(services)
        services = [item for item in services if item.get('service_uid', '') != uid]
        removed = len(services) < num_services
        self.setAnalyses(services)

        # Remove the service from the settings map
        settings = self.getAnalysisServicesSettings()
        settings = [item for item in settings if item.get('uid', '') != uid]
        self.setAnalysisServicesSettings(settings)

        return removed

registerType(ARTemplate, PROJECTNAME)
