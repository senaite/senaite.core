from AccessControl import ModuleSecurityInfo, allow_module
from bika.lims import logger
from bika.lims.browser import BrowserView
from DateTime import DateTime
from email import Encoders
from email.MIMEBase import MIMEBase
from plone.registry.interfaces import IRegistry
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.component import queryUtility
from zope.i18n.locales import locales
import Globals
import re
import urllib2
import os
import App

ModuleSecurityInfo('email.Utils').declarePublic('formataddr')
allow_module('csv')


def to_utf8(text):
    if text is None:
        text = ''
    return safe_unicode(text).encode('utf-8')


def to_unicode(text):
    if text is None:
        text = ''
    return safe_unicode(text)


# Wrapper for PortalTransport's sendmail - don't know why there sendmail
# method is marked private
ModuleSecurityInfo('Products.bika.utils').declarePublic('sendmail')
# Protected( Publish, 'sendmail')


def sendmail(portal, from_addr, to_addrs, msg):
    mailspool = portal.portal_mailspool
    mailspool.sendmail(from_addr, to_addrs, msg)


class js_log(BrowserView):

    def __call__(self, message):
        """Javascript sends a string for us to place into the log.
        """
        self.logger.info(message)

ModuleSecurityInfo('Products.bika.utils').declarePublic('printfile')


def printfile(portal, from_addr, to_addrs, msg):

    """ set the path, then the cmd 'lpr filepath'
    temp_path = 'C:/Zope2/Products/Bika/version.txt'

    os.system('lpr "%s"' %temp_path)
    """
    pass


def getUsers(context, roles, allow_empty=True):
    """ Present a DisplayList containing users in the specified
        list of roles
    """
    mtool = getToolByName(context, 'portal_membership')
    pairs = allow_empty and [['', '']] or []
    users = mtool.searchForMembers(roles=roles)
    for user in users:
        uid = user.getId()
        fullname = user.getProperty('fullname')
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


def formatDateQuery(context, date_id):
    """ Obtain and reformat the from and to dates
        into a date query construct
    """
    from_date = context.REQUEST.get('%s_fromdate' % date_id, None)
    if from_date:
        from_date = from_date + ' 00:00'
    to_date = context.REQUEST.get('%s_todate' % date_id, None)
    if to_date:
        to_date = to_date + ' 23:59'

    date_query = {}
    if from_date and to_date:
        date_query = {'query': [from_date, to_date],
                      'range': 'min:max'}
    elif from_date or to_date:
        date_query = {'query': from_date or to_date,
                      'range': from_date and 'min' or 'max'}

    return date_query


def formatDateParms(context, date_id):
    """ Obtain and reformat the from and to dates
        into a printable date parameter construct
    """
    from_date = context.REQUEST.get('%s_fromdate' % date_id, None)
    to_date = context.REQUEST.get('%s_todate' % date_id, None)

    date_parms = {}
    if from_date and to_date:
        date_parms = 'from %s to %s' % (from_date, to_date)
    elif from_date:
        date_parms = 'from %s' % (from_date)
    elif to_date:
        date_parms = 'to %s' % (to_date)

    return date_parms


def formatDuration(context, totminutes):
    """ Format a time period in a usable manner: eg. 3h24m
    """
    mins = totminutes % 60
    hours = (totminutes - mins) / 60

    if mins:
        mins_str = '%sm' % mins
    else:
        mins_str = ''

    if hours:
        hours_str = '%sh' % hours
    else:
        hours_str = ''

    return '%s%s' % (hours_str, mins_str)

# encode_header function copied from roundup's rfc2822 package.
hqre = re.compile(r'^[A-z0-9!"#$%%&\'()*+,-./:;<=>?@\[\]^_`{|}~ ]+$')

ModuleSecurityInfo('Products.bika.utils').declarePublic('encode_header')


def encode_header(header, charset='utf-8'):
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
    # max_encoded = 76 - len(charset) - 7
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
            sortabletitle = safe_unicode(sortabletitle, charset)[:30]
            sortabletitle = sortabletitle.encode(def_charset or 'utf-8')
            break
        except UnicodeError:
            pass
        except TypeError:
            # If we get a TypeError if we already have a unicode string
            sortabletitle = sortabletitle[:30]
            break
    return sortabletitle


