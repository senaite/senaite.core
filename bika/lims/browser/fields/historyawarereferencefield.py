# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.Registry import registerField
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.utils import to_utf8
import sys


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

        ts = getToolByName(instance, "translation_service").translate

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
            version_id = hasattr(targets[uid], 'version_id') and \
                       targets[uid].version_id or None
            if version_id is None:
                # attempt initial save of unversioned targets
                pr = getToolByName(instance, 'portal_repository')
                if pr.isVersionable(targets[uid]):
                    pr.save(obj=targets[uid],
                            comment=to_utf8(ts(_("Initial revision"))))
            if not hasattr(instance, 'reference_versions'):
                instance.reference_versions = {}
            if not hasattr(targets[uid], 'version_id'):
                targets[uid].version_id = None
            instance.reference_versions[uid] = targets[uid].version_id

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

    security.declarePrivate('get')

    def get(self, instance, aslist=False, **kwargs):
        """get() returns the list of objects referenced under the relationship.
        """
        try:
            uc = getToolByName(instance, "uid_catalog")
        except AttributeError as err:
            logger.error("AttributeError: {0}".format(err))
            return []

        try:
            res = instance.getRefs(relationship=self.relationship)
        except:
            pass

        pr = getToolByName(instance, 'portal_repository')

        rd = {}
        for r in res:
            if r is None:
                continue
            uid = r.UID()
            r = uc(UID=uid)[0].getObject()
            if hasattr(instance, 'reference_versions') and \
               hasattr(r, 'version_id') and \
               uid in instance.reference_versions and \
               instance.reference_versions[uid] != r.version_id and \
               r.version_id is not None:

                version_id = instance.reference_versions[uid]
                try:
                    result = pr._retrieve(r,
                                     selector=version_id,
                                     preserve=(),
                                     countPurged=True)
                    o = result.object
                # except ArchivistRetrieveError:
                #     o = r
                except:
                    # TODO Need to investigate
                    # TypeError: can't pickle instancemethod objects.
                    # At:
                    # Products.CMFEditions-2.2.21-py2.7.egg/Products/CMFEditions/CopyModifyMergeRepositoryTool.py", line 494, in _retrieve:    saved = transaction.savepoint()
                    # https://github.com/plone/Products.CMFEditions/blob/7360a8431c98fdcaecbaaaafd321fd3881a88f9b/Products/CMFEditions/CopyModifyMergeRepositoryTool.py#L494
                    e = sys.exc_info()
                    logger.error(
                        "Caught exception in"
                        " HistoryAwareReferenceField: %s" % str(e))
                    o = r
                rd[uid] = o
            else:
                rd[uid] = r

        # singlevalued ref fields return only the object, not a list,
        # unless explicitely specified by the aslist option

        if not self.multiValued:
            if len(rd) > 1:
                msg = "%s references for non multivalued field %s of %s" % \
                    (len(rd), self.getName(), instance)
                logger.warning(msg)
            if not aslist:
                if rd:
                    rd = [rd[uid] for uid in rd.keys()][0]
                else:
                    rd = None

        if not self.referencesSortable or not hasattr(aq_base(instance),
                                                      'at_ordered_refs'):
            if isinstance(rd, dict):
                return [rd[uid] for uid in rd.keys()]
            else:
                return rd
        refs = instance.at_ordered_refs
        order = refs[self.relationship]

        return [rd[uid] for uid in order if uid in rd.keys()]

registerField(HistoryAwareReferenceField,
              title="History Aware Reference",
              description="",
              )
