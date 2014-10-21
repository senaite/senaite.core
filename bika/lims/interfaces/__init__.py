from zope.interface import Interface


class IBikaLIMS(Interface):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "bika" theme, this interface must be its layer
    """


class IHaveNoBreadCrumbs(Interface):
    """Items which do not display breadcrumbs"""


class IClientFolder(Interface):
    """Client folder"""


class IClient(Interface):
    """Client"""


class IBatchFolder(Interface):
    """Batch folder"""


class IBatch(Interface):
    """Batch"""


class IBatchLabels(Interface):
    """Batch label"""


class IAnalysisRequest(Interface):
    """Analysis Request"""


class IAnalysisRequestAddView(Interface):
    """ AR Add view """


class IAnalysisRequestsFolder(Interface):
    """AnalysisRequests Folder"""


class IInvoiceView(Interface):
    """Invoice View"""


class IAnalysis(Interface):
    """Analysis"""


class IRoutineAnalysis(Interface):
    """This adapter distinguishes normal analyses from Duplicates, References,
    Rejections, etc.
    """


class IAnalysisSpec(Interface):
    """Analysis Specs"""


class IDuplicateAnalysis(Interface):
    """DuplicateAnalysis"""


class IQueryFolder(Interface):
    """Queries Folder"""


class IQuery(Interface):
    """Query collection object"""


class IReferenceAnalysis(Interface):
    """Reference Analyses """


class IReportFolder(Interface):
    """Report folder"""


class ISample(Interface):
    """Sample"""


class ISampleCondition(Interface):
    """Sample Condition"""


class ISampleConditions(Interface):
    """Sample Conditions"""


class ISampleMatrix(Interface):
    """Sample Matrix"""


class ISampleMatrices(Interface):
    """Sample Matrices"""


class ISamplePartition(Interface):
    """Sample"""


class ISamplesFolder(Interface):
    """Samples Folder"""


class ISamplingDeviation(Interface):
    """Sampling Deviation"""


class ISamplingDeviations(Interface):
    """Sampling Deviations"""


class IWorksheetFolder(Interface):
    """WorksheetFolder"""


class IWorksheet(Interface):
    """Worksheet"""


class IReferenceSample(Interface):
    """Reference Sample"""


class IReferenceSamplesFolder(Interface):
    """Reference Samples Folder"""


class IReportsFolder(Interface):
    """Reports Folder"""


class IInvoice(Interface):
    """Invoice"""


class IInvoiceBatch(Interface):
    """Invoice Batch"""


class IInvoiceFolder(Interface):
    """Invoices Folder"""


class IBikaSetup(Interface):
    ""


class IAnalysisCategory(Interface):
    ""


class IAnalysisCategories(Interface):
    ""


class IAnalysisService(Interface):
    ""


class IAnalysisServices(Interface):
    ""


class IAttachmentTypes(Interface):
    ""


class ICalculation(Interface):
    ""


class ICalculations(Interface):
    ""


class IContacts(Interface):
    ""


class IContact(Interface):
    ""


class IDepartments(Interface):
    ""


class IContainers(Interface):
    ""


class IContainerTypes(Interface):
    ""


class IInstrument(Interface):
    ""


class IInstruments(Interface):
    ""


class IInstrumentType(Interface):
    ""


class IInstrumentTypes(Interface):
    ""


class IAnalysisSpecs(Interface):
    ""


class IAnalysisProfile(Interface):
    ""


class IAnalysisProfiles(Interface):
    ""


class IARTemplate(Interface):
    ""


class IARTemplates(Interface):
    ""


class ILabContacts(Interface):
    ""


class ILabContact(Interface):
    ""


class IManufacturer(Interface):
    ""


class IManufacturers(Interface):
    ""


class IMethods(Interface):
    ""


class ILabProducts(Interface):
    ""


class ISamplePoint(Interface):
    ""


class ISamplePoints(Interface):
    ""


class IStorageLocation(Interface):
    ""


class IStorageLocations(Interface):
    ""


class ISampleType(Interface):
    ""


class ISampleTypes(Interface):
    ""


class ISRTemplates(Interface):
    ""


class ISupplier(Interface):
    ""


class ISuppliers(Interface):
    ""


class ISupplyOrder(Interface):
    ""


class ISupplyOrderFolder(Interface):
    ""


class ISubGroups(Interface):
    """Sub-groups configuration folder"""


class ISubGroup(Interface):
    """Sub-Group"""


class IPreservations(Interface):
    ""


class IReferenceDefinitions(Interface):
    ""


class IWorksheetTemplates(Interface):
    ""


class IBikaCatalog(Interface):
    "Marker interface for custom catalog"


class IBikaAnalysisCatalog(Interface):
    "Marker interface for custom catalog"


class IBikaSetupCatalog(Interface):
    "Marker interface for custom catalog"


class IIdServer(Interface):
    """ Interface for ID server """

    def generate_id(self, portal_type, batch_size=None):
        """ Generate a new id for 'portal_type' """


class IReferenceWidgetVocabulary(Interface):
    """Return values for reference widgets in AR contexts
    """

    def __call__(**kwargs):
        """
        """


class IDisplayListVocabulary(Interface):
    """Make vocabulary from catalog query.
    Return a DisplayList.
    kwargs are added to contentFilter.
    """

    def __call__(**kwargs):
        """
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
         spec_values: dict - the min/max/error values for the failed specification
        }

        If the adapter returns a value that resolves to boolean False, the
        analysis is assumed not to have triggered the out of range conditions

        If a result is present in the request, it is passed here to be checked.
        if result is None, the value from the database is checked.

        """


class IATWidgetVisibility(Interface):
    """Adapter to modify the default list of fields to show on each view.

    Archetypes uses a widget attribute called 'visible' to decide which
    fields are editable or viewable in different contexts (view and edit).

    This adapter lets you create/use arbitrary keys in the field.widget.visible
    attribute, or or any other condition to decide if a particular field is
    displayed or not.

    an attribute named 'sort', if present, is an integer.  It is used
    to allow some adapters to take preference over others.  It's default is '1000',
    other lower values will take preference over higher values.

    """

    def __call__(widget, instance, mode, vis_dict, default=None, field=None):
        """Returns the visibility attribute for this particular field, in the
        current context.

        :arg field: the AT schema field object
        :arg mode: 'edit', 'view', or some custom mode, eg 'add', 'secondary'
        :arg vis_dict: the original schema value of field.widget.visible
        :arg default: the value returned by the base Archetypes.Widget.isVisible

        In default Archetypes the value for the attribute on the field may either
        be a dict with a mapping for edit and view::

            visible = { 'edit' :'hidden', 'view': 'invisible' }

        Or a single value for all modes::

            True/1:  'visible'
            False/0: 'invisible'
            -1:      'hidden'

        visible: The field is shown in the view/edit screen
        invisible: The field is skipped when rendering the visVisibleiew/edit screen
        hidden: The field is added as <input type="hidden" />
        The default state is 'visible'.

        The default rules are always applied, but any IATWidgetVisibility adapters
        found are called and permitted to modify the value.

        """


class IAcquireFieldDefaults(Interface):
    """Register this adapter to define if and how the value for a field is acquired.

    The fields of an AT object which provides this interface, may make use of
    the "acquire" field attribute to request that their default value be calculated
    from a matching field in an acquisition parent.

        acquire=False,

	If attribute is not specified or the value is False, no action is taken.

	If value is True, then the object's ancestry is searched for a matching field,
	who's value is returned.

	If the value is a dictionary, then the bahaviour can be changed with these
	key:value pairs:

		'fieldname': string.
			The name of the field on the parent.
			Default=same fieldname as this field.

    """

    def __call__(context, field):
        """This function must return the surrogate field value directly.
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
    "Marker interface for a folder that can list ARImports"


class IARImport(Interface):
    "Marker interface for an ARImport"


class IARImportItem(Interface):
    "Marker interface for an ARImport"


class IPricelist(Interface):
    "Folder view marker for Pricelist"


class IPricelistFolder(Interface):
    "Folder view marker for PricelistFolder instance"


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


class IARPriorities(Interface):
    "Marker interface for a folder that lists ARPriority's"


class IARPriority(Interface):
    "Marker interface for an ARPriority"


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
