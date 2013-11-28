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


class IAnalysisProfiles(Interface):

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


class ISampleType(Interface):

    ""


class ISampleTypes(Interface):

    ""


class ISupplier(Interface):

    ""


class ISuppliers(Interface):
    ""
class ISupplyOrder(Interface):
    ""


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


class IWidgetVisibility(Interface):

    """Adapter to modify the default list of fields to show on each view.
    """

    def __call__():
        """Returns a dictionary, the keys are the keys of any field's
        "visibility" property dicts found in the schema, and the
        values are field names.
        """


class ISetupDataSetList(Interface):

    """Allow products to register distributed setup datasets (xlsx files).
    Each ISetupDataSetList adapter returns a list of values to be included in
    the load_setup_data view
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

