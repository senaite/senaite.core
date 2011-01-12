## Script (Python) "publish_batch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analysis_requests
##title=
##
contact_ar_map = {}
contact_uid_map = {}
email_ar_map = {}

for ar in analysis_requests:
    contact = ar.getContact()
    contact_uid = contact.UID()
    l = contact_ar_map.get(contact_uid, [])
    l.append(ar)
    contact_ar_map[contact_uid] = l
    contact_uid_map[contact_uid] =  contact
    # cc contacts
    for cc_contact in ar.getCCContact():
        cc_contact_uid = cc_contact.UID()
        l = contact_ar_map.get(cc_contact_uid, [])
        l.append(ar)
        contact_ar_map[cc_contact_uid] = l
        contact_uid_map[cc_contact_uid] =  cc_contact
    # cc emails
    cc_emails = ar.getCCEmails()
    if cc_emails:
        l = email_ar_map.get(cc_emails, [])
        l.append(ar)
        email_ar_map[cc_emails] = l

for contact_uid, ars in contact_ar_map.items():
    contact = contact_uid_map[contact_uid]
    context.publish_analysis_requests(contact, ars, None)

for cc_email, ars in email_ar_map.items():
    context.publish_analysis_requests(None, ars, cc_email)
