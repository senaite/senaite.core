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

from zope.interface import Interface


class ISenaiteSiteRoot(Interface):
    """Marker interface for the Senaite Site Root
    """


class IBikaLIMS(Interface):
    """Marker interface that defines a Zope 3 browser layer.

    N.B. Please use ISenaiteSite interface
    """


class ISenaiteSite(IBikaLIMS):
    """Marker interface for Zope 3 browser layers.
    """


class IAutoGenerateID(Interface):
    """Auto-generate ID with ID server
    """


class IMultiCatalogBehavior(Interface):
    """Support multiple catalogs for Dexterity contents
    """


class IActionHandlerPool(Interface):
    """Marker interface for the ActionHandlerPool utility
    """


class IAuditLog(Interface):
    """Marker interface for Audit Log
    """


class IAuditable(Interface):
    """Marker inteface for auditable contents
    """


class IDoNotSupportSnapshots(Interface):
    """Marker inteface for non-auditable contents
    """


class IAuditLogCatalog(Interface):
    """Audit Log Catalog
    """


class IGenerateID(Interface):
    """Marker Interface to generate an ID
    """


class IHaveNoBreadCrumbs(Interface):
    """Items which do not display breadcrumbs
    """


class IClientFolder(Interface):
    """Client folder
    """


class IClient(Interface):
    """Client
    """


class IBatchFolder(Interface):
    """Batch folder
    """


class IBatch(Interface):
    """Batch
    """


class IBatchLabels(Interface):
    """Batch label
    """


class IAnalysisRequest(Interface):
    """Analysis Request
    """


class IHaveDescendants(Interface):
    """Marker interface for objects that have Descendants
    """

    def getDescendants(self, all_descendants=False):
        """Returns descendants of this object
        :param all_descendants: if True, returns all descendants from hierarchy
        """


class IAnalysisRequestWithPartitions(IHaveDescendants):
    """Marker interface for Analysis Requests that have Partitions
    """


class IAnalysisRequestPartition(Interface):
    """Marker interface for Analysis Requests that are also Partitions
    """


class IAnalysisRequestRetest(Interface):
    """Marker interface for Analysis Requests that are Retests
    """


class IAnalysisRequestSecondary(Interface):
    """Marker interface for Secondary Analysis Requests
    """


class IAnalysisRequestAddView(Interface):
    """AR Add view
    """


class IAnalysisRequestsFolder(Interface):
    """AnalysisRequests Folder
    """


class IInvoiceView(Interface):
    """Invoice View
    """


class IAnalysis(Interface):
    """Analysis
    """


class IRoutineAnalysis(Interface):
    """This adapter distinguishes normal analyses from Duplicates, References,
    Rejections, etc.
    """


class IAnalysisSpec(Interface):
    """Analysis Specs
    """


class IDuplicateAnalysis(Interface):
    """DuplicateAnalysis
    """


class IReferenceAnalysis(Interface):
    """Reference Analyses
    """


class IRejectAnalysis(Interface):
    """This adapter distinguishes normal analyses from Duplicates, References,
    Rejections, etc.
    """


class IReportFolder(Interface):
    """Report folder
    """


class ISampleCondition(Interface):
    """Sample Condition
    """


class ISampleConditions(Interface):
    """Sample Conditions
    """


class ISampleMatrix(Interface):
    """Sample Matrix
    """


class ISampleMatrices(Interface):
    """Sample Matrices
    """


class ISamplingDeviation(Interface):
    """Sampling Deviation
    """


class ISamplingDeviations(Interface):
    """Sampling Deviations
    """


class IWorksheetFolder(Interface):
    """WorksheetFolder
    """


class IWorksheet(Interface):
    """Worksheet
    """


class IReferenceSample(Interface):
    """Reference Sample
    """


class IReferenceSamplesFolder(Interface):
    """Reference Samples Folder
    """


class IReportsFolder(Interface):
    """Reports Folder
    """


class IInvoice(Interface):
    """Invoice
    """


class IBikaSetup(Interface):
    """Marker interface for the LIMS Setup
    """


