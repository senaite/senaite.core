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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.CMFCore import permissions
from senaite.core.behaviors.utils import get_behavior_schema
from senaite.core.interfaces import IClientsGroup
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.annotation.interfaces import IAnnotations


TYPES_UIDS = "senaite.core.behaviors.clientshareable.types_uids"


class TypesAwareUIDReferenceField(UIDReferenceField):
    """A convenient field to handle UIDs of reference objects from different
    types (e.g. Client + ClientsGroup) properly and in a more efficient way
    """

    def set(self, object, value):
        super(TypesAwareUIDReferenceField, self).set(object, value)

        # remove all UIDs from types storage that are no longer present
        self._purge_types_storage(object)

        # extract the UIDs left in the types storage
        in_types = self._get_types_storage_uids(object)

        # store new UIDs in the types storage
        for ref in self.to_list(value):
            uid = self.get_uid(ref)
            if uid is None:
                continue
            if uid in in_types:
                # since we don't need to wake up the object, users without
                # View permission granted for the object can run the setter
                # without error while keeping the previous references intact
                continue

            self._add_to_types_storage(object, ref)

    def _add_to_types_storage(self, object, ref):
        """Stores the reference to the object's type storage
        """
        ref_obj = self.get_object(ref)
        if not ref_obj:
            logger.error("Cannot retrieve object {}".format(ref))
            return

        uid = self.get_uid(ref)
        storage = self.get_types_storage(object)
        portal_type = api.get_portal_type(ref_obj)
        if portal_type not in storage:
            storage[portal_type] = PersistentList()
        if uid not in storage[portal_type]:
            storage[portal_type].append(uid)

        if IClientsGroup.providedBy(ref_obj):
            for client in ref_obj.getClients():
                self._add_to_types_storage(object, client)

    def _get_types_storage_uids(self, object):
        """Returns a list with the UIDs stored in the types storage
        """
        in_types = []
        storage = self.get_types_storage(object)
        for portal_type, uids in storage.items():
            in_types.extend(uids)
        return in_types

    def _purge_types_storage(self, object):
        """Removes uids from the types storage that are no longer present
        """
        # all referenced uids
        ref_uids = self._get(object)

        # extract all uids stored in types storage
        in_types = self._get_types_storage_uids(object)

        # remove uids from the storage that are no longer referenced
        in_types = filter(lambda uid: uid not in ref_uids, in_types)
        in_types = list(set(in_types))
        for uid in in_types:
            self._remove_from_types(object, uid)

    def _remove_from_types(self, object, uid):
        """Remove the uid passed in from the types storage, if present
        """
        storage = self.get_types_storage(object)
        portal_types = storage.keys()
        for portal_type in portal_types:
            if uid in storage[portal_type]:
                storage[portal_type].remove(uid)

    def get_uids(self, object, portal_type):
        """Returns the stored UIDS for the given portal_type
        """
        if not portal_type:
            return self.get_raw(object)

        storage = self.get_types_storage(object)
        return storage.get(portal_type, [])

    def get_types_storage(self, obj):
        """Returns the annotation storage used to store the UIDs of the
        referenced objects, but grouped by portal_type
        """
        # Object might be a behavior instead of the object itself
        obj = self._get_content_object(obj)
        annotation = IAnnotations(obj)
        if annotation.get(TYPES_UIDS) is None:
            annotation[TYPES_UIDS] = PersistentDict()
        return annotation[TYPES_UIDS]


class IClientShareable(Interface):
    """Marker interface to implement by types for which ClientShareableBehavior
    can be applied
    """
    pass


class IClientShareableMarker(Interface):
    """Marker interface provided by objects with ClientShareableBehavior
    """
    pass


@provider(IFormFieldProvider)
class IClientShareableBehavior(model.Schema):
    """Behavior with schema fields to allow to share the context with users
    that belong to other clients
    """

    shared_with = TypesAwareUIDReferenceField(
        title=_(u"Clients or Groups"),
        description=_(
            u"Clients or groups of clients with whom this content will be "
            u"shared across. This content will become available on searches to "
            u"users that belong to any of the selected clients or groups "
            u"thanks to the role 'ClientGuest'"
        ),
        allowed_types=("Client", "ClientsGroup"),
        required=False,
    )

    directives.widget(
        "shared_with",
        UIDReferenceWidgetFactory,
        catalog="portal_catalog",
        query={
            "portal_type": ("Client", "ClientsGroup"),
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ],
        limit=15,
    )

    fieldset(
        "clientshareable",
        label=u"Client share",
        fields=["shared_with"],
    )


@implementer(IBehavior, IClientShareableBehavior)
class ClientShareableFactory(object):
    """Factory that provides IClientShareableBehavior"""

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context
        self._schema = None

    @property
    def schema(self):
        """Return the schema provided by the underlying behavior
        """
        if self._schema is None:
            behavior = IClientShareableBehavior
            self._schema = get_behavior_schema(self.context, behavior)
        return self._schema

    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        if fieldname not in self.schema:
            return None
        field = self.schema[fieldname]
        if raw:
            return field.getRaw
        return field.get

    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        if fieldname in self.schema:
            return self.schema[fieldname].set
        return None

    @security.protected(permissions.View)
    def getRawSharedWith(self):
        accessor = self.accessor("shared_with", raw=True)
        return accessor(self.context)

    @security.protected(permissions.View)
    def getSharedWith(self):
        accessor = self.accessor("shared_with")
        return accessor(self.context)

    @security.protected(permissions.ModifyPortalContent)
    def setSharedWith(self, value):
        mutator = self.mutator("shared_with")
        mutator(self.context, value)

    @security.protected(permissions.View)
    def getRawClients(self):
        """Returns the UIDs of all clients this object is shared with, either
        by direct assignment or indirectly via Clients Groups
        """
        field = self.schema["shared_with"]
        return field.get_uids(self, "Client")

    @security.protected(permissions.View)
    def getClients(self):
        """Returns all Client objects this object is shared with, either
        by direct assignment or indirectly via Clients Groups
        """
        return [api.get_object(obj) for obj in self.getRawClients()]

    shared_with = property(getSharedWith, setSharedWith)
