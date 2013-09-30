from Products.Archetypes.config import TOOL_NAME
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def resolve_request_lookup(context, request, fieldname):
    brains = []
    at = getToolByName(context, TOOL_NAME, None)
    for entry in request[fieldname].split("|"):
        contentFilter = {}
        for value in entry.split(","):
            if ":" in value:
                index, value = value.split(":", 1)
            else:
                index, value = 'id', value
            contentFilter[index] = value
        # search all possible catalogs
        if 'portal_type' in contentFilter:
            catalogs = at.getCatalogsByType(contentFilter['portal_type'])
        else:
            catalogs = [getToolByName(context, 'portal_catalog'), ]
        for catalog in catalogs:
            _brains = catalog(contentFilter)
            if _brains:
                brains.extend(_brains)
                break
    return brains


def set_fields_from_request(obj, request):
    """Search request for keys that match field names in obj.

    - Calls field mutator with request value
    - Calls Accessor to retrieve value
    - Returns a dict of fields and current values

    To set Reference fields embed the portal_catalog search

    ...& <FieldName>=index:value &...
    ...& <FieldName>=index:value|index:value &...

    """
    schema = obj.Schema()
    # fields contains all schema-valid field values from the request.
    fields = {}
    for fieldname, value in request.items():
        if fieldname not in schema:
            continue
        print schema[fieldname].type
        if schema[fieldname].type in ('reference'):
            brains = resolve_request_lookup(obj, request, fieldname)
            if not brains:
                raise BadRequest("Can't resolve reference: %s" % fieldname)
            if schema[fieldname].multiValued:
                value = [b.UID for b in brains]
            else:
                value = brains[0].UID
        fields[fieldname] = value
    # Write fields.
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
        obj.reindexObject()
