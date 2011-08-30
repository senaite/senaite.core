from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims.config import COUNTRY_NAMES
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
import sys
from Products.CMFEditions.Permissions import SaveNewVersion
from Products.Archetypes.config import REFERENCE_CATALOG
# I want all default behaviour including i18n.
from bika.lims import bikaMessageFactory as _

class HistoryAwareReferenceField(ReferenceField):
    """ Version aware references.

    Uses txhe object's version_id to retrieve target object
    data.  This means update_version_on_edit must be called
    when a versioned object is edited.

    If the current user has SaveNewVersion on the source.
    all existing reference versions will be updated to the
    current version_id of the target objects.

    """
    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """Mutator.

        check that new objects have a version
        XXX apply versioning on first save.

        take SaveNewVersion permission
        bump versions,
        save source:
        source's target should be latest version

        remove SaveNewVersion permission
        bump versions,
        save source:
        source's target should not be updated to latest

        """
        rc = getToolByName(instance, REFERENCE_CATALOG)
        targetUIDs = [ref.targetUID for ref in
                      rc.getReferences(instance, self.relationship)]

        if value is None:
            value = ()

        if not isinstance(value, (list, tuple)):
            value = value,
        elif not self.multiValued and len(value) > 1:
            raise ValueError, \
                  "Multiple values given for single valued field %r" % self

        pm = getToolByName(instance, "portal_membership")
        member = pm.getAuthenticatedMember()
        canSaveNewVersion = pm.checkPermission(SaveNewVersion, instance)

        #convert objects to uids
        #convert uids to objects
        uids = []
        targets = {}
        for v in value:
            if isinstance(v, basestring):
                uids.append(v)
                targets[v] = rc.lookupObject(v)
            else:
                uids.append(v.UID())
                targets[v.UID()] = v

        sub = [t for t in targetUIDs if t not in uids]
        add = [v for v in uids if v and v not in targetUIDs]

        if canSaveNewVersion:
            for uid in [t for t in targetUIDs if t not in sub+add ]:
                # update version_id of all existing references that aren't
                # in add or sub (default reference leaves these alone).
                version_id = hasattr(targets[uid], 'version_id') and \
                           targets[uid].version_id or None
                if not version_id:
                    # attempt initial save of unversioned targets
                    pr = getToolByName(instance, 'portal_repository')
                    if pr.isVersionable(targets[uid]):
                        pr.save(obj=instance, comment=_("Initial revision"))
                    else:
                        raise ValueError, "%s not versionable for field %s at %s" % \
                              (targets[uid],self.getName(), instance)
                    version_id = 0
                if not hasattr(instance, 'reference_versions'):
                    instance.reference_versions = {}
                instance.reference_versions[uid] = version_id

        # tweak keyword arguments for addReference
        addRef_kw = kwargs.copy()
        addRef_kw.setdefault('referenceClass', self.referenceClass)
        if addRef_kw.has_key('schema'): del addRef_kw['schema']
        for uid in add:
            __traceback_info__ = (instance, uid, value, targetUIDs)
            # throws IndexError if uid is invalid
            rc.addReference(instance, uid, self.relationship, **addRef_kw)

        for uid in sub:
            rc.deleteReference(instance, uid, self.relationship)

        if self.referencesSortable:
            if not hasattr( aq_base(instance), 'at_ordered_refs'):
                instance.at_ordered_refs = {}

            instance.at_ordered_refs[self.relationship] = tuple( filter(None, uids) )

        if self.callStorageOnSet:
            #if this option is set the reference fields's values get written
            #to the storage even if the reference field never use the storage
            #e.g. if i want to store the reference UIDs into an SQL field
            ObjectField.set(self, instance, self.getRaw(instance), **kwargs)

    security.declarePrivate('get')
    def get(self, instance, aslist=False, **kwargs):
        """get() returns the list of objects referenced under the relationship.
        """

        res = instance.getRefs(relationship=self.relationship)

        # singlevalued ref fields return only the object, not a list,
        # unless explicitely specified by the aslist option

        if not self.multiValued:
            if len(res) > 1:
                log("%s references for non multivalued field %s of %s" % (len(res),
                                                                          self.getName(),
                                                                          instance))
            if not aslist:
                if res:
                    res = res[0]
                else:
                    res = None

        if not self.referencesSortable or not hasattr( aq_base(instance), 'at_ordered_refs'):
            return res

        pr = getToolByName(instance, 'portal_repository')
        rd = {}
        for r in res:
            uid = r.UID()
            if uid in instance.reference_versions[uid]:
                version_id = instance.reference_versions[uid]
                o = pr.retrieve(r, selector=version_id).data.object
            else:
                o = r
            rd[uid] = o
        refs = instance.at_ordered_refs
        order = refs[self.relationship]

        return [rd[uid] for uid in order if uid in rd.keys()]

registerField(HistoryAwareReferenceField,
              title = "History Aware Reference",
              description = "",
              )
