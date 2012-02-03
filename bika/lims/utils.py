from AccessControl import ModuleSecurityInfo, allow_module
from DateTime import DateTime
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.TranslationServiceTool import TranslationServiceTool
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims import interfaces
from bika.lims import logger
from bika.lims.config import Publish
from email.Utils import formataddr
from plone.i18n.normalizer.interfaces import IIDNormalizer
from reportlab.graphics.barcode import getCodes, getCodeNames, createBarcodeDrawing
from zope.component import getUtility
from zope.interface import providedBy
import copy,re,urllib
import plone.protect
import transaction

ModuleSecurityInfo('email.Utils').declarePublic('formataddr')
allow_module('csv')

# Wrapper for PortalTransport's sendmail - don't know why there sendmail
# method is marked private
ModuleSecurityInfo('Products.bika.utils').declarePublic('sendmail')
#Protected( Publish, 'sendmail')
def sendmail(portal, from_addr, to_addrs, msg):
    mailspool = portal.portal_mailspool
    mailspool.sendmail(from_addr, to_addrs, msg)

ModuleSecurityInfo('Products.bika.utils').declarePublic('printfile')
def printfile(portal, from_addr, to_addrs, msg):
    import os

    """ set the path, then the cmd 'lpr filepath'
    temp_path = 'C:/Zope2/Products/Bika/version.txt'

    os.system('lpr "%s"' %temp_path)
    """
    pass

def getAnalysts(context):
    """ Present the LabManagers and Analysts as options for analyst
    """
    mtool = getToolByName(context, 'portal_membership')
    pairs = []
    analysts = mtool.searchForMembers(roles = ['Manager', 'LabManager', 'Analyst'])
    for member in analysts:
        uid = member.getId()
        fullname = member.getProperty('fullname')
        if fullname is None:
            fullname = uid
        pairs.append((uid, fullname))
    pairs.sort(lambda x, y: cmp(x[1], y[1]))
    return DisplayList(pairs)

def isActive(obj):
    """ Check if obj is inactive or cancelled.
    """
    wf = getToolByName(obj, 'portal_workflow')
    if (hasattr(obj, 'inactive_state') and obj.inactive_state == 'inactive') or \
       wf.getInfoFor(obj, 'inactive_state', 'active') == 'inactive':
        return False
    if (hasattr(obj, 'cancellation_state') and obj.inactive_state == 'cancelled') or \
       wf.getInfoFor(obj, 'cancellation_state', 'active') == 'cancelled':
        return False
    return True

def TimeOrDate(context, datetime, long_format = False):
    """ Return the Time date is today,
        otherwise return the Date.
        XXX timeordate needs long/short/time/date formats in bika_setup
    """
    localLongTimeFormat = context.portal_properties.site_properties.localLongTimeFormat
    localTimeFormat = context.portal_properties.site_properties.localTimeFormat
    localTimeOnlyFormat = context.portal_properties.site_properties.localTimeOnlyFormat

    if hasattr(datetime, 'Date'):
        if (datetime.Date() > DateTime().Date()) or long_format:
            dt = datetime.asdatetime().strftime(localLongTimeFormat)
        elif (datetime.Date() < DateTime().Date()):
            dt = datetime.asdatetime().strftime("%d %b %Y")
        elif datetime.Date() == DateTime().Date():
            dt = datetime.asdatetime().strftime(localTimeOnlyFormat)
        else:
            dt = datetime.asdatetime().strftime(localTimeFormat)
        dt = dt.replace("PM", "pm").replace("AM", "am")
        if len(dt) > 10:
            dt = dt.replace("12:00 am", "")
        if dt == "12:00 am":
            dt = datetime.asdatetime().strftime(localTimeFormat)
    else:
        dt = datetime
    return dt

class ajaxGetObject(BrowserView):
    """ return redirect url if the item exists
        passes the request to portal_catalog
        requires '_authenticator' in request.
    """
    def __call__(self):
        try:
            plone.protect.CheckAuthenticator(self.request)
            plone.protect.PostOnly(self.request)
        except:
            return ""
        pc = getToolByName(self.context, 'portal_catalog')
        id = self.request.get("id", '').replace("*", "")
        items = pc(self.request)
        if items:
            return items[0].getObject().absolute_url()

# encode_header function copied from roundup's rfc2822 package.
hqre = re.compile(r'^[A-z0-9!"#$%%&\'()*+,-./:;<=>?@\[\]^_`{|}~ ]+$')

ModuleSecurityInfo('Products.bika.utils').declarePublic('encode_header')
def encode_header(header, charset = 'utf-8'):
    """ Will encode in quoted-printable encoding only if header
    contains non latin characters
    """

    # Return empty headers unchanged
    if not header:
        return header

    # return plain header if it does not contain non-ascii characters
    if hqre.match(header):
        return header

    quoted = ''
    #max_encoded = 76 - len(charset) - 7
    for c in header:
        # Space may be represented as _ instead of =20 for readability
        if c == ' ':
            quoted += '_'
        # These characters can be included verbatim
        elif hqre.match(c):
            quoted += c
        # Otherwise, replace with hex value like =E2
        else:
            quoted += "=%02X" % ord(c)
            plain = 0

    return '=?%s?q?%s?=' % (charset, quoted)

def zero_fill(matchobj):
    return matchobj.group().zfill(8)

num_sort_regex = re.compile('\d+')

ModuleSecurityInfo('Products.bika.utils').declarePublic('sortable_title')
def sortable_title(portal, title):
    """Convert title to sortable title
    """
    if not title:
        return ''

    def_charset = portal.plone_utils.getSiteEncoding()
    sortabletitle = title.lower().strip()
    # Replace numbers with zero filled numbers
    sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
    # Truncate to prevent bloat
    for charset in [def_charset, 'latin-1', 'utf-8']:
        try:
            sortabletitle = unicode(sortabletitle, charset)[:30]
            sortabletitle = sortabletitle.encode(def_charset or 'utf-8')
            break
        except UnicodeError:
            pass
        except TypeError:
            # If we get a TypeError if we already have a unicode string
            sortabletitle = sortabletitle[:30]
            break
    return sortabletitle

def changeWorkflowState(content, state_id, acquire_permissions=False,
                        portal_workflow=None, **kw):
    """Change the workflow state of an object
    @param content: Content obj which state will be changed
    @param state_id: name of the state to put on content
    @param acquire_permissions: True->All permissions unchecked and on riles and
                                acquired
                                False->Applies new state security map
    @param portal_workflow: Provide workflow tool (optimisation) if known
    @param kw: change the values of same name of the state mapping
    @return: None
    """

    if portal_workflow is None:
        portal_workflow = getToolByName(content, 'portal_workflow')

    # Might raise IndexError if no workflow is associated to this type
    wf_def = portal_workflow.getWorkflowsFor(content)[0]
    wf_id= wf_def.getId()

    wf_state = {
        'action': None,
        'actor': None,
        'comments': "Setting state to %s" % state_id,
        'review_state': state_id,
        'time': DateTime(),
        }

    # Updating wf_state from keyword args
    for k in kw.keys():
        # Remove unknown items
        if not wf_state.has_key(k):
            del kw[k]
    if kw.has_key('review_state'):
        del kw['review_state']
    wf_state.update(kw)

    portal_workflow.setStatusOf(wf_id, content, wf_state)

    if acquire_permissions:
        # Acquire all permissions
        for permission in content.possible_permissions():
            content.manage_permission(permission, acquire=1)
    else:
        # Setting new state permissions
        wf_def.updateRoleMappingsFor(content)

    # Map changes to the catalogs
    content.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
    return
