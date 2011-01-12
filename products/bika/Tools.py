import sys
import os
import urllib
from App.class_init import InitializeClass
from Acquisition import ImplicitAcquisitionWrapper as iaw
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import permissions
#from Products.CMFPlone import transaction_note
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.config import REFERENCE_CATALOG
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Products.bika.config import ManageAnalysisRequest
from DateTime import DateTime

class ToolFolder(UniqueObject, Folder):
    """ Tool Folder """

    security = ClassSecurityInfo()
    id = 'tool_folder'
    managed_portal_type = ''
    listing_schema = BaseSchema
    default_template = 'tool_contents'

    def index_html(self, REQUEST, RESPONSE):
        """ return tool_contents template """
        template = getattr(self, self.default_template)
        return template(REQUEST = RESPONSE, RESPONSE = REQUEST) 

    security.declareProtected(permissions.AddPortalContent, 'invokeFactory')
    def invokeFactory(self
                     , type_name
                     , id
                     , RESPONSE = None
                     , *args
                     , **kw
                     ):
        '''Invokes the portal_types tool.'''
        pt = getToolByName(self, 'portal_types')
        myType = pt.getTypeInfo(self)
        args = (type_name, self, id, RESPONSE) + args
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = id
        return new_id

    security.declarePublic('getListingSchema')
    def getListingSchema(self):
        """ return listed fields """
        schema = iaw(self.listing_schema, self)
        return schema

InitializeClass(ToolFolder)


######################################################################
# ServicesTool
######################################################################

class ServicesTool(ToolFolder):
    """ Container for analysis services """

    security = ClassSecurityInfo()
    id = 'bika_services'
    title = 'Analysis services'
    description = 'Setup the services we offer our clients.'
    meta_type = 'Bika Services Tool'
    managed_portal_type = 'AnalysisService'
    listing_schema = None 
    default_template = 'analysisservices' 

InitializeClass(ServicesTool)


######################################################################
# LabSpecsTool
######################################################################

class LabSpecsTool(ToolFolder):
    """ Container for lab analysis specifications """

    security = ClassSecurityInfo()
    id = 'bika_analysisspecs'
    title = 'Lab analysis specifications'
    description = 'Set up the laboratory analysis service results specifications'
    meta_type = 'Bika Analysis Specs Tool'
    managed_portal_type = 'LabAnalysisSpec'
    listing_schema = None 
    default_template = 'labanalysisspecs' 

InitializeClass(LabSpecsTool)

######################################################################
# LabProfilesTool
######################################################################

from Products.bika.LabARProfile import schema as labprofiles_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'ProfileKey')
labprofiles_listing = make_listing_from_schema(labprofiles_schema, columns)

class LabProfilesTool(ToolFolder):
    """ Container for lab analysis profiles """

    security = ClassSecurityInfo()
    id = 'bika_arprofiles'
    title = 'Lab analysis profiles'
    description = 'Setup the analysis request profiles.'
    meta_type = 'Bika Analysis Profiles Tool'
    managed_portal_type = 'LabARProfile'
    listing_schema = labprofiles_listing 

InitializeClass(LabProfilesTool)


######################################################################
# ProductsTool
######################################################################

from Products.bika.LabProduct import schema as product_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'Volume', 'Unit', 'Price', 'VATAmount', 'TotalPrice')
product_listing = make_listing_from_schema(
    product_schema, columns
)

class ProductsTool(ToolFolder):
    """ Container for lab products """

    security = ClassSecurityInfo()
    id = 'bika_products'
    title = 'Lab products'
    description = 'Setup the products sold to our clients.'
    meta_type = 'Bika Products Tool'
    managed_portal_type = 'LabProduct'
    listing_schema = product_listing 

InitializeClass(ProductsTool)

######################################################################
# MethodsTool
######################################################################

from Products.bika.Method import schema as method_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title')
method_listing = make_listing_from_schema(
    method_schema, columns
)

class MethodsTool(ToolFolder):
    """ Container for lab methods """

    security = ClassSecurityInfo()
    id = 'bika_methods'
    title = 'Lab methods'
    description = 'Setup the methods used in the lab.'
    meta_type = 'Bika Methods Tool'
    managed_portal_type = 'Method'
    listing_schema = method_listing 

InitializeClass(MethodsTool)

######################################################################
# InstrumentsTool
######################################################################

from Products.bika.Instrument import schema as instrument_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'Type', 'Brand', 'Model', 'ExpiryDate')
instrument_listing = make_listing_from_schema(
    instrument_schema, columns
)

class InstrumentsTool(ToolFolder):
    """ Container for lab instruments """

    security = ClassSecurityInfo()
    id = 'bika_instruments'
    title = 'Lab instruments'
    description = 'Setup the instruments used in the lab.'
    meta_type = 'Bika Instruments Tool'
    managed_portal_type = 'Instrument'
    listing_schema = instrument_listing 

InitializeClass(InstrumentsTool)


######################################################################
# ClientStatusTool
######################################################################

from Products.bika.ClientStatus import schema as status_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title',)
status_listing = make_listing_from_schema(
    status_schema, columns
)

class ClientStatusTool(ToolFolder):
    """ Container for client status"""

    security = ClassSecurityInfo()
    id = 'bika_client_status'
    title = 'Client status'
    description = ''
    meta_type = 'Bika Client Status Tool'
    managed_portal_type = 'ClientStatus'
    listing_schema = status_listing 

InitializeClass(ClientStatusTool)


######################################################################
# ClientCategoriesTool
######################################################################

from Products.bika.ClientCategory import schema as category_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title',)
category_listing = make_listing_from_schema(
    category_schema, columns
)

class ClientCategoriesTool(ToolFolder):
    """ Container for client categories"""

    security = ClassSecurityInfo()
    id = 'bika_client_categories'
    title = 'Client categories'
    description = ''
    meta_type = 'Bika Client Categories Tool'
    managed_portal_type = 'ClientCategory'
    listing_schema = category_listing 

InitializeClass(ClientCategoriesTool)


######################################################################
# PublicationPreferenceTool
######################################################################

from Products.bika.ClientPublicationPreference import schema as \
    pubpref_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title',)
pubpref_listing = make_listing_from_schema(
    pubpref_schema, columns
)

class PublicationPreferenceTool(ToolFolder):
    """ Container for client publication preferences """

    security = ClassSecurityInfo()
    id = 'bika_publication_prefs'
    title = 'Publication preferences'
    description = ''
    meta_type = 'Bika Publication Preferences Tool'
    managed_portal_type = 'ClientPublicationPreference'
    listing_schema = pubpref_listing 

InitializeClass(PublicationPreferenceTool)


######################################################################
# InvoicePreferenceTool
######################################################################

from Products.bika.ClientInvoicePreference import schema as \
    invoicepref_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title',)
invoicepref_listing = make_listing_from_schema(
    invoicepref_schema, columns
)

class InvoicePreferenceTool(ToolFolder):
    """ Container for client invoice preferences """

    security = ClassSecurityInfo()
    id = 'bika_invoice_prefs'
    title = 'Invoice preferences'
    description = ''
    meta_type = 'Bika Invoice Preferences Tool'
    managed_portal_type = 'ClientInvoicePreference'
    listing_schema = invoicepref_listing 

InitializeClass(InvoicePreferenceTool)


######################################################################
# SampleTypesTool
######################################################################

from Products.bika.SampleType import schema as \
    sampletype_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'SampleTypeDescription')
sampletype_listing = make_listing_from_schema(
    sampletype_schema, columns
)

class SampleTypesTool(ToolFolder):
    """ Container for sample types """

    security = ClassSecurityInfo()
    id = 'bika_sampletypes'
    title = 'Sample Types'
    description = ''
    meta_type = 'Bika Sample Types Tool'
    managed_portal_type = 'SampleType'
    listing_schema = sampletype_listing 

InitializeClass(SampleTypesTool)


######################################################################
# StandardManufacturersTool
######################################################################

from Products.bika.StandardManufacturer import schema as \
    standardmanufacturer_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'StandardManufacturerDescription')
standardmanufacturer_listing = make_listing_from_schema(
    standardmanufacturer_schema, columns
)

class StandardManufacturersTool(ToolFolder):
    """ Container for standard manufacturers """

    security = ClassSecurityInfo()
    id = 'bika_standardmanufacturers'
    title = 'Standard Manufacturers'
    description = ''
    meta_type = 'Bika Standard Manufacturers Tool'
    managed_portal_type = 'StandardManufacturer'
    listing_schema = standardmanufacturer_listing 

InitializeClass(StandardManufacturersTool)

######################################################################
# StandardStocksTool
######################################################################

class StandardStocksTool(ToolFolder):
    """ Container for standard stocks """

    security = ClassSecurityInfo()
    id = 'bika_standardstocks'
    title = 'Standard Stocks'
    description = ''
    meta_type = 'Bika Standard Stocks Tool'
    managed_portal_type = 'StandardStock'
    listing_schema = None 
    default_template = 'standardstocks' 

InitializeClass(StandardStocksTool)

######################################################################
# SamplePointsTool
######################################################################

from Products.bika.SamplePoint import schema as \
    samplepoint_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'SamplePointDescription')
samplepoint_listing = make_listing_from_schema(
    samplepoint_schema, columns
)

