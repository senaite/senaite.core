# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import mimetypes
import os
import re
import tempfile
import urllib2
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_module
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from email import Encoders
from time import time

import types
from DateTime import DateTime
from Products.Archetypes.interfaces.field import IComputedField
from Products.Archetypes.public import DisplayList
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.DCWorkflow.events import AfterTransitionEvent
from bika.lims import api
from bika.lims import logger
from bika.lims.browser import BrowserView
from email.MIMEBase import MIMEBase
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from plone.subrequest import subrequest
from weasyprint import CSS, HTML
from weasyprint import default_url_fetcher
from zope.component import queryUtility
from zope.event import notify
from zope.i18n import translate
from zope.i18n.locales import locales

from bika.lims.interfaces import IClient
from bika.lims.interfaces import IClientAwareMixin

ModuleSecurityInfo('email.Utils').declarePublic('formataddr')
allow_module('csv')


def to_utf8(text):
    if text is None:
        text = ''
    unicode_obj = safe_unicode(text)
    # If it receives a dictionary or list, it will not work
    if isinstance(unicode_obj, unicode):
        return unicode_obj.encode('utf-8')
    return unicode_obj


def to_unicode(text):
    if text is None:
        text = ''
    return safe_unicode(text)


def t(i18n_msg):
    """Safely translate and convert to UTF8, any zope i18n msgid returned from
    a bikaMessageFactory _
    """
    text = to_unicode(i18n_msg)
    try:
        request = api.get_request()
        domain = getattr(i18n_msg, "domain", "senaite.core")
        text = translate(text, domain=domain, context=request)
    except UnicodeDecodeError:
        # TODO: This is only a quick fix
        logger.warn("{} couldn't be translated".format(text))
    return to_utf8(text)


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


class js_err(BrowserView):

    def __call__(self, message):
        """Javascript sends a string for us to place into the error log
        """
        self.logger.error(message)


class js_warn(BrowserView):

    def __call__(self, message):
        """Javascript sends a string for us to place into the warn log
        """
        self.logger.warning(message)


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
        if not fullname:
            fullname = uid
        pairs.append((uid, fullname))
    pairs.sort(lambda x, y: cmp(x[1], y[1]))
    return DisplayList(pairs)


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


def formatDecimalMark(value, decimalmark='.'):
    """
        Dummy method to replace decimal mark from an input string.
        Assumes that 'value' uses '.' as decimal mark and ',' as
        thousand mark.
        ::value:: is a string
        ::returns:: is a string with the decimal mark if needed
    """
    # We have to consider the possibility of working with decimals such as
    # X.000 where those decimals are important because of the precission
    # and significant digits matters
    # Using 'float' the system delete the extre desimals with 0 as a value
    # Example: float(2.00) -> 2.0
    # So we have to save the decimal length, this is one reason we are usnig
    # strings for results
    rawval = str(value)
    try:
        return decimalmark.join(rawval.split('.'))
    except:
        return rawval


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
    sortabletitle = str(title.lower().strip())
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

# TODO Remove this function
def logged_in_client(context, member=None):
    return api.get_current_client()

def changeWorkflowState(content, wf_id, state_id, **kw):
    """Change the workflow state of an object
    @param content: Content obj which state will be changed
    @param state_id: name of the state to put on content
    @param kw: change the values of same name of the state mapping
    @return: True if succeed. Otherwise, False
    """
    portal_workflow = api.get_tool("portal_workflow")
    workflow = portal_workflow.getWorkflowById(wf_id)
    if not workflow:
        logger.error("%s: Cannot find workflow id %s" % (content, wf_id))
        return False

    wf_state = {
        'action': kw.get("action", None),
        'actor': kw.get("actor", api.get_current_user().id),
        'comments': "Setting state to %s" % state_id,
        'review_state': state_id,
        'time': DateTime()
    }

    # Get old and new state info
    old_state = workflow._getWorkflowStateOf(content)
    new_state = workflow.states.get(state_id, None)
    if new_state is None:
        raise WorkflowException("Destination state undefined: {}"
                                .format(state_id))

    # Change status and update permissions
    portal_workflow.setStatusOf(wf_id, content, wf_state)
    workflow.updateRoleMappingsFor(content)

    # Notify the object has been transitioned
    notify(AfterTransitionEvent(content, workflow, old_state, new_state, None,
                                wf_state, None))

    # Map changes to catalog
    indexes = ["allowedRolesAndUsers", "review_state", "is_active"]
    content.reindexObject(idxs=indexes)
    return True


