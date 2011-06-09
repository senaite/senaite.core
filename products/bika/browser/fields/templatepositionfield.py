from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Registry import registerField

class TemplatePositionField(RecordsField):
    """a list of worksheet template rows """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'templateposition',
        'subfields' : ('pos', 'type', 'sub', 'dup'),
        'required_subfields' : ('pos', 'type'),
        'subfield_labels':{'pos': 'Position',
                           'type': 'Type',
                           'sub': 'Subtype',
                           'dup': 'Duplicate Of'},
        })
    security = ClassSecurityInfo()

registerField(TemplatePositionField,
              title = "Template Position",
              description = "Used for storing worksheet layout",
              )
