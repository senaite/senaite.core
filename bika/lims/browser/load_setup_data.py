from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger, bikaMessageFactory as _
from cStringIO import StringIO
from openpyxl.reader.excel import load_workbook
from os.path import join
from zipfile import ZipFile, ZIP_DEFLATED
import Globals
import tempfile
from xml.etree.ElementTree import XML

class LoadSetupData(BrowserView):
    template = ViewPageTemplateFile("templates/load_setup_data.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.title = _("Load Setup Data")
        self.description = _("Please.")

    def __call__(self):
        form = self.request.form
        plone_utils = getToolByName(self.context, 'plone_utils')
        tmp = tempfile.mktemp(prefix=Globals.INSTANCE_HOME)
        file_content = 'xlsx' in form and form['xlsx'].read()
        if not file_content:
            plone_utils.addPortalMessage(_("No file data submitted.  Please "
                                           "submit a valid Open XML Spreadsheet "
                                           "(.xlsx) file."))
            return self.template()
        open(tmp, "wb").write(file_content)
        wb = load_workbook(filename = tmp)
##        self.load_images(tmp)
        sheets = {}
        for sheetname in wb.get_sheet_names():
            sheets[sheetname] = wb.get_sheet_by_name(sheetname)
##        self.load_lab_users(sheets['Lab Users'])
        self.load_lab_contacts(sheets['Lab Contacts'])

        return self.template()

##    def load_images(self, filename):
##        archive = ZipFile(filename, 'r', ZIP_DEFLATED)
##        self.images = {}
##        for zipinfo in archive.filelist:
##            if zipinfo.filename.lower().endswith('.xml'):
##                xml = XML(archive.read(zipinfo.filename))
##        for xmlfile in archive/xl/drawings/*.xml:
##            drawing = xml.etree.ElementTree.XML(xmlfile.read())
##        drawings = xml.etree.ElementTree.XML

    def load_lab_users(self, sheet):
        portal_registration = getToolByName(self.context, 'portal_registration')
        portal_groups = getToolByName(self.context, 'portal_groups')
        portal_membership = getToolByName(self.context, 'portal_membership')
        translate = getToolByName(self.context, 'translation_service').translate
        plone_utils = getToolByName(self.context, 'plone_utils')

        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value
                 for col_nr in range(nr_cols)]
                  for row_nr in range(nr_rows)]
        fields = rows[1]
        for row in rows[2:]:
            row = dict(zip(fields, row))
            portal_registration.addMember(
                row['Username'],
                row['Password'],
                properties = {
                    'username': row['Username'],
                    'email': row['EmailAddress'],
                    'fullname': " ".join((row['Firstname'], row['Surname']))})
            group_ids = [g.strip() for g in row['Groups'].split(',')]
            for group_id in group_ids:
                group = portal_groups.getGroupById(group_id)
                if not group:
                    message = translate(
                        "message_invalid_group",
                        "bika",
                        {'group_id': group_id},
                        self.context,
                        default = "Invalid group: '${group_id}'.")
                    plone_utils.addPortalMessage(message)
                    return self.template()
                group.addMember(row['Username'])
            # If user is in LabManagers, add Owner local role on clients folder
            if 'LabManager' in group_ids:
                portal_membership.setLocalRoles(obj = self.context.clients,
                                                member_ids = (row['Username'],),
                                                member_role = 'Owner')

    def load_lab_contacts(self, sheet):
        portal_registration = getToolByName(self.context, 'portal_registration')
        portal_groups = getToolByName(self.context, 'portal_groups')
        portal_membership = getToolByName(self.context, 'portal_membership')
        translate = getToolByName(self.context, 'translation_service').translate
        plone_utils = getToolByName(self.context, 'plone_utils')

        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_labcontacts
        for row in rows[2:]:
            row = dict(zip(fields, row))
            labcontact_id = folder.generateUniqueId('LabContact')
            folder.invokeFactory('LabContact', id = labcontact_id)
            obj = folder[labcontact_id]
            obj.edit(Firstname = row['Firstname'],
                     Surname = row['Surname'],
                     EmailAddress = row['EmailAddress'],
                     BusinessPhone = row['BusinessPhone'],
                     BusinessFax = row['BusinessFax'],
                     MobilePhone = row['MobilePhone'],
                     JobTitle = row['JobTitle'],
                     Department = row['Department'])
##                     Signature = row['Signature'])
            obj.processForm()