class IAnalysisCategory(Interface):
    """Marker interface for an Analysis Category
    """


class IAnalysisCategories(Interface):
    """Marker interface for Analysis Categories
    """


class IBaseAnalysis(Interface):
    """Marker interface for base Analysis
    """


class IAnalysisService(Interface):
    """Marker interface for Analysis Service
    """


class IAnalysisServices(Interface):
    """Marker interface for Analysis Services
    """


class IAttachmentTypes(Interface):
    """Marker interface for Attachment types
    """


class ICalculation(Interface):
    """Marker interface for a Calculation
    """


class ICalculations(Interface):
    """Marker interface for Calculations
    """


class IContacts(Interface):
    """Marker interface for Contacts
    """


class IContact(Interface):
    """Marker interface for a single Contact
    """


class IDepartments(Interface):
    """Marker interface for a Departments
    """


class IContainers(Interface):
    """Marker interface for Containers
    """


class IContainerTypes(Interface):
    """Marker interface for Container types
    """


class IIdentifierTypes(Interface):
    """TODO: Remove in senaite.core 1.3.3
    """


class IHaveIdentifiers(Interface):
    """TODO: Remove in senaite.core 1.3.3
    """


class IInstrument(Interface):
    """Marker interface for an Instrument
    """


class IInstruments(Interface):
    """Marker interface for Instruments
    """


class IInstrumentType(Interface):
    """Marker interface for an instrument type
    """


class IInstrumentTypes(Interface):
    """Marker interface for instrument types
    """


class IInstrumentLocation(Interface):
    """A physical place, where instruments can be located
    """


class IInstrumentLocations(Interface):
    """Physical places, where instruments can be located
    """


class IInstrumentCalibration(Interface):
    """Instrument Calibration
    """


class IInstrumentCertification(Interface):
    """Instrument Certification
    """


class IInstrumentValidation(Interface):
    """Instrument Validation
    """


class IAnalysisSpecs(Interface):
    """Marker interface for Analysis Specs
    """


class IDynamicResultsRange(Interface):
    """Marker interface for Dynamic Result Range
    """


class IAnalysisProfile(Interface):
    """Marker interface for an Analysis Profile
    """


class IAnalysisProfiles(Interface):
    """Marker interface for analysis profiles
    """


class IARTemplate(Interface):
    """Marker interface for an AR Template
    """


class IARTemplates(Interface):
    """Marker interface for AR templates
    """


class ILaboratory(Interface):
    """Marker interface for Laboratory
    """


class ILabContacts(Interface):
    """Marker interface for Lab contacts
    """


class ILabContact(Interface):
    """Marker interface for a lab contact
    """


class IManufacturer(Interface):
    """Marker interface for Manufacturer
    """


class IManufacturers(Interface):
    """Marker interface for Manufacturers
    """


class IMethods(Interface):
    """Marker interface for Methods
    """


class IMethod(Interface):
    """Marker interface for Method
    """


class IMultifile(Interface):
    """Marker interface for a Multifile
    """


class ILabProducts(Interface):
    """Marker interface for Lab Products
    """

class ILabProduct(Interface):
    """Marker interface for a LabProduct
    """

class ISamplePoint(Interface):
    """Marker interface for a Sample Point
    """


class ISamplePoints(Interface):
    """Marker interface for Sample Points
    """


class IStorageLocation(Interface):
    """Marker interface for a Storage Location
    """


class IStorageLocations(Interface):
    """Marker interface for Storage Location
    """


class ISampleType(Interface):
    """Marker interface for a Sample Type
    """


class ISampleTypes(Interface):
    """Marker interface for Sample Types
    """


class ISupplier(Interface):
    """Marker interface for a Supplier
    """


class ISuppliers(Interface):
    """Marker interface for Suplliers
    """


class ISupplyOrder(Interface):
    """Marker interface for a Supplier Order
    """


class ISupplyOrderFolder(Interface):
    """Marker interface for Supply Order Folder
    """


class ISubGroups(Interface):
    """Sub-groups configuration folder
    """


class ISubGroup(Interface):
    """Sub-Group
    """


