# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility

from plone import protect

from bika.lims import api
from bika.lims import logger
from bika.lims.idserver import get_config
from bika.lims.idserver import get_current_year
from bika.lims import bikaMessageFactory as _
from bika.lims.numbergenerator import INumberGenerator


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
                value = self.to_int(value)
                message = ""
                if value == 0:
                    del self.storage[key]
                    message = _("Removed key {} from storage".format(key))
                else:
                    self.set_seed(key, value)
                    message = _("Seeding key {} to {}".format(key, value))
                self.add_status_message(message, "info")

        # Handle "Flush" action
        if form.get("flush", False):
            message = _("Flushed Number Storage")
            self.add_status_message(message, "warning")
            self.flush()
            return self.template()

        return self.template()

    def get_next_id_for(self, key):
        """Get a preview of the next number
        """
        portal_type = key.split("-")[0]
        config = get_config(None, portal_type=portal_type)
        id_template = config.get("form", "")
        number = self.storage.get(key) + 1
        spec = {
            "seq": number,
            "year": get_current_year(),
            "sample": "Sample",
            "sampleId": "SampleId",
            "sampleType": key.replace(portal_type, "").strip("-"),
        }
        return id_template.format(**spec)

    @property
    def storage(self):
        number_generator = getUtility(INumberGenerator)
        return number_generator.storage

    def to_int(self, number, default=0):
        """Returns an integer
        """
        try:
            return int(number)
        except (KeyError, ValueError):
            return self.to_int(default, 0)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def set_seed(self, key, value):
        """Set a number of the number generator
        """
        number_generator = getUtility(INumberGenerator)
        return number_generator.set_number(key, self.to_int(value))

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

    def flush(self):
        """ Flush the storage
        """
        number_generator = getUtility(INumberGenerator)
        number_generator.flush()
        return "IDServerView: Number storage flushed!"
