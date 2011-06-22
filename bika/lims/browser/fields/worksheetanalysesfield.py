from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Registry import registerField

class WorksheetAnalysesField(RecordsField):
    """a list of worksheet analyses """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'worksheetanalyses',
        'subfields' : ('uid', 'type', 'pos', 'key'),
        'subfield_types' : {'pos':'int'},
        'required_subfields' : ('uid', 'type', 'pos', 'key'),
        'subfield_labels':{'uid': 'UID',
                           'type': 'Type',
                           'pos': 'Position',
                           'key': 'Key value'},
        })
    security = ClassSecurityInfo()

registerField(WorksheetAnalysesField,
              title = "Worksheet Analyses",
              description = "Used for storing worksheet analyses layout",
              )
