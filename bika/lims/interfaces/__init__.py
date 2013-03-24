from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface

class IBikaLIMS(Interface):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "bika" theme, this interface must be its layer
    """

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

class IAnalysisRequestQuery(Interface):
    """Analysis Request query collections"""

class IAnalysisRequestsFolder(Interface):
    """AnalysisRequests Folder"""

class IAnalysis(Interface):
    """Analysis"""

class IDuplicateAnalysis(Interface):
    """DuplicateAnalysis"""

class IReferenceAnalysis(Interface):
    """Reference Analyses """

class IReportFolder(Interface):
    """Report folder"""

class ISample(Interface):
    """Sample"""

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

class IQueryFolder(Interface):
    """Queries Folder"""

class IInvoice(Interface):
    """Invoice"""

class IInvoiceBatch(Interface):
    """Invoice Batch"""

class IInvoiceFolder(Interface):
    """Invoices Folder"""

class IHaveNoBreadCrumbs(Interface):
    """Items which do not display breadcrumbs"""

class IIdServer(Interface):
    """ Interface for ID server """
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type' """

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
class ISamplePoints(Interface):
    ""
class ISampleTypes(Interface):
    ""
class ISupplier(Interface):
    ""
class ISuppliers(Interface):
    ""
class IPreservations(Interface):
    ""
class IReferenceDefinitions(Interface):
    ""
class IWorksheetTemplates(Interface):
    ""

class IBikaCatalog(Interface):
    ""
class IBikaSetupCatalog(Interface):
    ""

class IDisplayListVocabulary(Interface):
    "Return a DisplayList"
    def __call__():
        ""
