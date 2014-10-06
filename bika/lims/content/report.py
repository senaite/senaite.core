from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    FileField('ReportFile',
        widget = FileWidget(
            label=_("Report"),
        ),
    ),
    StringField('ReportType',
        widget = StringWidget(
            label=_("Report Type"),
            description=_("Report type"),
        ),
    ),
    ReferenceField('Client',
        allowed_types = ('Client',),
        relationship = 'ReportClient',
        widget = ReferenceWidget(
            label=_("Client"),
        ),
    ),
    ComputedField('ClientUID',
        expression = 'here.getClient() and here.getClient().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['id'].required = False
schema['title'].required = False

class Report(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(Report, PROJECTNAME)