def tmpID():
    import binascii
    return binascii.hexlify(os.urandom(16))


def isnumber(s):
    return api.is_floatable(s)


def senaite_url_fetcher(url):
    """Uses plone.subrequest to fetch an internal image resource.

    If the URL points to an external resource, the URL is handed
    to weasyprint.default_url_fetcher.

    Please see these links for details:

        - https://github.com/plone/plone.subrequest
        - https://pypi.python.org/pypi/plone.subrequest
        - https://github.com/senaite/senaite.core/issues/538

    :returns: A dict with the following keys:

        * One of ``string`` (a byte string) or ``file_obj``
          (a file-like object)
        * Optionally: ``mime_type``, a MIME type extracted e.g. from a
          *Content-Type* header. If not provided, the type is guessed from the
          file extension in the URL.
        * Optionally: ``encoding``, a character encoding extracted e.g. from a
          *charset* parameter in a *Content-Type* header
        * Optionally: ``redirected_url``, the actual URL of the resource
          if there were e.g. HTTP redirects.
        * Optionally: ``filename``, the filename of the resource. Usually
          derived from the *filename* parameter in a *Content-Disposition*
          header

        If a ``file_obj`` key is given, it is the caller’s responsibility
        to call ``file_obj.close()``.
    """

    logger.info("Fetching URL '{}' for WeasyPrint".format(url))

    # get the pyhsical path from the URL
    request = api.get_request()
    host = request.get_header("HOST")
    path = "/".join(request.physicalPathFromURL(url))

    # fetch the object by sub-request
    portal = api.get_portal()
    context = portal.restrictedTraverse(path, None)

    # We double check here to avoid an edge case, where we have the same path
    # as well in our local site, e.g. we have `/senaite/img/systems/senaite.png`,
    # but the user requested http://www.ridingbytes.com/img/systems/senaite.png:
    #
    # "/".join(request.physicalPathFromURL("http://www.ridingbytes.com/img/systems/senaite.png"))
    # '/senaite/img/systems/senaite.png'
    if context is None or host not in url:
        logger.info("URL is external, passing over to the default URL fetcher...")
        return default_url_fetcher(url)

    logger.info("URL is local, fetching data by path '{}' via subrequest".format(path))

    # get the data via an authenticated subrequest
    response = subrequest(path)

    # Prepare the return data as required by WeasyPrint
    string = response.getBody()
    filename = url.split("/")[-1]
    mime_type = mimetypes.guess_type(url)[0]
    redirected_url = url

    return {
        "string": string,
        "filename": filename,
        "mime_type": mime_type,
        "redirected_url": redirected_url,
    }


def createPdf(htmlreport, outfile=None, css=None, images={}):
    """create a PDF from some HTML.
    htmlreport: rendered html
    outfile: pdf filename; if supplied, caller is responsible for creating
             and removing it.
    css: remote URL of css file to download
    images: A dictionary containing possible URLs (keys) and local filenames
            (values) with which they may to be replaced during rendering.
    # WeasyPrint will attempt to retrieve images directly from the URL
    # referenced in the HTML report, which may refer back to a single-threaded
    # (and currently occupied) zeoclient, hanging it.  All image source
    # URL's referenced in htmlreport should be local files.
    """
    # A list of files that should be removed after PDF is written
    cleanup = []
    css_def = ''
    if css:
        if css.startswith("http://") or css.startswith("https://"):
            # Download css file in temp dir
            u = urllib2.urlopen(css)
            _cssfile = tempfile.mktemp(suffix='.css')
            localFile = open(_cssfile, 'w')
            localFile.write(u.read())
            localFile.close()
            cleanup.append(_cssfile)
        else:
            _cssfile = css
        cssfile = open(_cssfile, 'r')
        css_def = cssfile.read()

    htmlreport = to_utf8(htmlreport)

    for (key, val) in images.items():
        htmlreport = htmlreport.replace(key, val)

    # render
    htmlreport = to_utf8(htmlreport)
    renderer = HTML(string=htmlreport, url_fetcher=senaite_url_fetcher, encoding='utf-8')
    pdf_fn = outfile if outfile else tempfile.mktemp(suffix=".pdf")
    if css:
        renderer.write_pdf(pdf_fn, stylesheets=[CSS(string=css_def)])
    else:
        renderer.write_pdf(pdf_fn)
    # return file data
    pdf_data = open(pdf_fn, "rb").read()
    if outfile is None:
        os.remove(pdf_fn)
    for fn in cleanup:
        os.remove(fn)
    return pdf_data


