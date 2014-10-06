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

        So.

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        Update a client's existing address:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/update?", "&".join([
        ... "obj_path=/clients/client-1",
        ... "title=Test",
        ... "PostalAddress={'address': '1 Wendy Way', 'city': 'Johannesburg', 'zip': '9000', 'state': 'Gauteng', 'district': '', 'country':'South Africa'}"
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        quickly check that it saved:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/read?", "&".join([
        ... "id=client-1",
        ... "include_fields=PostalAddress",
        ... ]))
        >>> browser.contents
        '{...1 Wendy Way...}'

        Try the same with a nonsense fieldname:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/update?", "&".join([
        ... "obj_path=/clients/client-1",
        ... "Thing=Fish",
        ... ]))
        >>> browser.contents
        '{...The following request fields were not used: ...Thing...}'

        Setting the value of a RefereceField to "" or None (null) should not cause
        an error; setting an empty value should clear the field

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/update?", "&".join([
        ... "obj_path=/clients/client-1",
        ... 'DefaultCategories=',
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        """
        savepoint = transaction.savepoint()
        self.context = context
        self.request = request
        self.unused = [x for x in self.request.form.keys()]
        self.used("form.submitted")
        self.used("__ac_name")
        self.used("__ac_password")
        ret = {
            "url": router.url_for("update", force_external=True),
            "success": False,
            "error": True,
        }
        # always require obj_path
        self.require("obj_path")
        obj_path = self.request['obj_path']
        self.used("obj_path")

        site_path = request['PATH_INFO'].replace("/@@API/update", "")
        obj = context.restrictedTraverse(str(site_path + obj_path))

        try:
            fields = set_fields_from_request(obj, request)
            for field in fields:
                self.used(field)
        except:
            savepoint.rollback()
            raise

        ret['success'] = True
        ret['error'] = False

        if self.unused:
            raise BadRequest("The following request fields were not used: %s.  Request aborted." % self.unused)

        return ret


    def require(self, fieldname, allow_blank=False):
        """fieldname is required"""
        if self.request.form and fieldname not in self.request.form.keys():
            raise Exception("Required field not found in request: %s" % fieldname)
        if self.request.form and (not self.request.form[fieldname] or allow_blank):
            raise Exception("Required field %s may not have blank value")


    def used(self, fieldname):
        """fieldname is used, remove from list of unused fields"""
        if fieldname in self.unused:
            self.unused.remove(fieldname)


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
        self.context = context
        self.request = request
        self.unused = [x for x in self.request.form.keys()]
        self.used("form.submitted")
        self.used("__ac_name")
        self.used("__ac_password")
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
