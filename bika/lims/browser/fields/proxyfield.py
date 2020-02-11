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

import DateTime

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField

from bika.lims.fields import ExtensionField
from bika.lims.interfaces import IProxyField
from bika.lims import logger

"""A field that proxies to an object which is retrieved by the evaluation of
the `proxy` property, e.g. `proxy="context.getSample()"`.

See `docs/AnalysisRequest.rst` for further details.
"""


class ProxyField(ObjectField):
    """A field that proxies to another field of an object, which is retrieved
    by the `proxy` expression property.
    """
    implements(IProxyField)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'proxy',
        'mode': 'rw',
        'default': None,
        'proxy': None,
    })

    security = ClassSecurityInfo()

    security.declarePrivate('get_proxy')

    def get_proxy(self, instance):
        """Evaluate the `proxy` property to retrieve the proxy object.
        """
        # evaluates the 'proxy' expression on the field definition in the schema,
        # e.g. 'context.getSample()' on an AR
        return eval(self.proxy, {'context': instance, 'here': instance})

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """retrieves the value of the same named field on the proxy object
        """
        # The default value
        default = self.getDefault(instance)

        # Retrieve the proxy object
        proxy_object = self.get_proxy(instance)

        # Return None if we could not find a proxied object, e.g. through
        # the proxy expression 'context.getSample()' on an AR
        if proxy_object is None:
            logger.debug("Expression '{}' did not return a valid Proxy Object on {}"
                         .format(self.proxy, instance))
            return default

        # Lookup the proxied field by name
        field_name = self.getName()
        field = proxy_object.getField(field_name)

        # Bail out if the proxy object has no identical named field
        if field is None:
            raise KeyError("Object '{}' with id '{}' has no field named '{}'".format(
                proxy_object.portal_type, proxy_object.getId(), field_name))

        # return the value of the proxy field
        return field.get(proxy_object)

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """writes the value to the same named field on the proxy object
        """
        # Retrieve the proxy object
        proxy_object = self.get_proxy(instance)

        # Return None if we could not find a proxied object, e.g. through
        # the proxy expression 'context.getSample()' on an AR
        if not proxy_object:
            logger.debug("Expression '{}' did not return a valid Proxy Object on {}"
                         .format(self.proxy, instance))
            return None

        # Lookup the proxied field by name
        field_name = self.getName()
        field = proxy_object.getField(field_name)

        # Bail out if the proxy object has no identical named field.
        if field is None:
            raise KeyError("Object '{}' with id '{}' has no field named '{}'".format(
                proxy_object.portal_type, proxy_object.getId(), field_name))

        # set the value on the proxy object
        field.set(proxy_object, value, **kwargs)

        # get the current time
        now = DateTime.DateTime()

        # update the modification date of the proxied object
        proxy_object.setModificationDate(now)

        # update the modification date of the holding object
        instance.setModificationDate(now)


# Register the field
registerField(
    ProxyField,
    title='Proxy',
    description=('Used to proxy a value to a similar field on another object.')
)


class ExtProxyField(ExtensionField, ProxyField):
    """An Extended Proxy Field for its use in SchemaExtender"""
