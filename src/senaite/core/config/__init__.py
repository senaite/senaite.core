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

PROFILE_ID = "profile-senaite.core:default"
PROJECTNAME = "senaite.core"

# Tagged value on a schema, mapping a field name to the heading drawn
# above it on the edit form. The field named is the first of its
# section.
#
# Fieldsets do not nest: plone.supermodel's Fieldset holds a flat list
# of field names, so a tab of twenty settings could otherwise only be
# broken up by making more tabs, which scatters settings that belong
# together.
FIELDSET_SECTIONS = "senaite.core.fieldset_sections"
