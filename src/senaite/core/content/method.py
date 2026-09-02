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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import six

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveInstrument
from plone.app.textfield.value import RichTextValue
from plone.autoform import directives
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IMethod
from senaite.core.schema import RichTextField
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant

# Relationship name used by the Instrument to reference its methods. Reading it
# in reverse yields the instruments that support a given method.
INSTRUMENT_METHODS = "InstrumentMethods"


class InstrumentsField(UIDReferenceField):
    """Computed reference to the instruments supporting this method.

    The relation is stored on the Instrument side (`Instrument.Methods`,
    relationship `InstrumentMethods`). This field does not store anything on
    the method itself: it reads the back-references on read and, on write,
    propagates the change to the referenced instruments.
    """

    def get_raw(self, object):
        instance = self._get_content_object(object)
        return instance.getRawInstruments()

    def get(self, object):
        instance = self._get_content_object(object)
        return instance.getInstruments()

    def set(self, object, value):
        instance = self._get_content_object(object)
        instance.setInstruments(value)


class IMethodSchema(model.Schema):
    """Method content interface
    """

    title = schema.TextLine(
        title=_(u"title_method_title", default=u"Name"),
        required=True,
    )

    method_id = schema.TextLine(
        title=_(u"title_method_method_id", default=u"Method ID"),
        description=_(
            u"description_method_method_id",
            default=u"Define an identifier code for the method. "
                    u"It must be unique."),
        required=False,
    )

    description = schema.Text(
        title=_(u"title_method_description", default=u"Description"),
        description=_(u"description_method_description",
                      default=u"Short method description"),
        required=False,
    )

    accredited = schema.Bool(
        title=_(u"title_method_accredited", default=u"Accredited"),
        description=_(u"description_method_accredited",
                      default=u"Check if the method has been accredited"),
        required=False,
        default=False,
    )

    instructions = RichTextField(
        title=_(u"title_method_instructions", default=u"Instructions"),
        description=_(u"description_method_instructions",
                      default=u"Technical description and instructions "
                      u"intended for analysts"),
        required=False,
    )

    method_document = NamedBlobFile(
        title=_(u"title_method_document", default=u"Method Document"),
        description=_(u"description_method_document",
                      default=u"Load documents describing the method here"),
        required=False,
    )

    instruments = InstrumentsField(
        title=_(u"title_method_instruments", default=u"Instruments"),
        description=_(u"description_method_instruments",
                      default=u"Instruments supporting this method"),
        allowed_types=("Instrument", ),
        multi_valued=True,
        required=False,
    )

    calculations = UIDReferenceField(
        title=_(u"title_method_calculations", default=u"Calculations"),
        description=_(u"description_method_calculations",
                      default=u"Supported calculations of this method"),
        allowed_types=("Calculation", ),
        multi_valued=True,
        required=False,
    )

    directives.mode(calculation="hidden")
    calculation = UIDReferenceField(
        title=_(u"title_method_calculation", default=u"Calculation"),
        description=_(
            u"description_method_calculation",
            default=u"If required, select a calculation for the analysis "
                    u"services linked to this method. Calculations can be "
                    u"configured under the calculations item in the LIMS "
                    u"set-up"),
        allowed_types=("Calculation", ),
        multi_valued=False,
        required=False,
    )

    directives.widget(
        "instruments",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {"name": "title", "align": "left", "label": _(u"Title")},
        ],
        limit=15,
    )

    directives.widget(
        "calculations",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "Calculation",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {"name": "title", "align": "left", "label": _(u"Title")},
        ],
        limit=15,
    )

    @invariant
    def validate_method_id(data):
        """Checks if the Method ID is unique
        """
        method_id = data.method_id
        if not method_id:
            return
        # https://community.plone.org/t/dexterity-unique-field-validation
        # NOTE: there is no `method_id` catalog index, so we compare the
        #       Method ID of the existing methods in Python.
        context = getattr(data, "__context__", None)
        context_uid = api.get_uid(context) if context is not None else None
        query = {"portal_type": "Method"}
        for brain in api.search(query, SETUP_CATALOG):
            method = api.get_object(brain)
            if api.get_uid(method) == context_uid:
                # skip the object being edited
                continue
            if method.getMethodID() == method_id:
                raise Invalid(_("Method ID must be unique"))


