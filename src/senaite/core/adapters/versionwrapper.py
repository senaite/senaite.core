# -*- coding: utf-8 -*-

import inspect
from copy import deepcopy

from bika.lims import api
from bika.lims.api import snapshot as s_api
from bika.lims.utils import tmpID
from senaite.core.api import dtime
from senaite.core.interfaces import IVersionWrapper
from zope.interface import alsoProvides
from zope.interface import implementer


def restsricted_method(instance, func_name):
    """Restricted method to avoid harmful actions on the wrapper
    """
    def dummy(*args, **kw):
        raise AttributeError("It is not allowed to call the method '%s' "
                             "on a version wrapper!" % func_name)
    return dummy


@implementer(IVersionWrapper)
class VersionWrapper(object):
    """A content wrapper that retrieves versioned attributes
    """
    def __init__(self, content):
        self.content = content
        self.fields = api.get_fields(content)
        self.clone = None
        self.version = 0

    def __repr__(self):
        return "<{}:{}({}@v{})>".format(
            self.__class__.__name__,
            api.get_portal_type(self.content),
            api.get_id(self.content),
            self.version)

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

        if self.is_restricted_method(name):
            attr = restsricted_method(self, name)
        else:
            # load all other attributes from the clone
            attr = getattr(self.clone, name, None)

        if attr:
            return attr

        return super(VersionWrapper, self).__getattr__(name)

    def is_restricted_method(self, name):
        """Checks if the method is restricted
        """
        func_name = name.lower()
        attr = getattr(self.clone, name, None)
        is_callable = callable(attr)
        if func_name.startswith("set") and is_callable:
            return True
        elif func_name.startswith("manage_") and is_callable:
            return True
        elif "index" in func_name and is_callable:
            return True
        return False

    def get_version(self):
        return self.version

    def get_clone(self):
        return self.clone

    def load_latest_version(self):
        """Load the latest version of the content
        """
        version = s_api.get_version(self.content)
        self.load_version(version)

    def make_metaclass(self, prefix="Clone"):
        """Returns a new metaclass
        """
        cls_base = self.content.__class__
        cls_name = cls_base.__name__
        cls_dict = {"__module__": cls_base.__module__}
        return type(prefix + cls_name, (cls_base, ), cls_dict)

    def load_version(self, version=0):
        """Load a snapshopt version
        """
        MetaClass = self.make_metaclass()
        clone = MetaClass(tmpID())

        # make acquisition chain lookups possible
        clone = clone.__of__(self.content.aq_parent)

        # apply the versioned data to the clone
        clone.__dict__ = self.get_versioned_data(version)

        # apply class interfaces manually
        class_ifaces = self.content.__class__.__implemented__.flattened()
        alsoProvides(clone, *class_ifaces)

        # keep some backreferences on the clone
        clone._original = self.content
        clone._wrapper = self
        # BBB: used in services info popup
        clone.version_id = version

        # remember the clone and loaded version
        self.clone = clone
        self.version = version
        # BBB: used in services info popup
        self.version_id = version

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
                # assigned the processed snapshot value
                out[key] = self.process_snapshot_value(key, snapshot)

        return out

    def process_snapshot_value(self, key, snapshot):
        """Convert stringified snapshot values

        We try to match the required field type of the content object w/o using
        setters of the cloned object, as this might have side effects
        (reindexing, additional logic etc.).

        :param key: Processing key
        :param snapshot: The versioned snapshot
        :returns: Processed snapshot value
        """
        value = snapshot.get(key)

        # try to get the field
        field = self.fields.get(key)
        if not field:
            return value

        # directly convert empties, None and bool values
        if not value:
            return value
        elif value == "None":
            return None
        elif value in ["True", "False"]:
            return True if value == "True" else False

        # guess the required value type depending on the used field
        fieldclass = field.__class__.__name__.lower()
        fieldtype = getattr(field, "type", None)

        if fieldclass.startswith("date"):
            # convert date value
            return dtime.to_DT(value)
        elif fieldclass.startswith("integer"):
            return int(value)
        elif fieldclass.startswith("float"):
            return float(value)
        elif fieldclass == "fixedpointfield":
            # AT fixedpoint field
            return field._to_tuple(self.content, value)
        elif fieldclass == "durationfield":
            # AT duration field
            return {str(key): int(val) for key, val in value.items()}
        elif fieldclass == "emailsfield":
            # AT emails fields
            return value or ''
        elif fieldtype == "record":
            # AT record-like fields
            return value or {}
        return value


def VersionWrapperFactory(context):
    wrapper = VersionWrapper(context)
    wrapper.load_latest_version()
    return wrapper
