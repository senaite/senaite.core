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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl.SecurityInfo import ClassSecurityInfo
from plone.namedfile.field import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryField
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.content.base import Item
from senaite.core.interfaces import ISimpleFile
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer


class ISimpleFileSchema(model.Schema):
    """Schema interface for SimpleFile
    """

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    file = NamedBlobFile(
        title=u"File",
        description=u"Upload a file",
        required=True,
    )


# Mark the file field as the primary field
alsoProvides(ISimpleFileSchema["file"], IPrimaryField)


@implementer(ISimpleFile, ISimpleFileSchema)
class SimpleFile(Item):
    """A simple file content type for client attachments
    """

    _catalogs = ["senaite_attachments_catalog"]
    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def content_type(self):
        return getattr(self.file, "contentType", None)

    @security.protected(permissions.View)
    def get_size(self):
        return getattr(self.file, "size", 0)

    def getObjSize(self):
        """Returns the size of the file in human-readable format
        """
        size = self.get_size()
        if not size:
            return "0 KB"

        if size < 1024:
            return "{} B".format(size)
        elif size < 1048576:
            return "{} KB".format(size / 1024)
        else:
            return "{:.2f} MB".format(size / 1048576.0)
