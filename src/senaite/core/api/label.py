# -*- coding: utf-8 -*-

from bika.lims.api import create
from bika.lims.api import get_object
from bika.lims.api import get_senaite_setup
from bika.lims.api import is_string
from bika.lims.api import search
from persistent.list import PersistentList
from senaite.core import logger
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import ICanHaveLabels
from senaite.core.interfaces import IHaveLabels
from senaite.core.interfaces import ILabel
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

FIELD_NAME = "ExtLabels"
LABEL_STORAGE = "senaite.core.labels"


def get_storage(obj):
    """Get or create the audit log storage for the given object

    :param obj: Content object
    :returns: PersistentList
    """
    annotation = IAnnotations(obj)
    if annotation.get(LABEL_STORAGE) is None:
        annotation[LABEL_STORAGE] = PersistentList()
    return annotation[LABEL_STORAGE]


def validate_label(label):
    """Validates the label
    """
    if not is_string(label):
        raise TypeError("Expected label of type string, got %s" % type(label))
    return True


def is_label(obj):
    """Checks if the given object is a label

    :param obj: Object to check
    :returns: True if the object is a label
    """
    return ILabel.providedBy(obj)


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


def get_label_by_name(name, inactive=True):
    """Fetch a label by name

    :param name: Name of the label
    :returns: Label object or None
    """
    found = query_labels(title=name)
    if len(found) == 0:
        return None
    elif len(found) > 1:
        logger.warn("Found more than one label for '%s'"
                    "Returning the first label only" % name)
    return found[0]


def list_labels(inactive=False, **kw):
    """List all label titles
    """
    brains = query_labels(inactive=inactive, **kw)
    labels = map(lambda b: b.Title, brains)
    return list(set(labels))


def create_label(label, **kw):
    """Create new labels
    """
    validate_label(label)
    # Do not reate duplicate labels
    existing_label = get_label_by_name(label, inactive=True)
    if existing_label:
        return existing_label
    setup = get_senaite_setup()
    return create(setup.labels, "Label", title=label, **kw)


def get_labels(obj):
    """Get the attached labels from the annotation storage of the object
    """
    obj = get_object(obj)
    if not IHaveLabels.providedBy(obj):
        return []


def set_labels(obj, value):
    """Set the labels in the annotation storage of the object
    """


def has_labels(obj):
    """Check if the object has labels
    """
    return len(get_labels(obj)) > 0


def add_label(obj, label):
    """Add a label to the object

    :param obj: the object to label
    :param label: string or label object to add
    :returns: True if the object was labeled
    """
    # handle string labels
    if is_string(label):
        label = create_label(label)
    obj = get_object(obj)
    # Mark the object for schema extension
    alsoProvides(obj, ICanHaveLabels)
    labels = getLabels()
    if label in labels:
        return False
    # set the label with the extended setter
    setLabels(label)
    # add marker interface
    alsoProvides(obj, IHaveLabels)
    return True


def del_label(obj, label):
    """Remove a label from the object
    """
    # handle string labels
    if is_string(label):
        label = create_label(label)
    obj = get_object(obj)
    # Mark the object for schema extension
    alsoProvides(obj, ICanHaveLabels)
    labels = get_labels(obj)
    if label not in labels:
        return False
    new_labels = filter(lambda l: l == label, labels)
    obj.setLabels(new_labels)
    if not labels:
        noLongerProvides(obj, IHaveLabels)
    return True
