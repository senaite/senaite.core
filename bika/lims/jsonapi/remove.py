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