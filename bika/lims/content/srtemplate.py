# -*- coding:utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import SRTemplateARTemplatesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISamplingRoundTemplate
from bika.lims.utils import getUsers
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    # The default sampler for the rounds
    StringField('Sampler',
        required=1,
        searchable=True,
        vocabulary='_getSamplersDisplayList',
        widget=SelectionWidget(
            format='select',
            label = _("Sampler"),
        ),
    ),

    # The department responsible for the sampling round
    UIDReferenceField('Department',
        required=1,
        allowed_types=('Department',),
        vocabulary='_getDepartmentsDisplayList',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Department"),
            description = _("The laboratory department"),
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
        ),
    ),

    # The number of days between recurring field trips
    IntegerField('SamplingDaysFrequency',
        required=1,
        default=7,
        widget=IntegerWidget(
            label = _("Sampling Frequency"),
            description=_(
                "The number of days between recurring field trips"),
        ),
    ),

    TextField('Instructions',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain'),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Instructions"),
            append_only = False,
        ),
    ),

    UIDReferenceField('ARTemplates',
        schemata = 'AR Templates',
        required = 1,
        multiValued = 1,
        allowed_types = ('ARTemplate',),
        widget = SRTemplateARTemplatesWidget(
            label=_("AR Templates"),
            description=_("Select AR Templates to include"),
        )
    ),
))

schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class SRTemplate(BaseContent):
    implements(ISamplingRoundTemplate)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def _getSamplersDisplayList(self):
        """ Returns the available users in the system with the roles
            'LabManager' and/or 'Sampler'
        """
        return getUsers(self, ['LabManager', 'Sampler'])

    def _getDepartmentsDisplayList(self):
        """ Returns the available departments in the system. Only the
            active departments are shown, unless the object has an
            inactive department already assigned.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Department',
                                  inactive_state='active')]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(SRTemplate, PROJECTNAME)
