# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IBatchBookView
from Products.Archetypes.utils import mapply
from senaite.core import logger
from senaite.core.datamanagers import DataManager
from zope.component import adapter


@adapter(IAnalysisRequest)
class SampleDataManager(DataManager):
    """Data Manager for Samples
    """

    @property
    def fields(self):
        return api.get_fields(self.context)

    def is_field_readable(self, field):
        """Checks if the field is readable
        """
        return field.checkPermission("get", self.context)

    def is_field_writeable(self, field, context=None):
        """Checks if the field is writeable
        """
        if context is None:
            context = self.context
        return field.checkPermission("set", context)

    def get_field_by_name(self, name):
        """Get the field by name
        """
        field = self.fields.get(name)

        # try to fetch the field w/o the `get` prefix
        # this might be the case is some listings
        if field is None:
            # ensure we do not have the field setter as column
            name = name.split("get", 1)[-1]
            field = self.fields.get(name)

        return field

    def get(self, name):
        """Get sample field
        """
        # get the schema field
        field = self.get_field_by_name(name)

        # check if the field exists
        if field is None:
            raise AttributeError("Field '{}' not found".format(name))

        # Check the permission of the field
        if not self.is_field_readable(field):
            raise Unauthorized("Field '{}' not readable!".format(name))

        # return the value with the field accessor
        if hasattr(field, "getAccessor"):
            accessor = field.getAccessor(self.context)
            return accessor()
        else:
            # Set the value on the field directly
            return field.get(self.context)

    def set_analysis_result(self, name, value):
        """Handle Batchbook Results

        :param name: ID of the contained analysis
        :param value: Result of the Analysis

        :returns: True if the result was set, otherwise False
        """
        analysis = self.get_analysis_by_id(name)
        if not analysis:
            logger.error("Analysis '{}' not found".format(name))
            return False

        fields = api.get_fields(analysis)
        field = fields.get("Result")
        # Check the permission of the field
        if not self.is_field_writeable(field, analysis):
            logger.error("Field '{}' not writeable!".format(name))
            return False

        # set the analysis result with the mutator
        analysis.setResult(value)
        analysis.reindexObject()
        return True

    def get_analysis_by_id(self, name):
        """Get the analysis by ID
        """
        return self.context.get(name)

    def is_request_from_batchbook(self):
        """Checks if the request is coming from the batchbook

        If this is the case, the `name` does not refer to a field,
        but to an analysis and the `value` is always the result.

        :returns: True if the request was sent from the batchbook
        """
        req = api.get_request()
        view = req.PARENTS[0]
        return IBatchBookView.providedBy(view)

    def set(self, name, value):
        """Set sample field or analysis result
        """
        # set of updated objects
        updated_objects = set()

        # handle batchbook results set
        if self.is_request_from_batchbook():
            success = self.set_analysis_result(name, value)
            if not success:
                raise ValueError(
                    "Failed to set analysis result for '%s'" % name)
            return [self.context]

        # get the schema field
        field = self.get_field_by_name(name)

        if field is None:
            raise AttributeError("Field '{}' not found".format(name))

        # Check the permission of the field
        if not self.is_field_writeable(field):
            logger.error("Field '{}' not writeable!".format(name))
            return []
        # get the field mutator (works only for AT content types)
        if hasattr(field, "getMutator"):
            mutator = field.getMutator(self.context)
            mapply(mutator, value)
        else:
            # Set the value on the field directly
            field.set(self.context, value)

        updated_objects.add(self.context)

        # return a unified list of the updated objects
        return list(updated_objects)
