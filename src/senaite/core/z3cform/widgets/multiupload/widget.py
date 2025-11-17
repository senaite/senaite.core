# -*- coding: utf-8 -*-

import json
from bika.lims import api
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
    """Multi-file upload widget using React and react-dropzone
    """

    klass = u"multi-upload-widget"
    value = ()

    def update(self):
        super(MultiUploadWidget, self).update()

    @property
    def portal_url(self):
        """Return the portal URL"""
        return api.get_url(api.get_portal())

    @property
    def context_url(self):
        """Return the context URL"""
        return api.get_url(self.context)

    def get_data_attributes(self):
        """Return data attributes for the React widget"""
        return {
            "id": self.id,
            "name": self.name,
            "portal_url": self.portal_url,
            "context_url": self.context_url,
            "max_filesize": 104857600,  # 100MB default
            "accepted_types": {},  # Accept all file types by default
        }

    def render_data_attributes(self):
        """Render data attributes as HTML string"""
        attrs = []
        for key, value in self.get_data_attributes().items():
            json_value = json.dumps(value)
            # Escape quotes for HTML attribute
            json_value = json_value.replace('"', '&quot;')
            attrs.append('data-{}="{}"'.format(key, json_value))
        return " ".join(attrs)

    def extract(self, default=None):
        """Extract uploaded files from request
        """
        # Get the JSON data from the hidden field
        data_field = self.name + '.data'
        data = self.request.form.get(data_field, None)

        if data:
            try:
                # Parse the JSON data containing file IDs
                return json.loads(data)
            except (ValueError, TypeError):
                pass

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
