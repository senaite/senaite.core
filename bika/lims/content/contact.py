"""The contact person at an organisation.

$Id: Contact.py 2242 2010-04-08 22:17:03Z campbellbasset $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from bika.lims.content.person import Person

schema = Person.schema.copy() + Schema((
    LinesField('PublicationPreference',
        vocabulary = PUBLICATION_PREFS,
        schemata = 'Publication preference',
        widget = MultiSelectionWidget(
            label = 'Publication preference',
            label_msgid = 'label_publicationpreference',
        ),
    ),
    BooleanField('AttachmentsPermitted',
        default = False,
        schemata = 'Publication preference',
        widget = BooleanWidget(
            label = "Attachments Permitted",
            label_msgid = "label_attachments_permitted"
        ),
    ),
    ReferenceField('CCContact',
        schemata = 'Publication preference',
        vocabulary = 'getCCContactsDisplayList',
        multiValued = 1,
        allowed_types = ('Contact',),
        relationship = 'ContactContact',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label = 'Contacts to cc',
            label_msgid = 'label_contacts_cc',
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False

class Contact(VariableSchemaSupport, BrowserDefaultMixin, Person):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the contact's Fullname as title """
        return self.getFullname()

    security.declareProtected(ManageClients, 'hasUser')
    def hasUser(self):
        """ check if contact has user """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        pairs = []
        all_contacts = self.aq_parent.getContactsDisplayList().items()
        # remove myself
        for item in all_contacts:
            if item[0] != self.UID():
                pairs.append((item[0], item[1]))
        return DisplayList(pairs)

    def publish_analysis_requests(self, context, contact, analysis_requests, ccemail):
        ## Script (Python) "publish_analysis_requests"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=contact, context, analysis_requests, ccemail
        ##title=
        ##
        from DateTime import DateTime
        from email.Utils import formataddr
        from bika.lims.utils import sendmail, encode_header
        import re

        portal = context.portal_url.getPortalObject()
        pmt = portal.portal_mailtemplates
        lab = context.bika_labinfo.laboratory
        settings = context.bika_settings.settings
        lab_url = lab.getLabURL() or portal.absolute_url
        ar_results = portal.portal_mailtemplates.getTemplate('bika', 'ar_results')
        ar_dict = dict([ (ar.getRequestID(), ar) for ar in analysis_requests ])
        keys = ar_dict.keys()
        keys.sort()
        sorted_ars = [ ar_dict[key] for key in keys ]

        headers = {
                'Date': DateTime().rfc822(),
                'From': formataddr((encode_header(lab.Title()), lab.getEmailAddress()))
                }
        from_addr = headers['From']

        def these_attachments(attach_ars):
            extras = []
            for ar in attach_ars:
                for ar_attach in ar.getAttachment():
                    attachmentfile = ar_attach.getAttachmentFile()
                    extras.append((attachmentfile, getattr(attachmentfile, 'content_type',), getattr(attachmentfile, 'filename',)))
                for analysis in ar.getAnalyses():
                    for a_attach in analysis.getAttachment():
                        attachmentfile = a_attach.getAttachmentFile()
                        extras.append((attachmentfile, getattr(attachmentfile, 'content_type'), getattr(attachmentfile, 'filename',)))
            return extras

        def send_this_mail(contact, mail_ars, to_addrs):
            mail_attach = []
            mail_subject = get_mail_subject(mail_ars)
            if contact:
                if contact.getAttachmentsPermitted():
                    mail_attach = these_attachments(mail_ars)

            info = {'analysis_requests': mail_ars,
                    'mail_subject': mail_subject,
                    'laboratory': lab,
                    'contact': contact,
                    'output': 'email',
                    'lab_url': lab_url
                    }

            if mail_attach:
                message = pmt.createMessage(
                 'bika', 'ar_results', info, headers, text_format = 'html', files = mail_attach)
            else:
                message = pmt.createMessage(
                 'bika', 'ar_results', info, headers, text_format = 'html')
            sendmail(portal, from_addr, to_addrs, message)
            return

        def send_this_fax(fax_ars, to_addrs):
            mail_subject = get_mail_subject(fax_ars)
            info = {'analysis_requests': fax_ars,
                    'mail_subject': mail_subject,
                    'laboratory': lab,
                    'contact': contact,
                    'output': 'fax',
                    'lab_url': lab_url,
                    'portal': portal}

            message = pmt.createMessage(
                'bika', 'ar_results', info, headers, text_format = 'html')
            sendmail(portal, from_addr, to_addrs, message)
            # email copy to lab
            to_addrs = (from_addr,)
            sendmail(portal, from_addr, to_addrs, message)
            return

        def get_mail_subject(subject_ars):
            client = subject_ars[0].aq_parent
            subject_items = client.getEmailSubject()
            ai = co = cr = cs = False
            if 'ar' in subject_items:
                ai = True
            if 'co' in subject_items:
                co = True
            if 'cr' in subject_items:
                cr = True
            if 'cs' in subject_items:
                cs = True
            ais = []
            cos = []
            crs = []
            css = []
            blanks_found = False
            for ar in subject_ars:
                if ai:
                    ais.append(ar.getRequestID())
                if co:
                    if ar.getClientOrderNumber():
                        if not ar.getClientOrderNumber() in cos:
                            cos.append(ar.getClientOrderNumber())
                    else:
                        blanks_found = True
                if cr or cs:
                    sample = ar.getSample()
                if cr:
                    if sample.getClientReference():
                        if not sample.getClientReference() in crs:
                            crs.append(sample.getClientReference())
                    else:
                        blanks_found = True
                if cs:
                    if sample.getClientSampleID():
                        if not sample.getClientSampleID() in css:
                            css.append(sample.getClientSampleID())
                    else:
                        blanks_found = True

            tot_line = ''
            if ais:
                ais.sort()
                ar_line = 'ARs: %s' % ', '.join(ais)
                tot_line = ar_line
            if cos:
                cos.sort()
                cos_line = 'Orders: %s' % ', '.join(cos)
                if tot_line:
                    tot_line += ' '
                tot_line += cos_line
            if crs:
                crs.sort()
                crs_line = 'Refs: %s' % ', '.join(crs)
                if tot_line:
                    tot_line += ' '
                tot_line += crs_line
            if css:
                css.sort()
                css_line = 'Samples: %s' % ', '.join(css)
                if tot_line:
                    tot_line += ' '
                tot_line += css_line
            if tot_line:
                subject = 'Analysis results for %s' % tot_line
                if blanks_found:
                    subject += ' and others'
            else:
                subject = 'Analysis results'
            return subject


        email_option = False
        if contact:
            if 'email' in contact.getPublicationPreference():
                email_option = True
                email = contact.getEmailAddress()
                if not email:
                    email = contact.aq_parent.getEmailAddress()
                if not email:
                    email = lab.getEmailAddress()
                to_addr = headers['To'] = formataddr(
                    (encode_header(contact.getFullname()),
                      email)
                )
        else:
            if ccemail:
                email_option = True
                email = ccemail
                to_addr = headers['To'] = formataddr(
                    (encode_header(email), email))

        to_addrs = []
        if email_option:
            batch_max = settings.getBatchEmail()
            to_addrs.append(to_addr)
            # send copy to lab
            to_addrs.append(from_addr)

            to_addrs = tuple(to_addrs)
            i = 0
            j = 0
            max_ars = []
            mail_subject = []
            for i in range(len(sorted_ars)):
                max_ars.append(sorted_ars[i])
                j += 1
                if j == batch_max:
                    send_this_mail(contact, max_ars, to_addrs)
                    j = 0
                    max_ars = []
                    mail_subject = []
            if j > 0:
                send_this_mail(contact, max_ars, to_addrs)

        to_addrs = []
        if contact and 'fax' in contact.getPublicationPreference():
            fullname = contact.getFullname().replace(' ', '')
            fax_no = contact.getBusinessFax()
            if not fax_no:
                fax_no = contact.aq_parent.getFax()
            if not fax_no:
                fax_no = lab.getFax()
            if fax_no:
                fax_no.replace(' ', '')
                fax_mail = '%s@vax.co.za' % fax_no
            to_addr = headers['To'] = formataddr(
                (encode_header(fullname), fax_mail)
            )
            to_addrs.append(to_addr)

            to_addrs = tuple(to_addrs)

            batch_max = settings.getBatchFax()
            i = 0
            j = 0
            max_ars = []
            mail_subject = []
            for i in range(len(sorted_ars)):
                max_ars.append(sorted_ars[i])
                j += 1
                if j == batch_max:
                    send_this_fax(max_ars, to_addrs)
                    j = 0
                    max_ars = []
                    mail_subject = []
            if j > 0:
                send_this_fax(max_ars, to_addrs)

        to_addrs = []
        if contact and 'file' in contact.getPublicationPreference():
            to_addr = headers['To'] = formataddr(
                (encode_header(contact.getFullname()),
                  contact.getEmailAddress())
            )
            to_addrs.append(to_addr)
            # send copy to lab
            to_addrs.append(from_addr)

            to_addrs = tuple(to_addrs)
            mail_subject = get_mail_subject(sorted_ars)
            info = {'contact':contact,
                    'analysis_requests': sorted_ars,
                    'mail_subject': mail_subject,
                    'output': 'file',
                    'laboratory': lab,
                    }

            results_file = {}
            aret = context.ar_export_tool
            results_file = aret.export_file(info)
            attachments = []
            if contact.getAttachmentsPermitted():
                attachments = these_attachments(sorted_ars)
            attachments.append((results_file['file'], 'text/x-comma-separated-values', results_file['file_name']))
            message = pmt.createMessage(
                'bika', 'ar_results_csv', info, headers, text_format = 'html', files = attachments)
            sendmail(portal, from_addr, to_addrs, message)

        if contact and 'sms' in contact.getPublicationPreference():
            sms_gw = settings.getSMSGatewayAddress()
            if not sms_gw: raise "No SMS Gateway defined in settings"
            # XXX strips special chars - bika_settings.
            cell = "".join([c for c in contact.getMobilePhone() if c in '0123456789'])

            if sms_gw[0] == "@":
                to_addr = headers['To'] = formataddr(("SMSGateway", cell + sms_gw))
            else:
                to_addr = headers['To'] = formataddr(("SMSGateway", sms_gw))

            info = {'contact':contact,
                    'lab_url':lab_url,
                    'items': ", ".join([ar.getRequestID() for ar in analysis_requests]),
                   }
            message = pmt.createMessage('bika', 'sms', info, headers)
            sendmail(portal, from_addr, (to_addr,), message)

        to_addrs = []
        if contact and 'pdf' in contact.getPublicationPreference():
            to_addr = headers['To'] = formataddr(
                (encode_header(contact.getFullname()),
                  contact.getEmailAddress())
            )
            to_addrs.append(to_addr)
            # send copy to lab
            to_addrs.append(from_addr)

            to_addrs = tuple(to_addrs)
            mail_subject = get_mail_subject(sorted_ars)
            info = {'contact':contact,
                    'analysis_requests': sorted_ars,
                    'mail_subject': mail_subject,
                    'output': 'file',
                    'laboratory': lab,
                    }

            results_file = {}
            pdft = context.pdf_build_tool
            results_file = pdft.ar_results_pdf(info)
            attachments = []
            if contact.getAttachmentsPermitted():
                attachments = these_attachments(sorted_ars)
            attachments.append((results_file['file'], 'application/pdf', results_file['file_name']))
            message = pmt.createMessage(
                'bika', 'ar_results_csv', info, headers, text_format = 'html', files = attachments)
            sendmail(portal, from_addr, to_addrs, message)

atapi.registerType(Contact, PROJECTNAME)
