## Script (Python) "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##
REQUEST=context.REQUEST

# If someone has something on their clipboard, expire it.
if REQUEST.get('__cp', None) is not None:
    REQUEST.RESPONSE.expireCookie('__cp', path='/')

membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return state.set(status='failure', portal_status_message='Login failed')

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
initial_login = int(str(login_time) == '2000/01/01')
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

if initial_login:
    state.set(status='initial_login')
elif  must_change_password:
    state.set(status='change_password')

membership_tool.setLoginTimes()
membership_tool.createMemberArea()

groups_tool=context.portal_groups
member_groups = [groups_tool.getGroupById(group.id).getGroupName() 
                 for group in groups_tool.getGroupsByUserId(member.id)]

if 'clients' in member_groups:
    for obj in context.clients.objectValues():
        if member.id in obj.users_with_local_role('Owner'):
            dest = obj.absolute_url()
            break
elif 'labtechnicians' in member_groups:
    dest = context.worksheets.absolute_url()


return state
