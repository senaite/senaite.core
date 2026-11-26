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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Acquisition.interfaces import IAcquirer
from bika.lims import api
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.interfaces import IFactory
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class TemporaryContext(BrowserView):
    """Browser view that provides a temporary AT/Dexterity context

    The first name of the path is the portal type of the temporary context,
    e.g. `@@temporary_context/Sample`. A second name publishes a view of the
    temporary context with its own permission, e.g.
    `@@temporary_context/Sample/referencewidget_search/search`.
    """

    def __init__(self, context, request):
        super(TemporaryContext, self).__init__(context, request)
        self.portal_type = None

    def publishTraverse(self, request, name):
        """Traverse to the portal type and then to a view of the temporary
        context
        """
        if self.portal_type is None:
            self.portal_type = name
            return self
        context = self.create_temporary_context(self.portal_type)
        return self.get_view(context, name)

    def get_view(self, context, name):
        """Returns the view with the given name for the context
        """
        if name.startswith("@@"):
            name = name[2:]
        view = queryMultiAdapter((context, self.request), name=name)
        if view is None:
            raise NotFound(self, name, self.request)
        if IAcquirer.providedBy(view):
            view = view.__of__(context)
        return view

    def __call__(self):
        if self.portal_type is None:
            raise NotFound(self, self.__name__, self.request)
        context = self.create_temporary_context(self.portal_type)
        # call the context to return the rendered html
        return context()

    def create_temporary_context(self, portal_type):
        portal_types = api.get_tool("portal_types")
        if portal_type not in portal_types:
            raise TypeError("'%s' is not a valid portal_type" % portal_type)
        fti = portal_types[portal_type]
        tmp_id = "%s_temporary" % portal_type
        if fti.product:
            factory = fti._getFactoryMethod(self.context, check_security=0)
            factory(tmp_id)
            context = self.context[tmp_id]
            # remove the temporary created object
            self.context._delOb(tmp_id)
        else:
            factory = getUtility(IFactory, fti.factory)
            context = factory(tmp_id)
        # hook into acquisition chain
        context = context.__of__(self.context)
        # mark the context as temporary
        api.mark_temporary(context)
        return context
