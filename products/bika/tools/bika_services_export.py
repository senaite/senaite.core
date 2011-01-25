from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.bika.tools import ToolFolder
from cStringIO import StringIO
import csv
from Products.bika.interfaces.tools import Ibika_services_export
from five import grok

class bika_services_export(UniqueObject, SimpleItem):
    """ ServicesExportTool """

    grok.implements(Ibika_services_export)

    security = ClassSecurityInfo()
    id = 'bika_services_export'
    title = 'Services Export Tool'
    description = 'Exports Analysis Service Data.'
    meta_type = 'Services Export Tool'

    security.declareProtected(permissions.View, 'export_file')
    def export_file(self):

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

InitializeClass(bika_services_export)
