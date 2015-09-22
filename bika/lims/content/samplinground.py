from bika.lims import _
from plone.supermodel import model
from plone import api
from plone.indexer import indexer
from zope import schema
from plone.dexterity.content import Item
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IContextSourceBinder
from datetime import date
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip
from Products.CMFCore.permissions import ModifyPortalContent, AddPortalContent

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
            department_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(department_uid, str(department_uid), title))
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
            if container.portal_type == 'Client':
                if context.portal_type == 'Client' and container.UID() != context.UID():
                    continue
                elif context.portal_type == 'SamplingRound' and container.UID() != context.aq_parent.UID():
                    continue
            srt_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(srt_uid, str(srt_uid), title))
        return SimpleVocabulary(terms)

class AnalysisRequestTemplates(object):
    """Context source binder to provide a vocabulary of Lab and client's Sampling Round Templates.
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
            terms.append(SimpleVocabulary.createTerm(art_uid, str(art_uid), title))
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

        sr_template = schema.Choice(
                title=_(u"Sampling Rounds Template"),
                description=_(u"Analysis request templates to be included in the Sampling Round Template"),
                source=SamplingRoundTemplates(),
                required=False,
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
                required=True,
                source=Departments()
                )

        sampling_freq = schema.Int(
                title=_(u"Sampling frequency"),
                description=_(u"The number of days between recurring field trips"),
                required=True,
                default=7,
                )

        sampling_date = schema.Date(
                title=_(u"Sampling date"),
                description=_(u"The date to do the sampling process"),
                default=date.today(),
                required=True
                )

        environmental_conditions = schema.TextLine(
                title=_(u"Environmental conditions"),
                required=False
                )

        instructions = schema.Text(
                title=_(u"Instructions"),
                required=False
                )

        ar_templates = schema.List(
            title=_(u'Analysis Request Templates'),
            value_type=schema.Choice(
                source=AnalysisRequestTemplates()
            )
        )

        num_sample_points = schema.Int(
                title=_(u"Number of Sample Points"),
                description=_(u"the total number of Sample Points defined in the Round."),
                required=False,
                readonly=True,
                )

        num_containers = schema.Int(
                title=_(u"Number of Containers"),
                description=_(u"The total number of Containers included in the Round."),
                required=False,
                readonly=True,
                )

@indexer(ISamplingRound)
def analysisRequestTemplates(obj):
    return obj.getAnalysisRequestTemplates()

@indexer(ISamplingRound)
def samplingRoundSamplingDate(obj):
    date = obj.sampling_date
    return date.strftime("%Y-%m-%d")

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

    @property
    def num_sample_points(self):
        ar_brains = self.getAnalysisRequests()
        sp_num = 0
        for ar_brain in ar_brains:
            ar_samplepoint = ar_brain.getObject().getSamplePoint()
            if ar_samplepoint:
                sp_num += 1
        return sp_num

    @property
    def num_containers(self):
        ar_brains = self.getAnalysisRequests()
        containers = []
        for ar_brain in ar_brains:
            containers += ar_brain.getObject().getContainers()
        return len(containers)

    def getAnalysisRequests(self):
        """ Return all the Analysis Requests linked to the Sampling Round
        """
        # I have to get the catalog in this way because I can't do it with 'self'...
        pc = getToolByName(api.portal.get(), 'portal_catalog')
        contentFilter = {'portal_type': 'AnalysisRequest',
                         'cancellation_state': 'active',
                         'SamplingRoundUID': self.UID()}
        return pc(contentFilter)

    def getAnalysisRequestTemplates(self):
        """
        This functions builds a list of tuples with the object AnalysisRequestTemplates' uids and names.
        :return: A list of tuples where the first value of the tuple is the AnalysisRequestTemplate name and the
        second one is the AnalysisRequestTemplate UID. --> [(ART.title),(ART.UID),...]
        """
        l = []
        art_uids = self.ar_templates
        # I have to get the catalog in this way because I can't do it with 'self'...
        pc = getToolByName(api.portal.get(), 'uid_catalog')
        for art_uid in art_uids:
            art_obj = pc(UID=art_uid)
            if len(art_obj) != 0:
                l.append((art_obj[0].Title, art_uid))
        return l

    def hasUserAddEditPermission(self):
        """
        Checks if the current user has privileges to access to the editing view.
        From Jira LIMS-1549:
           - Creation/Edit: Lab manager, Client Contact, Lab Clerk, Client Contact (for Client-specific SRTs)
        :return: True/False
        """
        mtool = getToolByName(self, 'portal_membership')
        checkPermission = mtool.checkPermission
        # In bika_samplinground_workflow.csv there are defined the ModifyPortalContent statements. There is said that
        # client has ModifyPortalContent permission enabled, so here we have to check if the client satisfy the
        # condition wrote in the function's description
        if (checkPermission(ModifyPortalContent, self) or checkPermission(AddPortalContent, self)) \
                and 'Client' in api.user.get_current().getRoles():
            # Checking if the current user is a current client's contact
            userID = api.user.get_current().id
            contact_objs = self.getContacts()
            contact_ids = [obj.getUsername() for obj in contact_objs]
            if userID in contact_ids:
                return True
            else:
                return False
        return checkPermission(ModifyPortalContent, self) or checkPermission(AddPortalContent, self)

    def workflow_script_cancel(self):
        """
        When the round is cancelled, all its associated Samples and ARs are cancelled by the system.
        """
        if skip(self, "cancel"):
            return
        self.reindexObject(idxs=["cancellation_state", ])
        # deactivate all analysis requests in this sampling round.
        analysis_requests = self.getAnalysisRequests()
        for ar in analysis_requests:
            ar_obj = ar.getObject()
            workflow = getToolByName(self, 'portal_workflow')
            if workflow.getInfoFor(ar_obj, 'cancellation_state') != 'cancelled':
                doActionFor(ar.getObject(), 'cancel')
                doActionFor(ar.getObject().getSample(), 'cancel')