def attachPdf(mimemultipart, pdfreport, filename=None):
    part = MIMEBase('application', "pdf")
    part.add_header('Content-Disposition',
                    'attachment; filename="%s.pdf"' % (filename or tmpID()))
    part.set_payload(pdfreport)
    Encoders.encode_base64(part)
    mimemultipart.attach(part)


def get_invoice_item_description(obj):
    if obj.portal_type == 'AnalysisRequest':
        samplepoint = obj.getSamplePoint()
        samplepoint = samplepoint and samplepoint.Title() or ''
        sampletype = obj.getSampleType()
        sampletype = sampletype and sampletype.Title() or ''
        description = sampletype + ' ' + samplepoint
    elif obj.portal_type == 'SupplyOrder':
        products = obj.folderlistingFolderContents()
        products = [o.getProduct().Title() for o in products]
        description = ', '.join(products)
    return description


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
        logger.warning(
            'Probem accessing optionally hidden attributes in registry')

    return []


def dicts_to_dict(dictionaries, key_subfieldname):
    """Convert a list of dictionaries into a dictionary of dictionaries.

    key_subfieldname must exist in each Record's subfields and have a value,
    which will be used as the key for the new dictionary. If a key is duplicated,
    the earlier value will be overwritten.
    """
    result = {}
    for d in dictionaries:
        result[d[key_subfieldname]] = d
    return result


def format_supsub(text):
    """
    Mainly used for Analysis Service's unit. Transform the text adding
    sub and super html scripts:
    For super-scripts, use ^ char
    For sub-scripts, use _ char
    The expression "cm^2" will be translated to "cm²" and the
    expression "b_(n-1)" will be translated to "b n-1".
    The expression "n_(fibras)/cm^3" will be translated as
    "n fibras / cm³"
    :param text: text to be formatted
    """
    out = []
    subsup = []
    clauses = []
    insubsup = True
    for c in str(text):
        if c == '(':
            if insubsup is False:
                out.append(c)
                clauses.append(')')
            else:
                clauses.append('')

        elif c == ')':
            if len(clauses) > 0:
                out.append(clauses.pop())
                if len(subsup) > 0:
                    out.append(subsup.pop())

        elif c == '^':
            subsup.append('</sup>')
            out.append('<sup>')
            insubsup = True
            continue

        elif c == '_':
            subsup.append('</sub>')
            out.append('<sub>')
            insubsup = True
            continue

        elif c == ' ':
            if insubsup is True:
                out.append(subsup.pop())
            else:
                out.append(c)
        elif c in ['+', '-']:
            if len(clauses) == 0 and len(subsup) > 0:
                out.append(subsup.pop())
            out.append(c)
        else:
            out.append(c)

        insubsup = False

    while True:
        if len(subsup) == 0:
            break
        out.append(subsup.pop())

    return ''.join(out)


def drop_trailing_zeros_decimal(num):
    """ Drops the trailinz zeros from decimal value.
        Returns a string
    """
    out = str(num)
    return out.rstrip('0').rstrip('.') if '.' in out else out


def checkPermissions(permissions=[], obj=None):
    """
    Checks if a user has permissions for a given object.

    Args:
        permissions: The permissions the current user must be compliant with
        obj: The object for which the permissions apply

    Returns:
        1 if the user complies with all the permissions for the given object.
        Otherwise, it returns empty.
    """
    if not obj:
        return False
    sm = getSecurityManager()
    for perm in permissions:
        if not sm.checkPermission(perm, obj):
            return ''
    return True


def getFromString(obj, string, default=None):
    attr_obj = obj
    attrs = string.split('.')
    for attr in attrs:
        attr_obj = api.safe_getattr(attr_obj, attr, default=None)
        if not attr_obj:
            break
    return attr_obj or default


