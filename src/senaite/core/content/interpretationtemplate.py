# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IInterpretationTemplate
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope.interface import implementer


class IInterpretationTemplateSchema(model.Schema):
    """Results Interpretation Template content interface
    """
    # The behavior IRichTextBehavior applies to this content type, so it
    # already provides the "text" field that renders the TinyMCE's Wsiwyg

    analysis_templates = UIDReferenceField(
        title=_(u"Analysis templates"),
        description=_(
            u"If set, this interpretation template will only be available for "
            u"selection on samples that have assigned any of these analysis "
            u"templates",
        ),
        allowed_types=("ARTemplate", ),
        multi_valued=True,
        required=False,
    )

    sample_types = UIDReferenceField(
        title=_(u"Sample types"),
        description=_(
            u"If set, this interpretation template will only be available for "
            u"selection on samples from these types",
        ),
        allowed_types=("SampleType", ),
        multi_valued=True,
        required=False,
    )

    directives.widget(
        "analysis_templates",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "ARTemplate",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ],
        limit=15,
    )

    directives.widget(
        "sample_types",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SampleType",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ],
        limit=15,
    )


@implementer(IInterpretationTemplate, IInterpretationTemplateSchema,
             IDeactivable)
class InterpretationTemplate(Container):
    """Results Interpretation Template content
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()
    exclude_from_nav = True

    @security.protected(permissions.View)
    def getAnalysisTemplates(self):
        """Return the ARTemplate objects assigned to this template, if any
        """
        accessor = self.accessor("analysis_templates")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawAnalysisTemplates(self):
        """Return the UIDs of ARTemplate objects assigned, if any
        """
        accessor = self.accessor("analysis_templates", raw=True)
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisTemplates(self, value):
        mutator = self.mutator("analysis_templates")
        mutator(self.context, value)

    @security.protected(permissions.View)
    def getSampleTypes(self):
        """Return the SampleType objects assigned to this template, if any
        """
        accessor = self.accessor("sample_types")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawSampleTypes(self):
        """Return the UIDs of the SampleType objects assigned, if any
        """
        accessor = self.accessor("sample_types", raw=True)
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleTypes(self, value):
        mutator = self.mutator("sample_types")
        mutator(self.context, value)
