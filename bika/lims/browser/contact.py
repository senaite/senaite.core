from bika.lims import bikaMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import json

class ContactLoginDetailsView(BrowserView):
    """ The contact login details edit
    """
    template = ViewPageTemplateFile("templates/contact_login_details.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.form.has_key("submitted"):
            return contact_logindetails_submit(self.context, self.request)
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

def contact_logindetails_submit(context, request):

    def missing(field):
        message = context.translate('message_input_required',
            default = 'Input is required but no input given',
            domain='bika')
        errors.append(field + ': ' + message)

    def nomatch(field):
        message = context.translate('passwords_no_match',
            default = 'Passwords do not match',
            domain='bika')
        errors.append(field + ': ' + message)

    def minlimit(field):
        message = context.translate('password_length',
            default = 'Passwords must contain at least 5 characters',
            domain='bika')
        errors.append(field + ': ' + message)

    form = request.form

    if form.has_key("save_button"):
        contact = context
    password = form['password']
    username = form['username']
    confirm = form['confirm']
    email = form['email']
    errors = []

    if not username:
        missing('username')

    if not email:
        missing('email')

    reg_tool = context.portal_registration
    properties = context.portal_properties.site_properties
##    if properties.validate_email:
##        password = reg_tool.generatePassword()
##    else:
    if password!=confirm:
        nomatch('password')
        nomatch('confirm')

    if not password:
        missing('password')

    if not confirm:
        missing('confirm')

    if len(password) < 5:
        minlimit('password')
        minlimit('confirm')

    if errors:
        return json.dumps({'errors':errors})

    try:
        reg_tool.addMember(username,
                           password,
                           properties = {
                               'username': username,
                               'email': email,
                               'fullname': username})
    except ValueError, msg:
        return json.dumps({'errors': [str(msg),]})

    contact.setUsername(username)
    contact.setEmailAddress(email)
    contact.reindexObject()

    # Give contact an Owner local role on client
    pm = getToolByName(contact, 'portal_membership')
    pm.setLocalRoles(context.aq_parent,
                     member_ids=[username],
                     member_role='Owner')

    # add user to Clients group
    group=context.portal_groups.getGroupById('Clients')
    group.addMember(username)

##    if properties.validate_email or request.get('mail_me', 0):
##        reg_tool.registeredNotify(username)

    message = "Registered"
    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})