def user_fullname(obj, userid):
    """
    Returns the user full name as string.
    """
    member = obj.portal_membership.getMemberById(userid)
    if member is None:
        return userid
    member_fullname = member.getProperty('fullname')
    portal_catalog = getToolByName(obj, 'portal_catalog')
    c = portal_catalog(portal_type='Contact', getUsername=userid)
    contact_fullname = c[0].getObject().getFullname() if c else None
    return contact_fullname or member_fullname or userid


def user_email(obj, userid):
    """
    This function returns the user email as string.
    """
    member = obj.portal_membership.getMemberById(userid)
    if member is None:
        return userid
    member_email = member.getProperty('email')
    portal_catalog = getToolByName(obj, 'portal_catalog')
    c = portal_catalog(portal_type='Contact', getUsername=userid)
    contact_email = c[0].getObject().getEmailAddress() if c else None
    return contact_email or member_email or ''


def measure_time(func_to_measure):
    """
    This decorator allows to measure the execution time
    of a function and prints it to the console.
    :param func_to_measure: function to be decorated
    """
    def wrap(*args, **kwargs):
        start_time = time()
        return_value = func_to_measure(*args, **kwargs)
        finish_time = time()
        log = "%s took %0.4f seconds. start_time = %0.4f - finish_time = %0.4f\n" % (func_to_measure.func_name,
                                                                                     finish_time - start_time,
                                                                                     start_time,
                                                                                     finish_time)
        print log
        return return_value
    return wrap


def copy_field_values(src, dst, ignore_fieldnames=None, ignore_fieldtypes=None):
    ignore_fields = ignore_fieldnames if ignore_fieldnames else []
    ignore_types = ignore_fieldtypes if ignore_fieldtypes else []
    if 'id' not in ignore_fields:
        ignore_fields.append('id')

    src_schema = src.Schema()
    dst_schema = dst.Schema()

    for field in src_schema.fields():
        if IComputedField.providedBy(field):
            continue
        fieldname = field.getName()
        if fieldname in ignore_fields \
                or field.type in ignore_types \
                or fieldname not in dst_schema:
            continue
        value = field.get(src)
        if value:
            dst_schema[fieldname].set(dst, value)


def get_link(href, value=None, **kwargs):
    """
    Returns a well-formed link. If href is None/empty, returns an empty string
    :param href: value to be set for attribute href
    :param value: the text to be displayed. If None, the href itself is used
    :param kwargs: additional attributes and values
    :return: a well-formed html anchor
    """
    if not href:
        return ""
    anchor_value = value and value or href
    attr = render_html_attributes(**kwargs)
    return '<a href="{}" {}>{}</a>'.format(href, attr, anchor_value)


def get_link_for(obj, **kwargs):
    """Returns a well-formed html anchor to the object
    """
    if not obj:
        return ""
    href = api.get_url(obj)
    value = api.get_title(obj)
    return get_link(href=href, value=value, **kwargs)


def get_email_link(email, value=None):
    """
    Returns a well-formed link to an email address. If email is None/empty,
    returns an empty string
    :param email: email address
    :param link_text: text to be displayed. If None, the email itself is used
    :return: a well-formatted html anchor
    """
    if not email:
        return ""
    mailto = 'mailto:{}'.format(email)
    link_value = value and value or email
    return get_link(mailto, link_value)


def get_image(name, **kwargs):
    """Returns a well-formed image
    :param name: file name of the image
    :param kwargs: additional attributes and values
    :return: a well-formed html img
    """
    if not name:
        return ""
    portal_url = api.get_url(api.get_portal())
    attr = render_html_attributes(**kwargs)
    html = '<img src="{}/++resource++bika.lims.images/{}" {}/>'
    return html.format(portal_url, name, attr)


def get_progress_bar_html(percentage):
    """Returns an html that represents a progress bar
    """
    return '<div class="progress md-progress">' \
           '<div class="progress-bar" style="width: {0}%">{0}%</div>' \
           '</div>'.format(percentage or 0)


def render_html_attributes(**kwargs):
    """Returns a string representation of attributes for html entities
    :param kwargs: attributes and values
    :return: a well-formed string representation of attributes"""
    attr = list()
    if kwargs:
        attr = ['{}="{}"'.format(key, val) for key, val in kwargs.items()]
    return " ".join(attr).replace("css_class", "class")