class SamplePointsTool(ToolFolder):
    """ Container for sample points """

    security = ClassSecurityInfo()
    id = 'bika_samplepoints'
    title = 'Sample Points'
    description = ''
    meta_type = 'Bika Sample Points Tool'
    managed_portal_type = 'SamplePoint'
    listing_schema = samplepoint_listing 

InitializeClass(SamplePointsTool)

######################################################################
# WorksheetTemplatesTool
######################################################################

from Products.bika.WorksheetTemplate import schema as \
    worksheettemplate_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'WorksheetTemplateDescription')
worksheettemplate_listing = make_listing_from_schema(
    worksheettemplate_schema, columns
)

class WorksheetTemplatesTool(ToolFolder):
    """ Container for worksheet templates """

    security = ClassSecurityInfo()
    id = 'bika_worksheettemplates'
    title = 'Worksheet Templates'
    description = ''
    meta_type = 'Bika Worksheet Templates Tool'
    managed_portal_type = 'WorksheetTemplate'
    listing_schema = worksheettemplate_listing 

InitializeClass(WorksheetTemplatesTool)



######################################################################
# LabInfoTool
######################################################################

class LabInfoTool(ToolFolder):
    """ Container for laboratory """

    security = ClassSecurityInfo()
    id = 'bika_labinfo'
    title = 'Laboratory information'
    description = 'Laboratory information includes the name of the laboratory, contact numbers, physical and postal address, email address and the laboratory personnel and their contact details'
    meta_type = 'Bika Laboratory Information Tool'
    managed_portal_type = 'Laboratory'
    listing_schema = None 
    default_template = 'tool_labinfo_view'
    # XXX: Temporary workaround to enable importing of exported bika
    # instance. If '__replaceable__' is not set we get BadRequest, The
    # id is invalid - it is already in use.

    __replaceable__ = 1

    def manage_afterAdd(self, item, container):
        """ Add laboratory """
        self.invokeFactory(id = 'laboratory', type_name = 'Laboratory')


InitializeClass(LabInfoTool)

######################################################################
# AttachmentTypesTool
######################################################################

from Products.bika.AttachmentType import schema as attachmenttype_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'AttachmentTypeDescription')
attachmenttype_listing = make_listing_from_schema(attachmenttype_schema, columns)

class AttachmentTypesTool(ToolFolder):
    """ Container for departments"""

    security = ClassSecurityInfo()
    id = 'bika_attachmenttypes'
    title = 'Attachment types'
    description = 'Setup the attachment types'
    meta_type = 'Bika Attachment Types Tool'
    managed_portal_type = 'AttachmentType'
    listing_schema = attachmenttype_listing 

InitializeClass(AttachmentTypesTool)

######################################################################
# CalcTypesTool
######################################################################

from Products.bika.CalculationType import schema as calctype_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'CalculationTypeDescription')
calctype_listing = make_listing_from_schema(calctype_schema, columns)

class CalcTypesTool(ToolFolder):
    """ Container for departments"""

    security = ClassSecurityInfo()
    id = 'bika_calctypes'
    title = 'Calculation types'
    description = 'Setup the calculation types used for analyses'
    meta_type = 'Bika Calculation Types Tool'
    managed_portal_type = 'CalculationType'
    listing_schema = calctype_listing 

InitializeClass(CalcTypesTool)

######################################################################
# CategoriesTool
######################################################################

from Products.bika.AnalysisCategory import schema as category_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title',)
category_listing = make_listing_from_schema(category_schema, columns)

class CategoriesTool(ToolFolder):
    """ Container for analysis categories"""

    security = ClassSecurityInfo()
    id = 'bika_categories'
    title = 'Analysis Categories'
    description = 'Setup the categories for the analysis services'
    meta_type = 'Bika categories Tool'
    managed_portal_type = 'AnalysisCategory'
    listing_schema = category_listing 

InitializeClass(CategoriesTool)

######################################################################
# DepartmentsTool
######################################################################

from Products.bika.Department import schema as department_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'ManagerName')
department_listing = make_listing_from_schema(department_schema, columns)

class DepartmentsTool(ToolFolder):
    """ Container for departments"""

    security = ClassSecurityInfo()
    id = 'bika_departments'
    title = 'Lab departments'
    description = 'Setup the departments in the laboratory.'
    meta_type = 'Bika Departments Tool'
    managed_portal_type = 'Department'
    listing_schema = department_listing 

InitializeClass(DepartmentsTool)

######################################################################
# LabContactsTool
######################################################################

from Products.bika.LabContact import schema as labcontact_schema
from Products.bika.utils import make_listing_from_schema
columns = ('title', 'BusinessPhone', 'MobilePhone', 'EmailAddress')
labcontact_listing = make_listing_from_schema(labcontact_schema, columns)

class LabContactsTool(ToolFolder):
    """ Container for departments"""

    security = ClassSecurityInfo()
    id = 'bika_labcontacts'
    title = 'Lab contacts'
    description = 'Setup the laboratory contacts.'
    meta_type = 'Bika Lab Contacts Tool'
    managed_portal_type = 'LabContact'
    listing_schema = labcontact_listing 

InitializeClass(LabContactsTool)

######################################################################
# SettingsTool
######################################################################

class SettingsTool(ToolFolder):
    """ Container for bika settings """

    security = ClassSecurityInfo()
    id = 'bika_settings'
    title = 'Bika Settings'
    description = 'Configure password lifetime, auto log-off, VAT % and system prefixes.'
    meta_type = 'Bika Settings Tool'
    managed_portal_type = 'Laboratory'
    listing_schema = None 
    default_template = 'tool_settings_view'

    def manage_afterAdd(self, item, container):
        """ Add BikaSettings """
        self.invokeFactory(id = 'settings', type_name = 'BikaSettings')
        self.settings.setTitle('Bika settings')
        self.settings.setPrefixes([
            {'portal_type': 'AnalysisRequest',
             'prefix': 'AR-',
             'padding': '2',
            },
            {'portal_type': 'Sample',
             'prefix': 'S-',
             'padding': '5',
            },
            {'portal_type': 'Worksheet',
             'prefix': 'WS-',
             'padding': '5',
            },
            {'portal_type': 'Order',
             'prefix': 'O-',
             'padding': '4',
            },
            {'portal_type': 'Invoice',
             'prefix': 'I-',
             'padding': '4',
            },
            {'portal_type': 'ARImport',
             'prefix': 'B-',
             'padding': '4',
            },
            {'portal_type': 'StandardSample',
             'prefix': 'SS-',
             'padding': '4',
            },
            {'portal_type': 'StandardAnalysis',
             'prefix': 'SA-',
             'padding': '4',
            },
        ])


InitializeClass(SettingsTool)

######################################################################
# IDTool
######################################################################

class IDServerUnavailable(Exception):
    pass

