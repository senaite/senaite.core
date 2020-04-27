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

from bika.lims.interfaces import IJSONReadExtender, IARTemplate
from zope.component import adapts
from zope.interface import implements


class JSONReadExtender(object):
    """- Place additional information about profile services
    into the returned records.
    Used in AR Add to prevent extra requests
    """

    implements(IJSONReadExtender)
    adapts(IARTemplate)

    def __init__(self, context):
        self.context = context

    def render_template_partitions(self):
        """
        Supplies a more detailed view of the Partitions for this
        template.  It's built to mimic the partitions that are stored in the
        ar_add form state variable, so that when a partition is chosen, there
        is no further translation necessary.

        It combines the Analyses and Partitions AT schema field values.

        For some fields (separate, minvol) there is no information, when partitions
        are specified in the AR Template.

        :return a list of dictionaries like this:

            container
                     []
            container_titles
                     []
            preservation
                     []
            preservation_titles
                     []
            separate
                     false
            minvol
                     "0.0000 m3 "
            services
                     ["2fdc040e05bb42ca8b52e41761fdb795", 6 more...]
            service_titles
                     ["Copper", "Iron", "Magnesium", 4 more...]

        """
        Analyses = self.context.Schema()['Analyses'].get(self.context)
        Parts = self.context.Schema()['Partitions'].get(self.context)
        if not Parts:
            # default value copied in from content/artemplate.py
            Parts = [{'part_id': 'part-1',
                      'Container': '',
                      'Preservation': '',
                      'container_uid': '',
                      'preservation_uid': ''}]
        parts = []
        not_found = set()
        for Part in Parts:
            part = {
                'part_id': Part.get("part_id", "part-1"),
                'container_titles': Part.get("Container", ""),
                'container': Part.get("container_uid", ""),
                'preservation_titles': Part.get("Preservation", ""),
                'preservation': Part.get("preservation_uid", ""),
                'services': [],
                'service_titles': [],
            }
            for analysis in Analyses:
                uid = analysis['service_uid']
                partiton = analysis['partition']
                if partiton == part['part_id']:
                    part['services'].append(uid)
                    part['service_titles'].append(uid)
                    not_found.discard(analysis['service_uid'])
                else:
                    if uid in part['services']:
                        part['services'].remove(uid)
                    if uid in part['service_titles']:
                        part['service_titles'].remove(uid)
                    not_found.add(analysis['service_uid'])

            parts.append(part)

        # all others go into the first part.  Mostly this will be due to
        # partition info not being defined?
        for uid in not_found:
            if uid not in part['services']:
                parts[0]['services'].append(uid)
            if uid not in part['service_titles']:
               parts[0]['service_titles'].append(uid)

        return parts

    def __call__(self, request, data):
        bsc = self.context.bika_setup_catalog
        service_data = []
        for item in self.context.getAnalyses():
            service_uid = item['service_uid']
            service = bsc(UID=service_uid)[0].getObject()
            this_service = {'UID': service.UID(),
                            'Title': service.Title(),
                            'Keyword': service.getKeyword(),
                            'Price': service.getPrice(),
                            'VAT': service.getVAT(),
                            'PointOfCapture': service.getPointOfCapture(),
                            'CategoryTitle': service.getCategory().Title()}
            service_data.append(this_service)
        data['service_data'] = service_data
        data['Partitions'] = self.render_template_partitions()
