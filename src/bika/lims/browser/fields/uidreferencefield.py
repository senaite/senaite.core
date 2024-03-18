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

import six

from AccessControl import ClassSecurityInfo
from bika.lims import APIError
from Products.Archetypes.Field import Field, StringField
from bika.lims import logger
from bika.lims import api
from bika.lims.interfaces.field import IUIDReferenceField
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements

BACKREFS_STORAGE = "bika.lims.browser.fields.uidreferencefield.backreferences"


class ReferenceException(Exception):
    pass


class UIDReferenceField(StringField):
    """A field that stores References as UID values.  This acts as a drop-in
    replacement for Archetypes' ReferenceField. If no relationship is provided,
    the field won't keep backreferences in referenced objects
    """
    _properties = Field._properties.copy()
    _properties.update({
        'type': 'uidreference',
        'default': '',
        'default_content_type': 'text/plain',
        'relationship': '',
    })

    implements(IUIDReferenceField)

    security = ClassSecurityInfo()

    @property
    def keep_backreferences(self):
        """Returns whether this field must keep back references. Returns False
        if the value for property relationship is None or empty
        """
        relationship = getattr(self, "relationship", None)
        if relationship and isinstance(relationship, six.string_types):
            return True
        return False

    def get_relationship_key(self, context):
        """Return the configured relationship key or generate a new one
        """
        if not self.relationship:
            return context.portal_type + self.getName()
        return self.relationship

    def link_reference(self, source, target):
        """Link the target to the source
        """
        target_uid = api.get_uid(target)
        # get the annotation storage key
        key = self.get_relationship_key(target)
        # get all backreferences from the source
        # N.B. only like this we get the persistent mapping!
        backrefs = get_backreferences(source, relationship=None)
        if key not in backrefs:
            backrefs[key] = PersistentList()
        if target_uid not in backrefs[key]:
            backrefs[key].append(target_uid)
        return True

    def unlink_reference(self, source, target):
        """Unlink the target from the source
        """
        target_uid = api.get_uid(target)
        # get the storage key
        key = self.get_relationship_key(target)
        # get all backreferences from the source
        # N.B. only like this we get the persistent mapping!
        backrefs = get_backreferences(source, relationship=None)
        if key not in backrefs:
            logger.warn(
                "Referenced object {} has no backreferences for the key {}"
                .format(repr(source), key))
            return False
        if target_uid not in backrefs[key]:
            logger.warn("Target {} was not linked by {}"
                        .format(repr(target), repr(source)))
            return False
        backrefs[key].remove(target_uid)
        return True

    @security.public
    def get_uid(self, value):
        """Takes a brain or object (or UID), and returns a UID
        :param value: Brain, object, or UID
        :type value: Any
        :return: resolved UID
        """
        try:
            return api.get_uid(value)
        except APIError:
            return None

    @security.public
    def get(self, context, **kwargs):
        """Grab the stored value, and resolve object(s) from UID catalog.

        :param context: context is the object who's schema contains this field.
        :type context: BaseContent
        :param kwargs: kwargs are passed directly to the underlying get.
        :type kwargs: dict
        :return: object or list of objects for multiValued fields.
        :rtype: BaseContent | list[BaseContent]
        """
        uids = StringField.get(self, context, **kwargs)
        if not isinstance(uids, list):
            uids = [uids]

        # Do a direct search for all brains at once
        uc = api.get_tool("uid_catalog")
        references = uc(UID=uids)

        # Keep the original order of items
        references = sorted(references, key=lambda it: uids.index(it.UID))

        # Return objects by default
        full_objects = kwargs.pop("full_objects", True)
        if full_objects:
            references = [api.get_object(ref) for ref in references]

        if self.multiValued:
            return references
        elif references:
            return references[0]
        return None

    @security.public
    def getRaw(self, context, **kwargs):
        """Grab the stored value, and return it directly as UIDs.

        :param context: context is the object who's schema contains this field.
        :type context: BaseContent
        :param kwargs: kwargs are passed directly to the underlying get.
        :type kwargs: dict
        :return: UID or list of UIDs for multiValued fields.
        :rtype: string | list[string]
        """
        uids = StringField.get(self, context, **kwargs)
        if not isinstance(uids, list):
            uids = [uids]
        if self.multiValued:
            return filter(None, uids)
        return uids[0]

    def _set_backreferences(self, context, items, **kwargs):
        """Set the back references on the linked items

        This will set an annotation storage on the referenced items which point
        to the current context.
        """

        # Don't set any references during initialization.
        # This might cause a recursion error when calling `getRaw` to fetch the
        # current set UIDs!
        initializing = kwargs.get('_initializing_', False)
        if initializing:
            return

        # current set UIDs
        raw = self.getRaw(context) or []
        # handle single reference fields
        if isinstance(raw, six.string_types):
            raw = [raw, ]
        cur = set(raw)
        # UIDs to be set
        uids = set(map(api.get_uid, items))
        # removed UIDs
        removed = cur.difference(uids)
        # missing UIDs
        missing = uids.difference(cur)

        # Unlink removed UIDs from the source
        uc = api.get_tool("uid_catalog")
        for brain in uc(UID=list(removed)):
            source = api.get_object(brain)
            self.unlink_reference(source, context)

        # Link missing UIDs
        for brain in uc(UID=list(missing)):
            target = api.get_object(brain)
            self.link_reference(target, context)

    @security.public
    def set(self, context, value, **kwargs):
        """Accepts a UID, brain, or an object (or a list of any of these),
        and stores a UID or list of UIDS.

        :param context: context is the object who's schema contains this field.
        :type context: BaseContent
        :param value: A UID, brain or object (or a sequence of these).
        :type value: Any
        :param kwargs: kwargs are passed directly to the underlying get.
        :type kwargs: dict
        :return: None
        """
        if not isinstance(value, (list, tuple)):
            value = [value]

        # Extract uids and remove empties
        uids = [self.get_uid(item) for item in value]
        uids = filter(None, uids)

        # Back-reference current object to referenced objects
        if self.keep_backreferences:
            self._set_backreferences(context, uids, **kwargs)

        # Store the referenced objects as uids
        if not self.multiValued:
            uids = uids[0] if uids else ""
        StringField.set(self, context, uids, **kwargs)


