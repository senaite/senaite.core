# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""
Usage:
bin/zopectl run blis.py <ploneSiteId>
"""

from sys import argv
import transaction

plone = app[argv[1]]



transaction.commit()
