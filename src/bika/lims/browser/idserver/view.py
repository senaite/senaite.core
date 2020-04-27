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

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.idserver import get_config
from bika.lims.numbergenerator import INumberGenerator
from plone import protect
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implements


class IIDserverView(Interface):
    """IDServerView
    """


class IDServerView(BrowserView):
    """ This browser view is to house ID Server related functions
    """
    implements(IIDserverView)
    template = ViewPageTemplateFile("templates/numbergenerator.pt")

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        protect.CheckAuthenticator(self.request.form)

        self.portal = api.get_portal()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_border', 1)

        # Handle form submit
        form = self.request.form
        submitted = form.get("submitted", False)

        # nothing to do here
        if not submitted:
            return self.template()

        # Handle "Seed" action
        if form.get("seed", False):
            seeds = form.get("seeds", {})
            for key, value in seeds.items():
                value = api.to_int(value, None)
                message = ""
                if value is None:
                    message = _("Could not convert '{}' to an integer"
                                .format(value))
                elif value == 0:
                    del self.storage[key]
                    message = _("Removed key {} from storage".format(key))
                else:
                    self.set_seed(key, value)
                    message = _("Seeding key {} to {}".format(key, value))
                self.add_status_message(message, "info")

        return self.template()

    def get_id_template_for(self, key):
        """Get a preview of the next number
        """
        portal_type = key.split("-")[0]
        config = get_config(None, portal_type=portal_type)
        return config.get("form", "")

    @property
    def storage(self):
        number_generator = getUtility(INumberGenerator)
        return number_generator.storage

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def set_seed(self, key, value):
        """Set a number of the number generator
        """
        number_generator = getUtility(INumberGenerator)
        return number_generator.set_number(key, api.to_int(value))

    def seed(self):
        """ Reset the number from which the next generated sequence start.
            If you seed at 100, next seed will be 101
        """
        form = self.request.form
        prefix = form.get('prefix', None)
        if prefix is None:
            return 'No prefix provided'
        seed = form.get('seed', None)
        if seed is None:
            return 'No seed provided'
        if not seed.isdigit():
            return 'Seed must be a digit'
        seed = int(seed)
        if seed < 0:
            return 'Seed cannot be negative'

        new_seq = self.set_seed(prefix, seed)
        return 'IDServerView: "%s" seeded to %s' % (prefix, new_seq)
