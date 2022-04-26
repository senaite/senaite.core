# -*- coding: utf-8 -*-

import six

from Acquisition import aq_base
from bika.lims import api
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.behavior.interfaces import IBehavior
from plone.uuid.interfaces import ATTRIBUTE_NAME
from senaite.core import logger
from senaite.core.interfaces import IHaveUIDReferences
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IUIDReferenceField
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.schema import ASCIILine
from zope.schema import List

BACKREFS_STORAGE = "senaite.core.schema.uidreferencefield.backreferences"


@adapter(IHaveUIDReferences, IObjectCreatedEvent)
def on_object_created(object, event):
    """Link backreferences after the object was created

    This is necessary, because objects during initialization have no UID set!
    https://community.plone.org/t/accessing-uid-in-dexterity-field-setter/14468

    Therefore, and only for the creation case, we need to link the back
    references in this handler for all UID reference fields.
    """
    fields = api.get_fields(object)
    for name, field in fields.items():
        if not IUIDReferenceField.providedBy(field):
            continue
        # after creation, we only need to link backreferences
        value = field.get(object)
        # handle single valued reference fields
        if api.is_object(value):
            field.link_backref(value, object)
            logger.info(
                "Adding back reference from %s -> %s" % (
                    value, object))
        # handle multi valued reference fields
        elif isinstance(value, list):
            for ref in value:
                logger.info(
                    "Adding back reference from %s -> %s" % (
                        ref, object))
                field.link_backref(ref, object)


def get_backrefs(context, relationship, as_objects=False):
    """Return backreferences of the context

    :returns: List of UIDs that are linked by the relationship
    """
    context = aq_base(context)
    # get the backref annotation storage of the context
    backrefs = get_backref_storage(context)
    # get the referenced UIDs
    backref_uids = list(backrefs.get(relationship, []))

    if not backref_uids:
        return []

    if as_objects is True:
        return [api.get_object(uid) for uid in backref_uids]

    return backref_uids


def get_backref_storage(context):
    """Get the annotation storage for backreferences of the context
    """
    annotation = IAnnotations(context)
    if annotation.get(BACKREFS_STORAGE) is None:
        annotation[BACKREFS_STORAGE] = PersistentDict()
    return annotation[BACKREFS_STORAGE]


