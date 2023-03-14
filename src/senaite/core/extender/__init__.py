# -*- coding: utf-8 -*-

from archetypes.schemaextender.field import ExtensionField
from bika.lims.browser.fields.uidreferencefield import UIDReferenceField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Field import TextField


class ExtUIDReferenceField(ExtensionField, UIDReferenceField):
    """Extended UID Reference Field
    """


class ExtStringField(ExtensionField, StringField):
    """Extended String Field
    """


class ExtTextField(ExtensionField, TextField):
    """Extended Text Field
    """
