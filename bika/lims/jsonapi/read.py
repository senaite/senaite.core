from bika.lims import logger
from bika.lims.interfaces import IJSONReadExtender
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from plone.protect.authenticator import AuthenticatorView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from zope import interface
from zope.component import getAdapters
import App
import json
import Missing
import re


def read(context, request):

    tag = AuthenticatorView(context, request).authenticator()
    pattern = '<input .*name="(\w+)".*value="(\w+)"'
    _authenticator = re.match(pattern, tag).groups()[1]

    ret = {
        "url": router.url_for("read", force_external=True),
        "success": True,
        "error": False,
        "objects": [],
        "_authenticator": _authenticator,
    }
    debug_mode = App.config.getConfiguration().debug_mode
    catalog_name = request.get("catalog_name", "portal_catalog")
    if not catalog_name:
        raise ValueError("bad or missing catalog_name: " + catalog_name)
    catalog = getToolByName(context, catalog_name)
    indexes = catalog.indexes()
    contentFilter = {}
    for index in indexes:
        if index in request:
            if index == 'review_state' and "{" in request[index]:
                continue
            contentFilter[index] = request[index]
        if "{0}[]".format(index) in request:
            contentFilter[index] = request["{0}[]".format(index)]
    if 'limit' in request:
        try:
            contentFilter['sort_limit'] = int(request["limit"])
        except ValueError:
            pass
    sort_on = request.get('sort_on', 'id')
    contentFilter['sort_on'] = sort_on
    # sort order
    sort_order = request.get('sort_order', '')
    if sort_order:
        contentFilter['sort_order'] = sort_order
    else:
        sort_order = 'ascending'
        contentFilter['sort_order'] = 'ascending'

    include_fields = []
    if "include_fields" in request:
        include_fields = [x.strip() for x in request.get("include_fields", "").split(",")
                          if x.strip()]
    if "include_fields[]" in request:
        include_fields = request['include_fields[]']
    if debug_mode:
        logger.info("contentFilter: " + str(contentFilter))
        if include_fields:
            logger.info("include_fields: " + str(include_fields))

    # Get matching objects from catalog
    proxies = catalog(**contentFilter)

    # batching items
    page_nr = int(request.get("page_nr", 0))
    page_size = int(request.get("page_size", 10))
    first_item_nr = page_size*page_nr
    if first_item_nr > len(proxies):
        first_item_nr = 0
    page_proxies = proxies[first_item_nr:first_item_nr+page_size]
    for proxy in page_proxies:
        obj_data = {}
        # Place all proxy attributes into the result.
        for index in proxy.indexes():
            if include_fields and index not in include_fields:
                continue
            if index in proxy:
                val = getattr(proxy, index)
                if val != Missing.Value:
                    try:
                        json.dumps(val)
                    except:
                        continue
                    obj_data[index] = val
        # scan schema for fields and insert their values.
        obj = proxy.getObject()
        schema = obj.Schema()
        for field in schema.fields():
            fieldname = field.getName()
            if include_fields and fieldname not in include_fields:
                continue
            else:
                val = field.get(obj)
                if val:
                    if field.type == "blob":
                        continue
                    # I put the UID of all references here in *_uid.
                    if field.type == 'reference':
                        if type(val) in (list, tuple):
                            obj_data[fieldname+"_uid"] = [v.UID() for v in val]
                            val = [v.Title() for v in val]
                        else:
                            obj_data[fieldname+"_uid"] = val.UID()
                            val = val.Title()
                else:
                    val = ''
                try:
                    json.dumps(val)
                except:
                    val = str(val)
            obj_data[fieldname] = val
        obj_data['path'] = "/".join(obj.getPhysicalPath())
        # call any adapters that care to modify this data.
        adapters = getAdapters((obj, ), IJSONReadExtender)
        for name, adapter in adapters:
            obj_data = adapter(request, obj_data)

        ret['objects'].append(obj_data)
    ret['total_objects'] = len(proxies)
    ret['first_object_nr'] = first_item_nr
    last_object_nr = first_item_nr + len(page_proxies)
    if last_object_nr > ret['total_objects']:
        last_object_nr = ret['total_objects']
    ret['last_object_nr'] = last_object_nr

    if debug_mode:
        logger.info("{0} objects returned".format(len(ret['objects'])))
    return ret


class Read(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/read", "read", self.read, dict(methods=['GET', 'POST'])),
        )

    def read(self, context, request):
        """/@@API/read: Search the catalog and return data for all objects found

        Optional parameters:

            - catalog_name: uses portal_catalog if unspecified
            - limit  default=1
            - All catalog indexes are searched for in the request.

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
            objects: list of dictionaries, containing catalog metadata
        }
        """

        return read(context, request)
