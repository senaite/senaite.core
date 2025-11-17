# -*- coding: utf-8 -*-

from plone.namedfile.file import NamedBlobFile
from senaite.core.interfaces import IMultiUploadWidget
from senaite.core.interfaces import ISenaiteFormLayer
from z3c.form.browser import widget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import ITuple


@implementer_only(IMultiUploadWidget)
class MultiUploadWidget(widget.HTMLFormElement, Widget):
    """Multi-file upload widget using Dropzone.js
    """

    klass = u"multi-upload-widget"
    value = ()

    def update(self):
        super(MultiUploadWidget, self).update()

    def extract(self, default=None):
        """Extract uploaded files from request
        """
        # Get the uploaded files from the request
        files = self.request.form.get(self.name, [])

        if not isinstance(files, list):
            files = [files] if files else []

        # Filter out empty submissions
        files = [f for f in files if f and getattr(f, 'filename', None)]

        if files:
            return files

        # Check if we should keep existing files
        existing = self.request.form.get(self.name + '.existing', [])
        if existing:
            if not isinstance(existing, list):
                existing = [existing]
            return existing

        return default


@adapter(IMultiUploadWidget)
@implementer(IDataConverter)
class MultiUploadDataConverter(BaseDataConverter):
    """Data converter for multi-upload widget
    """

    def toWidgetValue(self, value):
        """Convert from field value to widget value
        """
        if value is None:
            return ()
        return value

    def toFieldValue(self, value):
        """Convert from widget value to field value
        """
        if not value:
            return ()

        result = []
        for item in value:
            if isinstance(item, NamedBlobFile):
                result.append(item)
            elif hasattr(item, 'read'):
                # It's a file upload object
                filename = getattr(item, 'filename', 'unknown')
                content_type = getattr(item, 'headers', {}).get('content-type', 'application/octet-stream')
                blob = NamedBlobFile(
                    data=item.read(),
                    filename=filename,
                    contentType=content_type
                )
                result.append(blob)

        return tuple(result)


@adapter(ITuple, ISenaiteFormLayer)
@implementer(IFieldWidget)
def MultiUploadWidgetFactory(field, request):
    """Factory for the multi-upload widget"""
    return FieldWidget(field, MultiUploadWidget(request))
