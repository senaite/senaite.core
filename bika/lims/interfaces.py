from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface

class IBikaLIMS(Interface):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "bika" theme, this interface must be its layer
       (in lims/viewlets/configure.zcml).
    """

class IClientFolder(Interface):
    """Client folder"""

class IClient(Interface):
    """Client"""

class IAnalysisRequest(Interface):
    """Analysis Request"""

class ISample(Interface):
    """Sample"""

class IWorksheetFolder(Interface):
    """WorksheetFolder"""

class IWorksheet(Interface):
    """Worksheet"""

class IReferenceSupplierFolder(Interface):
    """WorksheetFolder"""

class IInvoiceFolder(Interface):
    """ReferenceSupplierFolder"""

class IHaveNoBreadCrumbs(Interface):
    """Items which do not display breadcrumbs"""

class IIdServer(Interface):
    """ Interface for ID server """
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type' """

class IBikaSettings(Interface):
    ""
class IAnalysisCategories(Interface):
    ""
class IAnalysisServices(Interface):
    ""
class IAttachmentTypes(Interface):
    ""
class ICalculations(Interface):
    ""
class IDepartments(Interface):
    ""
class IInstruments(Interface):
    ""
class IAnalysisSpecs(Interface):
    ""
class ILabARProfiles(Interface):
    ""
class ILabContacts(Interface):
    ""
class IMethods(Interface):
    ""
class ILabProducts(Interface):
    ""
class ISamplePoints(Interface):
    ""
class ISampleTypes(Interface):
    ""
class IReferenceManufacturers(Interface):
    ""
class IReferenceDefinitions(Interface):
    ""
class IWorksheetTemplates(Interface):
    ""
