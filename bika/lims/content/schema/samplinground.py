# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from datetime import date

from Products.CMFCore.utils import getToolByName
from bika.lims import _
from plone.supermodel import model
from zope.interface import implements
from zope.schema import TextLine, Text, Choice, Date, List, Int
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


# I implemented it here because following this example
# (http://docs.plone.org/external/plone.app.dexterity/docs/advanced
# /vocabularies.html#named-vocabularies)
# was giving me an error: "TypeError: object() takes no parameters"
class Departments(object):
    """Context source binder to provide a vocabulary of departments.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'Department',
                         'inactive_state': 'active'}
        catalog = getToolByName(context, catalog_name)
        brains = catalog(contentFilter)
        terms = []
        for brain in brains:
            department_uid = brain.UID
            title = brain.Title
            terms.append(
                SimpleVocabulary.createTerm(department_uid, str(department_uid),
                                            title))
        return SimpleVocabulary(terms)


class SamplingRoundTemplates(object):
    """Context source binder to provide a vocabulary of Lab and client's 
    Sampling Round Templates.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'SRTemplate',
                         'inactive_state': 'active'}
        catalog = getToolByName(context, catalog_name)
        brains = catalog(contentFilter)
        terms = []
        for brain in brains:
            container = brain.getObject().aq_parent
            # Show only the client and lab's Sampling Round Templates
            if container.portal_type == 'Client':
                if context.portal_type == 'Client' and container.UID() != \
                        context.UID():
                    continue
                elif context.portal_type == 'SamplingRound' \
                        and container.UID() != context.aq_parent.UID():
                    continue
            srt_uid = brain.UID
            title = brain.Title
            terms.append(
                SimpleVocabulary.createTerm(srt_uid, str(srt_uid), title))
        return SimpleVocabulary(terms)


class AnalysisRequestTemplates(object):
    """Context source binder to provide a vocabulary of Lab and client's 
    Sampling Round Templates.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'ARTemplate',
                         'inactive_state': 'active'}
        catalog = getToolByName(context, catalog_name)
        brains = catalog(contentFilter)
        terms = []
        for brain in brains:
            container = brain.getObject().aq_parent
            # Show only the client and lab's Sampling Round Templates
            if container.portal_type == 'Client' and container != context:
                continue
            art_uid = brain.UID
            title = brain.Title
            terms.append(
                SimpleVocabulary.createTerm(art_uid, str(art_uid), title))
        return SimpleVocabulary(terms)


class Samplers(object):
    """Context source binder to provide a vocabulary of the samplers.
    :sampler_group: The role's names to obtain the objects
    """

    implements(IContextSourceBinder)

    def __init__(self, sampler_group):
        # Sampler group == role
        self.sampler_group = sampler_group

    def __call__(self, context):
        mtool = getToolByName(context, 'portal_membership')
        users = mtool.searchForMembers(roles=self.sampler_group)
        terms = []
        for user in users:
            member_id = user.getId()
            fullname = user.getProperty('fullname')
            if not fullname:
                fullname = member_id
            terms.append(SimpleVocabulary.createTerm(member_id, str(member_id),
                                                     fullname))
        return SimpleVocabulary(terms)


class ClientContacts(object):
    """Context source binder to provide a vocabulary of the client contacts.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        container = context.aq_parent
        terms = []
        # Show only the client's
        if container.portal_type == 'Client':
            contacts = container.getContacts()
            for cnt in contacts:
                c_id = cnt.getId()
                name = cnt.getFullname()
                if not name:
                    name = c_id
                terms.append(
                    SimpleVocabulary.createTerm(
                        c_id, str(c_id), name))
        return SimpleVocabulary(terms)


class ISamplingRound(model.Schema):
    """A Sampling round interface
    """

    title = TextLine(
        title=_(u"Title"),
        description=_(
            u"A short name that describes the Round for it to be easily "
            u"identified on forms and drop-down menus"),
        required=True
    )

    description = Text(
        title=_(u"Description"),
        description=_(
            u"This text is also displayed upon a mouse-over of the Title "
            u"field"),
        required=False
    )

    sr_template = Choice(
        title=_(u"Sampling Rounds Template"),
        description=_(
            u"Analysis request templates to be included in the Sampling Round "
            u"Template"),
        source=SamplingRoundTemplates(),
        required=False,
    )

    sampler = Choice(
        title=_(u"Sampler"),
        description=_(u"The default Sampler for these Sampling Round"),
        required=True,
        source=Samplers(['LabManager', 'Sampler']),
    )

    department = Choice(
        title=_(u"Department"),
        description=_(u"The lab department responsible for the sampling round"),
        required=True,
        source=Departments()
    )

    sampling_freq = Int(
        title=_(u"Sampling frequency"),
        description=_(u"The number of days between recurring field trips"),
        required=True,
        default=7,
    )

    sampling_date = Date(
        title=_(u"Sampling date"),
        description=_(u"The date to do the sampling process"),
        default=date.today(),
        required=True
    )

    environmental_conditions = TextLine(
        title=_(u"Environmental conditions"),
        required=False
    )

    instructions = Text(
        title=_(u"Instructions"),
        required=False
    )

    ar_templates = List(
        title=_(u'Analysis Request Templates'),
        value_type=Choice(
            source=AnalysisRequestTemplates()
        )
    )

    client_contact = Choice(
        title=_(u'Client contact who coordinates with the lab'),
        required=False,
        source=ClientContacts()
    )

    client_contact_in_charge_at_sampling_time = Choice(
        title=_(u'Client contact in charge at sampling time'),
        required=False,
        source=ClientContacts()
    )

    num_sample_points = Int(
        title=_(u"Number of Sample Points"),
        description=_(
            u"the total number of Sample Points defined in the Round."),
        required=False,
        readonly=True,
    )

    num_containers = Int(
        title=_(u"Number of Containers"),
        description=_(u"The total number of Containers included in the Round."),
        required=False,
        readonly=True,
    )
