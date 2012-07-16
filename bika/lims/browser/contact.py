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
                url = self.request.get_header("referer",
                                              self.context.absolute_url())
                self.request.response.redirect(url)

            form = self.request.form

            contact = self.context

            password = form['password']
            username = form['username']
            confirm = form['confirm']
            email = form['email']

            if not username:
                error('username',
                      PMF("Input is required but not given."))
                return

            if not email:
                error('email',
                      PMF("Input is required but not given."))
                return

            reg_tool = self.context.portal_registration
            properties = self.context.portal_properties.site_properties

##            if properties.validate_email:
##                password = reg_tool.generatePassword()
##            else:
            if password!=confirm:
                error('password',
                      PMF("Passwords do not match."))
                return

            if not password:
                error('password',
                      PMF("Input is required but not given."))
                return

            if not confirm:
                error('password',
                      PMF("Passwords do not match."))
                return

            if len(password) < 5:
                error('password',
                      PMF("Passwords must contain at least 5 letters."))
                return

            try:
                reg_tool.addMember(username,
                                   password,
                                   properties = {
                                       'username': username,
                                       'email': email,
                                       'fullname': username})
            except ValueError, msg:
                error(None, msg)
                return

            contact.setUsername(username)
            contact.setEmailAddress(email)
            contact.reindexObject()

            # If we're being created in a Client context, then give
            # the contact an Owner local role on client.
            if contact.aq_parent.portal_type == 'Client':
                contact.aq_parent.manage_setLocalRoles( username, ['Owner',] )
                if hasattr(aq_base(contact.aq_parent), 'reindexObjectSecurity'):
                    contact.aq_parent.reindexObjectSecurity()

                # add user to Clients group
                group=self.context.portal_groups.getGroupById('Clients')
                group.addMember(username)

            if properties.validate_email or self.request.get('mail_me', 0):
                reg_tool.registeredNotify(username)

            message = PMF("Member registered.")
            self.context.plone_utils.addPortalMessage(message, 'info')
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i