class IDTool(UniqueObject, SimpleItem):
    """ Portal ID Tool """

    security = ClassSecurityInfo()
    id = 'portal_ids'
    title = 'Portal Ids'
    description = 'Generates IDs for objects'
    meta_type = 'Portal ID Tool'
    listing_schema = None 
    default_template = 'tool_settings_view'

    security.declareProtected(permissions.View,
                              'generate_id')
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type'
        """
        if portal_type == 'News Item':
            portal_type = 'NewsItem'
        idserver_url = os.environ.get('IDServerURL')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_id = portal.getId()
        try:
            if batch_size:
                # GET
                f = urllib.urlopen('%s/%s%s?%s' % (
                        idserver_url,
                        portal_id,
                        portal_type,
                        urllib.urlencode({'batch_size': batch_size}))
                        )
            else:
                f = urllib.urlopen('%s/%s%s' % (
                    idserver_url, portal_id, portal_type
                    )
                )
            id = f.read()
            f.close()
        except:
            from sys import exc_info
            info = exc_info()
            import zLOG; zLOG.LOG('INFO', 0, '', 'generate_id raised exception: %s, %s \n idserver_url: %s' % (info[0], info[1], idserver_url))
            raise IDServerUnavailable('ID Server unavailable')
        return id

InitializeClass(IDTool)

######################################################################
# InstrumentImportTool
######################################################################

class InstrumentImportTool(UniqueObject, SimpleItem):
    """ InstrumentImportTool """

    security = ClassSecurityInfo()
    id = 'instrument_import_tool'
    title = 'Instrument Import Tool'
    description = 'Imports Instrument Data.'
    meta_type = 'Instrument Import Tool'

    security.declareProtected(ManageAnalysisRequest, 'import_file')
    def import_file(self, csvfile):
        import csv
        wf_tool = getToolByName(self, 'portal_workflow')
        prefixes = self.bika_settings.settings.getPrefixes()
        ws_prefix = 'WS-'
        for d in prefixes:
            if d['portal_type'] == 'Worksheet': 
                ws_prefix = d['prefix']
                break

        updateable_states = ['sample_received', 'assigned', 'open']
        reader = csv.reader(csvfile)
        samples = []
        batch_headers = None
        for row in reader:
            if not row: continue
            # a new batch starts
            if row[0] == 'Sample Id':
                headers = ['SampleID'] + row[5:]
                batch_headers = [x.strip() for x in headers]
                continue

            if not batch_headers: continue

            r = dict(zip(batch_headers, [row[0].strip()] + row[5:]))
            samples.append(r)

        results = {}
        ids = []
        map = self.getInstrumentKeywordToServiceIdMap()
        for sample in samples:
            sample_id = sample['SampleID']
            ids.append(sample_id)
            results[sample_id] = {}
            results[sample_id]['analyses'] = []
            results[sample_id]['errors'] = []
            results[sample_id]['added'] = []
            worksheet = False
            if sample_id[0:3] == ws_prefix:
                worksheet = True
                ws_id = sample_id.split('/')[0]
                pos = sample_id.split('/')[1]
            if worksheet:   # this is a worksheet 
                r = self.portal_catalog(portal_type = 'Worksheet',
                    id = ws_id)
                if len(r) == 0:
                    results[sample_id]['errors'].append('Not found')
                    continue
                ws = r[0].getObject()
                ws_state = wf_tool.getInfoFor(ws, 'review_state', '')
                if (ws_state not in updateable_states):
                    results[sample_id]['errors'].append('Worksheet in %s status '
                               '- not updated' % (ws_state))
                    continue
                these_analyses = ws.getPosAnalyses(pos)
                ws_analyses = {}
                for analysis in these_analyses:
                    ws_analyses[analysis.getService().getId()] = analysis
                these_service_ids = ws_analyses.keys()
            else:          # Analysis Request
                r = self.portal_catalog(portal_type = 'AnalysisRequest',
                    id = sample_id)
                if len(r) == 0:
                    results[sample_id]['errors'].append('Not found')
                    continue
                ar = r[0].getObject()
                ar_state = wf_tool.getInfoFor(ar, 'review_state', '')
                if (ar_state not in updateable_states):
                    results[sample_id]['errors'].append('Analysis request in %s status '
                               '- not updated' % (ar_state))
                    continue
                these_service_ids = ar.objectIds()

            for keyword, result in sample.items():
                if result == '':
                    continue
                if keyword == 'SampleID':
                    continue
                if map.has_key(keyword):
                    service_id = map[keyword]
                else:
                    results[sample_id]['errors'].append('Instrument keyword %s not found' % (keyword))
                    continue

                service = self.bika_services._getOb(service_id)
                service_title = service.Title()
                analysis = None
                if service_id in these_service_ids:
                    if worksheet:
                        analysis = ws_analyses[service_id]
                    else:
                        analysis = ar._getOb(service_id)
                    as_state = wf_tool.getInfoFor(analysis, 'review_state', '')
                    if (as_state in ['assigned']):
                        if (analysis.getResult() is None) or (analysis.getResult() == ''):
                            pass
                        else: 
                            results[sample_id]['errors'].append('%s has a result - not updated' % (service_title))
                            continue
                        
                         
                    if (as_state not in updateable_states):
                        results[sample_id]['errors'].append('%s in %s status ' 
                                   '- not updated' % (service_title, as_state))
                        continue
                    results[sample_id]['analyses'].append(service_title)
                else:
                    if worksheet:
                        # this is an error
                        results[sample_id]['errors'].append('%s not found' % (service_title))

                    else:
                        # create the analysis and set its status to 'not
                        # requested'
                        ar.invokeFactory(
                            id = service.id, type_name = 'Analysis')
                        analysis = ar._getOb(service_id)
                        discount = ar.getMemberDiscount()
                        if ar.getMemberDiscountApplies():
                            price = service.getDiscountedPrice()
                            totalprice = service.getTotalDiscountedPrice()
                        else:
                            price = service.getPrice()
                            totalprice = service.getTotalPrice()

                        analysis.edit(
                            Service = service,
                            Price = price,
                            Discount = discount,
                            VAT = service.getVAT(),
                            TotalPrice = totalprice,
                            Unit = service.getUnit(),
                        )
                        self.REQUEST.set('suppress_escalation', 1)
                        wf_tool.doActionFor(analysis, 'import')
                        del self.REQUEST.other['suppress_escalation']
                        results[sample_id]['added'].append('%s' % (service_title))

                if analysis:
                    analysis.setUncertainty(self.get_uncertainty(result, service))
                    analysis.setResult(result)
                    # set dummy titration values if required
                    if analysis.getCalcType() == 't':
                        analysis.setTitrationVolume(result)
                        analysis.setTitrationFactor('1')

        results_ids = {}
        results_ids['results'] = results
        results_ids['ids'] = ids
        return results_ids

    def getInstrumentKeywordToServiceIdMap(self):
        d = {}
        for p in self.portal_catalog(
                portal_type = 'AnalysisService'):
            obj = p.getObject()
            keyword = obj.getInstrumentKeyword()
            if keyword:
                d[keyword] = obj.getId()
        return d


InitializeClass(InstrumentImportTool)
######################################################################
# ARImportTool
######################################################################

class ARImportTool(UniqueObject, SimpleItem):
    """ ARImportTool """

    security = ClassSecurityInfo()
    id = 'ar_import_tool'
    title = 'AR Import Tool'
    description = 'Imports Analysis Request Data.'
    meta_type = 'AR Import Tool'

    security.declareProtected(ManageAnalysisRequest, 'import_file')
    def import_file(self, csvfile, filename, client_id, state):
        import csv
        slash = filename.rfind('\\')
        full_name = filename[slash + 1:]
        ext = full_name.rfind('.')
        if ext == -1:
            actual_name = full_name
        else:
            actual_name = full_name[:ext]
        log = []
        r = self.portal_catalog(portal_type = 'Client', id = client_id)
        if len(r) == 0:
            log.append('   Could not find Client %s' % client_id)
            return '\n'.join(log)
        client = r[0].getObject()
        wf_tool = getToolByName(self, 'portal_workflow')
        updateable_states = ['sample_received', 'assigned']
        reader = csv.reader(csvfile)
        samples = []
        sample_headers = None
        batch_headers = None
        row_count = 0
        sample_count = 0
        batch_remarks = []

        for row in reader:
            row_count = row_count + 1
            if not row: continue
            # a new batch starts
            if row_count == 1:
                if row[0] == 'Header':
                    continue
                else:
                    msg = '%s invalid batch header' % row
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)
            if row_count == 2:
                msg = None
                if row[1] != 'Import':
                    msg = 'Invalid batch header - Import required in cell B2'
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)
                full_name = row[2]
                ext = full_name.rfind('.')
                if ext == -1:
                    entered_name = full_name
                else:
                    entered_name = full_name[:ext]
                if entered_name.lower() != actual_name.lower():
                    msg = 'Actual filename, %s, does not match entered filename, %s' % (actual_name, row[2])
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)
                
                batch_headers = row[0:]
                arimport_id = self.generateUniqueId('ARImport')
                client.invokeFactory(id = arimport_id, type_name = 'ARImport')
                arimport = client._getOb(arimport_id)
                continue
            if row_count == 3:
                sample_count = sample_count + 1
                sample_headers = row[9:]
                continue
            if row_count == 4:
                continue
            if row_count == 5:
                continue
            if row_count == 6:
                continue

            samples.append(row)
        
        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request import">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Validating...">')
        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(samples))

        row_count = 0
        next_id = self.generateUniqueId('ARImportItem', batch_size = len(samples))
        (prefix, next_num) = next_id.split('_')
        next_num = int(next_num)
        for sample in samples:
            row_count = row_count + 1
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)
            item_remarks = []
            analyses = []
            for i in range(9, len(sample)):
                if sample[i] != '1':
                    continue
                analyses.append(sample_headers[(i - 9)])
            if len(analyses) > 0:
                aritem_id = '%s_%s' % (prefix, (str(next_num)))
                arimport.invokeFactory(id = aritem_id, type_name = 'ARImportItem')
                aritem = arimport._getOb(aritem_id)
                aritem.edit(
                    SampleName = sample[0],
                    ClientRef = sample[1],
                    ClientSid = sample[2],
                    SampleDate = sample[3],
                    SampleType = sample[4],
                    PickingSlip = sample[5],
                    ReportDryMatter = sample[6],
                    )
            
                aritem.setRemarks(item_remarks)
                aritem.setAnalyses(analyses)
                next_num += 1

        arimport.edit(
            ImportOption = 'c',
            FileName = batch_headers[2],
            ClientName = batch_headers[3],
            ClientID = batch_headers[4],
            ContactID = batch_headers[5],
            CCContactID = batch_headers[6],
            CCEmails = batch_headers[7],
            OrderID = batch_headers[8],
            QuoteID = batch_headers[9],
            SamplePoint = batch_headers[10],
            Remarks = batch_remarks,
            Analyses = sample_headers,
            DateImported = DateTime(),
            )

        valid = self.validate_arimport_c(arimport)
        REQUEST.RESPONSE.write('<script>document.location.href="%s/client_arimports?portal_status_message=%s%%20imported"</script>' % (client.absolute_url(), arimport_id))


    security.declareProtected(ManageAnalysisRequest, 'import_file_s')
    def import_file_s(self, csvfile, client_id, state):
        import csv

        log = []
        r = self.portal_catalog(portal_type = 'Client', id = client_id)
        if len(r) == 0:
            log.append('   Could not find Client %s' % client_id)
            return '\n'.join(log)
        client = r[0].getObject()
        wf_tool = getToolByName(self, 'portal_workflow')
        reader = csv.reader(csvfile)
        samples = []
        sample_headers = None
        batch_headers = None
        row_count = 0
        sample_count = 0
        batch_remarks = []
        in_footers = False
        last_rows = False
        temp_row = False
        temperature = ''

        for row in reader:
            row_count = row_count + 1
            if not row: continue

            if last_rows:
                continue
            if in_footers:
                continue
                if temp_row:
                    temperature = row[8]
                    temp_row = False
                    last_rows = True
                if row[8] == 'Temperature on Arrival:':
                    temp_row = True
                    continue
                

            if row_count > 11:
                if row[0] == '':
                    in_footers = True

            if row_count == 5:
                client_orderid = row[10]
                continue

            if row_count < 7:
                continue

            if row_count == 7:
                if row[0] != 'Client Name':
                    log.append('  Invalid file')
                    return '\n'.join(log)
                batch_headers = row[0:]
                arimport_id = self.generateUniqueId('ARImport')
                client.invokeFactory(id = arimport_id, type_name = 'ARImport')
                arimport = client._getOb(arimport_id)
                clientname = row[1]
                clientphone = row[5]
                continue

            if row_count == 8:
                clientaddress = row[1]
                clientfax = row[5]
                continue
            if row_count == 9:
                clientcity = row[1]
                clientemail = row[5]
                continue
            if row_count == 10:
                contact = row[1]
                ccemail = row[5]
                continue
            if row_count == 11:
                continue


            if not in_footers:
                samples.append(row)
        
        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request import">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Validating...">')
        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(samples))

        row_count = 0
        for sample in samples:
            row_count = row_count + 1
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)

            profiles = []
            for profile in sample[6:8]:
                if profile != None:
                    profiles.append(profile.strip())

            analyses = []
            for analysis in sample[8:11]:
                if analysis != None:
                    analyses.append(analysis.strip())

            aritem_id = self.generateUniqueId('ARImportItem')
            arimport.invokeFactory(id = aritem_id, type_name = 'ARImportItem')
            aritem = arimport._getOb(aritem_id)
            aritem.edit(
                ClientRef = sample[0],
                ClientRemarks = sample[1],
                ClientSid = sample[2],
                SampleDate = sample[3],
                SampleType = sample[4],
                NoContainers = sample[5],
                AnalysisProfile = profiles,
                Analyses = analyses,
                )
            

        arimport.edit(
            ImportOption = 's',
            ClientName = clientname,
            ClientID = client_id,
            ClientPhone = clientphone,
            ClientFax = clientfax,
            ClientAddress = clientaddress,
            ClientCity = clientcity,
            ClientEmail = clientemail,
            ContactName = contact,
            CCEmails = ccemail,
            Remarks = batch_remarks,
            OrderID = client_orderid,
            Temperature = temperature,
            DateImported = DateTime(),
            )

        valid = self.validate_arimport_s(arimport)
        REQUEST.RESPONSE.write('<script>document.location.href="%s/client_arimports?portal_status_message=%s%%20imported"</script>' % (client.absolute_url(), arimport_id))

InitializeClass(ARImportTool)

######################################################################
# ARExportTool
######################################################################

class ARExportTool(UniqueObject, SimpleItem):
    """ ARExportTool """

    security = ClassSecurityInfo()
    id = 'ar_export_tool'
    title = 'AR Export Tool'
    description = 'Exports Analysis Request Data.'
    meta_type = 'AR Export Tool'

    security.declareProtected(ManageAnalysisRequest, 'export_file')
    def export_file(self, info):
        import csv
        from cStringIO import StringIO
        plone_view = self.restrictedTraverse('@@plone')

        """ create the output file """
        delimiter = ','

        # make filename unique
        now = DateTime()
        filename = 'BikaResults%s.csv' % (now.strftime('%Y%m%d-%H%M%S'))

        if self.bika_settings.settings.getARAttachmentOption() == 'n':
            allow_ar_attach = False
        else:
            allow_ar_attach = True

        if self.bika_settings.settings.getAnalysisAttachmentOption() == 'n':
            allow_analysis_attach = False
        else:
            allow_analysis_attach = True

        # group the analyses
        analysisrequests = info['analysis_requests']
        ars = {}
        services = {}
        categories = {}
        dry_matter = 0
        for ar in analysisrequests:
            ar_id = ar.getId()
            ars[ar_id] = {}
            ars[ar_id]['Analyses'] = {}
            ars[ar_id]['Price'] = 0
            ars[ar_id]['Count'] = 0
            if ar.getReportDryMatter():
                dry_matter = 1
                ars[ar_id]['DM'] = True
            else:
                ars[ar_id]['DM'] = False


            analyses = {}
            # extract the list of analyses in this batch    
            for analysis in ar.getPublishedAnalyses():
                ars[ar_id]['Price'] += analysis.getPrice()
                ars[ar_id]['Count'] += 1
                service = analysis.Title()
                analyses[service] = {}
                analyses[service]['AsIs'] = analysis.getResult()
                analyses[service]['DM'] = analysis.getResultDM() or None
                analyses[service]['attach'] = analysis.getAttachment() or []
                if not services.has_key(service):
                    service_obj = analysis.getService()
                    category = service_obj.getCategoryName()
                    category_uid = service_obj.getCategoryUID()

                    if not categories.has_key(category):
                        categories[category] = []
                    categories[category].append(service)
                    services[service] = {}
                    services[service]['unit'] = service_obj.getUnit()
                    services[service]['DM'] = service_obj.getReportDryMatter()
                    services[service]['DMOn'] = False
                    if allow_analysis_attach:
                        if service_obj.getAttachmentOption() == 'n':
                            services[service]['attach'] = False
                        else:
                            services[service]['attach'] = True
                if services[service]['DM'] == True \
                and ar.getReportDryMatter():
                    services[service]['DMOn'] = True

            ars[ar_id]['Analyses'] = analyses

        # sort by category and title
        c_array = categories.keys()
        c_array.sort(lambda x, y:cmp(x.lower(), y.lower()))

        client = analysisrequests[0].aq_parent
        client_id = client.getClientID()
        client_name = client.Title()

        contact = info['contact']
        contact_id = contact.getUsername()
        contact_name = contact.getFullname()

        rows = []

        # header labels
        header = ['Header', 'Import/Export', 'File name', 'Client', \
                  'Client ID', 'Contact', 'Contact ID', 'CC Recipients', 'CCEmails']
        rows.append(header)    

        # header values
        cc_contacts = [cc.getUsername() for cc in ar.getCCContact()]
        ccs = ', '.join(cc_contacts)
        header = ['Header Data', 'Export', filename, client_name, \
                  client_id, contact_name, contact_id, ccs, ar.getCCEmails(), \
                  '']
        rows.append(header)    

        # category headers    
        s_array = []
        header = ['', '', '', '', '', '', '', '', '', '', '']
        for cat_name in c_array:
            service_array = categories[cat_name]
            service_array.sort(lambda x, y:cmp(x.lower(), y.lower()))
            for service_name in service_array:
                header.append(cat_name)
                if services[service_name]['DMOn']:
                    header.append('')
                if services[service_name]['attach']:
                    header.append('')
            s_array.extend(service_array)
        rows.append(header)    

        # column headers    
        header = ['Samples', 'Order ID', 'Client Reference', 'Client Sample ID', 'Sample Type', \
                  'Sample Point', 'Sampling Date', 'Bika Sample ID', \
                  'Bika AR ID', 'Date Received', 'Date Published']


        for service_name in s_array:
            if services[service_name]['unit']:
                analysis_service = '%s (%s)' % (service_name, services[service_name]['unit'])
            else:
                analysis_service = service_name
            if services[service_name]['DMOn']:
                analysis_service = '%s [As Fed]' % (analysis_service)
            header.append(analysis_service)
            if services[service_name]['DMOn']:
                analysis_dm = '%s [Dry]' % (service_name)
                header.append(analysis_dm)
            if services[service_name]['attach']:
                header.append('Attachments')
        count_cell = len(header)
        header.append('Total number of analyses')
        header.append('Price excl VAT')
        if allow_ar_attach:
            header.append('Attachments')


        rows.append(header)    


        # detail lines 
        total_count = 0
        total_price = 0
        count = 1
        for ar in analysisrequests:
            sample_num = 'Sample %s' % count
            ar_id = ar.getId()
            sample = ar.getSample()
            sample_id = sample.getId()
            sampletype = sample.getSampleType().Title()
            samplepoint = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            datereceived = plone_view.toLocalizedTime(ar.getDateReceived(), \
                           long_format = 1)
            datepublished = plone_view.toLocalizedTime(ar.getDatePublished(), \
                           long_format = 1)
            if sample.getDateSampled():
                datesampled = plone_view.toLocalizedTime(sample.getDateSampled(), long_format = 1)
            else:
                datesampled = None
            
            # create detail line
            detail = [sample_num, ar.getClientOrderNumber(), \
                      sample.getClientReference(), sample.getClientSampleID(), sampletype, \
                      samplepoint, datesampled, sample_id, ar_id, \
                      datereceived, datepublished]

            for service_name in s_array:
                if ars[ar_id]['Analyses'].has_key(service_name):
                    detail.append(ars[ar_id]['Analyses'][service_name]['AsIs'])
                    if services[service_name]['DMOn']:
                        detail.append(ars[ar_id]['Analyses'][service_name]['DM'])
                    if allow_analysis_attach:
                        if services[service_name]['attach'] == True:
                            attachments = ''
                            for attach in ars[ar_id]['Analyses'][service_name]['attach']:
                                file = attach.getAttachmentFile()
                                fname = getattr(file, 'filename')
                                attachments += fname
                            detail.append(attachments)
                else:
                    detail.append(' ')
                    if services[service_name]['DMOn']:
                        detail.append(' ')
                    if services[service_name]['attach'] == True:
                        detail.append(' ')

            for i in range(len(detail), count_cell):
                detail.append('')
            detail.append(ars[ar_id]['Count'])
            detail.append(ars[ar_id]['Price'])
            total_count += ars[ar_id]['Count']
            total_price += ars[ar_id]['Price']

            if allow_ar_attach:
                attachments = ''
                for attach in ar.getAttachment():
                    file = attach.getAttachmentFile()
                    fname = getattr(file, 'filename')
                    if attachments:
                        attachments += ', '
                    attachments += fname
                detail.append(attachments)

            rows.append(detail)
            count += 1

        detail = []
        for i in range(count_cell - 1):
            detail.append('')
        detail.append('Total')
        detail.append(total_count)
        detail.append(total_price)
        rows.append(detail)

        #convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter = delimiter, \
                quoting = csv.QUOTE_NONNUMERIC)
        assert(writer)

        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        file_data = {}
        file_data['file'] = result
        file_data['file_name'] = filename
        return file_data

InitializeClass(ARExportTool)

######################################################################
# ServicesExportTool
######################################################################

class ServicesExportTool(UniqueObject, SimpleItem):
    """ ServicesExportTool """

    security = ClassSecurityInfo()
    id = 'services_export_tool'
    title = 'Services Export Tool'
    description = 'Exports Analysis Service Data.'
    meta_type = 'Services Export Tool'

    security.declareProtected(permissions.View, 'export_file')
    def export_file(self):

        import csv
        from cStringIO import StringIO
        plone_view = self.restrictedTraverse('@@plone')

        """ create the output file """
        delimiter = ','

        filename = 'Services.csv'
        rows = []

        # header labels
        header = ['Analysis Category', 'Analysis Service', 'KeyWord', 'InstrumentKey', 'Price', 'Corporate Price']
        rows.append(header)    

        for s in self.portal_catalog(portal_type = 'AnalysisService',
                                     sort_on = 'sortable_title'):
            service = s.getObject()

            # create detail line
            detail = [service.getCategoryName(), service.Title(), service.getAnalysisKey(), service.getInstrumentKeyword(), service.getPrice(), service.getCorporatePrice()]
            rows.append(detail)


        #convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter = delimiter, \
                quoting = csv.QUOTE_NONNUMERIC)
        assert(writer)

        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = self.REQUEST.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type',
            'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.REQUEST.RESPONSE.write(result)

        return

InitializeClass(ServicesExportTool)

######################################################################
# ProfilesExportTool
######################################################################

class ProfilesExportTool(UniqueObject, SimpleItem):
    """ ProfilesExportTool """

    security = ClassSecurityInfo()
    id = 'profiles_export_tool'
    title = 'Profiles Export Tool'
    description = 'Exports Profile Data.'
    meta_type = 'Profiles Export Tool'

    security.declareProtected(permissions.View, 'export_file')
    def export_file(self, spec):
        import csv
        from cStringIO import StringIO
        plone_view = self.restrictedTraverse('@@plone')

        """ create the output file """
        delimiter = ','

        filename = 'Profiles.csv'

        rows = []

        # header labels
        header = ['Profile', 'Key', 'Owner' ]
        rows.append(header)    

        proxies = []

        client_uid = None

        if spec not in ['lab', 'all', 'clientandlab', ]:
            client_uid = spec

        if spec in ['clientandlab', ]:
            client = self.get_client_for_member()
            client_uid = client.UID()

        # get specific client profiles


        if client_uid:
            tool = getToolByName(self, REFERENCE_CATALOG)
            client = tool.lookupObject(client_uid)

            for p in self.portal_catalog(portal_type = 'ARProfile',
                                         getClientUID = client.UID(),
                                         sort_on = 'getProfileTitle'):

                profile = p.getObject()

                # create detail line
                detail = [profile.getProfileTitle(), profile.getProfileKey(), client.Title()]
                rows.append(detail)

        # get all client profiles
        if spec in ['all', ]:
            for c in self.portal_catalog(portal_type = 'Client',
                                     sort_on = 'sortable_title'):
                client_title = c.Title

                for p in self.portal_catalog(portal_type = 'ARProfile',
                                             getClientUID = c.UID,
                                             sort_on = 'getProfileTitle'):

                    profile = p.getObject()

                    # create detail line
                    detail = [profile.getProfileTitle(), profile.getProfileKey(), client_title]
                    rows.append(detail)

        # get lab profiles
        if spec in ['lab', 'all', 'clientandlab']:
            for p in self.portal_catalog(portal_type = 'LabARProfile',
                                     sort_on = 'getProfileTitle'):
                profile = p.getObject()

                # create detail line
                detail = [profile.getProfileTitle(), profile.getProfileKey(), 'Lab']
                rows.append(detail)

        #convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter = delimiter, \
                quoting = csv.QUOTE_NONNUMERIC)
        assert(writer)

        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = self.REQUEST.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type',
            'text/comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        self.REQUEST.RESPONSE.write(result)

        return

InitializeClass(ProfilesExportTool)
######################################################################
# PDFBuildTool
######################################################################

import string, cStringIO, tempfile
from reportlab import platypus
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import *
from reportlab.platypus import FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.lib.utils import haveImages, ImageReader
from PIL import Image as PIL_Image
from Products.CMFCore.utils import expandpath
from Products.PythonScripts.standard import newline_to_br

class PDFBuildTool(UniqueObject, SimpleItem):
    """ PDFBuildTool """

    security = ClassSecurityInfo()
    id = 'pdf_build_tool'
    title = 'PDF Build Tool'
    description = 'Build PDF'
    meta_type = 'PDF Build Tool'

    class MyPDFDoc :
        # with thanks to Jerome Alet's demo


        def __init__(self, context, filename, headings, all_first_heads, all_other_heads, all_ars, all_results, all_cats, all_oor, all_dries, all_attachments, all_remarks, all_managers, all_disclaimers, lab_title) :
            def myFirstPage(canvas, doc):
                canvas.saveState()
                drawLogos(canvas, doc)
                canvas.restoreState()


            def myLaterPages(canvas, doc):
                canvas.saveState()
                drawLogos(canvas, doc)
                canvas.restoreState()

            def drawLogos(canvas, doc):
                if self.logos[self.logo_imgs[0]] is not None :
                    # draws the logo if it exists
                    (image, width, height) = self.logos[self.logo_imgs[0]]
                    canvas.drawImage(image, 0.75 * inch, doc.pagesize[1] - inch * 1.2, width / 1.5, height / 1.5)
                if self.logos[self.logo_imgs[1]] is not None :
                    # draws the accreditation logo if it exists
                    (image, width, height) = self.logos[self.logo_imgs[1]]
                    canvas.drawImage(image, 5.5 * inch, doc.pagesize[1] - inch * 1.2, width / 1.5, height / 1.5)
                canvas.setFont('Helvetica', 10)
                canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)

            # save some datas
            self.context = context
            self.built = 0
            self.objects = []

            # get all the images we need now, in case we've got
            # several pages this will save some CPU

            self.logos = {}
            self.logo_imgs = ['logo_print.jpg', 'accreditation_print.jpg'] 
            for pic in self.logo_imgs:
                image = self.getImageFP(pic)
                self.logos[pic] = image

            images = {}
            icons = ['no_invoice.png', 'dry.png', 'accredited.jpg', 'exclamation.jpg', 'telephone.jpg', 'email.jpg', ]
            for pic in icons:
                image = self.getImageFromFS(pic, width = 12)
                images[pic] = image
            for manager in all_managers:
                owner = manager
                pic = 'Signature'
                image = self.getImageFromZODB(pic, owner)
                images[manager.getId()] = image


            #   save some colors
            bordercolor = colors.HexColor(0x999933)
            #backgroundcolor = colors.HexColor(0xD3D3AD)
            backgroundcolor = colors.HexColor(0xFFFFFF)
            dryheadcolor = colors.HexColor(0xA6B5DB)
            #drybodycolor = colors.HexColor(0xDAE0F0)
            drybodycolor = colors.HexColor(0xFFFFFF)
            #catcolor = colors.HexColor(0xB6C0D1)
            catcolor = colors.HexColor(0xFFFFFF)

            # we will build an in-memory document
            # instead of creating an on-disk file.
            self.report = cStringIO.StringIO()

            # initialise a PDF document using ReportLab's platypus
            self.doc = SimpleDocTemplate(self.report)

            # get page size
            page_width = self.doc.pagesize[0] - 1.5 * inch
            h_col_width = page_width / 2
            page_height = self.doc.pagesize[1] 

            # get the default style sheets
            self.StyleSheet = styles.getSampleStyleSheet()
            self.StyleSheet['Normal'].fontName = 'Helvetica'
            self.StyleSheet['Heading1'].fontName = 'Helvetica'

            # then build a simple doc with ReportLab's platypus
            self.append(Spacer(0, 20))

            h_table = platypus.Table(headings, colWidths = (h_col_width, h_col_width))

            style = platypus.TableStyle([('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                         ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                                         ('FONT', (0, 0), (-1, -1), 'Helvetica'),

                                       ])
            h_table.setStyle(style)
            self.append(h_table)

            self.append(Spacer(0, 10))
            
            no_ars = all_ars[0]

            col = page_width / ((no_ars * 2) + 4)

            for i in range(len(all_results)):
                these_ars = all_ars[i]
                these_results = all_results[i]
                these_dries = all_dries[i]
                cols = [col * 4, ]
                """ make as fed column wider than dry column """
                for j in range (these_ars):
                    cols.append(col * 1.4)
                    cols.append(col * 0.6)
                col_widths = tuple(cols)
                first_page = True
                if i > 0:
                    self.append(FrameBreak())
                    self.append(Spacer(0, 10))

                """ attachments """
                attachments = all_attachments[i]
                if len(attachments) == 1:
                    attachments[0][1] == 'None'
                else:
                    a_table = platypus.Table(attachments)
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('GRID', (0, 0), (-1, -1), 0.1, bordercolor),
                                   ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                   ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                                   ('BACKGROUND', (0, 0), (-1, 0), backgroundcolor),
                                   ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                    ]
                    style = platypus.TableStyle(table_style)
                    a_table.setStyle(style)
                    a_table.setStyle(style)
                    self.append(a_table)

                self.append(Spacer(0, 10))

                """ determine no of lines in attachment table """
                attachment_count = 0
                for attachment in attachments:
                    attachment_count += 1
                    attachment_count += attachment.count('\n')

                """ headings and results """

                
                general_table_style = [('ALIGN', (0, 0), (0, -1), 'LEFT'),
                               ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                               ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ]
               

                page_max = 18 - attachment_count

                these_oor = all_oor[i]
                these_cats = all_cats[i]
                num_lines = len(these_results)

                slice_end = 0

                while slice_end < num_lines:
                    """ headings """
                    table_style = list(general_table_style)
                    if first_page:
                        page_content = list(all_first_heads[i])
                        table_style.append(('GRID', (0, 0), (0, -1), 0.1, bordercolor))
                        table_style.append(('BACKGROUND', (0, 11), (-1, 11), backgroundcolor))
                        table_style.append(('LINEBELOW', (0, 10), (-1, 10,), 1, bordercolor))
                        table_style.append(('LINEBELOW', (0, 11), (-1, 11), 1, bordercolor))

                        """ span and box the header lines """
                        for j in range(11):
                            for k in range(these_ars):
                                table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))

                    else:
                        self.append(FrameBreak())
                        self.append(Spacer(0, 20))
                        page_content = list(all_other_heads[i])
                        table_style.append(('GRID', (0, 0), (0, -1), 0.1, bordercolor))
                        table_style.append(('BACKGROUND', (0, 4), (-1, 4), backgroundcolor))
                        table_style.append(('LINEBELOW', (0, 3), (-1, 3,), 1, bordercolor))
                        table_style.append(('LINEBELOW', (0, 4), (-1, 4), 1, bordercolor))

                        """ span and box the header lines """
                        for j in range(4):
                            for k in range(these_ars):
                                table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))

                    offset = len(page_content)

                    slice_start = slice_end
                    slice_end = slice_start + page_max
                    if slice_end > num_lines:
                        slice_end = num_lines
                    page_max = 30

                    page_results = these_results[slice_start: slice_end]

                    """ results """
                    page_content.extend(page_results)
                    c_table = platypus.Table(page_content, colWidths = col_widths)

                    for orig_highlight in these_oor:
                        if orig_highlight[1] < slice_start:
                            continue
                        if orig_highlight[1] >= slice_end:
                            continue
                        highlight = ((orig_highlight[0] * 2) + 1, orig_highlight[1] + offset - slice_start)
                        table_style.append(('TEXTCOLOR', highlight, highlight, colors.red))

                    table_length = len(page_content)
                    if first_page:
                        first_page = False

                        """ span and box the detail lines """
                        for k in range(these_ars):
                            for j in range(11, table_length):
                                if k in these_dries:
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 1, j), 0.1, bordercolor))
                                    table_style.append(('BOX', ((k * 2) + 2, j), ((k * 2) + 2, j), 0.1, bordercolor))
                                else:
                                    table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))
                        """ colour the dry matter columns """
                        for k in range(these_ars):
                            if k in these_dries:
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 11), ((k * 2) + 2, 11), dryheadcolor))
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 12), ((k * 2) + 2, -1), drybodycolor))
                    else:

                        """ span and box the detail lines """
                        for j in range(4, table_length):
                            for k in range(these_ars):
                                if k in these_dries:
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 1, j), 0.1, bordercolor))
                                    table_style.append(('BOX', ((k * 2) + 2, j), ((k * 2) + 2, j), 0.1, bordercolor))
                                else:
                                    table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))
                        """ colour the dry matter columns """
                        for k in range(these_ars):
                            if k in these_dries:
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 4), ((k * 2) + 2, 4), dryheadcolor))
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 5), ((k * 2) + 2, -1), drybodycolor))

                    """ colour and span the category lines """
                    for cat in these_cats:
                        if cat < slice_start:
                            continue
                        if cat >= slice_end:
                            continue
                        cat_box_start = (0, cat + offset - slice_start)
                        cat_box_end = (-1, cat + offset - slice_start)
                        table_style.append(('SPAN', cat_box_start, cat_box_end))
                        table_style.append(('BACKGROUND', cat_box_start, cat_box_end, catcolor))
                    style = platypus.TableStyle(table_style)
                    c_table.setStyle(style)
                    self.append(c_table)


                self.append(Spacer(0, 10))

                """ remarks """
                remarks = all_remarks[i]
                if remarks:
                    r_table = platypus.Table(remarks)
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('GRID', (0, 0), (-1, -1), 0.1, bordercolor),
                                   ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                   ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                                   ('BACKGROUND', (0, 0), (-1, 0), backgroundcolor),
                                   ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 9),
                                    ]
                    style = platypus.TableStyle(table_style)
                    r_table.setStyle(style)
                    self.append(KeepTogether(r_table))


                self.append(Spacer(0, 10))

                """ disclaimers """
                disclaimers = all_disclaimers[i]
                table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkgray),
                               ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ]
                style = platypus.TableStyle(table_style)
                h_spacer = 10
                d_stuff = []
                for disclaimer in disclaimers:
                    disclaimer.append(' ')
                d_table = platypus.Table(disclaimers, colWidths = (page_width - 3, 3))
                d_table.setStyle(style)
                self.append(d_table)

                i += 1

            self.append(Spacer(0, 10))
            """ signatures"""

            textStyle = ParagraphStyle('BodyText',
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 10)
            table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                           ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                           ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ]
            style = platypus.TableStyle(table_style)
            h_spacer = 6
            for manager in all_managers:
                keepers = []

                signatures = [(images[manager.getId()], ' '), ]

                s_table = platypus.Table(signatures, colWidths = (h_col_width, h_col_width))

                s_table.setStyle(style)
                keepers.append(s_table)

                m_stuff = []
                name = manager.Title()
                phone = manager.getBusinessPhone()
                email = manager.getEmailAddress()

                m_stuff.append([name, images['telephone.jpg'], phone, images['email.jpg'], email])
                x = page_width - (len(name) * h_spacer) - (len(phone) * h_spacer) - len(email) - 36 
                m_table = platypus.Table(m_stuff, colWidths = (len(name) * h_spacer, 18, len(phone) * h_spacer, 18, len(email) + x))
                m_table.setStyle(style)
                keepers.append(m_table)
                para = Paragraph(lab_title, textStyle)
                keepers.append(para)
                keepers.append(Spacer(0, 10))
                self.append(KeepTogether(keepers))


            # generation du document PDF
            self.doc.build(self.objects, onFirstPage = myFirstPage, onLaterPages = myLaterPages)

            self.built = 1

        def getImageFP(self, name) :
            """Retrieves an image filepath from the ZODB file system
            """
            location = self.context.aq_parent
            try :
                # try to get it from ZODB
                img_pointer = getattr(location, name)
                fp = expandpath(img_pointer._filepath)
            except AttributeError :
                # not found !
                return None

            return (fp, img_pointer.width, img_pointer.height)

        def getImageFromFS(self, name, width = None, height = None) :
            """Retrieves an Image from the ZODB file system
            """
            location = self.context.aq_parent
            try :
                # try to get it from ZODB
                img_pointer = getattr(location, name)
                fp = expandpath(img_pointer._filepath)
                if not width:
                    width = img_pointer.width
                if not height:
                    height = img_pointer.height
                p_img = platypus.Image(fp, width = width / 2, height = height / 2)

                return (p_img)
                
            except AttributeError :
                # not found !
                return None

        def getImageFromZODB(self, name, owner) :
            """Retrieves an Image from a ZODB object
            """
            # AVS
            try :
                # try to get it from ZODB
                img_pointer = getattr(owner, name)
                image = PIL_Image.open(cStringIO.StringIO(str(img_pointer.data)))
                width = img_pointer.width
                height = img_pointer.height
                filename = img_pointer.filename
                suffix = filename.split('.')[-1]


                try:
                    tmp_img = file(tempfile.mktemp(suffix = suffix), 'w+b')
                    tmp_img.write(img_pointer.data)
                    tmp_img.close()
                except IOError:
                    return []
                p_img = platypus.Image(tmp_img.name, width = width / 2, height = height / 2)
            
                return (p_img)
                #return ((p_img, width, height))
                
            except AttributeError :
                # not found !
                return None
        def append(self, object) :
            """Appends an object to our platypus "story" (using ReportLab's terminology)."""
            self.objects.append(object)

    security.declarePublic('ar_results_pdf')
    def ar_results_pdf(self, info):

        settings = self.aq_parent.bika_settings.settings
        max_batch = settings.getBatchEmail()


        laboratory = info['laboratory']
        lab_address = laboratory.getPostalAddress()
        if not lab_address:
            lab_address = laboratory.getBillingAddress()
        if not lab_address:
            lab_address = laboratory.getPhysicalAddress()

        contact = info['contact']
        client = contact.aq_parent
        contact_address = contact.getPostalAddress()
        if not contact_address:
            contact_address = client.getPostalAddress()
        if not contact_address:
            contact_address = client.getBillingAddress()
        if not contact_address:
            contact_address = contact.getPhysicalAddress()
        if not contact_address:
            contact_address = client.getPhysicalAddress()

        lab_accredited = laboratory.getLaboratoryAccredited()
        batch = info['analysis_requests']

        invoice_exclude = False
        out_of_range = []

        contact_stuff = contact.getFullname() + '\n' + client.Title()
        address = newline_to_br(contact_address.get('address', ''))
        contact_stuff = contact_stuff + '\n' + address
        location = contact_address.get('city', '')
        location = location + ', ' + contact_address.get('state', '')
        location = location + ', ' + contact_address.get('zip', '')
        location = location + ' ' + contact_address.get('country', '')
        contact_stuff = contact_stuff + '\n' + location
        
        lab_stuff = laboratory.Title()
        lab_title = laboratory.Title()
        address = newline_to_br(lab_address.get('address', ''))
        lab_stuff = lab_stuff + '\n' + address
        location = lab_address.get('city', '')
        location = location + ', ' + lab_address.get('state', '')
        location = location + ', ' + lab_address.get('zip', '')
        location = location + ' ' + lab_address.get('country', '')

        lab_stuff = lab_stuff + '\n' + location

        headings = []
        headings.append((contact_stuff, lab_stuff))

        all_first_heads = []
        all_other_heads = []
        all_results = []
        all_cats = []
        all_oor = []
        all_attachments = []
        all_remarks = []
        all_disclaimers = []
        all_ars = []
        all_dries = []
        ars = []
        managers = {}
        batch_cnt = 0
        for ar in info['analysis_requests']:
            responsible = ar.getManagers()
            for manager in responsible:
                if not managers.has_key(manager.getId()):
                    managers[manager.getId()] = manager
            if batch_cnt == max_batch:
                (first_heads, other_heads, results, cats, out_of_range, dries, attachments, remarks, disclaimers) = self.process_batch(ars, lab_accredited, lab_title)
                all_first_heads.append(first_heads)
                all_other_heads.append(other_heads)
                all_results.append(results)
                all_cats.append(cats)
                all_oor.append(out_of_range)
                all_ars.append(batch_cnt)
                all_dries.append(dries)
                all_attachments.append(attachments)
                all_remarks.append(remarks)
                all_disclaimers.append(disclaimers)
                ars = []
                batch_cnt = 0
            ars.append(ar)
            batch_cnt += 1

        if batch_cnt > 0:
            (first_heads, other_heads, results, cats, out_of_range, dries, attachments, remarks, disclaimers) = self.process_batch(ars, lab_accredited, lab_title)
            all_first_heads.append(first_heads)
            all_other_heads.append(other_heads)
            all_results.append(results)
            all_cats.append(cats)
            all_oor.append(out_of_range)
            all_attachments.append(attachments)
            all_remarks.append(remarks)
            all_disclaimers.append(disclaimers)
            all_ars.append(batch_cnt)
            all_dries.append(dries)

        all_managers = []
        m_keys = managers.keys()
        for m_key in m_keys:
            all_managers.append(managers[m_key])



        filename = "results.pdf"

        # tell the browser we send some PDF document
        # with the requested filename

        # get the document's content itself as a string of text
        file = self.MyPDFDoc(self, filename, headings, all_first_heads, all_other_heads, all_ars, all_results, all_cats, all_oor, all_dries, all_attachments, all_remarks, all_managers, all_disclaimers, lab_title)
        filecontent = file.report.getvalue() 

        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename=%s' % filename)
        file_data = {}
        file_data['file'] = filecontent
        file_data['file_name'] = filename
        return file_data

    def process_batch(self, ars, lab_accredited, lab_title): 
        service_info = self.get_services_from_requests(ars)
        services = service_info['Services']

        any_accredited = service_info['Accredited']
        accredited = lab_accredited and any_accredited

        plone_view = self.restrictedTraverse('@@plone')
        first_heads = []
        other_heads = []
        results = []
        oor = []
        dries = []
        cats = []
        first_heads.append(['Client Order ID', ])
        other_heads.append(['Client Order ID', ])
        first_heads.append(['Client Reference', ])
        other_heads.append(['Client Reference', ])
        first_heads.append(['Client Sample ID', ])
        other_heads.append(['Client Sample ID', ])
        first_heads.append(['Request ID', ])
        other_heads.append(['Request ID', ])
        first_heads.append(['Sample ID', ])
        first_heads.append(['Sample type', ])
        first_heads.append(['Sample point', ])
        first_heads.append(['Date sampled', ])
        first_heads.append(['Date received', ])
        first_heads.append(['Date published', ])
        first_heads.append(['Verified by', ])
        first_heads.append(['Analysis results', ])
        other_heads.append(['Analysis results', ])
        categoryStyle = ParagraphStyle('BodyText',
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 10)
        serviceStyle = ParagraphStyle('BodyText',
                                  leftIndent = 6,
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 9)
        category = None
        for service in services:
            if service.getCategoryName() != category:
                category = service.getCategoryName()
                print_data = category
                print_data = print_data.replace('&', '&amp;')
                print_data = print_data.replace('<', '&lt;')
                print_data = print_data.replace('>', '&gt;')
                para = Paragraph(print_data, categoryStyle)
                cat_line = [para]
                for i in range(len(ars)):
                    cat_line.append('')
                    cat_line.append('')
                results.append(cat_line)
            print_data = service.Title()
            if service.getUnit():
                print_data = '%s %s' % (print_data, service.getUnit())
            if service.getAccredited():
                print_data = '%s *' % (print_data)
            print_data = print_data.replace('&', '&amp;')
            print_data = print_data.replace('<', '&lt;')
            print_data = print_data.replace('>', '&gt;')
            para = Paragraph(print_data, serviceStyle)
            results.append([para])
        
        ar_analyses = {}
        ar_sampletype = {}
        for ar in ars:
            ar_analyses[ar.getRequestID()] = self.group_analyses_by_service(ar.getPublishedAnalyses())
            ar_sampletype[ar.getRequestID()] = ar.getSample().getSampleType().UID()
        
        paraStyle = ParagraphStyle('BodyText',
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 1,
                                  fontName = 'Helvetica',
                                  fontSize = 9)
        """ attachments """
        attachments = [['Attachments', ''], ]
        for ar in ars:
            if ar.getAttachment():
                attachments.append([ar.getRequestID(), ])
                att = ''
                for attachment in ar.getAttachment():
                    file = attachment.getAttachmentFile()
                    filename = getattr(file, 'filename')
                    filesize = file.getSize()
                    filesize = filesize / 1024
                    att_type = attachment.getAttachmentType().Title()
                    mime_type = self.lookupMime(file.getContentType())
                    print_att = '%s %s %s - %sKb' % (filename, att_type, mime_type, filesize)
                    if att:
                        att = '%s%s' % (att, '\n')
                    att = att + print_att
                    para = Paragraph(att, paraStyle)
                attachments[-1].append(para)
                
            analyses = ar.getPublishedAnalyses()
            for analysis in analyses:
                if analysis.getAttachment():
                    text = '%s - %s' % (ar.getRequestID(), analysis.Title())
                    text = text.replace('&', '&amp;')
                    text = text.replace('<', '&lt;')
                    text = text.replace('>', '&gt;')
                    para = Paragraph(text, serviceStyle)
                    attachments.append([para, ])
                    att = ''
                    for attachment in analysis.getAttachment():
                        file = attachment.getAttachmentFile()
                        filename = getattr(file, 'filename')
                        filesize = file.getSize()
                        filesize = filesize / 1024
                        att_type = attachment.getAttachmentType().Title()
                        mime_type = self.lookupMime(file.getContentType())
                        print_att = '%s %s %s - %sKb' % (filename, att_type, mime_type, filesize)
                        if att:
                            att = '%s%s' % (att, '\n')
                        att = att + print_att
                        para = Paragraph(att, paraStyle)
                    attachments[-1].append(para)
        
        """ remarks """

        remarks = [['Remarks', ''], ]
        for ar in ars:
            if ar.getNotes():
                para = Paragraph(ar.getNotes(), paraStyle)
                remarks.append([ar.getRequestID(), para])
            else:
                remarks.append([ar.getRequestID(), 'None'])
                

        """ ars """
        any_oor = False
        ar_cnt = 0
        for ar in ars:
            sample = ar.getSample()
            requestID = ar.getRequestID()

            text = ar.getClientOrderNumber() and ar.getClientOrderNumber() or ''
            para = Paragraph(text, paraStyle)
            first_heads[0].extend([para, ''])
            other_heads[0].extend([para, ''])
        
            """ temporary fix for long client refs not splitting """ 
            this_text = sample.getClientReference() and sample.getClientReference() or ''
            max_len = 40
            if len(ars) > 3:
                max_len = 16
            elif len(ars) > 2:
                max_len = 20
            elif len(ars) > 1:
                max_len = 30
            if len(this_text) > max_len:
                new_text = ''
                texts = this_text.split()
                for text in texts:
                    if len(text) > max_len:
                        start = 0
                        end = 0
                        while end < len(text):
                            end = end + max_len
                            new_text = new_text + ' ' + text[start:end]
                            start = end
                    else:
                        new_text = new_text + ' ' + text
                this_text = new_text
            para = Paragraph(this_text, paraStyle)
            first_heads[1].extend([para, ''])
            other_heads[1].extend([para, ''])

            text = sample.getClientSampleID() and sample.getClientSampleID() or ''
            para = Paragraph(text, paraStyle)
            first_heads[2].extend([para, ''])
            other_heads[2].extend([para, ''])

            first_heads[3].extend([requestID, ''])
            other_heads[3].extend([requestID, ''])
            first_heads[4].extend([sample.getSampleID(), ''])

            text = sample.getSampleType() and sample.getSampleType().Title() or ''
            para = Paragraph(text, paraStyle)
            first_heads[5].extend([para, ''])

            text = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            para = Paragraph(text, paraStyle)
            first_heads[6].extend([para, ''])

            if sample.getDateSampled():
                datesampled = plone_view.toLocalizedTime(sample.getDateSampled(), long_format = 1)
            else:
                datesampled = ' '
            para = Paragraph(datesampled, paraStyle)
            first_heads[7].extend([para, ''])

            datereceived = plone_view.toLocalizedTime(ar.getDateReceived(), long_format = 1)
            para = Paragraph(datereceived, paraStyle)
            first_heads[8].extend([para, ''])

            datepublished = plone_view.toLocalizedTime(ar.getDatePublished(), long_format = 1)
            para = Paragraph(datepublished, paraStyle)
            first_heads[9].extend([para, ''])

            first_heads[10].extend([self.get_analysisrequest_verifier(ar), ''])
            if ar.getReportDryMatter():
                dries.append(ar_cnt)
                first_heads[11].append('As Fed')
                first_heads[11].append('Dry')
                other_heads[4].append('As Fed')
                other_heads[4].append('Dry')
            else:
                first_heads[11].append('')
                first_heads[11].append('')
                other_heads[4].append('')
                other_heads[4].append('')
            line_cnt = 0

            category = None
            for service in services:
                if service.getCategoryName() != category:
                    category = service.getCategoryName()
                    cats.append(line_cnt)
                    line_cnt += 1
                service_id = service.getId()
                analysis_found = ar_analyses[requestID].has_key(service_id)
                if analysis_found:
                    analysis = ar_analyses[requestID].get(service_id, None)
                    result = analysis.getResult() or None
                    mou = analysis.getUncertainty() or None
                    result_class = self.result_in_range(analysis, ar_sampletype[requestID], 'client')
                    print_result = result
                    if result_class == 'out_of_range':
                        oor.append((ar_cnt, line_cnt))
                        any_oor = True
                        print_result = '%s !' % (print_result)
                    if mou:
                        print_result = '%s (+/- %s)' % (print_result, mou)
                    if analysis.getRetested():
                        print_result = '%s  %s' % (print_result, 'retested')
                    results[line_cnt].append(print_result)
                    if ar.getReportDryMatter():
                        if analysis.getResultDM():
                            results[line_cnt].append(analysis.getResultDM())
                        else:
                            results[line_cnt].append('')
                    else:
                        results[line_cnt].append('')
                else:
                    results[line_cnt].append('')
                    results[line_cnt].append('')

                line_cnt += 1
            ar_cnt += 1


        """ disclaimers """

        disclaimers = []
        if any_oor:
            disclaimers.append(['!   Result out of client specified range'])
        if accredited:
            disclaimers.append(['*   Methods included in the schedule of Accreditation for this Laboratory. Analysis remarks are not accredited'])
        disclaimers.append(['1.  Analysis results relate only to the samples tested'])                
        disclaimers.append(['2.  This document shall not be reproduced except in full, without the written approval of %s' % lab_title])

        return (first_heads, other_heads, results, cats, oor, dries, attachments, remarks, disclaimers)


InitializeClass(PDFBuildTool)


######################################################################
# AnalysisResetTool
######################################################################

class AnalysisResetTool(UniqueObject, SimpleItem):
    """ AnalysisResetTool """

    security = ClassSecurityInfo()
    id = 'analysis_reset_tool'
    title = 'Analysis ResetTool'
    description = 'Resets Analysis Data.'
    meta_type = 'Analysis Reset Tool'

    security.declareProtected(ManageAnalysisRequest, 'import_file')
    def import_file(self, csvfile):
        import csv
        msgs = []
        sfolder = self.bika_services
        
        reader = csv.reader(csvfile, delimiter = ',')
        analyses = []
        batch_headers = None
        counter = 0
        updated_price_counter = 0
        updated_cprice_counter = 0
        updated_both_counter = 0
        not_found_counter = 0
        dup_counter = 0
        invalid_counter = 0
        no_kw_counter = 0
        for row in reader:
            counter += 1
            if counter == 1:
                continue


            if len(row) > 2:
                keyword = row[2].strip()
            else:
                keyword = None

            if len(row) > 1:
                service = row[1]
            else:
                service = None
            if len(row) > 0:
                cat = row[0]
            else:
                cat = None

            if not keyword:
                msgs.append('%s %s %s: KeyWord required for identification' % (counter, cat, service))
                no_kw_counter += 1
                continue

            if len(row) > 5:
                new_cprice = row[5].strip()
                new_cprice = new_cprice.strip('$')
                if new_cprice:
                    try:
                        price = float(new_cprice)
                    except:
                        invalid_counter += 1
                        msgs.append('%s %s %s: corporate price %s is not numeric - not updated' % (counter, cat, service, new_cprice))
                        continue
            else:
                new_cprice = None


            if len(row) > 4:
                new_price = row[4].strip()
                new_price = new_price.strip('$')
                if new_price:
                    try:
                        price = float(new_price)
                    except:
                        invalid_counter += 1
                        msgs.append('%s %s %s: price %s is not numeric - not updated' % (counter, cat, service, new_price))
                        continue
            else:
                new_price = None

            if not (new_price or new_cprice):
                continue
        
            s_proxies = self.portal_catalog(portal_type = 'AnalysisService',
                                            getAnalysisKey = keyword)

            if len(s_proxies) > 1:
                msgs.append('%s %s %s: duplicate key %s' % (counter, cat, service, keyword))
                dup_counter += 1
                continue

            if len(s_proxies) < 1:
                not_found_counter += 1
                msgs.append('%s %s %s: analysis %s not found ' % (counter, cat, service, keyword))

            if len(s_proxies) == 1:
                service_obj = s_proxies[0].getObject()
                old_price = service_obj.getPrice()
                old_cprice = service_obj.getCorporatePrice()
                price_change = False
                cprice_change = False
                if new_price:
                    if old_price != new_price:
                        price_change = True
                        service_obj.edit(Price = new_price)
                        msgs.append('%s %s %s %s price updated from %s to %s' % (counter, cat, service, keyword, old_price, new_price))

                if new_cprice:
                    if old_cprice != new_cprice:
                        cprice_change = True
                        service_obj.edit(CorporatePrice = new_cprice)
                        msgs.append('%s %s %s %s corporate price updated from %s to %s' % (counter, cat, service, keyword, old_cprice, new_cprice))

                if price_change and cprice_change:
                    updated_both_counter += 1
                elif price_change:
                    updated_price_counter += 1
                elif cprice_change:
                    updated_cprice_counter += 1
            


        msgs.append('____________________________________________________')
        msgs.append('%s services in input file' % (counter - 1))
        msgs.append('%s services without keyword - not updated' % (no_kw_counter))
        msgs.append('%s duplicate services - not updated' % (dup_counter))
        msgs.append('%s services not found - not updated' % (not_found_counter))
        msgs.append('%s service price and corporate prices updated' % (updated_both_counter))
        msgs.append('%s service prices updated' % (updated_price_counter))
        msgs.append('%s service corporate prices updated' % (updated_cprice_counter))
        return msgs

InitializeClass(AnalysisResetTool)
