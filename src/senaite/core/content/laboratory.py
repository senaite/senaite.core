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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.


from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IDoNotSupportSnapshots
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from Products.CMFPlone.utils import safe_unicode
from plone.namedfile.field import NamedBlobImage
from senaite.core.config.widgets import get_labcontact_columns
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.organization import IOrganizationSchema
from senaite.core.content.organization import Organization
from senaite.core.interfaces import ILaboratory
from senaite.core.interfaces import IHideActionsMenu
from z3c.form.browser.textarea import TextAreaWidget
from zope import schema
from zope.interface import implementer


DEFAULT_ACCREDITATION_PAGE_HEADER = u"""${lab_name} has been accredited as
${accreditation_standard} conformant by ${accreditation_body_abbr},
${accreditation_body_name}<br/><br/> ${accreditation_body_abbr} is the single
national accreditation body assessing testing and calibration laboratories for
compliance to the ISO/IEC 17025 standard.<br/><br/>\n The following analysis
services have been included in the ${accreditation_body_abbr} schedule of
Accreditation for this Laboratory:
"""

class ILaboratorySchema(IOrganizationSchema):
    """Schema interface
    """

    directives.widget(
        "supervisor",
        UIDReferenceWidgetFactory,
        catalog=CONTACT_CATALOG,
        query={
            "portal_type": "LabContact",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${getFullname}</a>",
        columns=get_labcontact_columns,
        limit=5,
    )
    supervisor = UIDReferenceField(
        title=_(
            u"label_laboratory_supervisor",
            default=u"Supervisor"
        ),
        description=_(
            u"description_laboratory_supervisor",
            default=u"Supervisor of the Lab"
        ),
        allowed_types=("LabContact", ),
        multi_valued=False,
        required=True,
    )

    model.fieldset(
        "addresses",
        label=_(
            u"title_addresses_tab",
            default=u"Address"
        ),
        fields=[
            "lab_url",
        ]
    )
    directives.widget("lab_url", size=60)
    lab_url = schema.TextLine(
        title=_(
            u"title_laboratory_lab_url",
            default=u"Lab URL"),
        description=_(
            u"description_laboratory_lab_url",
            default=u"The Laboratory's web address"),
        required=False,
    )

    model.fieldset(
        "accreditation",
        label=_("Accreditation"),
        fields=[
            "confidence",
            "laboratory_accredited",
            "accreditation_body",
            "accreditation_body_url",
            "accreditation",
            "accreditation_reference",
            "accreditation_body_logo",
            "accreditation_page_header",
        ],
    )

    confidence = schema.Int(
        title=_(
            u"title_confidence_level",
            default=u"Confidence Level %"
        ),
        description=_(
            u"description_confidence_level",
            default=u"This value is reported "
            u"at the bottom of all published results"
        ),
        required=False,
    )

    laboratory_accredited = schema.Bool(
        title=_(
            u"title_laboratory_accredited",
            default=u"Laboratory Accredited"
        ),
        description=_(
            u"description_laboratory_accredited",
            default=u"Check this box if your laboratory is accredited"
        ),
        default=False,
        required=False,
    )

    accreditation_body = schema.TextLine(
        title=_(
            u"title_accreditation_body",
            default=u"Accreditation Body Abbreviation"
        ),
        description=_(
            u"description_accreditation_body",
            default=u"E.g. SANAS, APLAC, etc."),
        required=False,
    )

    accreditation_body_url = schema.TextLine(
        title=_(
            u"title_accreditation_body_url",
            default=u"Accreditation Body URL"),
        description=_(
            u"description_accreditation_body_url",
            default=u"Web address for the accreditation body"),
        required=False,
    )

    accreditation = schema.TextLine(
        title=_(
            u"title_accreditation",
            default=u"Accreditation"
        ),
        description=_(
            u"description_accreditation",
            default=u"The accreditation standard that applies, e.g. ISO 17025"
        ),
        required=False,
    )

    accreditation_reference = schema.TextLine(
        title=_(
            u"title_accreditation_reference",
            default=u"Accreditation Reference"
        ),
        description=_(
            u"description_accreditation_reference",
            default=u"The reference code issued "
            u"to the lab by the accreditation body"
        ),
        required=False,
    )

    accreditation_body_logo = NamedBlobImage(
        title=_(
            u"title_accreditation_body_logo",
            default=u"Accreditation Logo"),
        description=_(
            u"description_accreditation_body_logo",
            default=u"Please upload the logo you are authorised "
                    u"to use on your website and "
                    u"results reports by your accreditation body. "
                    u"Maximum size is 175 x 175 pixels."
        ),
        required=False,
    )

    directives.widget(
        "accreditation_page_header",
        TextAreaWidget,
        style=u"white-space:pre-wrap;font-size:8pt;",
        klass=u"text-monospace small text-secondary",
        rows=10
    )
    accreditation_page_header = schema.Text(
        title=_(
            u"title_accreditation_page_header",
            default=u"Accreditation page header"
        ),
        description=_(
            u"description_accreditation_page_header",
            default=u"Enter the details of your lab's service "
            u"accreditations here. The following fields are available: "
            u"lab_is_accredited, lab_name, "
            u"lab_country, confidence, accreditation_body_name, "
            u"accreditation_standard, accreditation_reference"
        ),
        default=DEFAULT_ACCREDITATION_PAGE_HEADER,
        required=False,
    )


@implementer(ILaboratory, ILaboratorySchema,
             IDoNotSupportSnapshots, IHideActionsMenu,
             IDeactivable)
class Laboratory(Organization):
    """A container for laboratory
    """
    _catalogs = [SETUP_CATALOG]
    security = ClassSecurityInfo()
    displayContentsTab = False

    def Title(self):
        title = self.getName() and self.getName() or _("Laboratory")
        return safe_unicode(title).encode("utf-8")

    @security.protected(permissions.View)
    def getLabURL(self):
        accessor = self.accessor("lab_url")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLabURL(self, value):
        mutator = self.mutator("lab_url")
        mutator(self, safe_unicode(value))

    LabURL = property(getLabURL, setLabURL)

    @security.protected(permissions.View)
    def getRawSupervisor(self):
        accessor = self.accessor("supervisor", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSupervisor(self):
        accessor = self.accessor("supervisor")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSupervisor(self, value):
        mutator = self.mutator("supervisor")
        mutator(self, value)

    Supervisor = property(getSupervisor, setSupervisor)

    @security.protected(permissions.View)
    def getConfidence(self):
        accessor = self.accessor("confidence")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setConfidence(self, value):
        mutator = self.mutator("confidence")
        mutator(self, value)

    Confidence = property(getConfidence, setConfidence)

    @security.protected(permissions.View)
    def getLaboratoryAccredited(self):
        accessor = self.accessor("laboratory_accredited")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLaboratoryAccredited(self, value):
        mutator = self.mutator("laboratory_accredited")
        mutator(self, value)

    LaboratoryAccredited = property(
        getLaboratoryAccredited, setLaboratoryAccredited)

    @security.protected(permissions.View)
    def getAccreditationBody(self):
        accessor = self.accessor("accreditation_body")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditationBody(self, value):
        mutator = self.mutator("accreditation_body")
        mutator(self, safe_unicode(value))

    AccreditationBody = property(
        getAccreditationBody, setAccreditationBody)

    @security.protected(permissions.View)
    def getAccreditationBodyURL(self):
        accessor = self.accessor("accreditation_body_url")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditationBodyURL(self, value):
        mutator = self.mutator("accreditation_body_url")
        mutator(self, safe_unicode(value))

    AccreditationBodyURL = property(
        getAccreditationBodyURL, setAccreditationBodyURL)

    @security.protected(permissions.View)
    def getAccreditation(self):
        accessor = self.accessor("accreditation")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditation(self, value):
        mutator = self.mutator("accreditation")
        mutator(self, safe_unicode(value))

    Accreditation = property(getAccreditation, setAccreditation)

    @security.protected(permissions.View)
    def getAccreditationReference(self):
        accessor = self.accessor("accreditation_reference")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditationReference(self, value):
        mutator = self.mutator("accreditation_reference")
        mutator(self, safe_unicode(value))

    AccreditationReference = property(
        getAccreditationReference, setAccreditationReference)

    @security.protected(permissions.View)
    def getAccreditationBodyLogo(self):
        accessor = self.accessor("accreditation_body_logo")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditationBodyLogo(self, value):
        mutator = self.mutator("accreditation_body_logo")
        mutator(self, value)

    AccreditationBodyLogo = property(
        getAccreditationBodyLogo, setAccreditationBodyLogo)

    @security.protected(permissions.View)
    def getAccreditationPageHeader(self):
        accessor = self.accessor("accreditation_page_header")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccreditationPageHeader(self, value):
        mutator = self.mutator("accreditation_page_header")
        mutator(self, safe_unicode(value))

    AccreditationPageHeader = property(
        getAccreditationPageHeader, setAccreditationPageHeader)
