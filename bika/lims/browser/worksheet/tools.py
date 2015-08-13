# coding=utf-8
from bika.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName


def checkUserAccess(worksheet, request, redirect=True):
    """ Checks if the current user has granted access to the worksheet.
        If the user is an analyst without LabManager, LabClerk and
        RegulatoryInspector roles and the option 'Allow analysts
        only to access to the Worksheets on which they are assigned' is
        ticked and the above condition is true, it will redirect to
        the main Worksheets view.
        Returns False if the user has no access, otherwise returns True
    """
    # Deny access to foreign analysts
    allowed = worksheet.checkUserAccess()
    if allowed == False and redirect == True:
        msg =  _('You do not have sufficient privileges to view '
                 'the worksheet ${worksheet_title}.',
                 mapping={"worksheet_title": worksheet.Title()})
        worksheet.plone_utils.addPortalMessage(msg, 'warning')
        # Redirect to WS list
        portal = getToolByName(worksheet, 'portal_url').getPortalObject()
        destination_url = portal.absolute_url() + "/worksheets"
        request.response.redirect(destination_url)

    return allowed

def checkUserManage(worksheet, request, redirect=True):
    """ Checks if the current user has granted access to the worksheet
        and if has also privileges for managing it. If the user has no
        granted access and redirect's value is True, redirects to
        /manage_results view. Otherwise, does nothing
    """
    allowed = worksheet.checkUserManage()
    if allowed == False and redirect == True:
        # Redirect to /manage_results view
        destination_url = worksheet.absolute_url() + "/manage_results"
        request.response.redirect(destination_url)

def showRejectionMessage(worksheet):
    """ Adds a portalMessage if
        a) the worksheet has been rejected and replaced by another or
        b) if the worksheet is the replacement of a rejected worksheet.
        Otherwise, does nothing.
    """
    if hasattr(worksheet, 'replaced_by'):
        uc = getToolByName(worksheet, 'uid_catalog')
        uid = getattr(worksheet, 'replaced_by')
        _ws = uc(UID=uid)[0].getObject()
        msg = _("This worksheet has been rejected.  The replacement worksheet is ${ws_id}",
                mapping={'ws_id':_ws.getId()})
        worksheet.plone_utils.addPortalMessage(msg)
    if hasattr(worksheet, 'replaces_rejected_worksheet'):
        uc = getToolByName(worksheet, 'uid_catalog')
        uid = getattr(worksheet, 'replaces_rejected_worksheet')
        _ws = uc(UID=uid)[0].getObject()
        msg = _("This worksheet has been created to replace the rejected "
                "worksheet at ${ws_id}",
                mapping={'ws_id':_ws.getId()})
        worksheet.plone_utils.addPortalMessage(msg)
