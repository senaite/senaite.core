# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.Archetypes.Registry import registerField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims import api


class HistoryAwareReferenceField(ReferenceField):
    """ Version aware references.

    Uses instance.reference_versions[uid] to record uid.version_id,
    to pin this reference to a specific version.

    The 'auto_update_backrefs' is a list of reference relationship names
    which will automatically be updated when this object's version is
    incremented:  https://github.com/bikalabs/Bika-LIMS/issues/84

    """
    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """ Mutator. """
        rc = getToolByName(instance, REFERENCE_CATALOG)
        targetUIDs = [ref.targetUID for ref in
                      rc.getReferences(instance, self.relationship)]

        # empty value
        if not value:
            value = ()
        # list with one empty item
        if type(value) in (list, tuple) and len(value) == 1 and not value[0]:
            value = ()

        if not value and not targetUIDs:
            return

        if not isinstance(value, (list, tuple)):
            value = value,
        elif not self.multiValued and len(value) > 1:
            raise ValueError("Multiple values given for single valued field %r" % self)

        #convert objects to uids
        #convert uids to objects
        uids = []
        targets = {}
        for v in value:
            if isinstance(v, basestring):
                uids.append(v)
                targets[v] = rc.lookupObject(v)
            elif hasattr(v, 'UID'):
                target_uid = callable(v.UID) and v.UID() or v.UID
                uids.append(target_uid)
                targets[target_uid] = v
            else:
                logger.info("Target has no UID: %s/%s" % (v, value))

        sub = [t for t in targetUIDs if t not in uids]
        add = [v for v in uids if v and v not in targetUIDs]

        newuids = [t for t in list(targetUIDs) + list(uids) if t not in sub]
        newuids = list(set(newuids))
        for uid in newuids:
            # update version_id of all existing references that aren't
            # about to be removed anyway (contents of sub)
            version_id = getattr(targets[uid], 'version_id', None)
            if not hasattr(instance, 'reference_versions'):
                instance.reference_versions = {}
            instance.reference_versions[uid] = version_id

        # tweak keyword arguments for addReference
        addRef_kw = kwargs.copy()
        addRef_kw.setdefault('referenceClass', self.referenceClass)
        if 'schema' in addRef_kw:
            del addRef_kw['schema']
        for uid in add:
            __traceback_info__ = (instance, uid, value, targetUIDs)
            # throws IndexError if uid is invalid
            rc.addReference(instance, uid, self.relationship, **addRef_kw)

        for uid in sub:
            rc.deleteReference(instance, uid, self.relationship)

        if self.referencesSortable:
            if not hasattr(aq_base(instance), 'at_ordered_refs'):
                instance.at_ordered_refs = {}

            instance.at_ordered_refs[self.relationship] = \
                tuple(filter(None, uids))

        if self.callStorageOnSet:
            #if this option is set the reference fields's values get written
            #to the storage even if the reference field never use the storage
            #e.g. if i want to store the reference UIDs into an SQL field
            ObjectField.set(self, instance, self.getRaw(instance), **kwargs)

    def get_referenced_version(self, instance, reference):
        """Returns the object from the reference history that matches with the
        version the instance points to
        """
        # Version of the referenced object to which the instance points to.
        # If no version found or None, assume the instance points to the first
        # version created (otherwise, it should have a value)
        referenced_version = getattr(instance, "reference_versions", {})
        referenced_version = referenced_version.get(reference.UID(), None) or 0

        # Current version of the referenced object.
        # If the object has not yet a version explicitly set (no history yet),
        # assume this is the first version created
        reference_version = getattr(reference, "version_id", None) or 0
        if reference_version == referenced_version:
            # The instance points to the latest version, no need to look for
            # previous versions
            return reference

        # The instance points to a previous version, need to get the exact
        # previous version the instance points to
        pr = getToolByName(instance, 'portal_repository')
        version_data = pr._retrieve(reference, selector=referenced_version,
                                    preserve=(), countPurged=True)
        return version_data.object

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """get() returns the list of objects referenced under the relationship.
        """
        # Get the referenced objects
        refs = instance.getRefs(relationship=self.relationship)
        if not self.multiValued and len(refs) > 1:
            msg = "%s references for non multivalued field %s of %s" % \
                  (len(refs), self.getName(), instance)
            logger.error(msg)
            return None

        # Get the suitable version of each referenced object
        refs = map(lambda ref: self.get_referenced_version(instance, ref), refs)
        if not self.multiValued:
            refs = refs and refs[0] or None

        return refs

registerField(HistoryAwareReferenceField,
              title="History Aware Reference",
              description="",
              )
