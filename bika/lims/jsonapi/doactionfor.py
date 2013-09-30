from bika.lims.jsonapi.read import read
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope import interface

import json
import transaction


class doActionFor(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/doActionFor", "doActionFor", self.do_action_for, dict(methods=['GET', 'POST'])),
        )

    def do_action_for(self, context, request):
        """/@@API/doActionFor: Perform workflow transition on values returned by jsonapi "read" function.

        Parameters used to locate objects are the same as used for the "read" method.

        Additional parameters:

            - action: The workflow transition to apply to found objects.

        """
        savepoint = transaction.savepoint()
        workflow = getToolByName(context, 'portal_workflow')
        uc = getToolByName(context, 'uid_catalog')

        action = request.get('action', '')
        if not action:
            raise BadRequest("No action specified in request")

        ret = {
            "url": router.url_for("read", force_external=True),
            "success": True,
            "error": False,
        }

        data = read(context, request)
        objects = data.get('objects', [])
        if len(objects) == 0:
            raise BadRequest("No matching objects found")
        for obj_dict in objects:
            try:
                obj = uc(UID=obj_dict['UID'])[0].getObject()
                workflow.doActionFor(obj, action)
            except Exception as e:
                savepoint.rollback()
                msg = "Cannot execute '{0}' on {1} ({2})".format(
                    action, obj, e.message)
                msg = msg.replace("${action_id}", action)
                raise BadRequest(msg)
        return ret
