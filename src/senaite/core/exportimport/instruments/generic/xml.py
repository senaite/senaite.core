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

""" General XML Worksheet exporter and instrument importer
"""
import json

title = "Generic XML"

options = {}

def Export(analyses):
    """ Write analyses to an XML file
    """
    return "aaa"

def Import(context, request):
    """ Read analysis results from an XML string
    """
    errors = []
    logs = []

    # Do import stuff here
    logs.append("Generic XML Import is not available")

    results = {'errors': errors, 'log': logs}
    return json.dumps(results)
