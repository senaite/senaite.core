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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.app.textfield import IRichTextValue
from plone.app.textfield.widget import RichTextFieldWidget  # TBD: port to core
from plone.autoform import directives
from plone.formwidget.namedfile.widget import NamedFileFieldWidget
from plone.schema.email import Email
from plone.supermodel import model
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ISetup
from senaite.core.schema import RichTextField
from senaite.impress import senaiteMessageFactory as _
from zope import schema
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_email_body_sample_publication(context):
    """Returns the default body text for publication emails
    """
    view = api.get_view("senaite_view", context=api.get_setup())
    if view is None:
        # Test fixture
        return u""
    tpl = ViewPageTemplateFile(
        "../browser/setup/templates/email_body_sample_publication.pt")
    return tpl(view)


@provider(IContextAwareDefaultFactory)
def default_email_from_sample_publication(context):
    """Returns the default email 'From' for results reports publish
    """
    portal_email = api.get_registry_record("plone.email_from_address")
    return portal_email


class ISetupSchema(model.Schema):
    """Schema and marker interface
    """

    email_from_sample_publication = Email(
        title=_(
            "title_senaitesetup_email_from_sample_publication",
            default="Publication 'From' address"
        ),
        description=_(
            "description_senaitesetup_email_from_sample_publication",
            default="E-mail to use as the 'From' address for outgoing e-mails "
                    "when publishing results reports. This address overrides "
                    "the value set at portal's 'Mail settings'."
        ),
        defaultFactory=default_email_from_sample_publication,
        required=False,
    )

    directives.widget("email_body_sample_publication", RichTextFieldWidget)
    email_body_sample_publication = RichTextField(
        title=_("title_senaitesetup_publication_email_text",
                default=u"Publication Email Text"),
        description=_(
            "description_senaitesetup_publication_email_text",
            default=u"Set the email body text to be used by default "
            "when sending out result reports to the selected recipients. "
            "You can use reserved keywords: "
            "$client_name, $recipients, $lab_name, $lab_address"),
        defaultFactory=default_email_body_sample_publication,
        required=False,
    )

    always_cc_responsibles_in_report_emails = schema.Bool(
        title=_(
            "title_senaitesetup_always_cc_responsibles_in_report_emails",
            default=u"Always send publication email to responsibles"),
        description=_(
            "description_senaitesetup_always_cc_responsibles_in_report_emails",
            default="When selected, the responsible persons of all involved "
            "lab departments will receive publication emails."
        ),
        default=True,
    )

    enable_global_auditlog = schema.Bool(
        title=_(u"Enable global Auditlog"),
        description=_(
            "The global Auditlog shows all modifications of the system. "
            "When enabled, all entities will be indexed in a separate "
            "catalog. This will increase the time when objects are "
            "created or modified."
        ),
        default=False,
    )

    # NOTE:
    # We use the `NamedFileFieldWidget` instead of `NamedImageFieldWidget`
    # by purpose! Using the latter rises this PIL error (appears only in log):
    # IOError: cannot identify image file <cStringIO.StringI object at ...>
    directives.widget("site_logo", NamedFileFieldWidget)
    site_logo = schema.Bytes(
        title=_(u"Site Logo"),
        description=_(u"This shows a custom logo on your SENAITE site."),
        required=False,
    )

    site_logo_css = schema.ASCII(
        title=_(u"Site Logo CSS"),
        description=_(
            u"Add custom CSS rules for the Logo, "
            u"e.g. height:15px; width:150px;"
        ),
        required=False,
    )

    immediate_results_entry = schema.Bool(
        title=_(u"Immediate results entry"),
        description=_(
            "description_senaitesetup_immediateresultsentry",
            default=u"Allow the user to directly enter results after sample "
            "creation, e.g. to enter field results immediately, or lab "
            "results, when the automatic sample reception is activated."
        ),
    )

    categorize_sample_analyses = schema.Bool(
        title=_("title_senaitesetup_categorizesampleanalyses",
                default=u"Categorize sample analyses"),
        description=_(
            "description_senaitesetup_categorizesampleanalyses",
            default=u"Group analyses by category for samples"
        ),
        default=False,
    )

    sample_analyses_required = schema.Bool(
        title=_("title_senaitesetup_sampleanalysesrequired",
                default=u"Require sample analyses"),
        description=_(
            "description_senaitesetup_sampleanalysesrequired",
            default=u"Analyses are required for sample registration"
        ),
        default=True,
    )

    # Allow Manual Analysis Result Capture Date
    allow_manual_result_capture_date = schema.Bool(
        title=_("title_senaitesetup_allow_manual_result_capture_date",
                default=u"Allow to set the result capture date"),
        description=_(
            "description_senaitesetup_allow_manual_result_capture_date",
            default=u"If this option is activated, the result capture date "
                    u"can be entered manually for analyses"),
        default=False)

    max_number_of_samples_add = schema.Int(
        title=_(
            u"label_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum value for 'Number of samples' field on "
                    u"registration"
        ),
        description=_(
            u"description_senaitesetup_maxnumberofsamplesadd",
            default=u"Maximum number of samples that can be created in "
                    u"accordance with the value set for the field 'Number of "
                    u"samples' on the sample registration form"
        ),
        default=10
    )

    date_sampled_required = schema.Bool(
        title=_(
            u"title_senaitesetup_date_sampled_required",
            default=u"Date sampled required"),
        description=_(
            u"description_senaitesetup_date_sampled_required",
            default=u"Select this to make DateSampled field required on "
                    u"sample creation. This functionality only takes effect "
                    u"when 'Sampling workflow' is not active"
        ),
        default=True,
    )

    show_lab_name_in_login = schema.Bool(
        title=_(
            u"title_senaitesetup_show_lab_name_in_login",
            default=u"Display laboratory name in the login page"),
        description=_(
            u"description_senaitesetup_show_lab_name_in_login",
            default=u"When selected, the laboratory name will be displayed"
                    u"in the login page, above the access credentials."
        ),
        default=False,
    )

    ###
    # Fieldsets
    ###
    model.fieldset(
        "samples",
        label=_("label_senaitesetup_fieldset_samples", default=u"Samples"),
        fields=[
            "max_number_of_samples_add",
            "date_sampled_required",
        ]
    )
    model.fieldset(
        "analyses",
        label=_("label_senaitesetup_fieldset_analyses", default=u"Analyses"),
        fields=[
            "immediate_results_entry",
            "categorize_sample_analyses",
            "sample_analyses_required",
            "allow_manual_result_capture_date",
        ]
    )

    model.fieldset(
        "notifications",
        label=_(u"Notifications"),
        fields=[
            "email_from_sample_publication",
            "email_body_sample_publication",
            "always_cc_responsibles_in_report_emails",
        ]
    )

    model.fieldset(
        "appearance",
        label=_(u"Appearance"),
        fields=[
            "site_logo",
            "site_logo_css",
            "show_lab_name_in_login",
        ]
    )


