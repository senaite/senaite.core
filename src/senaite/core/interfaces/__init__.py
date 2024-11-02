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

from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.protect.interfaces import IDisableCSRFProtection
from senaite.core.interfaces.catalog import *  # noqa:F401,F403
from senaite.core.interfaces.datamanager import IDataManager  # noqa:F401
from senaite.core.interfaces.widget import *  # noqa:F401,F403
from zope.interface import Interface


class ISenaiteCore(IDisableCSRFProtection):
    """Marker interface that defines a Zope 3 browser layer.

    NOTE: We disable CSRF protection site-wide.
    """


class ISenaiteFormLayer(IPloneFormLayer):
    """Used to override plone.app.z3cform forms

    Inherits from `z3c.form.interfaces.IFormLayer`
    """


class ISenaiteRegistryFactory(Interface):
    """Marker interface for factory registry records
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


class IMultiCatalogBehavior(Interface):
    """Support multiple catalogs for Dexterity contents
    """


class IAutoGenerateID(Interface):
    """Auto-generate ID with ID server
    """


class IIdServer(Interface):
    """Marker Interface for ID server
    """

    def generate_id(self, portal_type, batch_size=None):
        """Generate a new id for 'portal_type'
        """


class IIdServerVariables(Interface):
    """Marker interfaces for variables generator for ID Server
    """

    def get_variables(self, **kw):
        """Returns a dict with variables
        """


class IIdServerTypeID(Interface):
    """Marker interface for type id resolution for ID Server
    """

    def get_type_id(self, **kw):
        """Returns the type id for the context passed in the constructor, that
        is used for custom ID formatting, regardless of the real portal type of
        the context. Return None if no type id can be resolved by this adapter
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


class ITemporaryObject(Interface):
    """Marker interface for temporary objects

    This is similar to the `creationFlag`, but skips indexing for any object
    that implements this interface.

    Also see: `senaite.core.patches.catalog.catlog_object`
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


class IAnalysisProfile(Interface):
    """Marker interface for analysis profiles
    """


class IAnalysisProfiles(Interface):
    """Marker interface for analysis profiles setup folder
    """


class IAnalysisCategory(Interface):
    """Marker interface for an Analysis Category
    """


class IAnalysisCategories(Interface):
    """Marker interface for Analysis Categories
    """


class IHaveAnalysisCategory(Interface):
    """Marker interface for objects that have AnalysisCategory(ies) assigned
    """

    def getCategory(self):
        """Returns the category(ies) assigned to this instance
        """

    def getCategoryUID(self):
        """Returns the UID of the category(ies) assigned to this instance
        """

    def getCategoryTitle(self):
        """Returns the title of the category(ies) assigned to this instance
        """


class IAttachmentType(Interface):
    """Marker interface for attachment type
    """


class IAttachmentTypes(Interface):
    """Marker interface for attachment types setup folder
    """


class ISampleContainers(Interface):
    """Marker interface for sample container setup folder
    """


class ISampleContainer(Interface):
    """Marker interface for sample containers
    """


class IDepartments(Interface):
    """Marker interface for departments setup folder
    """


class IDepartment(Interface):
    """Marker interface for departments
    """


class ISampleConditions(Interface):
    """Marker interface for sample conditions setup folder
    """


class ISampleCondition(Interface):
    """Marker interface for sample conditions
    """


class ISamplePoint(Interface):
    """Marker interface for sample points
    """


class ISamplePoints(Interface):
    """Marker interface for sample points setup folder
    """


class ISamplePreservations(Interface):
    """Marker interface for preservations setup folder
    """


class ISamplePreservation(Interface):
    """Marker interface for preservations
    """


class ISampleMatrices(Interface):
    """Marker interface for sample matrices setup folder
    """


class ISampleMatrix(Interface):
    """Marker interface for sample matrices
    """


class ISampleTemplates(Interface):
    """Marker interface for sample templates setup folder
    """


class ISampleTemplate(Interface):
    """Marker interface for sample template
    """


class ISubGroup(Interface):
    """Marker interface for subgroup
    """


class ISubGroups(Interface):
    """Marker interface for subgroups setup folder
    """


class ISamplingDeviation(Interface):
    """Sampling Deviation
    """


class ISamplingDeviations(Interface):
    """Sampling Deviations
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


class IInterpretationTemplates(Interface):
    """Marker interface for interpretation templates objects
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


class IManufacturers(Interface):
    """Marker interface for manufacturers container
    """


class IManufacturer(Interface):
    """Marker interface for manufacturers
    """


class IInstrumentType(Interface):
    """Marker interface for an instrument type
    """


class IInstrumentTypes(Interface):
    """Marker interface for instrument types
    """


class IInstrumentLocation(Interface):
    """Marker interface for a physical place, where instruments can be located
    """


class IInstrumentLocations(Interface):
    """Marker interface for instrument locations folder
    """


class IStorageLocations(Interface):
    """Marker interface for storage locations setup folder
    """


class IStorageLocation(Interface):
    """Marker interface for storage locations
    """


class IBatchLabel(Interface):
    """Marker interface for Batch Label
    """


class IBatchLabels(Interface):
    """Marker interface for Batch Labels container
    """


class ISupplier(Interface):
    """Marker interface for a Supplier
    """


class ISuppliers(Interface):
    """Marker interface for Suplliers
    """


class IASTMImporter(Interface):
    """Marker interface for ASTM Wrappers
    """

    def import_data(data):
        """Import the processed JSON data from the wrapper
        """


class IClientAwareMixin(Interface):
    """Marker interface for objects that can be bound to a Client, either
    because they can be added inside a Client folder or because it can be
    assigned through a Reference field
    """

    def getClient(self):
        """Returns the client this object is bound to, if any
        """

    def getClientUID(self):
        """Returns the client UID this object is bound to, if any
        """


class IContainerTypes(Interface):
    """Marker interface for container types setup folder
    """


class IContainerType(Interface):
    """Marker interface for container type
    """


class IDynamicAnalysisSpec(Interface):
    """Marker interface for Dynamic analysis spec item
    """


class IDynamicAnalysisSpecs(Interface):
    """Marker interface for Dynamic analysis specs folder
    """


class ILabProduct(Interface):
    """Marker interface for lab product
    """


class ILabProducts(Interface):
    """Marker interface for lab products folder
    """


class IHavePrice(Interface):
    """Marker interface for objects that have a Price
    """

    def getPrice(self):
        """Returns the price of the instance
        """

    def getTotalPrice(self):
        """Returns the total price of the instance
        """


class ISampleType(Interface):
    """Marker interface for Sample Type
    """


class ISampleTypes(Interface):
    """Marker interface for Sample Types container
    """


class IWorksheetTemplates(Interface):
    """Marker interface for Worksheet Templates
    """


class IWorksheetTemplate(Interface):
    """Marker interface for Worksheet Template
    """