class IPreservations(Interface):
    """Marker interface for Preservations
    """


class IReferenceDefinitions(Interface):
    """Marker interface for Reference Definitions
    """


class IWorksheetTemplates(Interface):
    """Marker interface for Worksheet Templates
    """

class IWorksheetTemplate(Interface):
    """Marker interface for Worksheet Template
    """

class IBikaCatalog(Interface):
    """Marker interface for bika_catalog
    """


class IBikaAnalysisCatalog(Interface):
    """Marker interface for bika_analysis_catalog
    """


class IBikaSetupCatalog(Interface):
    """Marker interface for bika_setup_catalog
    """


class IBikaCatalogAnalysisRequestListing(Interface):
    """Marker interface for bika_catalog_analysisrequest_listing
    """


class IBikaCatalogAutoImportLogsListing(Interface):
    """Marker interface for bika_catalog_autoimportlogs_listing
    """


class IBikaCatalogWorksheetListing(Interface):
    """Marker interface for bika_catalog_worksheet_listing
    """


class IBikaCatalogReport(Interface):
    """Marker interface for bika_catalog_report
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


class IReferenceWidgetVocabulary(Interface):
    """Return values for reference widgets in AR contexts
    """

    def __call__(**kwargs):
        """Call method
        """


class IDisplayListVocabulary(Interface):
    """Make vocabulary from catalog query.

    Return a DisplayList.
    kwargs are added to contentFilter.
    """

    def __call__(**kwargs):
        """Call method
        """


class IFieldIcons(Interface):
    """Used to signal an analysis result out of range alert
    """

    def __call__(self, result=None, **kwargs):
        """Returns a dictionary: with the keys 'field', 'icon', 'message'.

        If result is specified, it's checked instead of the database.  This
        is for form validations.

        Analysis range checkers can include a 'specification' in kwargs to
        override the spec derived from the context. It should be a dict
        w/ 'min', 'max', and 'error' keys.
        """


class IResultOutOfRange(Interface):
    """Any code which wants to check some condition and flag an Analysis as
    out of range, uses this interface
    """
    def __call(result=None):
        """The adapter must return a dictionary to indicate range out of bounds:
        {
         out_of_range: boolean - the result is out of bounds,
         acceptable: boolean - the result is in acceptable error margin,
         spec_values: dict - the min/max/error values for the failed spec
        }

        If the adapter returns a value that resolves to boolean False, the
        analysis is assumed not to have triggered the out of range conditions

        If a result is present in the request, it is passed here to be checked.
        if result is None, the value from the database is checked.

        """


class IATWidgetVisibility(Interface):
    """Adapter to modify the default list of fields to show on each view.

    Archetypes uses a widget attribute called 'visible' to decide which fields
    are editable or viewable in different contexts (view and edit).

    This adapter lets you create/use arbitrary keys in the field.widget.visible
    attribute, or or any other condition to decide if a particular field is
    displayed or not.

    an attribute named 'sort', if present, is an integer.
    It is used to allow some adapters to take preference over others.
    It's default is '1000', other lower values will take preference over higher
    values.
    """

    def __call__(widget, instance, mode, vis_dict, default=None, field=None):
        """Returns the visibility attribute for this particular field, in the
        current context.

        :arg field: the AT schema field object
        :arg mode: 'edit', 'view', or some custom mode, eg 'add', 'secondary'
        :arg vis_dict: the original schema value of field.widget.visible
        :arg default: value returned by the base Archetypes.Widget.isVisible

        In default Archetypes the value for the attribute on the field may
        either be a dict with a mapping for edit and view::

            visible = { 'edit' :'hidden', 'view': 'invisible' }

        Or a single value for all modes::

            True/1:  'visible'
            False/0: 'invisible'
            -1:      'hidden'

        visible: The field is shown in the view/edit screen
        invisible: The field is skipped when rendering the visVisibleiew/edit
                   screen
        hidden: The field is added as <input type="hidden" />
        The default state is 'visible'.

        The default rules are always applied, but any IATWidgetVisibility
        adapters found are called and permitted to modify the value.
        """


class ISetupDataSetList(Interface):
    """Allow products to register distributed setup datasets (xlsx files).

    Each ISetupDataSetList adapter returns a list of values to be included in
    the load_setup_data view
    """


class IJSONReadExtender(Interface):
    """This interface allows an adapter to modify an object's data before
    it is sent to the HTTP response.
    """

    def __call__(obj_data):
        """obj_data is the current python dictionary that will go to json.
        it should be modified in place, there is no need to return a value.
        """


class ISetupDataImporter(Interface):
    """ISetupDataImporter adapters are responsible for importing sections of
    the load_setup_data xlsx workbooks.
    """


class IPricelist(Interface):
    """Folder view marker for Pricelist
    """


class IPricelistFolder(Interface):
    """Folder view marker for PricelistFolder instance
    """


class IProductivityReport(Interface):
    """Reports are enumerated manually in reports/*.pt - but addional reports
    can be added to this list by extension packages using this adapter.

    The adapter must return a dictionary:

    {
     title: text (i18n translated),
     description: text (i18n translated),
     query_form: html <fieldset> of controls used to enter report
                 parameters (excluding <form> tags and <submit> button)
     module: The name of the module containing a class named "Report"
             an instance of this class will be used to create the report
    }
    """


class IAdministrationReport(Interface):
    """Reports are enumerated manually in reports/*.pt - but addional reports
    can be added to this list by extension packages using this adapter.

    The adapter must return a dictionary:

    {
     title: text (i18n translated),
     description: text (i18n translated),
     query_form: html <fieldset> of controls used to enter report
                 parameters (excluding <form> tags and <submit> button)
     module: The name of the module containing a class named "Report"
             an instance of this class will be used to create the report
    }
    """


class IHeaderTableFieldRenderer(Interface):
    """
    Allows an adapter to return the HTML content of the rendered field view,
    in header_table listings. The adapter must be registered with
    name=FieldName.

    If the field is a Reference, and the user has View permission on the
    target object, the field is rendered as <a href="absolute_url">Title</a>.

    If no adapter is found, and the field is not a reference, it is rendered
    with the normal AT field view machine.

    In a ZCML somewhere:

        <adapter
          for="bika.lims.interfaces.IAnalysisRequest"
          factory="package.module.spanner"
          provides="bika.lims.interfaces.IHeaderTableFieldRenderer"
          name="NameOfArchetypesField"
        />

    and the callable:

        class spanner:
            def __init__(self, context):
                self.context = context
            def __call__(self, field):
                field_content = field.get(self.context)
                return "<span>%"+field_content+"</span>"

    """

    def __call__(field):
        """
        Accepts an Archetypes Field, returns HTML.
        """


class IReflexRule(Interface):
    """Marker interface for a Reflex Rule
    """


class IReflexRuleFolder(Interface):
    """Marker interface for the Reflex Rule Folder
    """


class IDepartment(Interface):
    """Marker interface for a Department
    """


class IProxyField(Interface):
    """A field that proxies transparently to the field of another object.
    Mainly needed for AnalysisRequest fields that are actually stored on the
    Sample.
    """


class IRemarksField(Interface):
    """An append-only TextField which saves information about each edit
    """


class IARAnalysesField(Interface):
    """A field that manages AR Analyses
    """


class IFrontPageAdapter(Interface):
    """Front Page Url Finder Adapter's Interface
    """

    def get_front_page_url(self):
        """Get url of necessary front-page
        """


class INumberGenerator(Interface):
    """A utility to generates unique numbers by key
    """


class ITopRightHTMLComponentsHook(Interface):
    """Marker interface to hook html components in bikalisting
    """


class ITopLeftHTMLComponentsHook(Interface):
    """Marker interface to hook html components in bikalisting
    """


class ITopWideHTMLComponentsHook(Interface):
    """Marker interface to hook html components in bikalisting
    """


class IGetDefaultFieldValueARAddHook(Interface):
    """Marker interface to hook default
    """


class IGetStickerTemplates(Interface):
    """Marker interface to get stickers for a specific content type.

    An IGetStickerTemplates adapter should return a result with the
    following format:

    :return: [{'id': <template_id>,
             'title': <template_title>}, ...]
    """


class IARReport(Interface):
    """Marker interface for published AR Reports
    """


class ICancellable(Interface):
    """Marker for those objects that can be cancelled (have state "cancelled")
    """


class IDeactivable(Interface):
    """Marker for those objects that can be deactivated (have state "inactive")
    """


class IWorkflowActionAdapter(Interface):
    """Marker for adapters in charge of processing workflow action requests
    from views
    """


class IWorkflowActionUIDsAdapter(IWorkflowActionAdapter):
    """Marker for adapters in charge of processing workflow action requests
    from views, but meant for redirection only
    """


class IVerified(Interface):
    """Marker interface for verified objects
    """


class ISubmitted(Interface):
    """Marker interface for submitted objects
    """


class IReceived(Interface):
    """Marker interface for received objects
    """


class IInternalUse(Interface):
    """Marker interface for objects only lab personnel must have access
    """


class IDetachedPartition(Interface):
    """Marker interface for samples that have been detached from its primary
    """


class IGuardAdapter(Interface):
    """Marker interface for guard adapters
    """

    def guard(self, transition):
        """Return False if you want to block the transition
        """


class IAddSampleFieldsFlush(Interface):
    """Marker interface for field dependencies flush for Add Sample form
    """

    def get_flush_settings(self):
        """Returns a dict where the key is the name of the field and the value
        is an array dependencies as field names
        """


class IAddSampleObjectInfo(Interface):
    """Marker interface for objects metadata mapping
    """

    def get_object_info(self):
        """Returns the dict representation of the context object for its
        correct consumption by Sample Add form:

        {'id': <id_of_the_object>,
         'uid': <uid_of_the_object>,
         'title': <title_of_the_object>,
         'filter_queries': {
             <dependent_field_name>: {
                 <catalog_index>: <criteria>
             }
         },
         'field_values': {
             <dependent_field_name>: {
                <uid>: <dependent_uid>,
                <title>: <dependent_title>
            }
         }

        Besides the basic keys (id, uid, title), two additional keys can be
        provided:
        - filter_queries: contains the filter queries for other fields to be
          applied when the value of current field changes.
        - field_values: contains default values for other fields to be applied
          when the value of the current field changes.
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


class ISampleTypeAwareMixin(Interface):
    """Marker interface for objects that can be assigned to one, or multiple
    SampleType objects through a ReferenceField
    """

    def getSampleType(self):
        """Returns the sample type(s) assigned to this object, if any
        """

    def getSampleTypeUID(self):
        """Returns the UID(s) of the Sample Type(s) assigned to this object
        """

    def getSampleTypeTitle(self):
        """Returns the title or a comma separated list of sample type titles
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


class IHaveInstrument(Interface):
    """Marker interface for objects that have Instrument(s) assigned
    """

    def getInstrument(self):
        """Returns the instrument or instruments the instance is assigned to
        """


class IHaveDepartment(Interface):
    """Marker interface for objects that have Department(s) assigned
    """

    def getDepartment(self):
        """Returns the department or departments the instance is assigned to
        """


class IOrganisation(Interface):
    """Marker interface for IOrganisation object
    """

    def getName(self):
        """Returns the name of the organisation. Masks Title()
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


class IARImportFolder(Interface):
    """Marker interface for a folder that contains ARImports
    TODO: Legacy type. Remove after 1.3.3
    """


class IARImport(Interface):
    """Marker interface for an ARImport
    TODO: Legacy type. Remove after 1.3.3
    """


class ISamplingRoundTemplates(Interface):
    """Marker interface for Sampling Round Templates
    TODO: Legacy type. Remove after 1.3.3
    """


class ISamplingRoundTemplate(Interface):
    """Marker interface for a Sampling Round Template
    TODO: Legacy type. Remove after 1.3.3
    """


class IHideActionsMenu(Interface):
    """Marker interface that can be applied for conttents that should not
    display the content actions menu
    """
