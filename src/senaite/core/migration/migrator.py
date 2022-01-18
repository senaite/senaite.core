# -*- coding: utf-8 -*-

import json

import six

from Acquisition import aq_parent
from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IAuditable
from plone.dexterity.interfaces import IDexterityContent
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IField
from senaite.core.interfaces import IContentMigrator
from senaite.core.interfaces import IFieldMigrator
from senaite.core.migration.utils import copyPermMap
from z3c.form.interfaces import IDataManager
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import directlyProvidedBy
from zope.interface import implementer

SKIP_FIELDS = [
    "id",
    "allowDiscussion",
    "subject",
    "location",
    "contributors",
    "creators",
    "effectiveDate",
    "expirationDate",
    "language",
    "rights",
    "creation_date",
]


@implementer(IContentMigrator)
class ContentMigrator(object):
    """SENAITE content migrator
    """
    def __init__(self, src, target):
        self.src = src
        self.target = target

    def migrate(self):
        """Run the migration
        """
        raise NotImplementedError("Must be implemented by subclass")

    def uncatalog_object(self, obj):
        """Uncatalog the object for all catalogs
        """
        # uncatalog from registered catalogs
        obj.unindexObject()
        # explicitly uncatalog from uid_catalog
        uid_catalog = api.get_tool("uid_catalog")
        url = "/".join(obj.getPhysicalPath()[2:])
        uid_catalog.uncatalog_object(url)

    def catalog_object(self, obj):
        """Catalog the object
        """
        obj.reindexObject()

    def copy_uid(self, obj, uid):
        """Set uid on object
        """
        if api.is_dexterity_content(obj):
            setattr(obj, "_plone.uuid", uid)
        elif api.is_at_content(obj):
            setattr(obj, "_at_uid", uid)
        else:
            raise TypeError("Cannot set UID on that object")

    def copy_dates(self, src, target):
        """copy modification/creation date
        """
        created = api.get_creation_date(src)
        modified = api.get_modification_date(src)
        target.creation_date = created
        target.setModificationDate(modified)

    def copy_creators(self, src, target):
        """Copy creators
        """
        target.setCreators(src.listCreators())

    def copy_workflow_history(self, src, target):
        """Copy workflow history
        """
        wfh = getattr(src, "workflow_history", None)
        if wfh:
            wfh = copyPermMap(wfh)
            target.workflow_history = wfh

    def copy_marker_interfaces(self, src, target):
        """Copy marker interfaces
        """
        alsoProvides(target, directlyProvidedBy(src))

    def copy_snapshots(self, src, target):
        """copy over snapshots from source -> target
        """
        snapshots = api.snapshot.get_snapshots(src)
        storage = api.snapshot.get_storage(target)
        storage[:] = map(json.dumps, snapshots)[:]
        alsoProvides(target, IAuditable)

    def delete_object(self, obj):
        """delete the object w/o firing events
        """
        self.uncatalog_object(obj)
        parent = aq_parent(obj)
        parent._delObject(obj.getId(), suppress_events=True)

    def copy_fields(self, src, target, mapping):
        """Copy fields
        """
        src_fields = api.get_fields(src)
        for fname, field in src_fields.items():
            if fname in SKIP_FIELDS:
                continue
            field_migrator = getMultiAdapter(
                (field, src, target), interface=IFieldMigrator)
            # migrate the field
            field_migrator.migrate(mapping)


class ATDXContentMigrator(ContentMigrator):
    """Migrate from AT to DX contents
    """
    adapts(IBaseObject, IDexterityContent)

    def migrate(self, mapping=None, delete_src=True):
        """Migrate AT content to DX

        :param mapping: a mapping from source schema field name to a tuple of
                        (accessor name, target field name, default value)
        """
        if mapping is None:
            mapping = {}

        # copy_fields
        self.copy_fields(self.src, self.target, mapping)

        # copy the UID
        self.copy_uid(self.src, self.target)

        # copy auditlog
        self.copy_snapshots(self.src, self.target)

        # copy creators
        self.copy_creators(self.src, self.target)

        # copy workflow history
        self.copy_workflow_history(self.src, self.target)

        # copy marker interfaces
        self.copy_marker_interfaces(self.src, self.target)

        # copy dates
        self.copy_dates(self.src, self.target)

        # uncatalog the source object
        self.uncatalog_object(self.src)

        # reindex the new object
        self.catalog_object(self.target)

        # delete source object if requested
        if delete_src:
            self.delete_object(self.src)


@implementer(IFieldMigrator)
class FieldMigrator(object):
    """SENAITE field migrator
    """
    def __init__(self, field, src, target):
        self.field = field
        self.src = src
        self.target = target

    def migrate(self):
        raise NotImplementedError("Must be implemented by subclass")


class ATDXFieldMigrator(FieldMigrator):
    """SENAITE AT to DX field migrator
    """
    adapts(IField, IBaseObject, IDexterityContent)

    def migrate(self, mapping):
        # get all fields on the target
        target_fields = api.get_fields(self.target)

        fieldname = self.field.getName()

        # check if we have a mapping for this field
        accessor, target_fieldname, default = (None, None, None, )
        if fieldname in mapping:
            accessor, target_fieldname, default = mapping[fieldname]

        target_field = None
        if target_fieldname:
            # get the target field with the mapped name
            target_field = target_fields.get(target_fieldname)
        else:
            # check for a field with the same name on the target
            target_field = target_fields.get(fieldname)

        # no target field found ...
        if target_field is None:
            logger.info("Skipping migration for field '%s'" % fieldname)
            return False

        if accessor:
            # get the source field value from the accessor
            value = getattr(self.src, accessor, default)
            if callable(value):
                value = value()
        else:
            # get the source value with the default getter from the field
            value = self.field.get(fieldname)

        # always convert string values to unicode for dexterity fields
        if isinstance(value, six.string_types):
            value = api.safe_unicode(value)

        # set the value with the datamanager (another point to override)
        dm = getMultiAdapter(
            (self.target, target_field), interface=IDataManager)
        if dm:
            dm.set(value)
        else:
            target_field.set(self.target, value)

        logger.info("Migrated field %s -> %s" % (fieldname, target_fieldname))
