
from AccessControl import ModuleSecurityInfo, allow_module
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.TranslationServiceTool import TranslationServiceTool
from reportlab.graphics.barcode import getCodes,getCodeNames,createBarcodeDrawing
from Products.Five.browser import BrowserView
from bika.lims import interfaces
from bika.lims.config import Publish
from email.Utils import formataddr
from zope.component._api import getUtility
import plone.protect
import copy
import re

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

def TimeOrDate(context, datetime, long_format=False):
    """ Return the Time date is today,
        otherwise return the Date. """
    localLongTimeFormat = context.portal_properties.site_properties.localLongTimeFormat
    localTimeFormat = context.portal_properties.site_properties.localTimeFormat
    localTimeOnlyFormat = context.portal_properties.site_properties.localTimeOnlyFormat

    if hasattr(datetime, 'Date'):
        if (datetime.Date() > DateTime().Date()) or long_format:
            dt = datetime.asdatetime().strftime(localLongTimeFormat)
        elif datetime.Date() == DateTime().Date():
            dt = datetime.asdatetime().strftime(localTimeOnlyFormat)
        else:
            dt = datetime.asdatetime().strftime(localTimeFormat)
        dt = dt.replace("PM","pm").replace("AM","am")
        if len(dt) > 10:
            dt = dt.replace("12:00 am","")
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
        id = self.request.get("id", '').replace("*","")
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

ModuleSecurityInfo('Products.bika.utils').declarePublic('generateUniqueId')
def generateUniqueId (self, type_name, batch_size = None):
    """Generate a unique ID for sub objects of the client
    """
    IdServer = getUtility(interfaces.IIdServer)()

    # get prefix
    prefixes = self.bika_setup.getPrefixes()
    type_name.replace(' ', '')
    for d in prefixes:
        if type_name != d['portal_type']: continue
        prefix, padding = d['prefix'], d['padding']
        if batch_size:
            next_id = str(IdServer.generate_id(prefix, batch_size = batch_size))
        else:
            next_id = str(IdServer.generate_id(prefix))
        if padding:
            next_id = next_id.zfill(int(padding))
        return '%s%s' % (prefix, next_id)

    if batch_size:
        next_id = str(IdServer.generate_id(type_name, batch_size = batch_size))
    else:
        next_id = str(IdServer.generate_id(type_name))
    return '%s_%s' % (type_name.lower(), next_id)


