"""
    AnalysisRequests often use the same configurations.
    AnalysisProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisProfileAnalysesWidget
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.field import RecordsField
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
    StringField('ProfileKey',
        widget = StringWidget(
            label = _("Profile Keyword"),
            description = _("The profile's keyword is used to uniquely identify " + \
                          "it in import files. It has to be unique, and it may " + \
                          "not be the same as any Calculation Interim field ID."),
        ),
    ),
    ReferenceField('Service',
        schemata = 'Analyses',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisProfileAnalysisService',
        widget = AnalysisProfileAnalysesWidget(
            label = _("Profile Analyses"),
            description = _("The analyses included in this profile, grouped per category"),
        )
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _("Remarks"),
            append_only = True,
        ),
    ),
    # Custom settings for the assigned analysis services
    # https://jira.bikalabs.com/browse/LIMS-1324
    # Fields:
    #   - uid: Analysis Service UID
    #   - hidden: True/False. Hide/Display in results reports
    RecordsField('AnalysisServicesSettings',
         required=0,
         subfields=('uid', 'hidden',),
         widget=ComputedWidget(visible=False),
    ),
),
)
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']

class AnalysisProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getClientUID(self):
        return self.aq_parent.UID();

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            profile, returns a dictionary with the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings() \
                if s.get('uid','') == uid]
        return sets[0] if sets else {'uid': uid}

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this profile, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                profile or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('%s is not valid' % uid)
        return sets.get('hidden', False)

registerType(AnalysisProfile, PROJECTNAME)
