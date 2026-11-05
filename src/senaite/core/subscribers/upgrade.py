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

from senaite.core import logger
from senaite.core.api.catalog import get_damaged_objects


def before_upgrade_step(event):
    """Start the list of damaged objects of the upgrade step
    """
    del get_damaged_objects()[:]


def after_upgrade_step(event):
    """List the objects the upgrade step skipped because they cannot be loaded
    """
    damaged = get_damaged_objects()
    if not damaged:
        return
    logger.error("The upgrade step skipped {} objects that cannot be "
                 "loaded:".format(len(damaged)))
    for path, reason in damaged:
        logger.error("  {} ({})".format(path, reason))
    del damaged[:]
