## Script (Python) "email_standardsamples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Email standard samples
##
from DateTime import DateTime
from email.Utils import formataddr
from Products.bika.utils import sendmail, encode_header

portal = context.portal_url.getPortalObject()
pmt = portal.portal_mailtemplates
lab = context.bika_labinfo.laboratory
request = context.REQUEST

standard_samples = portal.portal_mailtemplates.getTemplate(
    'bika', request.mail_template)

headers = {}
headers['Date'] = DateTime().rfc822()
from_addr = headers['From'] = formataddr(
    ( encode_header(lab.Title()), lab.getEmailAddress() )
)

if request.has_key('Contact_email_address'):
    contact_address = request.Contact_email_address
    msg = 'portal_status_message=Standard sample list sent to %s' % (
        contact_address)
else:
    contact = context.reference_catalog.lookupObject(request.Contact_uid)
    contact_address = formataddr(
        ( encode_header(contact.getFullname()),
          contact.getEmailAddress() )
    )
    msg = 'portal_status_message=Standard sample list sent to %s at %s' % (
        contact.Title(), contact.getEmailAddress())


to_addrs = []
to_addr = headers['To'] = contact_address
to_addrs.append(to_addr)
# send copy to lab
to_addrs.append(from_addr)

to_addrs = tuple(to_addrs)
info = {'portal': portal}

message = pmt.createMessage(
    'bika', request.mail_template, info, headers, text_format='html')
sendmail(portal, from_addr, to_addrs, message)

request.RESPONSE.redirect('%s/standardsamples?%s' % (context.absolute_url(), msg))


