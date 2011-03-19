from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Registry import registerField

class SpecField(RecordsField):
    """a list of in-range analysis result specifications
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'analysisspec',
        'subfields' : ('service', 'min', 'max', 'error'),
        'required_subfields' : ('service', 'min', 'max', 'error'),
        'subfield_labels':{'service': 'Analysis Service',
                           'min': 'Min',
                           'max': 'Max',
                           'error': '% Error'},
        })
    security = ClassSecurityInfo()

registerField(SpecField,
              title = "Analysis Result Specification",
              description = "Used for storing analysis result range specifications",
              )
