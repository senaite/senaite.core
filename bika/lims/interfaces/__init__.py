# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import Interface


class IBikaLIMS(Interface):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "bika" theme, this interface must be its layer
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


class ISample(Interface):
    """Sample
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


class ISamplePartition(Interface):
    """Sample
    """


class ISamplesFolder(Interface):
    """Samples Folder
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


class IInvoiceBatch(Interface):
    """Invoice Batch
    """


class IInvoiceFolder(Interface):
    """Invoices Folder
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
    """Marker interface for identifier types
    """


class IHaveIdentifiers(Interface):
    """If this interface is provided by an AT object, the object will
    automatically be given an 'Identifiers' field, which will be associated
    with the bika_identifiertypes in site setup.
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


class ISamplingRoundTemplates(Interface):
    """Marker interface for Sampling Round Templates
    """


class ISamplingRoundTemplate(Interface):
    """Marker interface for a Sampling Round Template
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


class IBatchSearchableText(Interface):
    """Marker Interface for BatchSearchableText
    """

    def get_plain_text_fields(self):
        """Returns field names as a list of strings
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


class IARImportFolder(Interface):
    """Marker interface for a folder that contains ARImports
    """


class IARImport(Interface):
    """Marker interface for an ARImport
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


class IQualityControlReport(Interface):
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


class ISamplePrepWorkflow(Interface):
    """This flag enables the sample_prep workflow transitions to be inserted
    into an object's workflow chain.
    """


class ICustomPubPref(Interface):
    """Marker interface for CustomPubPref
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


class IAcquireFieldDefaults(Interface):
    """Register this adapter to define if and how the value for a field is
    acquired.

    An instance's schema fields may delegate the responsibility of providing
    default values to their acquisition parents by providing an attribute
    "acquire=True".

    During object creation this behaviour will walk up the acquisition chain
    looking for a matching field, and if one is found it's current value will
    be used as the default for this field.

    By default the acquisition chain is searched for a field named
    identically to the destination field, but this can be configured with an
    attribute "acquire_fieldname='FieldName'".

    If the source field is found on a parent but contains a False-ish value,
    or if the adapter otherwise returns None (this will be the case if the
    walker reaches the SiteRoot), the schema's original AT default is used.

    No attempt is made to type check the fields - the value of the parent
    field is simply injected into getDefaults().
    """

    def __call__(context, field):
        """This function must return the surrogate (source) value directly.
        """


class IProxyField(Interface):
    """A field that proxies transparently to the field of another object.
    Mainly needed for AnalysisRequest fields that are actually stored on the
    Sample.
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
