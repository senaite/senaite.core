from Products.Archetypes.config import TOOL_NAME
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def handle_errors(f):
    """ simple JSON error handler
    """
    import traceback
    from plone.jsonapi.core.helpers import error

    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            var = traceback.format_exc()
            return error(var)
    return decorator


def resolve_request_lookup(context, request, fieldname):
    if fieldname not in request:
        return []
    brains = []
    at = getToolByName(context, TOOL_NAME, None)
    entries = request[fieldname] if type(request[fieldname]) in (list, tuple) \
              else [request[fieldname], ]
    for entry in entries:
        contentFilter = {}
        for value in entry.split("|"):
            if ":" in value:
                index, value = value.split(":", 1)
            else:
                index, value = 'id', value
            if index in contentFilter:
                v = contentFilter[index]
                v = v if type(v) in (list, tuple) else [v, ]
                v.append(value)
                contentFilter[index] = v
            else:
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
    """Search request for keys that match field names in obj,
    and call field mutator with request value.
    """
    schema = obj.Schema()
    # fields contains all schema-valid field values from the request.
    fields = {}
    for fieldname, value in request.items():
        if fieldname not in schema:
            continue
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
        mutator = field.set(obj, value)
    obj.reindexObject()
