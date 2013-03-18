""" An AnalysisRequest report, containing the report itself in pdf and html
    format. Also, includes information about the date when was published, from
    who, the report recipients (and their emails) and the publication mode
"""
from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.public import ReferenceField, FileField, \
        StringField, Schema, BaseFolder
from plone.app.blob.field import BlobField
from Products.Archetypes.references import HoldingReference
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
    ReferenceField('AnalysisRequest',
       allowed_types=('AnalysisRequest',),
       relationship='ReportAnalysisRequest',
       referenceClass=HoldingReference,
       required=1,
    ),
    BlobField('Pdf',
    ),
    StringField('Html',
    ),
    StringField('SMS',
    ),
    RecordsField('Recipients',
        type='recipients',
        subfields=('UID', 'Username', 'Fullname', 'EmailAddress',
                   'PublicationModes'),
    ),
))

schema['id'].required = False
schema['title'].required = False


class ARReport(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(ARReport, PROJECTNAME)
