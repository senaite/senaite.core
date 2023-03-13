# -*- coding: utf-8 -*-

from Products.Archetypes.Field import StringField
from archetypes.schemaextender.field import ExtensionField
from bika.lims.browser.fields.uidreferencefield import UIDReferenceField


class ExtUIDReferenceField(ExtensionField, UIDReferenceField):
    """Extended UID Reference Field
    """


class ExtStringField(ExtensionField, StringField):
    """Extended String Field
    """
