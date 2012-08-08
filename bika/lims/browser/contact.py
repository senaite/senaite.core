from Acquisition import aq_parent, aq_inner, aq_base
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import json

class ContactLoginDetailsView(BrowserView):
    """ The contact login details edit
    """
    template = ViewPageTemplateFile("templates/login_details.pt")

    def __call__(self):

        if self.request.form.has_key("submitted"):

            def error(field, message):
                if field:
                    message = "%s: %s" % (field, message)
                self.context.plone_utils.addPortalMessage(message, 'error')
                return self.template()

            form = self.request.form
            contact = self.context

            password = form.get('password', '')
            username = form.get('username', '')
            confirm = form.get('confirm', '')
            email = form.get('email', '')

            if not username:
                return error('username', PMF("Input is required but not given."))

            if not email:
                return error('email', PMF("Input is required but not given."))

            reg_tool = self.context.portal_registration
            properties = self.context.portal_properties.site_properties

##            if properties.validate_email:
##                password = reg_tool.generatePassword()
##            else:
            if password!=confirm:
                return error('password', PMF("Passwords do not match."))

            if not password:
                return error('password', PMF("Input is required but not given."))

            if not confirm:
                return error('password', PMF("Passwords do not match."))

            if len(password) < 5:
                return error('password', PMF("Passwords must contain at least 5 letters."))

            try:
                reg_tool.addMember(username,
                                   password,
                                   properties = {
                                       'username': username,
                                       'email': email,
                                       'fullname': username})
            except ValueError, msg:
                return error(None, msg)

            contact.setUsername(username)
            contact.setEmailAddress(email)

            # If we're being created in a Client context, then give
            # the contact an Owner local role on client.
            if contact.aq_parent.portal_type == 'Client':
                contact.aq_parent.manage_setLocalRoles( username, ['Owner',] )
                if hasattr(aq_base(contact.aq_parent), 'reindexObjectSecurity'):
                    contact.aq_parent.reindexObjectSecurity()

                # add user to Clients group
                group=self.context.portal_groups.getGroupById('Clients')
                group.addMember(username)

            contact.reindexObject()

            if properties.validate_email or self.request.get('mail_me', 0):
                try:
                    reg_tool.registeredNotify(username)
                except:
                    import transaction
                    transaction.abort()
                    return error(
                        None, PMF("SMTP server disconnected."))



            message = PMF("Member registered.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            return self.template()
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i
