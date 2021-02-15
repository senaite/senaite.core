# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from bika.lims import api
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IRoutineAnalysis
from Products.Archetypes.utils import mapply
from senaite.core import logger
from senaite.core.datamanagers import DataManager
from zope.component import adapter


@adapter(IRoutineAnalysis)
class RoutineAnalysisDataManager(DataManager):
    """Data Manager for Routine Analyses
    """

    @property
    def fields(self):
        return api.get_fields(self.context)

    def is_field_readable(self, field):
        """Checks if the field is readable
        """
        return field.checkPermission("get", self.context)

    def is_field_writeable(self, field):
        """Checks if the field is writeable
        """
        return field.checkPermission("set", self.context)

    def get(self, name):
        """Get analysis field
        """
        # schema field
        field = self.fields.get(name)

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

    def set(self, name, value):
        """Set analysis field/interim value
        """
        # set of updated objects
        updated_objects = set()

        # schema field
        field = self.fields.get(name)

        # interims
        interims = self.context.getInterimFields()
        interim_keys = map(lambda i: i.get("keyword"), interims)

        # schema field found
        if field:
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

        # interim key found
        elif name in interim_keys:
            # Check the permission of the field
            interim_field = self.fields.get("InterimFields")
            if not self.is_field_writeable(interim_field):
                logger.error("Interim field '{}' not writeable!".format(name))
                return []
            for interim in interims:
                if interim.get("keyword") == name:
                    interim["value"] = value
            self.context.setInterimFields(interims)

        # recalculate dependent results for result and interim fields
        if name == "Result" or name in interim_keys:
            updated_objects.add(self.context)
            updated_objects.update(self.recalculate_results(self.context))

        # return a unified list of the updated objects
        return list(updated_objects)

    def recalculate_results(self, obj, recalculated=None):
        """Recalculate the result of the object and its dependents

        :returns: List of recalculated objects
        """
        if recalculated is None:
            recalculated = set()

        # avoid double recalculation in recursion
        if obj in recalculated:
            return set()

        # recalculate own result
        if obj.calculateResult(override=True):
            # append object to the list of recalculated results
            recalculated.add(obj)
        # recalculate dependent analyses
        for dep in obj.getDependents():
            if dep.calculateResult(override=True):
                # TODO the `calculateResult` method should return False here!
                if dep.getResult() in ["NA", "0/0"]:
                    continue
                recalculated.add(dep)
            # recalculate dependents of dependents
            for ddep in dep.getDependents():
                recalculated.update(
                    self.recalculate_results(
                        ddep, recalculated=recalculated))
        return recalculated


@adapter(IReferenceAnalysis)
class ReferenceAnalysisDataManager(RoutineAnalysisDataManager):
    """Data Manager for Reference Analyses
    """
