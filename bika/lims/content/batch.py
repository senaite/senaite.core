from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBatch
from bika.lims.utils import isActive
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip
from datetime import timedelta
from zope.interface import implements
import json
import plone

schema = BikaSchema.copy() + Schema((
    StringField('BatchID',
        searchable=True,
        required=0,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible = False,
            label=_("Batch ID"),
        )
    ),
    StringField('ClientBatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            label=_("Client Batch ID")
        )
    ),
    LinesField('BatchLabels',
        vocabulary = "BatchLabelVocabulary",
        widget=MultiSelectionWidget(
            label=_("Batch labels"),
            format="checkbox",
        )
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
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

class Batch(BaseContent):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the BatchID or id as title """
        return safe_unicode(self.getBatchID()).encode('utf-8')

    security.declarePublic('getBatchID')
    def getBatchID(self):
        return self.getId()

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'BatchLabel',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequests(self):
        bc = getToolByName(self, 'bika_catalog')
        uid = self.UID()
        return [b.getObject() for b in bc(portal_type='AnalysisRequest', getBatchUID=uid)]

    def workflow_guard_receive(self):
        """Permitted when all Samples are > sample_received
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 'sample_due']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    def workflow_script_receive(self, state_info):
        skip(self, 'receive')

    def workflow_guard_open(self):
        """Permitted when at least one sample is < sample_received
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 'sample_due']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return True
        return False

    def workflow_script_open(self, state_info):
        skip(self, 'open')
        # reset everything and return to open state
        self.setDateReceived(None)
        self.reindexObject(idxs = ["getDateReceived", ])

    def workflow_guard_submit(self):
        """Permitted when all samples >= to_be_verified
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 'sample_due', 'sample_received']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    # def workflow_script_submit(self, state_info):
    #     skip(self, 'open')

    def workflow_guard_verify(self):
        """Permitted when all samples >= verified
        """
        wf = getToolByName(self, 'portal_workflow')
        states = ['sample_registered', 'to_be_sampled', 'sampled', 'to_be_preserved', 'sample_due', 'sample_received',
                  'to_be_verified']
        for o in self.getAnalysisRequests():
            if wf.getInfoFor(o, 'review_state') in states:
                return False
        return True

    # def workflow_script_verify(self, state_info):
    #     skip(self, 'open')

    # def workflow_guard_close(self):
    #     return True

    # def workflow_script_close(self, state_info):
    #     skip(self, 'open')

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
