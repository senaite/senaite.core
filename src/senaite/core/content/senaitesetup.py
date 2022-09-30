# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.app.textfield import IRichTextValue
from plone.app.textfield.widget import RichTextFieldWidget  # TBD: port to core
from plone.autoform import directives
from plone.formwidget.namedfile.widget import NamedFileFieldWidget
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


class ISetupSchema(model.Schema):
    """Schema and marker interface
    """

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

    ###
    # Fieldsets
    ###
    model.fieldset(
        "analyses",
        label=_("label_senaitesetup_fieldset_analyses", default=u"Analyses"),
        fields=[
            "immediate_results_entry",
            "categorize_sample_analyses",
        ]
    )

    model.fieldset(
        "notifications",
        label=_(u"Notifications"),
        fields=[
            "email_body_sample_publication",
        ]
    )

    model.fieldset(
        "appearance",
        label=_(u"Appearance"),
        fields=[
            "site_logo",
            "site_logo_css",
        ]
    )


@implementer(ISetup, ISetupSchema, IHideActionsMenu)
class Setup(Container):
    """SENAITE Setup Folder
    """
    security = ClassSecurityInfo()

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
