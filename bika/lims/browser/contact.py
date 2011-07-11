from bika.lims import bikaMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import json

class ContactLoginDetailsView(BrowserView):
    """ The contact login details edit
    """
    template = ViewPageTemplateFile("templates/contact_login_details.pt")

    def __init__(self, context, request):
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
        errors[field] = field + ': ' + message

    def nomatch(field):
        message = context.translate('passwords_no_match',
            default = 'Passwords do not match',
            domain='bika')
        errors[field] = field + ': ' + message

    def minlimit(field):
        message = context.translate('password_length',
            default = 'Passwords must contain at least 5 characters',
            domain='bika')
        errors[field] = field + ': ' + message

    form = request.form

    if form.has_key("save_button"):
        contact = context
    password = form['password']
    username = form['username']
    confirm = form['confirm']
    email = form['email']
    errors = {}

    if not username:
        missing('username')

    if not email:
        missing('email')

    reg_tool = context.portal_registration
    properties = context.portal_properties.site_properties
    if properties.validate_email:
        password = reg_tool.generatePassword()
    else:
        if password!=confirm:
            nomatch('password')
            nomatch('confirm')

        if not password:
            missing('password')

        if not confirm:
            missing('confirm')
        
        if not errors.has_key('password'):
            if len(password) < 5:
                minlimit('password')
                minlimit('confirm')


    if not errors.has_key('username') and not reg_tool.isMemberIdAllowed(username):
        message = context.translate('login_in_use',
            default = 'The login name you selected is already in use or is not valid. Please choose another',
            domain='bika')
        errors['username'] = 'username: ' + message


    if errors:
        return json.dumps({'errors':errors})

    reg_tool.addMember(username, password, properties=request)
    contact.setUsername(username)
    contact.setEmailAddress(email)
    contact.reindexObject()

    # Give contact an Owner local role on client
    pm = context.portal_membership
    pm.setLocalRoles( obj=context.aq_parent, member_ids=[username],
        member_role='Owner')

    # add user to clients group 
    group=context.portal_groups.getGroupById('clients')
    group.addMember(username)

    if properties.validate_email or request.get('mail_me', 0):
        try:
            reg_tool.registeredNotify(username)
        except ConflictError:
            raise
        except Exception, err: 

            #XXX registerdNotify calls into various levels.  Lets catch all exceptions.
            #    Should not fail.  They cant CHANGE their password ;-)  We should notify them.
            #
            # (MSL 12/28/03) We also need to delete the just made member and return to the join_form.
               


            message = context.translate('email_invalid',
                default = 'We were unable to send your password to your email address: %s. Please enter a valid email address' %s(err),
                domain='bika')
            errors['email'] = 'email: ' + message

    if errors:
        return json.dumps({'errors':errors})

    message = "Registered"
    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})

