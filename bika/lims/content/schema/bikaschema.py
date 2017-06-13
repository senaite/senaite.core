# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.public import BaseSchema
from plone.app.folder.folder import ATFolderSchema
from . import Storage

BikaSchema = BaseSchema.copy()
BikaSchema['id'].widget.visible = False
BikaSchema['id'].storage = Storage()
BikaSchema['description'].widget.visible = False
BikaSchema['description'].schemata = 'default'
BikaSchema['description'].default_content_type = 'text/plain'
BikaSchema['description'].allowable_content_types = ('text/plain',)
BikaSchema['description'].storage = Storage()
BikaSchema['allowDiscussion'].widget.visible = False
BikaSchema['creators'].widget.visible = False
BikaSchema['contributors'].widget.visible = False
BikaSchema['rights'].widget.visible = False
BikaSchema['effectiveDate'].widget.visible = False
BikaSchema['expirationDate'].widget.visible = False
BikaSchema['subject'].widget.visible = False
BikaSchema['language'].widget.visible = False
BikaSchema['location'].widget.visible = False

BikaSchema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
BikaSchema['title']._validationLayer()
BikaSchema['title'].storage = Storage()

BikaFolderSchema = ATFolderSchema.copy()
BikaFolderSchema['excludeFromNav'].widget.visible = False
BikaFolderSchema['nextPreviousEnabled'].widget.visible = False
BikaFolderSchema['id'].widget.visible = False
BikaFolderSchema['id'].storage = Storage()
BikaFolderSchema['description'].widget.visible = False
BikaFolderSchema['description'].storage = Storage()
BikaFolderSchema['allowDiscussion'].widget.visible = False
BikaFolderSchema['creators'].widget.visible = False
BikaFolderSchema['contributors'].widget.visible = False
BikaFolderSchema['rights'].widget.visible = False
BikaFolderSchema['effectiveDate'].widget.visible = False
BikaFolderSchema['expirationDate'].widget.visible = False
BikaFolderSchema['subject'].widget.visible = False
BikaFolderSchema['language'].widget.visible = False
BikaFolderSchema['location'].widget.visible = False
BikaFolderSchema['locallyAllowedTypes'].schemata = 'settings'
BikaFolderSchema['immediatelyAddableTypes'].schemata = 'settings'
BikaFolderSchema['constrainTypesMode'].schemata = 'settings'
BikaFolderSchema['locallyAllowedTypes'].widget.visible = False
BikaFolderSchema['immediatelyAddableTypes'].widget.visible = False
BikaFolderSchema['constrainTypesMode'].widget.visible = False

BikaFolderSchema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
BikaFolderSchema['title']._validationLayer()
BikaFolderSchema['title'].storage = Storage()
