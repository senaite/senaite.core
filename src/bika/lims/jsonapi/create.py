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

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from bika.lims.idserver import renameAfterCreation
from bika.lims.jsonapi import set_fields_from_request
from bika.lims.permissions import AccessJSONAPI
from bika.lims.utils import tmpID
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import _createObjectByType
from zExceptions import BadRequest
from zope import event
from zope import interface

import transaction

class Create(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        self.context = context
        self.request = request

    @property
    def routes(self):
        return (
            ("/create", "create", self.create, dict(methods=['GET', 'POST'])),
        )


    def create(self, context, request):
        """/@@API/create: Create new object.

        Required parameters:

            - obj_type = portal_type of new object.
            - obj_path = path of new object, from plone site root. - Not required for
             obj_type=AnalysisRequest

        Optionally:

            - obj_id = ID of new object.

        All other parameters in the request are matched against the object's
        Schema.  If a matching field is found in the schema, then the value is
        taken from the request and sent to the field's mutator.

        Reference fields may have their target value(s) specified with a
        delimited string query syntax, containing the portal_catalog search:

            <FieldName>=index1:value1|index2:value2

        eg to set the Client of a batch:

            ...@@API/update?obj_path=<path>...
            ...&Client=title:<client_title>&...

        And, to set a multi-valued reference, these both work:

            ...@@API/update?obj_path=<path>...
            ...&InheritedObjects:list=title:AR1...
            ...&InheritedObjects:list=title:AR2...

            ...@@API/update?obj_path=<path>...
            ...&InheritedObjects[]=title:AR1...
            ...&InheritedObjects[]=title:AR2...

        The Analysis_Specification parameter is special, it mimics
        the format of the python dictionaries, and only service Keyword
        can be used to reference services.  Even if the keyword is not
        actively required, it must be supplied:

            <service_keyword>:min:max:error tolerance

        The function returns a dictionary as a json string:

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
        }

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        Simple AR creation, no obj_path parameter is required:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "Client=portal_type:Client|id:client-1",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "Services:list=portal_type:AnalysisService|title:Copper",
        ... "Services:list=portal_type:AnalysisService|title:Magnesium",
        ... "SamplingDate=2013-09-29",
        ... "Specification=portal_type:AnalysisSpec|title:Apple Pulp",
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        If some parameters are specified and are not located as existing fields or properties
        of the created instance, the create should fail:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create?", "&".join([
        ... "obj_type=Batch",
        ... "obj_path=/batches",
        ... "title=Test",
        ... "Thing=Fish"
        ... ]))
        >>> browser.contents
        '{...The following request fields were not used: ...Thing...}'

        Now we test that the AR create also fails if some fields are spelled wrong

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "thing=Fish",
        ... "Client=portal_type:Client|id:client-1",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "Services:list=portal_type:AnalysisService|title:Copper",
        ... "Services:list=portal_type:AnalysisService|title:Magnesium",
        ... "SamplingDate=2013-09-29"
        ... ]))
        >>> browser.contents
        '{...The following request fields were not used: ...thing...}'

        """
        savepoint = transaction.savepoint()
        self.context = context
        self.request = request
        self.unused = [x for x in self.request.form.keys()]
        self.used("form.submitted")
        self.used("__ac_name")
        self.used("__ac_password")
        # always require obj_type
        self.require("obj_type")
        obj_type = self.request['obj_type']
        self.used("obj_type")
        # AnalysisRequest shortcut: creates Sample, Partition, AR, Analyses.
        if obj_type == "AnalysisRequest":
            raise BadRequest("Creation of Analysis Request through JSON API is "
                             "not supported. Request aborted.")
        # Other object types require explicit path as their parent
        self.require("obj_path")
        obj_path = self.request['obj_path']
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        self.used("obj_path")
        site_path = request['PATH_INFO'].replace("/@@API/create", "")
        parent = context.restrictedTraverse(str(site_path + obj_path))
        # normal permissions still apply for this user
        if not getSecurityManager().checkPermission(AccessJSONAPI, parent):
            msg = "You don't have the '{0}' permission on {1}".format(
                AccessJSONAPI, parent.absolute_url())
            raise Unauthorized(msg)

        obj_id = request.get("obj_id", "")
        _renameAfterCreation = False
        if not obj_id:
            _renameAfterCreation = True
            obj_id = tmpID()
        self.used(obj_id)

        ret = {
            "url": router.url_for("create", force_external=True),
            "success": True,
            "error": False,
        }

        try:
            obj = _createObjectByType(obj_type, parent, obj_id)
            obj.unmarkCreationFlag()
            if _renameAfterCreation:
                renameAfterCreation(obj)
            ret['obj_id'] = obj.getId()
            ret['obj_uid'] = obj.UID()
            used_fields = set_fields_from_request(obj, request)
            for field in used_fields:
                self.used(field)
            obj.reindexObject()
            obj.aq_parent.reindexObject()
            event.notify(ObjectInitializedEvent(obj))
            obj.at_post_create_script()
        except:
            savepoint.rollback()
            raise

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
