from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from bika.lims.permissions import AccessJSONAPI
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from zope import interface


class JSONAPI(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/create", "create", self.create, dict(methods=['GET'])),
        )

    def create(self, context, request):

        obj_path = request.get("obj_path", "")
        if not obj_path:
            raise ValueError("bad or missing obj_path: " + obj_path)
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        obj_id = request.get("obj_id", "")
        if not obj_id:
            raise ValueError("bad or missing obj_id: " + obj_id)
        obj_type = request.get("obj_type", "")
        if not obj_type:
            raise ValueError("bad or missing obj_type: " + obj_type)

        site_path = request['PATH_INFO'].replace("/@@API/create", "")
        parent = context.restrictedTraverse(site_path + obj_path)
        if not getSecurityManager().checkPermission("AccessJSONAPI", parent):
            msg = "You don't have the '{0}' permission on {1}".format(
                AccessJSONAPI, parent.absolute_url())
            raise Unauthorized(msg)
        parent.invokeFactory(obj_type, obj_id)
        obj = parent[obj_id].Schema()
        obj.unmarkCreationFlag()

        ret = {"url": router.url_for("create", force_external=True),
               "success": True}

        schema = obj.Schema()
        fieldnames = [f for f in request.keys() if f in schema]

        for fieldname in fieldnames:
            if fieldname in schema:
                field = schema[fieldname]
                mutator = field.getMutator(obj)
                if mutator and callable(mutator):
                    mutator(request[fieldname])
                accessor = field.getAccessor(obj)
                if accessor and callable(accessor):
                    ret[fieldname] = accessor()

        return ret
