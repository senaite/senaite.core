# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.autoform import directives
from plone.supermodel import model
from plone.app.textfield.widget import RichTextFieldWidget  # TBD: port to core
from plone.app.textfield import IRichTextValue
from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ISetup
from senaite.core.schema import RichTextField
from senaite.impress import senaiteMessageFactory as _
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
        title=_(u"Publication Email Text"),
        description=_(
            "The default text that is used for the publication email."),
        defaultFactory=default_email_body_sample_publication,
        required=False,
    )

    ###
    # Fieldsets
    ###

    # model.fieldset(
    #     "notifications",
    #     label=_(u"Notifications"),
    #     fields=[
    #         "email_body_sample_publication",
    #     ]
    # )


@implementer(ISetup, ISetupSchema, IHideActionsMenu)
class Setup(Container):
    """SENAITE Setup Folder
    """
    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getRawEmailBodySamplePublication(self):
        accessor = self.accessor("email_body_sample_publication")
        value = accessor(self)
        if IRichTextValue.providedBy(value):
            value = value.raw
        return value

    @security.protected(permissions.View)
    def getEmailBodySamplePublication(self):
        accessor = self.accessor("email_body_sample_publication")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEmailBodySamplePublication(self, value):
        mutator = self.mutator("email_body_sample_publication")
        return mutator(self, value)
