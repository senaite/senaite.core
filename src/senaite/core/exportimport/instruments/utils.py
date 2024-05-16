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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import re

from bika.lims import api


def format_keyword(keyword):
    """Removes special characters from a keyword.

    Analysis Services must have this kind of keywords. E.g. if assay name from
    the Instrument is 'HIV-1 2.0', an AS must be created on Bika with the
    keyword 'HIV120'
    """
    result = ""
    if keyword:
        result = re.sub(r"\W", "", keyword)
        result = re.sub("_", "", result)
    return result


def get_instrument_import_override(override):
    over = [False, False]
    if override == "nooverride":
        over = [False, False]
    elif override == "override":
        over = [True, False]
    elif override == "overrideempty":
        over = [True, True]
    return over


def get_instrument_import_ar_allowed_states(allowed_state):
    status = ["sample_received", "to_be_verified"]
    if allowed_state == "received":
        status = ["sample_received"]
    elif allowed_state == "received_tobeverified":
        status = ["sample_received", "to_be_verified"]
    return status


def get_instrument_results_file(request=None):
    if request is None:
        request = api.get_request()
    return request.form.get("instrument_results_file")


def get_instrument_results_file_format(request=None):
    if request is None:
        request = api.get_request()
    return request.form.get("instrument_results_file_format")


def get_results_override(request=None):
    if request is None:
        request = api.get_request()
    return request.form.get("results_override")


def get_artoapply(request=None):
    if request is None:
        request = api.get_request()
    return request.form.get("artoapply")


def get_instrument(request=None):
    if request is None:
        request = api.get_request()
    return request.form.get("artoapply")
