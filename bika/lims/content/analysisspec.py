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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import Schema
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields import ResultsRangesField
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.content.sampletype import SampleTypeAwareMixin
from bika.lims.interfaces import IAnalysisSpec
from bika.lims.interfaces import IDeactivable

schema = Schema((

    UIDReferenceField(
        'SampleType',
        allowed_types=('SampleType',),
        required=1,
        widget=ReferenceWidget(
            label=_("Sample Type"),
            showOn=True,
            catalog_name=SETUP_CATALOG,
            base_query=dict(
                is_active=True,
                sort_on="sortable_title",
                sort_order="ascending"
            ),
        ),
    ),

    UIDReferenceField(
        'DynamicAnalysisSpec',
        allowed_types=('DynamicAnalysisSpec',),
        required=0,
        widget=ReferenceWidget(
            label=_("Dynamic Analysis Specification"),
            showOn=True,
            catalog_name=SETUP_CATALOG,
            base_query=dict(
                sort_on="sortable_title",
                sort_order="ascending"
            ),
        ),
    ),

)) + BikaSchema.copy() + Schema((

    ResultsRangesField(
        'ResultsRange',
        required=1,
        widget=AnalysisSpecificationWidget(
            label=_("Specifications"),
            description=_(
                "'Min' and 'Max' values indicate a valid results range. Any "
                "result outside this results range will raise an alert. 'Min "
                "warn' and 'Max warn' values indicate a shoulder range. Any "
                "result outside the results range but within the shoulder "
                "range will raise a less severe alert. If the result is out of "
                "range, the value set for '< Min' or '< Max' will be displayed "
                "in lists and results reports instead of the real result.")
        ),
    ),
))

schema['description'].widget.visible = True
schema['title'].required = True


class AnalysisSpec(BaseFolder, HistoryAwareMixin, ClientAwareMixin,
                   SampleTypeAwareMixin):
    """Analysis Specification
    """
    implements(IAnalysisSpec, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the title if possible, else return the Sample type.
        Fall back on the instance's ID if there's no sample type or title.
        """
        if self.title:
            title = self.title
        else:
            title = self.getSampleTypeTitle() or ""
        return safe_unicode(title).encode('utf-8')

    def contextual_title(self):
        parent = self.aq_parent
        if parent == self.bika_setup.bika_analysisspecs:
            return self.title + " (" + translate(_("Lab")) + ")"
        else:
            return self.title + " (" + translate(_("Client")) + ")"


atapi.registerType(AnalysisSpec, PROJECTNAME)
