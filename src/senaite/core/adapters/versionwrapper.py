# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.api import snapshot as s_api
from plone.dexterity.interfaces import IDexterityContent
from Products.Archetypes.interfaces import IBaseContent
from senaite.core.interfaces import IVersionWrapper
from zope.interface import directlyProvides
from zope.interface import implementer
from copy import deepcopy
from bika.lims.utils import tmpID


@implementer(IVersionWrapper)
class VersionWrapper(object):
    """A content wrapper that retrieves versioned attributes
    """
    def __init__(self, content):
        self.content = content
        self.clone = None
        self.version = 0

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
        clone.__dict__ = deepcopy(self.content.__dict__)

        if api.is_dexterity_content(self.content):
            directlyProvides(clone, IDexterityContent)
        elif api.is_at_content(self.content):
            directlyProvides(clone, IBaseContent)
        else:
            TypeError("Expected AT or DX content, got %r" % type(self.content))

        # fetch the snapshot of the object
        snapshot = s_api.get_snapshot_by_version(self.content, version)
        if not snapshot:
            raise KeyError("Version %s not found" % version)

        clone.__dict__.update(snapshot)
        self.clone = clone
        self.version = version

    def __getattr__(self, name):
        """Dynamic lookups of non-found attributes
        """
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


def VersionWrapperFactory(context):
    wrapper = VersionWrapper(context)
    wrapper.load_latest_version()
    return wrapper
