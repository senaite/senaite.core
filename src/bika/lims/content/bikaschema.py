# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.public import BaseSchema
from plone.app.folder.folder import ATFolderSchema

BikaSchema = BaseSchema.copy()
BikaSchema['id'].widget.visible = False
BikaSchema['description'].widget.visible = False
BikaSchema['description'].schemata = 'default'
BikaSchema['description'].default_content_type = 'text/plain'
BikaSchema['description'].allowable_content_types = ('text/plain',)
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

BikaFolderSchema = ATFolderSchema.copy()
BikaFolderSchema['excludeFromNav'].widget.visible = False
BikaFolderSchema['nextPreviousEnabled'].widget.visible = False
BikaFolderSchema['id'].widget.visible = False
BikaFolderSchema['description'].widget.visible = False
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
