from bika.lims.jsonapi.read import read
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope import interface
import json
import transaction


class Remove(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/remove", "remove", self.remove, dict(methods=['GET', 'POST'])),
        )

    def remove(self, context, request):
        """/@@API/remove: Remove existing object

        Required parameters:

            - UID: UID for the object.

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
        }

        So.

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD
        >>> blah = portal.portal_catalog(Type = "Contact")[-1]
        >>> uid = blah.UID

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/remove?UID="+uid)
        >>> browser.contents
        '{..."success": true...}'
        """

        savepoint = transaction.savepoint()
        uc = getToolByName(context, 'uid_catalog')

        _uid = request.get('UID', '')
        if not _uid:
            raise BadRequest("No UID specified in request")

        ret = {
            "url": router.url_for("remove", force_external=True),
            "success": True,
            "error": False,
        }
        
        data = uc(UID=_uid)
        if not data:
            raise BadRequest("No objects found")
        
        for proxy in data:
            try:
                parent = proxy.getObject().aq_parent
                parent.manage_delObjects([proxy.id])
            except Exception as e:
                savepoint.rollback()
                msg = "Cannot delete '{0}' because ({1})".format(_uid, e.message)
                raise BadRequest(msg)
        return ret
