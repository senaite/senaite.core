## Script (Python) "get_requests_from_session"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get analysis requests by resolving uids on session
##

from DateTime import DateTime
from email.Utils import formataddr
from Products.bika.utils import sendmail, encode_header

rc = context.reference_catalog
session = context.REQUEST.SESSION
analysis_requests = [rc.lookupObject(uid) for uid in session.get('uids', [])]

contact_ar_map = {}
contact_uid_map = {}

for ar in analysis_requests:
    contact = ar.getContact()
    if 'print' in contact.getPublicationPreference():
        contact_uid = contact.UID()
        l = contact_ar_map.get(contact_uid, [])
        l.append(ar)
        contact_ar_map[contact_uid] = l
        contact_uid_map[contact_uid] =  contact

messages = []
portal = context.portal_url.getPortalObject()
pmt = portal.portal_mailtemplates
lab = context.bika_labinfo.laboratory

ar_results = portal.portal_mailtemplates.getTemplate(
    'bika', 'ar_results')

headers = {}
headers['Date'] = DateTime().rfc822()
from_addr = headers['From'] = formataddr(
    ( encode_header(lab.Title()), lab.getEmailAddress() )
)

settings = context.bika_settings
batch_max = settings.getBatchEmail()

for contact_uid, ars in contact_ar_map.items():
    contact = contact_uid_map[contact_uid]

    ar_dict = {}
    sorted_ars = []
    for ar in ars:
        ar_dict[ar.getRequestID()] = ar
    ar_keys = ar_dict.keys()
    ar_keys.sort()
    for ar_key in ar_keys:
        sorted_ars.append(ar_dict[ar_key])

    max_ars = []
    ar_ids = []
    i = j = 0
    for i in range(len(sorted_ars)):
        max_ars.append(sorted_ars[i])
        ar_ids.append(sorted_ars[i].getRequestID())
        j += 1
        if j == batch_max:
            info = {'analysis_requests': max_ars,
                    'analysis_request_ids': ar_ids,
                    'laboratory': lab,
                    'contact': contact,
                    }

            messages.append(info)
            j = 0
            max_ars = []
            ar_ids = []
    if j > 0:
        info = {'analysis_requests': max_ars,
                'analysis_request_ids': ar_ids,
                'laboratory': lab,
                'contact': contact,
                }

        messages.append(info)

return messages
