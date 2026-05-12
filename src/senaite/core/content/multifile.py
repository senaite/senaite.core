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

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from bika.lims.api import safe_unicode as u
from bika.lims.interfaces import IDeactivable
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.content.base import Container
from senaite.core.interfaces import IMultifile
from zope import schema
from zope.interface import implementer


class IMultifileSchema(model.Schema):
    """Multifile Schema
    """

    document_id = schema.TextLine(
        title=_(
            u"label_multifile_document_id",
            default=u"Document ID"
        ),
        required=True,
    )

    file = NamedBlobFile(
        title=_(
            u"label_multifile_file",
            default=u"Document"
        ),
        description=_(
            u"description_multifile_file",
            default=u"File upload"
        ),
        required=True,
    )

    document_version = schema.TextLine(
        title=_(
            u"label_multifile_document_version",
            default=u"Document Version"
        ),
        required=False,
    )

    document_location = schema.TextLine(
        title=_(
            u"label_multifile_document_location",
            default=u"Document Location"
        ),
        description=_(
            u"description_multifile_document_location",
            default=u"Location where the document set is shelved"
        ),
        required=False,
    )

    document_type = schema.TextLine(
        title=_(
            u"label_multifile_document_type",
            default=u"Document Type"
        ),
        description=_(
            u"description_multifile_document_type",
            default=u"Type of document (e.g. user manual, instrument "
                    u"specifications, image, ...)"
        ),
        required=True,
    )


@implementer(IMultifile, IMultifileSchema, IDeactivable)
class Multifile(Container):
    """A Document/File attachment
    """
    security = ClassSecurityInfo()

    def Title(self):
        """Return the DocumentID as Title
        """
        return self.getDocumentID() or self.getId()

    @security.protected(permissions.View)
    def getDocumentID(self):
        accessor = self.accessor("document_id")
        value = accessor(self)
        if not value:
            return ""
        return u(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDocumentID(self, value):
        mutator = self.mutator("document_id")
        mutator(self, u(value))

    @security.protected(permissions.View)
    def getFile(self):
        accessor = self.accessor("file")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setFile(self, value):
        mutator = self.mutator("file")
        mutator(self, value)

    @security.protected(permissions.View)
    def getDocumentVersion(self):
        accessor = self.accessor("document_version")
        value = accessor(self)
        if not value:
            return ""
        return u(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDocumentVersion(self, value):
        mutator = self.mutator("document_version")
        mutator(self, u(value))

    @security.protected(permissions.View)
    def getDocumentLocation(self):
        accessor = self.accessor("document_location")
        value = accessor(self)
        if not value:
            return ""
        return u(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDocumentLocation(self, value):
        mutator = self.mutator("document_location")
        mutator(self, u(value))

    @security.protected(permissions.View)
    def getDocumentType(self):
        accessor = self.accessor("document_type")
        value = accessor(self)
        if not value:
            return ""
        return u(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDocumentType(self, value):
        mutator = self.mutator("document_type")
        mutator(self, u(value))

    # BBB: AT schema field properties for backward compatibility
    DocumentID = property(getDocumentID, setDocumentID)
    File = property(getFile, setFile)
    DocumentVersion = property(getDocumentVersion, setDocumentVersion)
    DocumentLocation = property(getDocumentLocation, setDocumentLocation)
    DocumentType = property(getDocumentType, setDocumentType)
