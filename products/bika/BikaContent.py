from Products.Archetypes.public import *

BikaSchema = BaseSchema.copy()

IdField = BikaSchema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
