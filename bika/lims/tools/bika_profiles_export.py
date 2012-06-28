from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.config import REFERENCE_CATALOG
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.tools import ToolFolder
from cStringIO import StringIO
import csv
from bika.lims.interfaces.tools import Ibika_profiles_export
from zope.interface import implements

class bika_profiles_export(UniqueObject, SimpleItem):
    """ ProfilesExportTool """

    implements(Ibika_profiles_export)

    security = ClassSecurityInfo()
    id = 'bika_profiles_export'
    title = 'Profiles Export Tool'
    description = 'Exports Profile Data.'
    meta_type = 'Profiles Export Tool'

    security.declareProtected(permissions.View, 'export_file')
    def export_file(self, spec):
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

            for p in self.portal_catalog(portal_type = 'AnalysisProfile',
                                         getClientUID = client.UID(),
                                         sort_on = 'sortable_title'):

                profile = p.getObject()

                # create detail line
                detail = [profile.Title(), profile.getProfileKey(), client.Title()]
                rows.append(detail)

        # get all client profiles
        if spec in ['all', ]:
            for c in self.portal_catalog(portal_type = 'Client',
                                     sort_on = 'sortable_title'):
                client_title = c.Title

                for p in self.portal_catalog(portal_type = 'AnalysisProfile',
                                             getClientUID = c.UID,
                                             sort_on = 'sortable_title'):

                    profile = p.getObject()

                    # create detail line
                    detail = [profile.Title(), profile.getProfileKey(), client_title]
                    rows.append(detail)

        # get lab profiles
        if spec in ['lab', 'all', 'clientandlab']:
            for p in self.portal_catalog(portal_type = 'AnalysisProfile',
                                     sort_on = 'sortable_title'):
                profile = p.getObject()

                # create detail line
                detail = [profile.Title(), profile.getProfileKey(), 'Lab']
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

InitializeClass(bika_profiles_export)
