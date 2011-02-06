## Script (Python) "email_query_result"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Email query result
##
from DateTime import DateTime
from email.Utils import formataddr
from Products.bika.utils import sendmail, encode_header

portal = context.portal_url.getPortalObject()
pmt = portal.portal_mailtemplates
lab = context.bika_labinfo.laboratory
request = context.REQUEST
settings = context.bika_settings

ar_query_results = portal.portal_mailtemplates.getTemplate(
    'bika', request.mail_template)

headers = {}
headers['Date'] = DateTime().rfc822()
from_addr = headers['From'] = formataddr(
    (encode_header(lab.Title()), lab.getEmailAddress())
)

if request.has_key('Contact_email_address'):
    contact = None
    contact_address = request.Contact_email_address
    msg = 'portal_status_message=Query result sent to %s' % (
        contact_address)
else:
    contact = context.reference_catalog.lookupObject(request.Contact_uid)
    contact_address = formataddr(
        (encode_header(contact.getFullname()),
          contact.getEmailAddress())
    )
    msg = 'portal_status_message=Query result sent to %s at %s' % (
        contact.Title(), contact.getEmailAddress())


to_addrs = []
to_addr = headers['To'] = contact_address
to_addrs.append(to_addr)
# send copy to lab
to_addrs.append(from_addr)

#context.format_date_query(request.date_index)
context.format_date_query('DateSampled')
context.format_date_query('getDateRequested')
context.format_date_query('getDateReceived')
context.format_date_query('getDatePublished')
if request.mail_template == 'ar_query_results':
    results = context.query_analysis_requests() or []
else:
    results = context.queryCatalog() or []

to_addrs = tuple(to_addrs)

batch_max = settings.getBatchEmail()
j = 0
max_ars = []

for i in range(len(results)):
    max_ars.append(results[i])
    j += 1
    if j == batch_max:
        info = {'request': request,
                'results': max_ars,
                'contact': contact,
                'laboratory': lab,
                'portal': portal}
        message = pmt.createMessage(
            'bika', request.mail_template, info, headers, text_format = 'html')
        sendmail(portal, from_addr, to_addrs, message)
        j = 0
        max_ars = []
if j > 0:
    info = {'request': request,
            'results': max_ars,
            'contact': contact,
            'laboratory': lab,
            'portal': portal}
    message = pmt.createMessage(
        'bika', request.mail_template, info, headers, text_format = 'html')
    sendmail(portal, from_addr, to_addrs, message)

request.RESPONSE.redirect('%s?%s' % (context.query_form.absolute_url(), msg))
