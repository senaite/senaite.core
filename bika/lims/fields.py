"""Generic field extensions
"""
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import Implicit
from Acquisition import ImplicitAcquisitionWrapper
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IExtensionField
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField
from Products.ATExtensions.ateapi import RecordField, RecordsField
from zope.interface import implements


class ExtBooleanField(ExtensionField, BooleanField):

    "Field extender"


class ExtComputedField(ExtensionField, ComputedField):

    "Field extender"


class ExtDateTimeField(ExtensionField, DateTimeField):

    "Field extender"


class ExtIntegerField(ExtensionField, IntegerField):

    "Field extender"


class ExtLinesField(ExtensionField, LinesField):

    "Field extender"


class ExtRecordField(ExtensionField, RecordField):

    "Field extender"


class ExtRecordsField(ExtensionField, RecordsField):

    "Field extender"


class ExtReferenceField(ExtensionField, ReferenceField):

    "Field extender"


class ExtStringField(ExtensionField, StringField):

    "Field extender"


class ExtTextField(ExtensionField, TextField):

    "Field extender"

#
# Method Initialization
# apply default getters and setters to schemaextender fields.
#


def apply_default_methods(context):

    for field in context.schema.fields():
        fieldname = field.getName()
        if getattr(context, 'get'+fieldname, None) is None:
            setattr(context, 'get'+fieldname, field_getter(context, fieldname))
        if getattr(context, 'set'+fieldname, None) is None:
            setattr(context, 'set'+fieldname, field_setter(context, fieldname))


class field_getter:

    def __init__(self, context, fieldname, **kwargs):
        self.context = context
        self.fieldname = fieldname

    def __call__(self):
        return self.context.Schema()[self.fieldname].getAccessor(self.context)(**kwargs)


class field_setter:

    def __init__(self, context, fieldname):
        self.context = context
        self.fieldname = fieldname

    def __call__(self, value, **kwargs):
        return self.context.Schema()[self.fieldname].getMutator(self.context)(value, **kwargs)



