from bika.lims.browser import BrowserView
from DateTime import DateTime
from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.Registry import registerWidget
import plone

from plone.intelligenttext.transforms import \
     convertWebIntelligentPlainTextToHtml, \
     convertHtmlToWebIntelligentPlainText

class ajaxSetRemarks(BrowserView):
    """ Modify Remarks field and return new rendered field value
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        field = self.context.Schema()["Remarks"]
        value = self.request['value'].strip() + "\n\n"
        existing = self.context.getRemarks(mimetype='text/x-web-intelligent').strip()

        date = DateTime().rfc822()
        user = getSecurityManager().getUser()
        divider = "=== %s (%s)\n" % (date, user)

        remarks = convertWebIntelligentPlainTextToHtml(divider) + \
            convertWebIntelligentPlainTextToHtml(value) + \
            convertWebIntelligentPlainTextToHtml(existing)

        self.context.setRemarks(divider + value + existing, mimetype='text/x-web-intelligent')

        return remarks.strip()
