# -*- coding: utf-8 -*-

import inspect
from copy import deepcopy

import six
from bika.lims import api
from bika.lims.api import snapshot as s_api
from bika.lims.utils import tmpID
from plone.dexterity.interfaces import IDexterityContent
from Products.Archetypes.interfaces import IBaseContent
from senaite.core.api import dtime
from senaite.core.interfaces import IVersionWrapper
from zope.interface import directlyProvides
from zope.interface import implementer


@implementer(IVersionWrapper)
class VersionWrapper(object):
    """A content wrapper that retrieves versioned attributes
    """
    def __init__(self, content):
        self.content = content
        self.clone = None
        self.version = 0

    def __repr__(self):
        return "<{}:{}({})>".format(
            self.__class__.__name__,
            api.get_portal_type(self.content),
            api.get_uid(self.content))

    def __getattr__(self, name):
        """Dynamic lookups for attributes
        """
        # support for tab completion in PDB
        if name == "__members__":
            return [k for k, v in inspect.getmembers(self.content)]

        if name in self.content.__dict__:
            # try to lookup the value from the snapshot
            if name in self.snapshot:
                return self.snapshot.get(name)

        # load setters from the wrapped content directly
        if name.startswith("set"):
            attr = getattr(self.content, name, None)
        else:
            # load all other attributes from the clone
            attr = getattr(self.clone, name, None)

        if attr:
            return attr

        return super(VersionWrapper, self).__getattr__(name)

    def get_version(self):
        return self.version

    def load_latest_version(self):
        """Load the latest version of the content
        """
        version = s_api.get_version(self.content)
        self.load_version(version)

    def load_version(self, version=0):
        """Load a snapshopt version
        """
        class Clone(self.content.__class__):
            pass

        # create a clone
        clone = Clone(tmpID())

        # make acquisition chain lookups possible
        clone = clone.__of__(self.content.aq_parent)

        # apply the versioned data to the clone
        clone.__dict__ = self.get_versioned_data(version)

        # workaround for APIError:
        # <Clone at /plone/setup/departments/department-2> is not supported
        if api.is_dexterity_content(self.content):
            directlyProvides(clone, IDexterityContent)
        elif api.is_at_content(self.content):
            directlyProvides(clone, IBaseContent)
        else:
            TypeError("Expected AT or DX content, got %r" % type(self.content))

        # remember the clone and loaded version
        self.clone = clone
        self.version = version

    def get_versioned_data(self, version):
        """Get the versioned data of the current content

        :param version: Version to fetch from the snapshot storage
        :returns: dictionary of versioned data
        """
        out = {}

        # get first a copy of the current content __data__
        data = deepcopy(self.content.__dict__)

        # fetch the snapshot of the object
        snapshot = s_api.get_snapshot_by_version(self.content, version)
        if not snapshot:
            raise KeyError("Version %s not found" % version)

        for key, value in data.items():

            # keep the original if we have no snapshot value
            if key not in snapshot:
                out[key] = value
            else:
                # get the snapshot value
                snap_value = snapshot.get(key)
                # assigned the processed snapshot value
                out[key] = self.process_snapshot_value(snap_value, value)

        return out

    def process_snapshot_value(self, value, original_value, default=None):
        """Convert stringified snapshot values

        We try to match the required field type of the content object w/o using
        setters of the cloned object, as this might have side effects
        (reindexing, additional logic etc.).

        :param value: Snapshot value
        :param original_value: Current set value on the content object
        :returns: Processed snapshot value
        """
        if not value:
            return default
        # convert None types
        if value in ["None", ""]:
            return None
        # convert boolean types
        if value in ["True", "False"]:
            return True if value == "True" else False
        if isinstance(original_value, six.types.IntType):
            value = int(value)
        if isinstance(original_value, six.types.FloatType):
            value = float(value)
        # convert date values
        if dtime.is_date(original_value) and value:
            return dtime.to_DT(value)
        return value


def VersionWrapperFactory(context):
    wrapper = VersionWrapper(context)
    wrapper.load_latest_version()
    return wrapper
