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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import ManageBika
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import ILaboratory

DEFAULT_ACCREDITATION_PAGE_HEADER = """${lab_name} has been accredited as
${accreditation_standard} conformant by ${accreditation_body_abbr},
${accreditation_body_name}<br/><br/> ${accreditation_body_abbr} is the single
national accreditation body assessing testing and calibration laboratories for
compliance to the ISO/IEC 17025 standard.<br/><br/>\n The following analysis
services have been included in the ${accreditation_body_abbr} schedule of
Accreditation for this Laboratory:
"""

schema = Organisation.schema.copy() + Schema((

    StringField(
        "LabURL",
        schemata="Address",
        write_permission=ManageBika,
        widget=StringWidget(
            size=60,
            label=_("Lab URL"),
            description=_("The Laboratory's web address"),
        ),
    ),

    UIDReferenceField(
        "Supervisor",
        required=0,
        allowed_types=("LabContact",),
        write_permission=ManageBika,
        widget=ReferenceWidget(
            label=_("Supervisor"),
            description=_("Supervisor of the Lab"),
            showOn=True,
            catalog_name=SETUP_CATALOG,
            base_query=dict(
                is_active=True,
                sort_on="sortable_title",
                sort_order="ascending",
            ),
        )
    ),

    IntegerField(
        "Confidence",
        schemata="Accreditation",
        widget=IntegerWidget(
            label=_("Confidence Level %"),
            description=_("This value is reported at the bottom of all "
                          "published results"),
        ),
    ),

    BooleanField(
        "LaboratoryAccredited",
        default=False,
        schemata="Accreditation",
        write_permission=ManageBika,
        widget=BooleanWidget(
            label=_("Laboratory Accredited"),
            description=_("Check this box if your laboratory is accredited"),
        ),
    ),

    StringField(
        "AccreditationBody",
        schemata="Accreditation",
        write_permission=ManageBika,
        widget=StringWidget(
            label=_("Accreditation Body Abbreviation"),
            description=_("E.g. SANAS, APLAC, etc."),
        ),
    ),

    StringField(
        "AccreditationBodyURL",
        schemata="Accreditation",
        write_permission=ManageBika,
        widget=StringWidget(
            label=_("Accreditation Body URL"),
            description=_("Web address for the accreditation body"),
        ),
    ),

    StringField(
        "Accreditation",
        schemata="Accreditation",
        write_permission=ManageBika,
        widget=StringWidget(
            label=_("Accreditation"),
            description=_("The accreditation standard that applies, "
                          "e.g. ISO 17025"),
        ),
    ),

    StringField(
        "AccreditationReference",
        schemata="Accreditation",
        write_permission=ManageBika,
        widget=StringWidget(
            label=_("Accreditation Reference"),
            description=_("The reference code issued to the lab by the "
                          "accreditation body"),
        ),
    ),

    ImageField(
        "AccreditationBodyLogo",
        schemata="Accreditation",
        widget=ImageWidget(
            label=_("Accreditation Logo"),
            description=_(
                "Please upload the logo you are authorised to use on your "
                "website and results reports by your accreditation body. "
                "Maximum size is 175 x 175 pixels.")
        ),
    ),

    TextField(
        "AccreditationPageHeader",
        schemata="Accreditation",
        default=DEFAULT_ACCREDITATION_PAGE_HEADER,
        widget=TextAreaWidget(
            label=_("Accreditation page header"),
            description=_(
                "Enter the details of your lab's service accreditations here. "
                "The following fields are available:  lab_is_accredited, "
                "lab_name, lab_country, confidence, accreditation_body_name, "
                "accreditation_standard, accreditation_reference<br/>"),
            rows=10
        ),
    ),
))


IdField = schema["id"]
IdField.widget.visible = {"edit": "hidden", "view": "invisible"}

schema["Name"].validators = ()
# Update the validation layer after change the validator in runtime
schema["Name"]._validationLayer()


class Laboratory(UniqueObject, Organisation):
    """Laboratory content
    """
    implements(ILaboratory)

    security = ClassSecurityInfo()
    displayContentsTab = False
    isPrincipiaFolderish = 0
    schema = schema

    def Title(self):
        title = self.getName() and self.getName() or _("Laboratory")
        return safe_unicode(title).encode("utf-8")


registerType(Laboratory, PROJECTNAME)
