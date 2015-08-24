from bika.lims import _
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from plone.dexterity.content import Item
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

# I implemented it here because following this example
# (http://docs.plone.org/external/plone.app.dexterity/docs/advanced/vocabularies.html#named-vocabularies)
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
            department_id = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(department_id, str(department_id), title))
        return SimpleVocabulary(terms)

class SamplingRoundTemplates(object):
    """Context source binder to provide a vocabulary of Lab and client's Sampling Round Templates.
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
            if container.portal_type == 'Client' and container != context:
                continue
            srt_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(srt_uid, str(srt_uid), title))
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
            terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), fullname))
        return SimpleVocabulary(terms)


class ISamplingRound(model.Schema):
        """A Sampling round interface
        """

        title = schema.TextLine(
                title=_(u"Title"),
                description=_(u"A short name that describes the Round for it to be easily "
                              u"identified on forms and drop-down menus"),
                required=True
                )

        description = schema.Text(
                title=_(u"Description"),
                description=_(u"This text is also displayed upon a mouse-over of the Title field"),
                required=False
                )

        sampler = schema.Choice(
                title=_(u"Sampler"),
                description=_(u"The default Sampler for these Sampling Round"),
                required=True,
                source=Samplers(['LabManager', 'Sampler']),
                )

        department = schema.Choice(
                title=_(u"Department"),
                description=_(u"The lab department responsible for the sampling round"),
                required=False,
                source=Departments()
                )

        sampling_freq = schema.Int(
                title=_(u"Sampling frequency"),
                description=_(u"The number of days between recurring field trips"),
                required=True
                )

        sr_template = schema.Choice(
                title=_(u"Sampling Rounds Template"),
                description=_(u"Analysis request templates to be included in the Sampling Round Template"),
                source=SamplingRoundTemplates(),
                required=True,
                )

        sampling_date = schema.Date(
                title=_(u"Sampling date"),
                description=_(u"The date to do the sampling process"),
                required=False
                )

        instructions = RichText(
                title=_(u"Instructions"),
                required=False
                )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class SamplingRound(Item):
    """
    A Sampling round class.
    - Sampling Rounds are fully fledged LIMS objects which adhere to workflow. They are created with initial status open
      and when all data are captured they are closed.
    Programmers: Sampling Rounds groups Samples very much like 'Batches' do for ARs
    - The ARs and Samples created per Sampling Round, enter the standard Bika workflow. There is one exception:
      LIMS-1559 Samples belonging to a Sampling Round that was closed earlier can be disposed of in bulk from the
      Sampling Round screen, and the date and 'disposer' details capture there. Like other LIMS objects, Sampling Rounds
      can be cancelled at any given time.
    Programmers: Cancelling is a secondary workflow, like that for cancelling and the Round's original status is
    maintained, e.g. an open Round can have a cancelled status as well as closed Rounds.
    """
    implements(ISamplingRound)
    # Add your class methods and properties here
    pass