@implementer(ISetup, ISetupSchema, IHideActionsMenu)
class Setup(Container):
    """SENAITE Setup Folder
    """
    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getEmailFromSamplePublication(self):
        """Returns the 'From' address for publication emails
        """
        accessor = self.accessor("email_from_sample_publication")
        email = accessor(self)
        if not email:
            email = default_email_from_sample_publication(self)
        return email

    @security.protected(permissions.ModifyPortalContent)
    def setEmailFromSamplePublication(self, value):
        """Set the 'From' address for publication emails
        """
        mutator = self.mutator("email_from_sample_publication")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEmailBodySamplePublication(self):
        """Returns the transformed email body text for publication emails
        """
        accessor = self.accessor("email_body_sample_publication")
        value = accessor(self)
        if IRichTextValue.providedBy(value):
            # Transforms the raw value to the output mimetype
            value = value.output_relative_to(self)
        if not value:
            # Always fallback to default value
            value = default_email_body_sample_publication(self)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setEmailBodySamplePublication(self, value):
        """Set email body text for publication emails
        """
        mutator = self.mutator("email_body_sample_publication")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAlwaysCCResponsiblesInReportEmail(self):
        """Returns if responsibles should always receive publication emails
        """
        accessor = self.accessor("always_cc_responsibles_in_report_emails")
        return accessor(self)

    @security.protected(permissions.View)
    def setAlwaysCCResponsiblesInReportEmail(self, value):
        """Set if responsibles should always receive publication emails
        """
        mutator = self.mutator("always_cc_responsibles_in_report_emails")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEnableGlobalAuditlog(self):
        """Returns if the global Auditlog is enabled
        """
        accessor = self.accessor("enable_global_auditlog")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEnableGlobalAuditlog(self, value):
        """Enable/Disable global Auditlogging
        """
        if value is False:
            # clear the auditlog catalog
            catalog = api.get_tool(AUDITLOG_CATALOG)
            catalog.manage_catalogClear()
        mutator = self.mutator("enable_global_auditlog")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSiteLogo(self):
        """Returns the global site logo
        """
        accessor = self.accessor("site_logo")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteLogo(self, value):
        """Set the site logo
        """
        mutator = self.mutator("site_logo")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSiteLogoCSS(self):
        """Returns the global site logo
        """
        accessor = self.accessor("site_logo_css")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteLogoCSS(self, value):
        """Set the site logo
        """
        mutator = self.mutator("site_logo_css")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getImmediateResultsEntry(self):
        """Returns if immediate results entry is enabled or not
        """
        accessor = self.accessor("immediate_results_entry")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setImmediateResultsEntry(self, value):
        """Enable/Disable global Auditlogging
        """
        mutator = self.mutator("immediate_results_entry")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getCategorizeSampleAnalyses(self):
        """Returns if analyses should be grouped by category for samples
        """
        accessor = self.accessor("categorize_sample_analyses")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCategorizeSampleAnalyses(self, value):
        """Enable/Disable grouping of analyses by category for samples
        """
        mutator = self.mutator("categorize_sample_analyses")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSampleAnalysesRequired(self):
        """Returns if analyses are required in sample add form
        """
        accessor = self.accessor("sample_analyses_required")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleAnalysesRequired(self, value):
        """Allow/Disallow to create samples without analyses
        """
        mutator = self.mutator("sample_analyses_required")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAllowManualResultCaptureDate(self):
        """Returns if analyses are required in sample add form
        """
        accessor = self.accessor("allow_manual_result_capture_date")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAllowManualResultCaptureDate(self, value):
        """Allow/Disallow to create samples without analyses
        """
        mutator = self.mutator("allow_manual_result_capture_date")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getMaxNumberOfSamplesAdd(self):
        """Returns the maximum number of samples that can be created for each
        column in sample add form in accordance with the value set for the
        field 'Number of samples'
        """
        accessor = self.accessor("max_number_of_samples_add")
        return api.to_int(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setMaxNumberOfSamplesAdd(self, value):
        """Sets the maximum number of samples that can be created for each
        column in sample add form in accordance with the value set for the
        field 'Number of samples'
        """
        mutator = self.mutator("max_number_of_samples_add")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getDateSampledRequired(self):
        """Returns whether the DateSampled field is required on sample creation
        when the sampling workflow is not active
        """
        accessor = self.accessor("date_sampled_required")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDateSampledRequired(self, value):
        """Sets whether the entry of a value for DateSampled field on sample
        creation is required when the sampling workflow is not active
        """
        mutator = self.mutator("date_sampled_required")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getShowLabNameInLogin(self):
        """Returns if the laboratory name has to be displayed in login page
        """
        accessor = self.accessor("show_lab_name_in_login")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShowLabNameInLogin(self, value):
        """Show/hide the laboratory name in the login page
        """
        mutator = self.mutator("show_lab_name_in_login")
        return mutator(self, value)
