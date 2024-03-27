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

from bika.lims.config import WS_TEMPLATES_ADDON_DIR

from senaite.core.interfaces import ISenaiteRegistryFactory

from plone.resource.utils import iterDirectoriesOfType
from plone.registry.recordsproxy import RecordsProxy

from zope.interface import implementer


@implementer(ISenaiteRegistryFactory)
class WSTemplatesPrintFactory(RecordsProxy):
    """ Proxy for IWorksheetViewRegistry
    """

    def __init__(self, registry, schema, omitted=(), prefix=None):
        """ Init method
        """
        super(WSTemplatesPrintFactory, self).__init__(registry, schema, omitted, prefix)

    @property
    def worksheet_print_templates_order(self):
        all_templates = []
        directories = sorted(iterDirectoriesOfType(WS_TEMPLATES_ADDON_DIR), key=lambda d: d.__name__)
        for templates_resource in directories:
            prefix = templates_resource.__name__
            templates = [tpl for tpl in templates_resource.listDirectory() if tpl.endswith(".pt")]
            for template in sorted(templates):
                all_templates.append("{0}:{1}".format(prefix, template))

        order = super(WSTemplatesPrintFactory, self).__getattr__("worksheet_print_templates_order") or []
        templates = sorted(all_templates, key=lambda item: order.index(item) if item in order else len(order))
        ordered_templates = filter(lambda item: item, templates)
        return list(ordered_templates)
