## Controller Python Script "edit_login_details"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm', came_from_prefs=None
##title=Register a User
##
from ZODB.POSException import ConflictError

REQUEST=context.REQUEST

portal_registration=context.portal_registration
site_properties=context.portal_properties.site_properties

username = REQUEST['username']

password=REQUEST.get('password') or portal_registration.generatePassword()
portal_registration.addMember(username, password, properties=REQUEST)

context.setUsername(username)
context.setEmailAddress(REQUEST['email'])
context.reindexObject()
# Give contact an Owner local role on client
pm = context.portal_membership
pm.setLocalRoles( obj=context.aq_parent, member_ids=[username],
    member_role='Owner')

# add user to clients group 
group=context.portal_groups.getGroupById('clients')
group.addMember(username)

if site_properties.validate_email or REQUEST.get('mail_me', 0):
    try:
        portal_registration.registeredNotify(username)
    except ConflictError:
        raise
    except Exception, err: 

        #XXX registerdNotify calls into various levels.  Lets catch all exceptions.
        #    Should not fail.  They cant CHANGE their password ;-)  We should notify them.
        #
        # (MSL 12/28/03) We also need to delete the just made member and return to the join_form.
               
        state.setError('email', 'We were unable to send your password to your email address: '+str(err))
        state.set(came_from='logged_in')
        context.acl_users.userFolderDelUsers([username,])
        return state.set(status='failure', portal_status_message='Please enter a valid email address.')
        
state.set(portal_status_message=REQUEST.get('portal_status_message', 'Registered.'))
state.set(came_from=REQUEST.get('came_from','logged_in'))

if came_from_prefs:
    state.set(status='prefs')

from Products.CMFPlone import transaction_note
transaction_note('%s registered' % username)

return state
