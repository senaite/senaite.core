##############################################################################
#
# VersionedReferenceField - Versioned Reference Field
# Copyright (C) 2006 Zest Software
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: _field.py 6202 2006-03-27 12:21:53Z nouri $
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerField, registerWidget


class VersionedReferenceWidget(atapi.ReferenceWidget):
    _properties = atapi.ReferenceWidget._properties.copy()
    _properties.update({
        'type': 'versionedreference',
        'macro': 'versionedreference',
        'size': '6',
        'helper_js': ('versionedreference.js',),
        })


class VersionedReferenceField(atapi.ReferenceField):
    _properties = atapi.ReferenceField._properties.copy()
    _properties.update({
        'widget': VersionedReferenceWidget,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        atapi.ReferenceField.set(self, instance, value, **kwargs)

        if value is None:
            value = ()

        if not isinstance(value, (list, dict)):
            value = value,

        #convert objects to uids if necessary
        uids = []
        for v in value:
            if isinstance(v, str):
                uids.append(v)
            else:
                uids.append(v.UID())

##        for revision in instance._constructAnnotatedHistory(max):
##            obj = revision['object'].__of__(parent)
##            yield (obj, DateTime(revision['time']), revision['description'],
##                   revision['user_name'])

##        refs = instance.getReferenceImpl(self.relationship)
##        for ref in refs:
##            version =1
##            ref.order = version

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        return refs

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        return refs



registerWidget(
    VersionedReferenceWidget,
    title='Versioned Reference',
    used_for=('Products.VersionedReferenceField.VersionedReferenceField',)
    )

registerField(
    VersionedReferenceField,
    title="Versioned Reference Field",
    description=("Reference field that knows about an order of refs.")
    )
