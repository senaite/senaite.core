from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBatch
from bika.lims.workflow import skip
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

schema = BikaFolderSchema.copy() + Schema((
    StringField(
        'BatchID',
        searchable=True,
        required=0,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible=False,
            label=_("Batch ID"),
        )
    ),
    StringField(
        'ClientBatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            label=_("Client Batch ID")
        )
    ),
    LinesField(
        'BatchLabels',
        vocabulary="BatchLabelVocabulary",
        widget=MultiSelectionWidget(
            label=_("Batch labels"),
            format="checkbox",
        )
    ),
    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        default_output_type="text/html",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        )
    )
)
)


schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].required = False
schema['description'].widget.visible = True


class Batch(ATFolder):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Batch ID if title is not defined """
        titlefield = self.Schema().getField('title')
        if titlefield.widget.visible:
            return safe_unicode(self.title).encode('utf-8')
        else:
            return safe_unicode(self.id).encode('utf-8')

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getClientTitle(self):
        schema = self.Schema()
        value = ""
        if 'Client' in schema:
            value = ['Client'].get(self)
            if value:
                return value.Title()
        return value

    def getContactTitle(self):
        return ""

    def getProfileTitle(self):
        return ""

    def getAnalysisCategory(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getCategoryTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysisService(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getServiceTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    security.declarePublic('getBatchID')

    def getBatchID(self):
        return self.getId()

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type='BatchLabel',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequests(self):
        bc = getToolByName(self, 'bika_catalog')
        uid = self.UID()
        return [b.getObject() for b in bc(portal_type='AnalysisRequest',
                                          getBatchUID=uid)]

    def workflow_guard_receive(self):
        """Permitted when all Samples are > sample_received
        """
        wf = getToolByName(self, 'portal_workflow')
        state = wf.getInfoFor(self, 'review_state')
        # receive originates from different states
        if state == 'open':
            # we want to make sure all ARs are > sample_due:
            states = ['sample_registered',
                      'to_be_sampled',
                      'sampled',
                      'to_be_preserved',
                      'sample_due']
            for o in self.getAnalysisRequests():
                if wf.getInfoFor(o, 'review_state') in states:
                    return False
            return True
        elif state == 'to_be_verified':
            # we want to make sure at least one AR < t_b_v
            states = ['sample_registered',
                      'to_be_sampled',
                      'sampled',
                      'to_be_preserved',
                      'sample_due',
                      'sample_received']
            for o in self.getAnalysisRequests():
                if wf.getInfoFor(o, 'review_state') in states:
                    return True

    def workflow_script_receive(self, state_info):
        skip(self, 'receive')

    def workflow_guard_open(self):
        """Permitted when at least one sample is < sample_received
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered',
                  'to_be_sampled',
                  'sampled',
                  'to_be_preserved',
                  'sample_due']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return True
        return False

    def workflow_script_open(self, state_info):
        skip(self, 'open')
        # reset everything and return to open state
        self.setDateReceived(None)
        self.reindexObject(idxs=["getDateReceived", ])

    def workflow_guard_submit(self):
        """Permitted when all ars >= to_be_verified
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered',
                  'to_be_sampled',
                  'sampled',
                  'to_be_preserved',
                  'sample_due',
                  'sample_received']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    def workflow_script_submit(self, state_info):
        skip(self, 'open')

    def workflow_guard_verify(self):
        """Permitted when all ars >= verified
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered',
                  'to_be_sampled',
                  'sampled',
                  'to_be_preserved',
                  'sample_due',
                  'sample_received',
                  'to_be_verified']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    def workflow_script_verify(self, state_info):
        skip(self, 'open')

    def workflow_guard_close(self):
        """Permitted when all ars >= verified
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered',
                  'to_be_sampled',
                  'sampled',
                  'to_be_preserved',
                  'sample_due',
                  'sample_received',
                  'to_be_verified',
                  'verified']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    def workflow_script_close(self, state_info):
        skip(self, 'open')

    def workflow_guard_publish(self):
        return True

    # doesn't work, action url in bika_publication_workflow does it.
    # def workflow_script_publish(self, state_info):
    #     self.REQUEST.RESPONSE.redirect(self.absolute_url() + "/publish")

    def workflow_guard_republish(self):
        return self.workflow_guard_publish()

    # bika_publication_workflow republish action currently goes to "/publish"
    # def workflow_script_republish(self, state_info):
    #     self.workflow_script_publish(state_info)

registerType(Batch, PROJECTNAME)
