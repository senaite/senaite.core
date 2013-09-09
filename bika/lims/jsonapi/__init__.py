from Products.Archetypes.config import TOOL_NAME
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest

import json


def set_fields_from_request(obj, request):
    """Search request for keys that match field names in obj.

    - Calls field mutator with request value
    - Calls Accessor to retrieve value
    - Returns a dict of fields and current values

    To set Reference fields:

    ...& <FieldName>=<obj type>:<obj title> &...

    """
    at = getToolByName(obj, TOOL_NAME, None)
    schema = obj.Schema()
    # fields contains all schema-valid field values from the request.
    fields = {}
    for fieldname, value in request.items():
        if fieldname not in schema:
            continue
        if ":" in value:
            # Reference field lookup
            field = schema[fieldname]
            dst_type, title = value.split(":", 1)
            result = None
            brains = []
            # search all possible catalogs
            for catalog in at.getCatalogsByType(dst_type):
                brains = catalog({'portal_type': dst_type, 'Title': title})
                if not brains:
                    continue
            if not brains:
                raise BadRequest("Object of type '%s' not found (title='%s')" %
                                 (dst_type, title))
            value = brains[0].UID
        fields[fieldname] = value
    # write and then read each field.
    ret = {}
    for fieldname, value in fields.items():
        field = schema[fieldname]
        fieldtype = field.getType()
        if fieldtype == 'Products.Archetypes.Field.BooleanField':
            if value.lower() in ('0', 'false', 'no') or not value:
                value = False
            else:
                value = True
        elif fieldtype in ['Products.ATExtensions.field.records.RecordsField',
                           'Products.ATExtensions.field.records.RecordField']:
            try:
                value = eval(value)
            except:
                raise BadRequest(fieldname + ": Invalid JSON/Python variable")
        mutator = field.getMutator(obj)
        if mutator and callable(mutator):
            mutator(value)
        accessor = field.getAccessor(obj)
        if accessor and callable(accessor):
            val = accessor()
            if hasattr(val, 'Title') and callable(val.Title):
                val = val.Title()
            ret[fieldname] = json.dumps(val)
    return ret
