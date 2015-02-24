## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from bika.lims.utils import logged_in_client
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
REQUEST=context.REQUEST

membership_tool=getToolByName(context, 'portal_membership')
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    email_login = getToolByName(
        context, 'portal_properties').site_properties.getProperty('use_email_as_login')
    if email_login:
        context.plone_utils.addPortalMessage(_(u'Login failed. Both email address and password are case sensitive, check that caps lock is not enabled.'), 'error')
    else:
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
    return state.set(status='failure')

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
initial_login = int(str(login_time) == '2000/01/01')
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

if initial_login:
    state.set(status='initial_login')
elif must_change_password:
    state.set(status='change_password')

membership_tool.loginUser(REQUEST)

client = logged_in_client(context, member)
registry = getUtility(IRegistry)
if 'bika.lims.client.default_landing_page' in registry:
    landing_page = registry['bika.lims.client.default_landing_page']
else:
    landing_page = 'analysisrequests'

if client:
    url = client.absolute_url() + "/" + landing_page
    return context.REQUEST.response.redirect(url)

groups_tool=context.portal_groups
member_groups = [groups_tool.getGroupById(group.id).getGroupName()
                 for group in groups_tool.getGroupsByUserId(member.id)]

groups_tool=context.portal_groups
member_groups = [groups_tool.getGroupById(group.id).getGroupName()
                 for group in groups_tool.getGroupsByUserId(member.id)]

if 'Analysts' in member_groups:
    url = context.worksheets.absolute_url()
    return context.REQUEST.RESPONSE.redirect(url)

elif 'Samplers' in member_groups:
    # We only route to the to_be_sampled list if there are
    # sample partitions waiting to be "sampled".
    bsc = getToolByName(context, 'bika_setup_catalog')
    url = context.samples.absolute_url()
    if bsc(portal_type='SamplePartition', review_state='to_be_sampled'):
        url += "/list_review_state=to_be_sampled"
    return context.REQUEST.RESPONSE.redirect(url)

return state
