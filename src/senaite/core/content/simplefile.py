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
from senaite.core.content.mixins import ClientAwareMixin
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
class SimpleFile(Item, ClientAwareMixin):
    """A simple file content type for client attachments.

    Drag-and-drop uploads land this content under a Client,
    so it carries the `IClientAwareMixin` marker so the
    `allowedRolesAndUsers` indexer adds the identity-bound
    `client:<uid>` token and the dynamic role provider grants
    Owner/Client to the linked client contact.
    """

    _catalogs = ["senaite_attachments_catalog"]
    security = ClassSecurityInfo()

    @property
    @security.protected(permissions.View)
    def content_type(self):
        """Return the content type of the file"""
        return getattr(self.file, "contentType", None)

    @security.protected(permissions.View)
    def get_size(self):
        """Return the file size in bytes"""
        return getattr(self.file, "size", 0)

    @security.protected(permissions.View)
    def get_filename(self):
        """Return the filename as unicode"""
        from bika.lims import api
        filename = getattr(self.file, "filename", u"")
        return api.safe_unicode(filename)

    @security.protected(permissions.View)
    def get_formatted_size(self):
        """Return the file size in human-readable format"""
        size = self.get_size()
        if not size:
            return u"0 B"

        for unit in [u"B", u"KB", u"MB", u"GB"]:
            if size < 1024.0:
                return u"{:.1f} {}".format(size, unit)
            size /= 1024.0
        return u"{:.1f} TB".format(size)
