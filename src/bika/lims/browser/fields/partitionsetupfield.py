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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8 as _c
from magnitude import mg
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Registry import registerField
from Products.CMFCore.utils import getToolByName
from senaite.core.browser.fields.records import RecordsField


def getContainers(instance,
                  minvol=None,
                  allow_blank=True,
                  show_container_types=True,
                  show_containers=True):
    """ Containers vocabulary

    This is a separate class so that it can be called from ajax to filter
    the container list, as well as being used as the AT field vocabulary.

    Returns a tuple of tuples: ((object_uid, object_title), ())

    If the partition is flagged 'Separate', only containers are displayed.
    If the Separate flag is false, displays container types.

    XXX bsc = self.portal.senaite_catalog_setup
    XXX obj = bsc(getKeyword='Moist')[0].getObject()
    XXX u'Container Type: Canvas bag' in obj.getContainers().values()
    XXX True

    """

    bsc = getToolByName(instance, 'senaite_catalog_setup')

    items = [['', _('Any')]] if allow_blank else []

    containers = []
    for container in bsc(portal_type='Container', sort_on='sortable_title'):
        container = container.getObject()

        # verify container capacity is large enough for required sample volume.
        if minvol is not None:
            capacity = container.getCapacity()
            try:
                capacity = capacity.split(' ', 1)
                capacity = mg(float(capacity[0]), capacity[1])
                if capacity < minvol:
                    continue
            except (ValueError, TypeError):
                # if there's a unit conversion error, allow the container
                # to be displayed.
                pass

        containers.append(container)

    if show_containers:
        # containers with no containertype first
        for container in containers:
            if not container.getContainerType():
                items.append([container.UID(), container.Title()])

    ts = getToolByName(instance, 'translation_service').translate
    cat_str = _c(ts(_('Container Type')))
    containertypes = [c.getContainerType() for c in containers]
    containertypes = dict([(ct.UID(), ct.Title())
                           for ct in containertypes if ct])
    for ctype_uid, ctype_title in containertypes.items():
        ctype_title = _c(ctype_title)
        if show_container_types:
            items.append([ctype_uid, "%s: %s" % (cat_str, ctype_title)])
        if show_containers:
            for container in containers:
                ctype = container.getContainerType()
                if ctype and ctype.UID() == ctype_uid:
                    items.append([container.UID(), container.Title()])

    items = tuple(items)
    return items


class PartitionSetupField(RecordsField):
    _properties = RecordsField._properties.copy()
    _properties.update({
        'subfields': (
            'sampletype',
            'separate',
            'preservation',
            'container',
            'vol',
            # 'retentionperiod',
        ),
        'subfield_labels': {
            'sampletype': _('Sample Type'),
            'separate': _('Separate Container'),
            'preservation': _('Preservation'),
            'container': _('Container'),
            'vol': _('Required Volume'),
            # 'retentionperiod': _('Retention Period'),
        },
        'subfield_types': {
            'separate': 'boolean',
            'vol': 'string',
            'container': 'selection',
            'preservation': 'selection',
        },
        'subfield_vocabularies': {
            'sampletype': 'SampleTypes',
            'preservation': 'Preservations',
            'container': 'Containers',
        },
        'subfield_sizes': {
            'sampletype': 1,
            'preservation': 6,
            'vol': 8,
            'container': 6,
            # 'retentionperiod':10,
        }
    })
    security = ClassSecurityInfo()

    security.declarePublic('SampleTypes')

    def SampleTypes(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'senaite_catalog_setup')
        items = []
        for st in bsc(portal_type='SampleType',
                      is_active=True,
                      sort_on='sortable_title'):
            st = st.getObject()
            title = st.Title()
            items.append((st.UID(), title))
        items = [['', '']] + list(items)
        return DisplayList(items)

    security.declarePublic('Preservations')

    def Preservations(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'senaite_catalog_setup')
        items = [[c.UID, c.title] for c in
                 bsc(portal_type='Preservation',
                     is_active=True,
                     sort_on='sortable_title')]
        items = [['', _('Any')]] + list(items)
        return DisplayList(items)

    security.declarePublic('Containers')

    def Containers(self, instance=None):
        instance = instance or self
        items = getContainers(instance, allow_blank=True)
        return DisplayList(items)


registerField(PartitionSetupField, title="", description="")
