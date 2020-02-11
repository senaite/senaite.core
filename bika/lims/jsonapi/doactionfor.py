# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.jsonapi.read import read
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
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
            ("/doActionFor_many", "doActionFor_many", self.do_action_for_many, dict(methods=['GET', 'POST'])),
        )

    def do_action_for(self, context, request):
        """/@@API/doActionFor: Perform workflow transition on values returned
        by jsonapi "read" function.

        Required parameters:

            - action: The workflow transition to apply to found objects.

        Parameters used to locate objects are the same as used for the "read"
        method.

        """
        savepoint = transaction.savepoint()
        workflow = getToolByName(context, 'portal_workflow')
        uc = getToolByName(context, 'uid_catalog')

        action = request.get('action', '')
        if not action:
            raise BadRequest("No action specified in request")

        ret = {
            "url": router.url_for("doActionFor", force_external=True),
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
                obj.reindexObject()
            except Exception as e:
                savepoint.rollback()
                msg = "Cannot execute '{0}' on {1} ({2})".format(
                    action, obj, e.message)
                msg = msg.replace("${action_id}", action)
                raise BadRequest(msg)
        return ret


    def do_action_for_many(self, context, request):
        """/@@API/doActionFor: Perform workflow transition on a list of objects.

        required parameters:

            - obj_paths: a json encoded list of objects to transition.
            - action: the id of the transition

        """
        savepoint = transaction.savepoint()
        workflow = getToolByName(context, 'portal_workflow')
        site_path = request['PATH_INFO'].replace("/@@API/doActionFor_many", "")

        obj_paths = json.loads(request.get('f', '[]'))
        action = request.get('action', '')
        if not action:
            raise BadRequest("No action specified in request")

        ret = {
            "url": router.url_for("doActionFor_many", force_external=True),
            "success": True,
            "error": False,
        }

        for obj_path in obj_paths:
            if not obj_path.startswith("/"):
                obj_path = "/" + obj_path
            obj = context.restrictedTraverse(str(site_path + obj_path))
            if obj_path.startswith(site_path):
                obj_path = obj_path[len(site_path):]
            try:
                workflow.doActionFor(obj, action)
                obj.reindexObject()
            except Exception as e:
                savepoint.rollback()
                msg = "Cannot execute '{0}' on {1} ({2})".format(
                    action, obj, e.message)
                msg = msg.replace("${action_id}", action)
                raise BadRequest(msg)
        return ret
