# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""
Usage:
bin/zopectl run blis.py <ploneSiteId>
"""

from sys import argv
import transaction

plone = app[argv[1]]



transaction.commit()
