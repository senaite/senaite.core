from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def set_fields_from_request(obj, request):
    """Search request for keys that match field names in obj.

    - Calls field mutator with request value
    - Calls Accessor to retrieve value
    - Returns a dict of fields and current values

    If the field name in the request is <portal_type>_<index>
    Then the corrosponding index will be used to look up the object
    from the uid_catalog.  This is for setting reference fields, and the
    UID of the object found will be sent to the mutator.

    """
    schema = obj.Schema()
    # fields contains all schema-valid field values from the request.
    fields = {}
    for key, value in request.items():
        if "_" in key:
            fieldname, index = key.split("_", 1)
            if fieldname not in schema:
                continue
            pc = getToolByName(obj, "portal_catalog")
            brains = pc({'portal_type': fieldname, index: request[key]})
            if not brains:
                # object lookup failure need not be fatal;
                # XXX for now we silently ignore lookup failure here,
                continue
            value = brains[0].UID if brains else request[fieldname]
        else:
            fieldname = key
            if fieldname not in schema:
                continue
            value = request[fieldname]
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
            ret[fieldname] = str(val)
    return ret
