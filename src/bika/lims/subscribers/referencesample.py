# -*- coding: utf-8 -*-

from bika.lims import api


def ObjectEditedEventHandler(obj, event):
    """Event called after modifying a ReferenceSample, that is not in the
    creation stage any more. It updates the ID of the reference sample with the
    value of field ManualID if valid and different from current id
    """
    # compare with current id
    obj_id = obj.getId()
    manual_id = obj.getManualId()
    if obj_id == manual_id:
        return

    # check if this new id is valid
    parent = api.get_parent(obj)
    if not api.is_valid_id(manual_id, container=parent):
        return

    # re-assign id and reindex
    obj.setId(manual_id)
    obj.reindexObject()
