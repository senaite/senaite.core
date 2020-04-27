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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from bika.lims import api
from bika.lims import logger
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.Registry import registerField

VERSION_ID = "version_id"
REFERENCE_VERSIONS = "reference_versions"


class HistoryAwareReferenceField(ReferenceField):
    """Version aware references.

    Uses instance.reference_versions[uid] to record uid.version_id,
    to pin this reference to a specific version.
    """
    security = ClassSecurityInfo()

    def get_versioned_references_for(self, instance):
        """Returns the versioned references for the given instance
        """
        vrefs = []

        # Retrieve the referenced objects
        refs = instance.getRefs(relationship=self.relationship)

        ref_versions = getattr(instance, REFERENCE_VERSIONS, None)
        # No versions stored, return the original references
        if ref_versions is None:
            return refs

        for ref in refs:
            uid = api.get_uid(ref)
            # get the linked version to the reference
            version = ref_versions.get(uid)
            # append the versioned reference
            vrefs.append(self.retrieve_version(ref, version))

        return vrefs

    def retrieve_version(self, obj, version):
        """Retrieve the version of the object
        """
        current_version = getattr(obj, VERSION_ID, None)

        if current_version is None:
            # No initial version
            return obj

        if str(current_version) == str(version):
            # Same version
            return obj

        # Retrieve the object from the repository
        pr = api.get_tool("portal_repository")
        # bypass permission check to AccessPreviousVersions
        result = pr._retrieve(
            obj, selector=version, preserve=(), countPurged=True)
        return result.object

    def get_backreferences_for(self, instance):
        """Returns the backreferences for the given instance

        :returns: list of UIDs
        """
        rc = api.get_tool("reference_catalog")
        backreferences = rc.getReferences(instance, self.relationship)
        return map(lambda ref: ref.targetUID, backreferences)

    def preprocess_value(self, value, default=tuple()):
        """Preprocess the value for set
        """
        # empty value
        if not value:
            return default

        # list with one empty item
        if isinstance(value, (list, tuple)):
            if len(value) == 1 and not value[0]:
                return default

        if not isinstance(value, (list, tuple)):
            value = value,

        return value

    def link_version(self, source, target):
        """Link the current version of the target on the source
        """
        if not hasattr(target, VERSION_ID):
            # no initial version of this object!
            logger.warn("No iniatial version found for '{}'"
                        .format(repr(target)))
            return

        if not hasattr(source, REFERENCE_VERSIONS):
            source.reference_versions = {}

        target_uid = api.get_uid(target)
        # store the current version of the target on the source
        source.reference_versions[target_uid] = target.version_id
        # persist changes that occured referenced versions
        source._p_changed = 1

    def unlink_version(self, source, target):
        """Unlink the current version of the target from the source
        """
        if not hasattr(source, REFERENCE_VERSIONS):
            return
        target_uid = api.get_uid(target)
        if target_uid in source.reference_versions[target_uid]:
            # delete the version
            del source.reference_versions[target_uid]
            # persist changes that occured referenced versions
            source._p_changed = 1
        else:
            logger.warn("No version link found on '{}' -> '{}'"
                        .format(repr(source), repr(target)))

    def add_reference(self, source, target, **kwargs):
        """Add a new reference
        """
        # Tweak keyword arguments for addReference
        addRef_kw = kwargs.copy()
        addRef_kw.setdefault("referenceClass", self.referenceClass)
        if "schema" in addRef_kw:
            del addRef_kw["schema"]
        uid = api.get_uid(target)
        rc = api.get_tool("reference_catalog")
        # throws IndexError if uid is invalid
        rc.addReference(source, uid, self.relationship, **addRef_kw)
        # link the version of the reference
        self.link_version(source, target)

    def del_reference(self, source, target, **kwargs):
        """Remove existing reference
        """
        rc = api.get_tool("reference_catalog")
        uid = api.get_uid(target)
        rc.deleteReference(source, uid, self.relationship)
        # unlink the version of the reference
        self.link_version(source, target)

    @security.private
    def set(self, instance, value, **kwargs):
        """Set (multi-)references
        """
        value = self.preprocess_value(value)
        existing_uids = self.get_backreferences_for(instance)

        if not value and not existing_uids:
            logger.warning("Field and value is empty!")
            return

        if not self.multiValued and len(value) > 1:
            raise ValueError("Multiple values given for single valued field {}"
                             .format(repr(self)))

        set_uids = []
        for val in value:
            if api.is_uid(val):
                set_uids.append(val)
            elif api.is_object(val):
                set_uids.append(api.get_uid(val))
            else:
                logger.error("Target has no UID: %s/%s" % (val, value))

        sub = filter(lambda uid: uid not in set_uids, existing_uids)
        add = filter(lambda uid: uid not in existing_uids, set_uids)

        for uid in set(existing_uids + set_uids):
            # The object to link
            target = api.get_object(uid)
            # Add reference to object
            if uid in add:
                __traceback_info__ = (instance, uid, value, existing_uids)
                self.add_reference(instance, target, **kwargs)
            # Delete reference to object
            elif uid in sub:
                self.del_reference(instance, target, **kwargs)

    @security.private
    def get(self, instance, aslist=False, **kwargs):
        """Get (multi-)references
        """
        refs = self.get_versioned_references_for(instance)

        if not self.multiValued:
            if len(refs) > 1:
                logger.warning("Found {} references for non-multivalued "
                               "reference field '{}' of {}".format(
                                   len(refs), self.getName(), repr(instance)))
            if not aslist:
                if refs:
                    refs = refs[0]
                else:
                    refs = None

        if not self.referencesSortable or not hasattr(
                aq_base(instance), "at_ordered_refs"):
            return refs

        refs = instance.at_ordered_refs
        order = refs[self.relationship]
        if order is None:
            return refs

        by_uid = dict(map(lambda ob: (api.get_uid(ob), ob), refs))
        return [by_uid[uid] for uid in order if uid in by_uid]


registerField(HistoryAwareReferenceField,
              title="History Aware Reference",
              description="")
