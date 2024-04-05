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

    @property
    def worksheet_print_templates_order(self):
        """ Computing getter for this registry field.
            Updating the list of templates based on data from the registry
            and new templates founded in configured directories
            and not saved in the registry.

        :returns: The ordered list of templates
        """

        all_templates = []
        directory_iterator = iterDirectoriesOfType(WS_TEMPLATES_ADDON_DIR)
        directories = sorted(directory_iterator, key=lambda d: d.__name__)
        for resource in directories:
            prefix = resource.__name__
            templates = [tpl for tpl in resource.listDirectory() if tpl.endswith(".pt")]
            for template in sorted(templates):
                all_templates.append("{0}:{1}".format(prefix, template))

        # Get the ordered list of templates from the parent class
        order = self.__getattr__("worksheet_print_templates_order") or []

        def sort_templates(item):
            return order.index(item) if item in order else len(order)

        templates = sorted(all_templates, key=sort_templates)
        return list(filter(None, templates))