@implementer(IMethod, IMethodSchema, IHaveInstrument, IDeactivable)
class Method(Container):
    """A method describes how an analysis is performed

    Methods can be assigned to analysis services and define which instruments
    and calculations are possible.
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getMethodID(self):
        accessor = self.accessor("method_id")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setMethodID(self, value):
        mutator = self.mutator("method_id")
        mutator(self, api.safe_unicode(value or ""))

    # BBB: AT schema field property
    MethodID = property(getMethodID, setMethodID)

    @security.protected(permissions.View)
    def getAccredited(self):
        accessor = self.accessor("accredited")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccredited(self, value):
        mutator = self.mutator("accredited")
        mutator(self, bool(value))

    # BBB: AT schema field property
    Accredited = property(getAccredited, setAccredited)

    @security.protected(permissions.View)
    def getInstructions(self):
        accessor = self.accessor("instructions")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setInstructions(self, value):
        # wrap plain (html) strings into a rich text value
        if isinstance(value, six.string_types):
            value = RichTextValue(
                api.safe_unicode(value), "text/html", "text/x-html-safe")
        mutator = self.mutator("instructions")
        mutator(self, value)

    # BBB: AT schema field property
    Instructions = property(getInstructions, setInstructions)

    @security.protected(permissions.View)
    def getMethodDocument(self):
        accessor = self.accessor("method_document")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setMethodDocument(self, value):
        mutator = self.mutator("method_document")
        mutator(self, value)

    # BBB: AT schema field property
    MethodDocument = property(getMethodDocument, setMethodDocument)

    @security.protected(permissions.View)
    def getInstruments(self):
        """Instruments capable to perform this method
        """
        instruments = map(api.get_object, self.getRawInstruments())
        return list(instruments)

    @security.protected(permissions.View)
    def getRawInstruments(self):
        """List of Instrument UIDs capable to perform this method
        """
        backrefs = get_backreferences(self, INSTRUMENT_METHODS)
        # XXX: The backrefs might contain UIDs of deactivated instruments,
        #      which will show up in the UI as just their UID.
        active_instrument_uids = filter(
            lambda uid: api.get_review_status(uid) == "active", backrefs)
        return list(active_instrument_uids)

    @security.protected(permissions.ModifyPortalContent)
    def setInstruments(self, value):
        """Set the method on the selected instruments
        """
        # filter out empty value
        value = filter(lambda uid: uid, value)

        # handle removed instruments
        existing = self.getRawInstruments()
        to_remove = filter(lambda uid: uid not in value, existing)

        # remove method from removed instruments
        for uid in to_remove:
            instrument = api.get_object_by_uid(uid)
            methods = instrument.getMethods()
            methods.remove(self)
            instrument.setMethods(methods)

        # add method to new added instruments
        for uid in value:
            instrument = api.get_object_by_uid(uid)
            methods = instrument.getMethods()
            if self in methods:
                continue
            methods.append(self)
            instrument.setMethods(methods)

    # BBB: AT schema field property
    Instruments = property(getInstruments, setInstruments)

    @security.protected(permissions.View)
    def getCalculations(self):
        """List of Calculation objects supported by this method
        """
        accessor = self.accessor("calculations")
        return accessor(self) or []

    @security.protected(permissions.View)
    def getRawCalculations(self):
        """List of Calculation UIDs supported by this method
        """
        accessor = self.accessor("calculations", raw=True)
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setCalculations(self, value):
        """Set the available calculations for the method
        """
        if not value:
            value = []
        value = filter(api.is_uid, value)
        mutator = self.mutator("calculations")
        mutator(self, value)

    # BBB: AT schema field property
    Calculations = property(getCalculations, setCalculations)

    @security.protected(permissions.View)
    def getCalculation(self):
        """Default calculation for the analysis services linked to this method
        """
        accessor = self.accessor("calculation")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawCalculation(self):
        """UID of the default calculation
        """
        accessor = self.accessor("calculation", raw=True)
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCalculation(self, value):
        """Set the default calculation for the method
        """
        mutator = self.mutator("calculation")
        mutator(self, value)

    # BBB: AT schema field property
    Calculation = property(getCalculation, setCalculation)
