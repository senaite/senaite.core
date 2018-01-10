# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from Products.Archetypes import atapi
from plone.app.blob.field import FileField
from Products.Archetypes.public import BaseContent
from bika.lims.interfaces import IMultifile
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import bikaMessageFactory as _
from bika.lims import config


schema = BikaSchema.copy() + atapi.Schema((

    atapi.StringField('DocumentID',
    required=1,
    validators=('uniquefieldvalidator',),
    widget = atapi.StringWidget(
        label=_("Document ID"),
        )
    ),

    FileField('File',
    required=1,
    widget = atapi.FileWidget(
        label=_("Document"),
        description=_("File upload "),
        )
    ),

    atapi.StringField('DocumentVersion',
    widget = atapi.StringWidget(
        label=_("Document Version"),
        )
    ),

    atapi.StringField('DocumentLocation',
    widget = atapi.StringWidget(
        label=_("Document Location"),
        description=_("Location where the document set is shelved"),
        )
    ),

    atapi.StringField('DocumentType',
    required=1,
    widget = atapi.StringWidget(
        label=_("Document Type"),
        description=_("Type of document (e.g. user manual, instrument specifications, image, ...)"),
        )
    ),
))

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False

class Multifile(BaseContent):
    # It implements the IEthnicity interface
    implements(IMultifile)
    schema = schema

# Activating the content type in Archetypes' internal types registry
atapi.registerType(Multifile, config.PROJECTNAME)
