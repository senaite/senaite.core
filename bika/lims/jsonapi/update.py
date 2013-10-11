from bika.lims.jsonapi import set_fields_from_request
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from zExceptions import BadRequest
from zope import interface
import transaction

class Update(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/update", "update", self.update, dict(methods=['GET', 'POST'])),
        )

    def update(self, context, request):
        """/@@API/update: Update existing object values

        Required parameters:

            - obj_path: path to the object, relative to plone site root.
            - fields: json value, dict: key:value = fieldname:value.

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
            <fieldname>: <current value>
            ...
        }
        """
        savepoint = transaction.savepoint()

        ret = {
            "url": router.url_for("update", force_external=True),
            "success": False,
            "error": True,
            "objects": [],
        }
        obj_path = request.get("obj_path", "")
        if not obj_path:
            raise BadRequest("missing obj_path")
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        site_path = request['PATH_INFO'].replace("/@@API/update", "")
        obj = context.restrictedTraverse(site_path + obj_path)

        try:
            set_fields_from_request(obj, request)
        except:
            savepoint.rollback()
            raise

        ret['success'] = True
        ret['error'] = False

        return ret
