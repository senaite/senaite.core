# -*- coding: utf-8 -*-

from bika.lims.api import create
from bika.lims.api import get_object
from bika.lims.api import get_senaite_setup
from bika.lims.api import search
from bika.lims.api import is_string
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import IHaveLabels
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


def validate_label(label):
    """Validates the label
    """
    if not is_string(label):
        raise TypeError("Expected label of type string, got %s" % type(labels))
    return True


def query_labels(inactive=False, **kw):
    """Fetch all labels by a catalog query
    """
    catalog = SETUP_CATALOG
    query = {
        "portal_type": "Label",
        "is_active": True,
        "sort_on": "title",
    }
    # Allow to update the query with the keywords
    query.update(kw)
    if inactive:
        del query["is_active"]
    return search(query, catalog)


def list_labels():
    """List all label titles
    """
    brains = query_labels()
    labels = map(lambda b: b.Title, brains)
    return list(set(labels))


def create_label(label, skip_duplicates=True, **kw):
    """Create new labels
    """
    validate_label(label)
    if skip_duplicates and label in list_labels():
        return None
    setup = get_senaite_setup()
    container = setup.get("labels")
    if container is None:
        return None
    return create(container, "Label", title=label, **kw)


def get_labels(obj):
    """Return the labels of this object
    """
    obj = get_object(obj)
    if not IHaveLabels.providedBy(obj):
        return []
    return obj.getLabels()


def has_labels(obj):
    """Check if the object has labels
    """
    return len(get_labels(obj)) > 0


def add_label(obj, label):
    """Add a label to the object
    """
    validate_label(label)
    obj = get_object(obj)
    alsoProvides(obj, IHaveLabels)
    labels = obj.getLabels()
    if label in labels:
        return False
    obj.setLabel(label)
    noLongerProvides(obj, IHaveLabels)
    return True


def del_label(obj, label):
    """Remove a label from the object
    """
    obj = get_object(obj)
    labels = get_labels(obj)
    if label not in labels:
        return False
    new_labels = filter(lambda l: l == label, labels)
    obj.setLabels(new_labels)
    if not labels:
        alsoProvides(obj, IHaveLabels)
    labels = obj.getLabels()
    if label in labels:
        return False
    obj.setLabel(label)
    return True
