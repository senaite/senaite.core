from bika.lims.utils import getUsers
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope import interface
import json
import transaction

class getUsers(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/getusers", "getusers", self.getusers, dict(methods=['GET', 'POST'])),
        )

    def getusers(self, context, request):
        """/@@API/getusers: Return users belonging to specified roles

        Required parameters:

            - roles: The role of which users to return

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
            users: list of dictionaries: {fullname: fullname, userid: userid}
        }
        
        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/getusers?roles:list=Manager&roles:list=Analyst")
        >>> browser.contents
        '{...test_labmanager1...}'
        >>> browser.contents
        '{...test_analyst1...}'
        
        >>> browser.open(portal_url+"/@@API/getusers")
        >>> browser.contents
        'No roles specified'
        """
        roles = request.get('roles','')

        if len(roles) == 0:
            raise BadRequest("No roles specified")
        
        mtool = getToolByName(context, 'portal_membership') 
        users = []
        for user in mtool.searchForMembers(roles=roles):
            uid = user.getId()
            fullname = user.getProperty('fullname')
            if not fullname:
                fullname = uid
            users.append({'fullname':fullname, 'userid': uid})
            
        ret = {
            "url": router.url_for("remove", force_external=True),
            "success": True,
            "error": False,
            'users': users,
        }
        return ret
    