@implementer(IUIDReferenceField)
class UIDReferenceField(List, BaseField):
    """Stores UID references to other objects
    """

    value_type = ASCIILine(title=u"UID")

    def __init__(self, allowed_types=None, multi_valued=True, **kw):
        if allowed_types is None:
            allowed_types = ()
        self.allowed_types = allowed_types
        self.multi_valued = multi_valued
        super(UIDReferenceField, self).__init__(**kw)

    def is_initializing(self, object):
        """Checks if the object is initialized at the moment

        Background:

        Objects being created do not have a UID set.
        Therefore, ths backreferences need to be postponed to an event handler.

        https://community.plone.org/t/accessing-uid-in-dexterity-field-setter/14468
        """
        uid = getattr(object, ATTRIBUTE_NAME, None)
        if uid is None:
            return True
        return False

    def to_list(self, value, filter_empty=True):
        """Ensure the value is a list
        """
        if isinstance(value, six.string_types):
            value = [value]
        elif api.is_object(value):
            value = [value]
        elif value is None:
            value = []
        if filter_empty:
            value = filter(None, value)
        return value

    def get_relationship_key(self, context):
        """Relationship key used for backreferences

        The key used for the annotation storage on the referenced object to
        remember the current object UID.

        :returns: storage key to lookup back references
        """
        portal_type = api.get_portal_type(context)
        return "%s.%s" % (portal_type, self.__name__)

    def get_uid(self, value):
        """Value -> UID

        :parm value: object/UID/SuperModel
        :returns: UID
        """
        try:
            return api.get_uid(value)
        except api.APIError:
            return None

    def get_object(self, value):
        """Value -> object

        :returns: Object or None
        """
        try:
            return api.get_object(value)
        except api.APIError:
            return None

    def get_allowed_types(self):
        """Returns the allowed reference types

        :returns: tuple of allowed_types
        """
        allowed_types = self.allowed_types
        if not allowed_types:
            allowed_types = ()
        elif isinstance(allowed_types, six.string_types):
            allowed_types = (allowed_types, )
        return allowed_types

    def set(self, object, value):
        """Set UID reference

        :param object: the instance of the field
        :param value: object/UID/SuperModel
        :type value: list/tuple/str
        """

        # always mark the object if references are set
        # NOTE: there might be multiple UID reference field set on this object!
        if value:
            alsoProvides(object, IHaveUIDReferences)

        # always handle all values internally as a list
        value = self.to_list(value)

        # convert to UIDs
        uids = []
        for v in value:
            uid = self.get_uid(v)
            if uid is None:
                continue
            uids.append(uid)

        # current set UIDs
        existing = self.to_list(self.get_raw(object))

        # filter out new/removed UIDs
        added_uids = [u for u in uids if u not in existing]
        added_objs = filter(None, map(self.get_object, added_uids))

        removed_uids = [u for u in existing if u not in uids]
        removed_objs = filter(None, map(self.get_object, removed_uids))

        # link backreferences of new uids
        for added_obj in added_objs:
            self.link_backref(added_obj, object)

        # unlink backreferences of removed UIDs
        for removed_obj in removed_objs:
            self.unlink_backref(removed_obj, object)

        super(UIDReferenceField, self).set(object, uids)

    def unlink_backref(self, source, target):
        """Remove backreference from the source to the target

        :param source: the object where the backref is stored (our reference)
        :param target: the object where the backref points to (our object)
        :returns: True when the backref was removed, False otherwise
        """

        # Target might be a behavior instead of the object itself
        if IBehavior.providedBy(target):
            target = target.context

        # This should be actually not possible
        if self.is_initializing(target):
            raise ValueError("Objects in initialization state "
                             "can not have existing back references!")

        target_uid = self.get_uid(target)
        # get the storage key
        key = self.get_relationship_key(target)
        # get all backreferences from the source
        backrefs = get_backref_storage(source)
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

    def link_backref(self, source, target):
        """Add backreference from the source to the target

        :param source: the object where the backref is stored (our reference)
        :param target: the object where the backref points to (our object)
        :returns: True when the backref was written
        """

        # Target might be a behavior instead of the object itself
        if IBehavior.providedBy(target):
            target = target.context

        # Object is initializing and don't have an UID!
        # -> Postpone to set back references in event handler
        if self.is_initializing(target):
            logger.info("Object is in initialization state. "
                        "Back references will be set in event handler")
            return

        target_uid = api.get_uid(target)
        # get the annotation storage key
        key = self.get_relationship_key(target)
        # get all backreferences
        backrefs = get_backref_storage(source)
        if key not in backrefs:
            backrefs[key] = PersistentList()
        if target_uid not in backrefs[key]:
            backrefs[key].append(target_uid)
        return True

    def get(self, object):
        """Get referenced objects

        :param object: instance of the field
        :returns: list of referenced objects
        """
        return self._get(object, as_objects=True)

    def get_raw(self, object):
        """Get referenced UIDs

        NOTE: Called from the data manager `query` method
              to get the widget value

        :param object: instance of the field
        :returns: list of referenced UIDs
        """
        return self._get(object, as_objects=False)

    def _get(self, object, as_objects=False):
        """Returns single/multi value

        :param object: instance of the field
        :param as_objects: Flag for UID/object returns
        :returns: list of referenced UIDs
        """

        # when creating a new object the context is the container
        # which does not have the field
        if self.interface and not self.interface.providedBy(object):
            if self.multi_valued:
                return []
            return None

        uids = super(UIDReferenceField, self).get(object)

        if not uids:
            uids = []
        elif not isinstance(uids, (list, tuple)):
            uids = [uids]

        if as_objects is True:
            uids = filter(None, map(self.get_object, uids))

        if self.multi_valued:
            return uids
        if len(uids) == 0:
            return None
        return uids[0]

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(UIDReferenceField, self)._validate(value)
        # check if the fields accepts single values only
        if not self.multi_valued and len(value) > 1:
            raise ValueError("Single valued field accepts at most 1 value")

        # check for valid UIDs
        for uid in value:
            if not api.is_uid(uid):
                raise ValueError("Invalid UID: '%s'" % uid)

        # check if the type is allowed
        allowed_types = self.get_allowed_types()
        if allowed_types:
            objs = filter(None, map(self.get_object, value))
            types = set(map(api.get_portal_type, objs))
            if not types.issubset(allowed_types):
                raise ValueError("Only the following types are allowed: %s"
                                 % ",".join(allowed_types))