def get_registry_value(key, default=None):
    """
    Gets the utility for IRegistry and returns the value for the key passed in.
    If there is no value for the key passed in, returns default value
    :param key: the key in the registry to look for
    :param default: default value if the key is not registered
    :return: value in the registry for the key passed in
    """
    registry = queryUtility(IRegistry)
    return registry.get(key, default)


def check_permission(permission, obj):
    """
    Returns if the current user has rights for the permission passed in against
    the obj passed in
    :param permission: name of the permission
    :param obj: the object to check the permission against for the current user
    :return: 1 if the user has rights for this permission for the passed in obj
    """
    mtool = api.get_tool('portal_membership')
    object = api.get_object(obj)
    return mtool.checkPermission(permission, object)


def to_int(value, default=0):
    """
    Tries to convert the value passed in as an int. If no success, returns the
    default value passed in
    :param value: the string to convert to integer
    :param default: the default fallback
    :return: int representation of the value passed in
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return to_int(default, default=0)


def get_strings(data):
    """
    Convert unicode values to strings even if they belong to lists or dicts.
    :param data: an object.
    :return: The object with all unicode values converted to string.
    """
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')

    # if this is a list of values, return list of string values
    if isinstance(data, list):
        return [get_strings(item) for item in data]

    # if this is a dictionary, return dictionary of string keys and values
    if isinstance(data, dict):
        return {
            get_strings(key): get_strings(value)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def get_unicode(data):
    """
    Convert string values to unicode even if they belong to lists or dicts.
    :param data: an object.
    :return: The object with all string values converted to unicode.
    """
    # if this is a common string, return its unicode representation
    if isinstance(data, str):
        return safe_unicode(data)

    # if this is a list of values, return list of unicode values
    if isinstance(data, list):
        return [get_unicode(item) for item in data]

    # if this is a dictionary, return dictionary of unicode keys and values
    if isinstance(data, dict):
        return {
            get_unicode(key): get_unicode(value)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def is_bika_installed():
    """Check if Bika LIMS is installed in the Portal
    """
    qi = api.portal.get_tool("portal_quickinstaller")
    return qi.isProductInstalled("bika.lims")


def get_display_list(brains_or_objects=None, none_item=False):
    """
    Returns a DisplayList with the items sorted by Title
    :param brains_or_objects: list of brains or objects
    :param none_item: adds an item with empty uid and text "Select.." in pos 0
    :return: DisplayList (uid, title) sorted by title ascending
    :rtype: DisplayList
    """
    if brains_or_objects is None:
        return get_display_list(list(), none_item)

    items = list()
    for brain in brains_or_objects:
        uid = api.get_uid(brain)
        if not uid:
            continue
        title = api.get_title(brain)
        items.append((uid, title))

    # Sort items by title ascending
    items.sort(lambda x, y: cmp(x[1], y[1]))

    # Add the first item?
    if none_item:
        items.insert(0, ('', t('Select...')))

    return DisplayList(items)


def to_choices(display_list):
    """Converts a display list to a choices list
    """
    if not display_list:
        return []

    return map(
        lambda item: {
            "ResultValue": item[0],
            "ResultText": item[1]},
        display_list.items())


def chain(obj):
    """Generator to walk the acquistion chain of object, considering that it
    could be a function.

    If the thing we are accessing is actually a bound method on an instance,
    then after we've checked the method itself, get the instance it's bound to
    using im_self, so that we can continue to walk up the acquistion chain from
    it (incidentally, this is why we can't juse use aq_chain()).
    """
    context = aq_inner(obj)

    while context is not None:
        yield context

        func_object = getattr(context, "im_self", None)
        if func_object is not None:
            context = aq_inner(func_object)
        else:
            # Don't use aq_inner() since portal_factory (and probably other)
            # things, depends on being able to wrap itself in a fake context.
            context = aq_parent(context)


def get_client(obj):
    """Returns the client the object passed-in belongs to, if any

    This walks the acquisition chain up until we find something which provides
    either IClient or IClientAwareMixin
    """
    for obj in chain(obj):
        if IClient.providedBy(obj):
            return obj
        elif IClientAwareMixin.providedBy(obj):
            # ClientAwareMixin can return a Client, even if there is no client
            # in the acquisition chain
            return obj.getClient()

    return None
