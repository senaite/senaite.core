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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IMethod
from bika.lims.utils import t
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import ComputedField
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


schema = BikaSchema.copy() + Schema((

    # Method ID should be unique, specified on MethodSchemaModifier
    StringField(
        "MethodID",
        searchable=1,
        required=0,
        validators=("uniquefieldvalidator",),
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("Method ID"),
            description=_("Define an identifier code for the method. "
                          "It must be unique."),
        ),
    ),

    TextField(
        "Instructions",
        default_content_type="text/plain",
        allowed_content_types=("text/plain", ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Instructions"),
            description=_("Technical description and instructions "
                          "intended for analysts"),
        ),
    ),

    BlobFileField(
        "MethodDocument",  # XXX Multiple Method documents please
        widget=FileWidget(
            label=_("Method Document"),
            description=_("Load documents describing the method here"),
        )
    ),

    # The instruments linked to this method. Don't use this
    # method, use getInstrumentUIDs() or getInstruments() instead
    LinesField(
        "_Instruments",
        vocabulary="getInstrumentsDisplayList",
        widget=MultiSelectionWidget(
            modes=("edit"),
            label=_("Instruments"),
            description=_(
                "The selected instruments have support for this method. "
                "Use the Instrument edit view to assign "
                "the method to a specific instrument"),
        ),
    ),

    # All the instruments available in the system. Don't use this
    # method to retrieve the instruments linked to this method, use
    # getInstruments() or getInstrumentUIDs() instead.
    LinesField(
        "_AvailableInstruments",
        vocabulary="_getAvailableInstrumentsDisplayList",
        widget=MultiSelectionWidget(
            modes=("edit"),
        )
    ),

    # If no instrument selected, always True. Otherwise, the user will
    # be able to set or unset the value. The behavior for this field
    # is controlled with javascript.
    BooleanField(
        "ManualEntryOfResults",
        default=False,
        widget=BooleanWidget(
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use "
                          "this method can be set manually"),
            modes=("edit"),
        )
    ),

    # Only shown in readonly view. Not in edit view
    ComputedField(
        "ManualEntryOfResultsViewField",
        expression="context.isManualEntryOfResults()",
        widget=BooleanWidget(
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use "
                          "this method can be set manually"),
            modes=("view"),
        ),
    ),

    # Calculations associated to this method. The analyses services
    # with this method assigned will use the calculation selected here.
    UIDReferenceField(
        "Calculation",
        vocabulary="_getCalculations",
        allowed_types=("Calculation",),
        accessor="getCalculationUID",
        widget=SelectionWidget(
            visible={"edit": "visible", "view": "visible"},
            format="select",
            checkbox_bound=0,
            label=_("Calculation"),
            description=_(
                "If required, select a calculation for the The analysis "
                "services linked to this method. Calculations can be "
                "configured under the calculations item in the LIMS set-up"),
            catalog_name="bika_setup_catalog",
            base_query={"is_active": True},
        )
    ),
    BooleanField(
        "Accredited",
        schemata="default",
        default=True,
        widget=BooleanWidget(
            label=_("Accredited"),
            description=_("Check if the method has been accredited"))
    ),
))

schema["description"].schemata = "default"
schema["description"].widget.visible = True
schema["description"].widget.label = _("Description")
schema["description"].widget.description = _(
    "Describes the method in layman terms. "
    "This information is made available to lab clients")


class Method(BaseFolder):
    """Method content
    """
    implements(IMethod, IDeactivable, IHaveInstrument)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.public
    def getCalculation(self):
        """Returns the assigned calculation

        :returns: Calculation object
        """
        return self.getField("Calculation").get(self)

    @security.public
    def getCalculationUID(self):
        """Returns the UID of the assigned calculation

        NOTE: This is the default accessor of the `Calculation` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Calculation UID
        """
        calculation = self.getCalculation()
        if not calculation:
            return None
        return api.get_uid(calculation)

    def isManualEntryOfResults(self):
        """Indicates if manual entry of results is allowed.

        If no instrument is selected for this method, returns True. Otherwise,
        returns False by default, but its value can be modified using the
        ManualEntryOfResults Boolean Field
        """
        instruments = self.getInstruments()
        return len(instruments) == 0 or self.getManualEntryOfResults()

    def _getCalculations(self):
        """Available Calculations registered in Setup
        """
        bsc = getToolByName(self, "bika_setup_catalog")
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type="Calculation",
                              is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ("", t(_("None"))))
        return DisplayList(items)

    def getInstrument(self):
        """Instruments capable to perform this method.
        Required by IHaveInstrument
        """
        return self.getInstruments()

    def getInstruments(self):
        """Instruments capable to perform this method
        """
        return self.getBackReferences("InstrumentMethods")

    def getInstrumentUIDs(self):
        """UIDs of the instruments capable to perform this method
        """
        return map(api.get_uid, self.getInstruments())

    def getInstrumentsDisplayList(self):
        """Instruments capable to perform this method
        """
        items = [(i.UID(), i.Title()) for i in self.getInstruments()]
        return DisplayList(list(items))

    def _getAvailableInstrumentsDisplayList(self):
        """Available instruments registered in the system

        Only instruments with state=active will be fetched
        """
        bsc = getToolByName(self, "bika_setup_catalog")
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type="Instrument",
                              is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(Method, PROJECTNAME)
