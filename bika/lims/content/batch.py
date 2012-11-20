from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBatch
from datetime import timedelta
from bika.lims.utils import isActive
from zope.interface import implements
import plone
import json

schema = BikaSchema.copy() + Schema((
    StringField('BatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            visible = False,
            label=_("Batch ID"),
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
        res = self.getBatchID()
        return str(res).encode('utf-8')

    security.declarePublic('getBatchID')
    def getBatchID(self):
        return self.getId()

    security.declarePublic('getCCContacts')
    def getCCContacts(self):
        """ Return JSON containing all Lab contacts (with empty default CC lists).
        This function is used to set form values for javascript.
        """
        contact_data = []
        for contact in self.bika_setup.bika_labcontacts.objectValues('LabContact'):
            if isActive(contact):
                this_contact_data = {'title': contact.Title(),
                                     'uid': contact.UID(), }
                ccs = []
                if hasattr(contact, 'getCCContact'):
                    for cc in contact.getCCContact():
                        if isActive(cc):
                            ccs.append({'title': cc.Title(),
                                        'uid': cc.UID(),})
                this_contact_data['ccs_json'] = json.dumps(ccs)
                this_contact_data['ccs'] = ccs
            contact_data.append(this_contact_data)
        contact_data.sort(lambda x, y:cmp(x['title'].lower(),
                                          y['title'].lower()))
        return contact_data

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
        uid = self.context.UID()
        return [b.getObject() for b in bc(portal_type='AnalysisRequest',
                                          getBatchUID=uid)]

registerType(Batch, PROJECTNAME)
