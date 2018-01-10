# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
