# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInstrumentCertification
from plone.app.blob.field import FileField as BlobFileField
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    StringField('TaskID',
        widget = StringWidget(
            label=_("Task ID"),
            description=_("The instrument's ID in the lab's asset register"),
        )
    ),

    ReferenceField('Instrument',
        allowed_types=('Instrument',),
        relationship='InstrumentCertificationInstrument',
        widget=StringWidget(
            visible=False,
        )
    ),

    ComputedField('InstrumentUID',
        expression = 'context.getInstrument() and context.getInstrument().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    # Set the Certificate as Internal
    # When selected, the 'Agency' field is hidden
    BooleanField('Internal',
        default=False,
        widget=BooleanWidget(
            label=_("Internal Certificate"),
            description=_("Select if is an in-house calibration certificate")
        )
    ),

    StringField('Agency',
        widget = StringWidget(
            label=_("Agency"),
            description=_("Organization responsible of granting the calibration certificate")
        ),
    ),

    DateTimeField('Date',
        widget = DateTimeWidget(
            label=_("Date"),
            description=_("Date when the calibration certificate was granted"),
        ),
    ),

    DateTimeField('ValidFrom',
        with_time = 1,
        with_date = 1,
        required = 1,
        widget = DateTimeWidget(
            label=_("From"),
            description=_("Date from which the calibration certificate is valid"),
        ),
    ),

    DateTimeField('ValidTo',
        with_time = 1,
        with_date = 1,
        required = 1,
        widget = DateTimeWidget(
            label=_("To"),
            description=_("Date until the certificate is valid"),
        ),
    ),

    ReferenceField('Preparator',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentCertificatePreparator',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Prepared by"),
            description=_("The person at the supplier who prepared the certificate"),
            size=30,
            base_query={'inactive_state': 'active'},
            showOn=True,
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'JobTitle', 'width': '20', 'label': _('Job Title')},
                      {'columnName': 'Title', 'width': '80', 'label': _('Name')}
                     ],
        ),
    ),

    ReferenceField('Validator',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentCertificateValidator',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Approved by"),
            description=_("The person at the supplier who approved the certificate"),
            size=30,
            base_query={'inactive_state': 'active'},
            showOn=True,
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'JobTitle', 'width': '20', 'label': _('Job Title')},
                      {'columnName': 'Title', 'width': '80', 'label': _('Name')}
                     ],
        ),
    ),

    BlobFileField('Document',
        widget = FileWidget(
            label=_("Report upload"),
            description=_("Load the certificate document here"),
        )
    ),

    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),

))

schema['title'].widget.label=_("Certificate Code")

class InstrumentCertification(BaseFolder):
    implements(IInstrumentCertification)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type='LabContact',
                           inactive_state='active',
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

atapi.registerType(InstrumentCertification, PROJECTNAME)
