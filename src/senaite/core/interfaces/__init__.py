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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.z3cform.interfaces import IPloneFormLayer
from senaite.core.interfaces.datamanager import IDataManager
from zope.interface import Interface
from senaite.core.interfaces.catalog import *


class ISenaiteCore(Interface):
    """Marker interface that defines a Zope 3 browser layer.
    """


class ISenaiteFormLayer(IPloneFormLayer):
    """Used to override plone.app.z3cform forms

    Inherits from `z3c.form.interfaces.IFormLayer`
    """


class IShowDisplayMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Display" menu
    """


class IShowFactoriesMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Add" menu
    """


class IHideActionsMenu(Interface):
    """Marker interface that can be applied for contents that should not
    display the content actions menu
    """


class IAjaxEditForm(Interface):
    """Ajax edit form adapter
    """

    def initialized(data):
        """Called once after the edit form was rendered

        :param data: JSON payload of the edit form.
                     Contains at least `form`, `name`, `value`
        :returns: A dictionary with update instructions for the frontend logic
        """

    def modified(data):
        """Called for each field modification

        :param data: JSON payload of the edit form.
                     Contains at least `form`, `name`, `value`
        :returns: A dictionary with update instructions for the frontend logic
        """


class INumberGenerator(Interface):
    """A utility to generates unique numbers by key
    """


class IContainer(Interface):
    """SENAITE Base Container
    """


class IItem(Interface):
    """SENAITE Base Item
    """


class ISetup(Interface):
    """Marker interface for setup folder
    """


class ISamples(Interface):
    """Marker interface for samples main folder
    """


class ISamplesView(Interface):
    """Marker interface for samples listing view
    """


class IHaveUIDReferences(Interface):
    """Marker interface when the object contains UID references
    """


class ISampleContainers(Interface):
    """Marker interface for sample container setup folder
    """


class ISampleContainer(Interface):
    """Marker interface for sample containers
    """


class IContentMigrator(Interface):
    """Marker interface for content migrator
    """


class IFieldMigrator(Interface):
    """Marker interface for field migrator
    """


class IDynamicLocalRoles(Interface):
    """Marker interface for objects with dynamic assignment of local roles
    """


class IInterpretationTemplate(Interface):
    """Marker interface for interpretation template objects
    """


class ILabels(Interface):
    """Marker interface for labels container
    """


class ILabel(Interface):
    """Marker interface for labels
    """


class ICanHaveLabels(Interface):
    """Marker interface for labeled capable objects
    """


class IHaveLabels(ICanHaveLabels):
    """Marker interface for labeled objects

    NOTE: We inherit from `ICanHaveLabels` to always show the schema extended
          fields for already labeled objects
    """


class IReferenceWidgetDataProvider(Interface):
    """Extract required data for the reference widget
    """

    def to_dict():
        """Provide a dictionary with JSON serializable object information
        """
