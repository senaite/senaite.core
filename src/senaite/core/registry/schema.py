# -*- coding: utf-8 -*-

from bika.lims import api
from plone.autoform import directives
from senaite.impress import senaiteMessageFactory as _
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


@provider(IContextAwareDefaultFactory)
def default_email_body_sample_publication(context):
    """Returns the default body text for publication emails
    """
    # Workaround to use page templates
    view = api.get_view("senaite_view")
    tpl = ViewPageTemplateFile("templates/email_body_sample_publication.pt")
    return tpl(view)


class ISenaiteRegistry(Interface):
    """Senaite registry schema
    """

    directives.widget("email_body_sample_publication", klass="richTextWidget")
    email_body_sample_publication = schema.Text(
        title=_(u"Publication Email Text"),
        description=_(
            "The default text that is used for the publication email. "
            " sending publication reports."),
        defaultFactory=default_email_body_sample_publication,
        required=False,
    )
