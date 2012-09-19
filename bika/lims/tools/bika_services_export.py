from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.tools import ToolFolder
from cStringIO import StringIO
import csv
from bika.lims.interfaces.tools import Ibika_services_export
from zope.interface import implements

class bika_services_export(UniqueObject, SimpleItem):
    """ ServicesExportTool """

    implements(Ibika_services_export)

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
        header = ['Analysis Category', 'Analysis Service', 'KeyWord', 'InstrumentKey', 'Price', 'bulk discount']
        rows.append(header)

        for s in self.portal_catalog(portal_type = 'AnalysisService',
                                     sort_on = 'sortable_title'):
            service = s.getObject()

            # create detail line
            detail = [service.getCategoryTitle(), service.Title(), service.getKeyword(), service.getInstrumentKeyword(), service.getPrice(), service.getBulkPrice()]
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
