from Products.Archetypes.public import BaseSchema
from plone.app.folder.folder import ATFolder, ATFolderSchema

BikaSchema = BaseSchema.copy()
BikaSchema['id'].widget.visible = False
BikaSchema['description'].widget.visible = False
BikaSchema['allowDiscussion'].widget.visible = False
BikaSchema['creators'].widget.visible = False
BikaSchema['contributors'].widget.visible = False
BikaSchema['rights'].widget.visible = False
BikaSchema['effectiveDate'].widget.visible = False
BikaSchema['expirationDate'].widget.visible = False
BikaSchema['subject'].widget.visible = False
BikaSchema['language'].widget.visible = False
BikaSchema['location'].widget.visible = False

BikaFolderSchema = ATFolderSchema.copy()
BikaFolderSchema['excludeFromNav'].widget.visible = False
BikaFolderSchema['nextPreviousEnabled'].widget.visible = False
