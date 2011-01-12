from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.Widget import ReferenceWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from archetypes.referencebrowserwidget import ReferenceBrowserWidget

class ReferenceBrowserListingWidget(ReferenceBrowserWidget):
    _properties = ReferenceBrowserWidget._properties.copy()
    _properties.update({
        'macro' : 'referencebrowserlisting',
        'helper_js': ('referencebrowserlisting.js',),
        'columns': (),
        })

    security = ClassSecurityInfo()    


registerWidget(ReferenceBrowserListingWidget,
               title = 'Reference Browser Listing Widget',
               description = ('Extends the Reference Browser widget to list referenced objects according to a custom schema .'),
               used_for = ('Products.Archetypes.Field.ReferenceField',)
               )

registerPropertyType('listing_schema', 'schema', ReferenceBrowserListingWidget)
