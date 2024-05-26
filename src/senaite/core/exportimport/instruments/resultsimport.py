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

from zope import deprecation

from senaite.core.exportimport.instruments.parser import InstrumentResultsFileParser  # noqa: F401, E501
from senaite.core.exportimport.instruments.parser import InstrumentCSVResultsFileParser  # noqa: F401, E501
from senaite.core.exportimport.instruments.parser import InstrumentTXTResultsFileParser  # noqa: F401, E501
from senaite.core.exportimport.instruments.importer import AnalysisResultsImporter  # noqa: F401, E501

deprecation.deprecated(
    "AnalysisResultsImporter",
    "Moved to senaite.core.exportimport.instruments.importer")

deprecation.deprecated(
    "InstrumentResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentCSVResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentTXTResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")