def logged_in_client(context, member=None):
    if not member:
        membership_tool = getToolByName(context, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()

    client = None
    groups_tool = context.portal_groups
    member_groups = [groups_tool.getGroupById(group.id).getGroupName()
                 for group in groups_tool.getGroupsByUserId(member.id)]

    if 'Clients' in member_groups:
        for obj in context.clients.objectValues("Client"):
            if member.id in obj.users_with_local_role('Owner'):
                client = obj
    return client


def changeWorkflowState(content, wf_id, state_id, acquire_permissions=False,
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
    found_wf = 0
    for wf_def in portal_workflow.getWorkflowsFor(content):
        if wf_id == wf_def.getId():
            found_wf = 1
            break
    if not found_wf:
        logger.error("%s: Cannot find workflow id %s" % (content, wf_id))

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
        if k not in wf_state:
            del kw[k]
    if 'review_state' in kw:
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


def tmpID():
    import binascii
    return binascii.hexlify(os.urandom(16))


def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def createPdf(htmlreport, outfile=None, css=None):
    debug_mode = App.config.getConfiguration().debug_mode
    # XXX css must be a local file - urllib fails under robotframework tests.
    css_def = ''
    if css:
        if css.startswith("http://") or css.startswith("https://"):
            # Download css file in temp dir
            u = urllib2.urlopen(css)
            _cssfile = Globals.INSTANCE_HOME + '/var/' + tmpID() + '.css'
            localFile = open(_cssfile, 'w')
            localFile.write(u.read())
            localFile.close()
        else:
            _cssfile = css
        cssfile = open(_cssfile, 'r')
        css_def = cssfile.read()
    if not outfile:
        outfile = Globals.INSTANCE_HOME + "/var/" + tmpID() + ".pdf"

    from weasyprint import HTML, CSS
    import os
    if css:
        HTML(string=htmlreport, encoding='utf-8').write_pdf(outfile,
            stylesheets=[CSS(string=css_def)])
    else:
        HTML(string=htmlreport, encoding='utf-8').write_pdf(outfile)

    if debug_mode:
        htmlfilepath = Globals.INSTANCE_HOME + "/var/" + tmpID() + ".html"
        htmlfile = open(htmlfilepath, 'w')
        htmlfile.write(htmlreport)
        htmlfile.close()
    return open(outfile, 'r').read();

def attachPdf(mimemultipart, pdfreport, filename=None):
    part = MIMEBase('application', "application/pdf")
    part.add_header('Content-Disposition',
                    'attachment; filename="%s.pdf"' % (filename or tmpID()))
    part.set_payload(pdfreport)
    Encoders.encode_base64(part)
    mimemultipart.attach(part)


def get_invoice_item_description(obj):
    sample = obj.getSample()
    sampleID = sample.Title()
    clientref = sample.getClientReference()
    clientsid = sample.getClientSampleID()
    samplepoint = sample.getSamplePoint()
    samplepoint = samplepoint and samplepoint.Title() or ''
    sampletype = sample.getSampleType()
    sampletype = sampletype and sampletype.Title() or ''
    orderno = obj.getClientOrderNumber() or ''
    item_description = orderno + ' ' + clientref + ' ' + clientsid + ' ' + sampleID + ' ' + sampletype + ' ' + samplepoint
    return item_description


def currency_format(context, locale):
    locale = locales.getLocale(locale)
    currency = context.bika_setup.getCurrency()
    symbol = locale.numbers.currencies[currency].symbol
    def format(val):
        return '%s %0.2f' % (symbol, val)
    return format


def getHiddenAttributesForClass(classname):
    try:
        registry = queryUtility(IRegistry)
        hiddenattributes = registry.get('bika.lims.hiddenattributes', ())
        if hiddenattributes is not None:
            for alist in hiddenattributes:
                if alist[0] == classname:
                    return alist[1:]
    except:
        raise RuntimeError(
                'Probem accessing optionally hidden attributes in registry')

    return []

def isAttributeHidden(classname, fieldname):
    try:
        registry = queryUtility(IRegistry)
        hiddenattributes = registry.get('bika.lims.hiddenattributes', ())
        if hiddenattributes is not None:
            for alist in hiddenattributes:
                if alist[0] == classname:
                    return fieldname in alist[1:]
    except:
        raise RuntimeError(
                'Probem accessing optionally hidden attributes in registry')

    return False


