# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import Field, StringField
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.api import is_at_content, is_brain, is_dexterity_content
from bika.lims.interfaces.field import IUIDReferenceField
from zope.interface import implements


class ReferenceException(Exception):
    pass


def is_uid(context, value):
    """Checks that the string passed is a valid UID of an existing object

    :param context: Context is only used for acquiring uid_catalog tool.
    :type context: BaseContent
    :param value: A UID.
    :type value: string
    :return: True if the value is a UID and exists as an entry in uid_catalog.
    :rtype: bool
    """
    uc = getToolByName(context, 'uid_catalog')
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

    if value:
        if is_at_content(value) or is_dexterity_content(value):
            return value
        else:
            uc = getToolByName(context, 'uid_catalog')
            brains = uc(UID=value)
            if brains:
                return brains[0].getObject()


class UIDReferenceField(StringField):
    """A field that stores References as UID values.
    """
    _properties = Field._properties.copy()
    _properties.update({
        'type': 'uidreference',
        'default': '',
        'default_content_type': 'text/plain',
        # a 'relationship' key is required here so that Reference Widgets will
        # continue to work.  However, if the value is false-ish, then the
        # relationship will be named portal_type + fieldname
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
        obj = _get_object(context, value)
        if obj:
            return obj
        logger.error(
            "{}.{}: Resolving UIDReference failed for {}.  No object will "
            "be returned.".format(context, self.getName(), value))

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
        elif is_brain(value):
            ret = value.UID
        elif is_at_content(value):
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
        if self.multiValued:
            # Only return objects which actually exist; this is necessary here
            # because there are no BackReferences, or HoldingReferences.
            # This opens the possibility that deletions leave hanging
            # references.
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
                backrefs = get_backreferences(item)  # NB: no relationship!
                if key not in backrefs:
                    backrefs[key] = []
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


def get_backreferences(context, relationship=None):
    """Return backreferences informed by UIDReferenceField values.

    Relationship can be provided as a parameter of the UIDReferenceField.  If
    this is not present on the field, then it will be composed from a
    concatenation of the portal_type and fieldname of the field that is
    initiating the reference.  When calling get_backreferences with a
    relationship argument supplied, the backreferences will be returned as a
    copy of the backreferences list, with all UIDs dereferenced into objects.

    If you do not provide a relationship parameter to get_backreferences,
    then the entire set of backreferences to the context object is returned
    (by reference).  In this case, UIDs are returned as values, instead of
    objects, and modifying the resulting variable will cause the
    backreferences to be modified in the data.
    """
    instance = context.aq_base
    if not hasattr(instance, '_uidreference_backreferences'):
        instance._uidreference_backreferences = {}
    backrefs = instance._uidreference_backreferences
    if relationship:
        backrefs = [_get_object(context, b)
                    for b in backrefs.get(relationship, [])]
    return backrefs
