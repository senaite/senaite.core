from bika.lims.jsonapi import set_fields_from_request
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from zExceptions import BadRequest
from zope import interface
import json
import transaction


class Update(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/update", "update", self.update, dict(methods=['GET', 'POST'])),
            ("/update_many", "update_many", self.update_many, dict(methods=['GET', 'POST'])),
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
        }
        obj_path = request.get("obj_path", "")
        if not obj_path:
            raise BadRequest("missing obj_path")
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        site_path = request['PATH_INFO'].replace("/@@API/update", "")
        obj = context.restrictedTraverse(str(site_path + obj_path))

        try:
            set_fields_from_request(obj, request)
        except:
            savepoint.rollback()
            raise

        ret['success'] = True
        ret['error'] = False

        return ret

    def update_many(self, context, request):
        """/@@API/update_many: Update existing object values

        This is a wrapper around the update method, allowing multiple updates
        to be combined into a single request.

        required parameters:

            - input_values: A json-encoded dictionary.
              Each key is an obj_path, and each value is a dictionary
              containing key/value pairs to be set on the object.

        Return value:

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
            updates: return values from update
        }
        """
        ret = {
            "url": router.url_for("update_many", force_external=True),
            "success": False,
            "error": True,
            "updates": [],
        }

        input_values = json.loads(request.get('input_values', '[]'))
        if not input_values:
            raise BadRequest("missing input_values")
        site_path = request['PATH_INFO'].replace("/@@API/update_many", "")

        for obj_path, i in input_values.items():
            savepoint = transaction.savepoint()
            if not obj_path.startswith("/"):
                obj_path = "/" + obj_path
            if obj_path.startswith(site_path):
                obj_path = obj_path[len(site_path):]
            obj = context.restrictedTraverse(str(site_path + obj_path))
            this_ret = {
                "url": router.url_for("update_many", force_external=True),
                "success": False,
                "error": True,
            }
            try:
                set_fields_from_request(obj, i)
            except:
                savepoint.rollback()
                raise
            this_ret['success'] = True
            this_ret['error'] = False
            ret['updates'].append(this_ret)
        ret['success'] = True
        ret['error'] = False
        return ret
