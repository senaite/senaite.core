# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseContent import BaseContent
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
    replacement for Archetypes' ReferenceField.  A relationship is required
    but if one is not provided, it will be composed from a concatenation
    of `portal_type` + `fieldname`.
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

    @security.public
    def get_object(self, context, value):
        """Resolve a UID to an object.

        :param context: context is the object containing the field's schema.
        :type context: BaseContent
        :param value: A UID.
        :type value: string
        :return: Returns a Content object.
        :rtype: BaseContent
        """
        if not value:
            return None
        obj = _get_object(context, value)
        if obj is None:
            logger.warning(
                "{}.{}: Resolving UIDReference failed for {}.  No object will "
                "be returned.".format(context, self.getName(), value))
        return obj

    @security.public
    def get_uid(self, context, value):
        """Takes a brain or object (or UID), and returns a UID.

        :param context: context is the object who's schema contains this field.
        :type context: BaseContent
        :param value: Brain, object, or UID.
        :type value: Any
        :return: resolved UID.
        :rtype: string
        """
        # Empty string or list with single empty string, are commonly
        # passed to us from form submissions
        if not value or value == ['']:
            ret = ''
        elif api.is_brain(value):
            ret = value.UID
        elif api.is_at_content(value) or api.is_dexterity_content(value):
            ret = value.UID()
        elif is_uid(context, value):
            ret = value
        else:
            raise ReferenceException("{}.{}: Cannot resolve UID for {}".format(
                context, self.getName(), value))
        return ret

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
        value = StringField.get(self, context, **kwargs)
        if not value:
            return [] if self.multiValued else None
        if self.multiValued:
            # Only return objects which actually exist; this is necessary here
            # because there are no HoldingReferences. This opens the
            # possibility that deletions leave hanging references.
            ret = filter(
                lambda x: x, [self.get_object(context, uid) for uid in value])
        else:
            ret = self.get_object(context, value)
        return ret

    @security.public
    def getRaw(self, context, aslist=False, **kwargs):
        """Grab the stored value, and return it directly as UIDs.

        :param context: context is the object who's schema contains this field.
        :type context: BaseContent
        :param aslist: Forces a single-valued field to return a list type.
        :type aslist: bool
        :param kwargs: kwargs are passed directly to the underlying get.
        :type kwargs: dict
        :return: UID or list of UIDs for multiValued fields.
        :rtype: string | list[string]
        """
        value = StringField.get(self, context, **kwargs)
        if not value:
            return [] if self.multiValued else None
        if self.multiValued:
            ret = value
        else:
            ret = self.get_uid(context, value)
            if aslist:
                ret = [ret]
        return ret

    def _set_backreferences(self, context, items):
        if items:
            if self.relationship:
                key = self.relationship
            else:
                key = context.portal_type + self.getName()
            uid = context.UID()
            for item in items:
                # Because no relationship is passed to get_backreferences,
                # the entire set of backrefs is returned by reference.
                backrefs = get_backreferences(item, relationship=None)
                if key not in backrefs:
                    backrefs[key] = PersistentList()
                if uid not in backrefs[key]:
                    backrefs[key].append(uid)

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
        if self.multiValued:
            if not value:
                value = []
            if type(value) not in (list, tuple):
                value = [value, ]
            ret = [self.get_object(context, val) for val in value if val]
            self._set_backreferences(context, ret)
            uids = [self.get_uid(context, r) for r in ret if r]
            StringField.set(self, context, uids, **kwargs)
        else:
            # Sometimes we get given a list here with an empty string.
            # This is generated by html forms with empty values.
            # This is a single-valued field though, so:
            if isinstance(value, list) and value:
                if len(value) > 1:
                    logger.warning(
                        "Found values '\'{}\'' for singleValued field <{}>.{} "
                        "- using only the first value in the list.".format(
                            '\',\''.join(value), context.UID(), self.getName()))
                value = value[0]
            ret = self.get_object(context, value)
            if ret:
                self._set_backreferences(context, [ret, ])
                uid = self.get_uid(context, ret)
                StringField.set(self, context, uid, **kwargs)
            else:
                StringField.set(self, context, '', **kwargs)


def is_uid(context, value):
    """Checks that the string passed is a valid UID of an existing object

    :param context: Context is only used for acquiring uid_catalog tool.
    :type context: BaseContent
    :param value: A UID.
    :type value: string
    :return: True if the value is a UID and exists as an entry in uid_catalog.
    :rtype: bool
    """
    uc = api.get_tool('uid_catalog', context=context)
    brains = uc(UID=value)
    return brains and True or False


def _get_object(context, value):
    """Resolve a UID to an object.

    :param context: context is the object containing the field's schema.
    :type context: BaseContent
    :param value: A UID.
    :type value: string
    :return: Returns a Content object.
    :rtype: BaseContent
    """

    if api.is_at_content(value) or api.is_dexterity_content(value):
        return value
    elif value and is_uid(context, value):
        uc = api.get_tool('uid_catalog', context=context)
        brains = uc(UID=value)
        assert len(brains) == 1
        return brains[0].getObject()


def get_storage(context):
    annotation = IAnnotations(context)
    if annotation.get(BACKREFS_STORAGE) is None:
        annotation[BACKREFS_STORAGE] = PersistentDict()
    return annotation[BACKREFS_STORAGE]


def _get_catalog_for_uid(uid):
    at = api.get_tool('archetype_tool')
    uc = api.get_tool('uid_catalog')
    pc = api.get_tool('portal_catalog')
    # get uid_catalog brain for uid
    ub = uc(UID=uid)[0]
    # get portal_type of brain
    pt = ub.portal_type
    # get the registered catalogs for portal_type
    cats = at.getCatalogsByType(pt)
    # try avoid 'portal_catalog'; XXX multiple catalogs in setuphandlers.py?
    cats = [cat for cat in cats if cat != pc]
    if cats:
        return cats[0]
    return pc


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
