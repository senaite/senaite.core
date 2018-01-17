# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""Generic field extensions
"""

from Products.ATExtensions.ateapi import RecordField
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import AnnotationStorage
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import ComputedField
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import FloatField
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextField
from archetypes.schemaextender.interfaces import IExtensionField
from zope.interface import implements
from zope.site.hooks import getSite

from bika.lims.browser.fields.proxyfield import ProxyField


class ExtensionField(object):

    """Mix-in class to make Archetypes fields not depend on generated
    accessors and mutators, and use AnnotationStorage by default.

    """

    implements(IExtensionField)

    storage = AnnotationStorage()

    def __init__(self, *args, **kwargs):
        super(ExtensionField, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs

    def getAccessor(self, instance):
        def accessor():
            if self.getType().endswith('ReferenceField'):
                return self.get(instance.__of__(getSite()))
            else:
                return self.get(instance)
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor():
            if self.getType().endswith('ReferenceField'):
                return self.getRaw(instance.__of__(getSite()))
            else:
                return self.getRaw(instance)
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            if self.getType().endswith('ReferenceField'):
                self.set(instance.__of__(getSite()), value)
            else:
                self.set(instance, value)
        return mutator

    def getIndexAccessor(self, instance):
        name = getattr(self, 'index_method', None)
        if name is None or name == '_at_accessor':
            return self.getAccessor(instance)
        elif name == '_at_edit_accessor':
            return self.getEditAccessor(instance)
        elif not isinstance(name, basestring):
            raise ValueError('Bad index accessor value: %r', name)
        else:
            return getattr(instance, name)

class ExtBooleanField(ExtensionField, BooleanField):

    "Field extender"


class ExtComputedField(ExtensionField, ComputedField):

    "Field extender"


class ExtDateTimeField(ExtensionField, DateTimeField):

    "Field extender"


class ExtFloatField(ExtensionField, FloatField):

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


class ExtProxyField(ExtensionField, ProxyField):

    """Field extender"""
