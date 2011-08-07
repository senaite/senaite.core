""" View utilities.
"""
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import *
from AccessControl.User import *

class ViewAsUser(BrowserView):
    """ render a context with the roles and permissions of a certain user.
          user=username
    """
    def __call__(self):
        """Login the user"""
        if 'user' in self.request.keys():
            self.errors = {}
            user = self.request['user']
            if user not in [member['username'] for member in self.members()]:
                self.errors['user'] = user
                return
            acl_users = getToolByName(self.context, 'acl_users')
            # newSecurityManager/getSecurityManager/setSecurityManager
            acl_users.session._setupSession(user, self.request.RESPONSE)
            page = self.context()
            acl_users.session._setupSession('admin', self.request.RESPONSE)
            return page

    def members(self):
        membership = getToolByName(self.context, 'portal_membership')
        members = membership.listMembers()
        results = []
        for member in members:
            results.append({'username': member.id,
                            'fullname': member.getProperty('fullname')})
        return results
