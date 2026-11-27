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

import hashlib

from bika.lims import api
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from zExceptions import NotFound

# Seconds the browser uses the site logo before it asks again
LOGO_MAX_AGE = 86400


def get_site_logo():
    """Return the base64 encoded site logo of the SENAITE setup

    :returns: Encoded site logo or None
    """
    setup = api.get_senaite_setup()
    if not setup:
        return None
    return setup.getSiteLogo()


def get_site_logo_version(site_logo):
    """Return a version of the site logo that changes with its contents

    :param site_logo: Encoded site logo of the SENAITE setup
    :returns: Hex digest of the site logo
    """
    return hashlib.md5(site_logo).hexdigest()


class SiteLogo(Download):
    """Sends the site logo of the SENAITE setup
    """

    def __init__(self, context, request):
        super(SiteLogo, self).__init__(context, request)
        self.data = None

    def __call__(self):
        site_logo = get_site_logo()
        if not site_logo:
            raise NotFound("site-logo")

        etag = '"{}"'.format(get_site_logo_version(site_logo))
        response = self.request.response
        response.setHeader("ETag", etag)
        response.setHeader("Cache-Control",
                           "public, max-age={}".format(LOGO_MAX_AGE))
        if self.is_cached(etag):
            response.setStatus(304)
            return ""

        filename, data = b64decode_file(site_logo)
        self.filename = filename
        self.data = NamedImage(data=data, filename=filename)
        return super(SiteLogo, self).__call__()

    def is_cached(self, etag):
        """Checks if the browser has the site logo with this ETag already
        """
        header = self.request.getHeader("If-None-Match")
        if not header:
            return False
        tags = [tag.strip().replace("W/", "") for tag in header.split(",")]
        return etag in tags or "*" in tags

    def _getFile(self):
        return self.data
