# -*- coding: utf-8 -*-

from plone.app.blob.interfaces import IFileUpload


class ISenaiteFileUpload(IFileUpload):
    """Marker interface for ZPublisher.HTTPRequest.FileUpload class
    """
