# -*- coding: utf-8 -*-

from archetypes.schemaextender.field import ExtensionField
from bika.lims.browser.fields.uidreferencefield import UIDReferenceField


class ExtUIDReferenceField(ExtensionField, UIDReferenceField):
    """Extended UID Reference Field
    """
