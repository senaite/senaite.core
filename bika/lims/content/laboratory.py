# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from plone.app import folder
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.organisation import Organisation
from bika.lims.config import ManageBika, PROJECTNAME
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets.uidselectionwidget import UIDSelectionWidget
from bika.lims.utils import getUsers
from bika.lims import api

schema = Organisation.schema.copy() + Schema((
    StringField('LabURL',
        schemata = 'Address',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label=_("Lab URL"),
            description=_("The Laboratory's web address"),
        ),
    ),
    UIDReferenceField(
        'Supervisor',
        required=0,
        allowed_types=('LabContact',),
        vocabulary='_getLabContacts',
        write_permission = ManageBika,
        widget=UIDSelectionWidget(
            format='select',
            label=_("Supervisor"),
            description=_("Supervisor of the Lab")
        )
    ),
    IntegerField('Confidence',
        schemata = 'Accreditation',
        widget = IntegerWidget(
            label=_("Confidence Level %"),
            description=_("This value is reported at the bottom of all published results"),
        ),
    ),
    BooleanField('LaboratoryAccredited',
        default = False,
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = BooleanWidget(
            label=_("Laboratory Accredited"),
            description=_("Check this box if your laboratory is accredited"),
        ),
    ),
    StringField('AccreditationBody',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Body Abbreviation"),
            description=_("E.g. SANAS, APLAC, etc."),
        ),
    ),
    StringField('AccreditationBodyURL',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Body URL"),
            description=_("Web address for the accreditation body"),
        ),
    ),
    StringField('Accreditation',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation"),
            description=_("The accreditation standard that applies, e.g. ISO 17025"),
        ),
    ),
    StringField('AccreditationReference',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label=_("Accreditation Reference"),
            description=_("The reference code issued to the lab by the accreditation body"),
        ),
    ),
    ImageField('AccreditationBodyLogo',
        schemata = 'Accreditation',
        widget = ImageWidget(
            label=_("Accreditation Logo"),
            description = _(
                "Please upload the logo you are authorised to use on your "
                "website and results reports by your accreditation body. "
                "Maximum size is 175 x 175 pixels.")
        ),
    ),
    TextField('AccreditationPageHeader',
        schemata = 'Accreditation',
        default = "${lab_name} has been accredited as ${accreditation_standard} conformant by ${accreditation_body_abbr}, ${accreditation_body_name}<br/><br/>" + \
                  "${accreditation_body_abbr} is the single national accreditation body assessing testing and calibration laboratories for compliance to the ISO/IEC 17025 standard.<br/></br/>\n" + \
                  "The following analysis services have been included in the ${accreditation_body_abbr} schedule of Accreditation for this Laboratory:",
        widget = TextAreaWidget(
            label=_("Accreditation page header"),
            description = _(
                "Enter the details of your lab's service accreditations "
                "here.  The following fields are available:  lab_is_accredited, "
                "lab_name, lab_country, confidence, accreditation_body_name, "
                "accreditation_standard, accreditation_reference<br/>"),
                rows = 10
        ),
    ),
))



IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

schema['Name'].validators = ()
# Update the validation layer after change the validator in runtime
schema['Name']._validationLayer()

class Laboratory(UniqueObject, Organisation):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(View, 'getSchema')
    def getSchema(self):
        return self.schema

    def Title(self):
        title = self.getName() and self.getName() or _("Laboratory")
        return safe_unicode(title).encode('utf-8')

    def _getLabContacts(self):
        bsc = api.get_tool('bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = [['', '']]
        for contact in bsc(portal_type='LabContact',
                           inactive_state='active',
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

registerType(Laboratory, PROJECTNAME)
