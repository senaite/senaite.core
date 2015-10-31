from Products.Archetypes.config import TOOL_NAME
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from bika.lims.utils import safe_unicode
import json
import Missing
import sys, traceback


def handle_errors(f):
    """ simple JSON error handler
    """
    import traceback
    from plone.jsonapi.core.helpers import error

    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            var = traceback.format_exc()
            return error(var)

    return decorator


def get_include_fields(request):
    """Retrieve include_fields values from the request
    """
    include_fields = []
    rif = request.get("include_fields", "")
    if "include_fields" in request:
        include_fields = [x.strip()
                          for x in rif.split(",")
                          if x.strip()]
    if "include_fields[]" in request:
        include_fields = request['include_fields[]']
    return include_fields


def load_brain_metadata(proxy, include_fields):
    """Load values from the catalog metadata into a list of dictionaries
    """
    ret = {}
    for index in proxy.indexes():
        if not index in proxy:
            continue
        if include_fields and index not in include_fields:
            continue
        val = getattr(proxy, index)
        if val != Missing.Value:
            try:
                json.dumps(val)
            except:
                continue
            ret[index] = val
    return ret


def load_field_values(instance, include_fields):
    """Load values from an AT object schema fields into a list of dictionaries
    """
    ret = {}
    schema = instance.Schema()
    for field in schema.fields():
        fieldname = field.getName()
        if include_fields and fieldname not in include_fields:
            continue
        try:
            val = field.get(instance)
        except AttributeError:
            # If this error is raised, make a look to the add-on content expressions used to obtain their data.
            print "AttributeError:", sys.exc_info()[1]
            print "Unreachable object. Maybe the object comes from an Add-on"
            print traceback.format_exc()

        if val:
            if field.type == "blob" or field.type == 'file':
                continue
            # I put the UID of all references here in *_uid.
            if field.type == 'reference':
                if type(val) in (list, tuple):
                    ret[fieldname + "_uid"] = [v.UID() for v in val]
                    val = [safe_unicode(v.Title()) for v in val]
                else:
                    ret[fieldname + "_uid"] = val.UID()
                    val = safe_unicode(val.Title())
            elif field.type == 'boolean':
                val = True if val else False
            elif field.type == 'text':
                val = safe_unicode(val)

        try:
            json.dumps(val)
        except:
            val = str(val)
        ret[fieldname] = val
    return ret


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
        elif 'uid' in contentFilter:
            # If a uid is found, the object could be searched for its own uid
            uc = getToolByName(context, 'uid_catalog')
            return uc(UID=contentFilter['uid'])

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

    The list of fields for which schema mutators were found
    is returned.
    """
    schema = obj.Schema()
    # fields contains all schema-valid field values from the request.
    fields = {}
    for fieldname, value in request.items():
        if fieldname not in schema:
            continue
        if schema[fieldname].type in ('reference'):
            brains = []
            if value:
                brains = resolve_request_lookup(obj, request, fieldname)
                if not brains:
                    raise BadRequest("Can't resolve reference: %s" % fieldname)
            if schema[fieldname].multiValued:
                value = [b.UID for b in brains] if brains else []
            else:
                value = brains[0].UID if brains else None
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
        if mutator:
            mutator(value)
        else:
            field.set(obj, value)
    obj.reindexObject()
    return fields.keys()