def get_storage(context):
    annotation = IAnnotations(context)
    if annotation.get(BACKREFS_STORAGE) is None:
        annotation[BACKREFS_STORAGE] = PersistentDict()
    return annotation[BACKREFS_STORAGE]


def _get_catalog_for_uid(uid):
    at = api.get_tool('archetype_tool')
    uc = api.get_tool('uid_catalog')
    # get uid_catalog brain for uid
    ub = uc(UID=uid)[0]
    # get portal_type of brain
    pt = ub.portal_type
    # get the registered catalogs for portal_type
    cats = at.getCatalogsByType(pt)
    if cats:
        return cats[0]
    return uc


def get_backreferences(context, relationship=None, as_brains=None):
    """Return all objects which use a UIDReferenceField to reference context.

    :param context: The object which is the target of references.
    :param relationship: The relationship name of the UIDReferenceField.
    :param as_brains: Requests that this function returns only catalog brains.
        as_brains can only be used if a relationship has been specified.

    This function can be called with or without specifying a relationship.

    - If a relationship is provided, the return value will be a list of items
      which reference the context using the provided relationship.

      If relationship is provided, then you can request that the backrefs
      should be returned as catalog brains.  If you do not specify as_brains,
      the raw list of UIDs will be returned.

    - If the relationship is not provided, then the entire set of
      backreferences to the context object is returned (by reference) as a
      dictionary.  This value can then be modified in-place, to edit the stored
      backreferences.
    """

    instance = context.aq_base
    raw_backrefs = get_storage(instance)

    if not relationship:
        assert not as_brains, "You cannot use as_brains with no relationship"
        return raw_backrefs

    backrefs = list(raw_backrefs.get(relationship, []))
    if not backrefs:
        return []

    if not as_brains:
        return backrefs

    cat = _get_catalog_for_uid(backrefs[0])
    return cat(UID=backrefs)
