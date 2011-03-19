from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Registry import registerField

class WSTemplateAnalysesField(RecordsField):
    """a list of worksheet template rows """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'wstemplateanalyses',
        'subfields' : ('pos', 'type', 'services', 'count'),
        'required_subfields' : ('pos', 'type'),
        'subfield_labels':{'pos': 'Position',
                           'type': 'Type',
                           'services': 'Services',
                           'count': 'Count'},
        })
    security = ClassSecurityInfo()

registerField(WSTemplateAnalysesField,
              title = "Template Position",
              description = "Used for storing worksheet layout",
              )
