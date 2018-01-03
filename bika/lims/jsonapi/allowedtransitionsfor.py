# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

from Products.CMFCore.utils import getToolByName
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from zExceptions import BadRequest
from zope.interface import implements


class allowedTransitionsFor(object):
    implements(IRouteProvider)

    def initialize(self, context, request):
        self.context = context
        self.request = request

    @property
    def routes(self):
        return (
            ("/allowedTransitionsFor_many", "allowedTransitionsFor_many",
                self.allowed_transitions_for_many,
                dict(methods=['GET', 'POST'])),
        )

    def allowed_transitions_for_many(self, context, request):
        """/@@API/allowedTransitionsFor_many: Returns a list of dictionaries. Each
        dictionary has the following structure:
            {'uid': <uid_object_passed_in>,
             'transitions': [{'id': action_id, 'title': 'Action Title'}, 
                             {...}]
        
        Required parameters:
            - uid: uids of the objects to get the allowed transitions from
        """
        wftool = getToolByName(context, "portal_workflow")
        uc = getToolByName(context, 'uid_catalog')
        uids = json.loads(request.get('uid', '[]'))
        if not uids:
            raise BadRequest("No object UID specified in request")

        allowed_transitions = []
        try:
            brains = uc(UID=uids)
            for brain in brains:
                obj = brain.getObject()
                trans = [{'id': t['id'], 'title': t['title']} for t in
                         wftool.getTransitionsFor(obj)]
                allowed_transitions.append(
                    {'uid': obj.UID(), 'transitions': trans})
        except Exception as e:
            msg = "Cannot get the allowed transitions ({})".format(e.message)
            raise BadRequest(msg)

        ret = {
            "url": router.url_for("allowedTransitionsFor_many",
                                  force_external=True),
            "success": True,
            "error": False,
            "transitions": allowed_transitions
        }
        return ret
