# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo

from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.Field import Field, StringField
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
from bika.lims.interfaces.field import IUIDReferenceField
from plone.api.portal import get_tool
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


def is_brain(brain_or_object):
    """Checks if the passed in object is a portal catalog brain
    
    :param brain_or_object: Any object; probably a content object or a brain.
    :type brain_or_object: Any
    :return: True if the object is a brain
    :rtype: bool
    """
    return ICatalogBrain.providedBy(brain_or_object)


def is_at_content(brain_or_object):
    """Checks if the passed in object is an AT content type
    
    :param brain_or_object: Any object; probably a content object or a brain.
    :type brain_or_object: Any
    :return: True if object is an AT Content Type (instance of BaseObject).
    :rtype: bool
    """
    return isinstance(brain_or_object, BaseObject)


class UIDReferenceField(StringField):
    """A field that stores References as UID values.
    """
    _properties = Field._properties.copy()
    _properties.update({
        'type': 'uidreference',
        'default': '',
        'default_content_type': 'text/plain',
        # relationship is required, this allows us to mimic a real AT
        # Reference.  This field doesn't have backreferences (yet?), so we
        # don't need a value here:
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
        elif is_at_content(value):
            return value
        else:
            try:
                uc = getToolByName(context, 'uid_catalog')
            except AttributeError:
                # Sometimes an object doesn't have an acquisition chain,
                # in these cases we just hope that get_tool's call to
                # getSite doesn't fuck up.
                uc = get_tool('uid_catalog')
            brains = uc(UID=value)
            if brains:
                return brains[0].getObject()
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
        :return: object or list of objects for multiValued fields.
        :rtype: BaseContent | list[BaseContent]
        """
        if self.multiValued:
            if type(value) not in (list, tuple):
                value = [value, ]
            ret = [self.get_uid(context, val) for val in value]
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
            ret = self.get_uid(context, value)
        StringField.set(self, context, ret, **kwargs)
