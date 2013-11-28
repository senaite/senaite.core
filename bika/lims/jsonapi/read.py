from bika.lims import logger
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from zope import interface
import App
import Missing
import json


def ar_analysis_values(obj):
    ret = []
    workflow = getToolByName(obj, 'portal_workflow')
    analyses = obj.getAnalyses(cancellation_state='active')
    for proxy in analyses:
        if proxy.review_state == 'retracted':
            continue
        ret.append({})
        # Place all proxy attributes into the result.
        for index in proxy.indexes():
            if index in proxy:
                val = getattr(proxy, index)
                if val != Missing.Value:
                    try:
                        json.dumps(val)
                    except:
                        continue
                    ret[-1][index] = val
        # Then schema field values
        analysis = proxy.getObject()
        schema = analysis.Schema()
        for field in schema.fields():
            accessor = field.getAccessor(analysis)
            if accessor and callable(accessor):
                val = accessor()
                if hasattr(val, 'Title') and callable(val.Title):
                    val = val.Title()
                try:
                    json.dumps(val)
                except:
                    val = str(val)
                ret[-1][field.getName()] = val
        if analysis.getRetested():
            retracted = obj.getAnalyses(review_state='retracted',
                                        title=analysis.Title(),
                                        full_objects=True)
            prevs = sorted(retracted, key=lambda item: item.created())
            prevs = [{'created': str(p.created()),
                      'Result': p.getResult(),
                      'InterimFields': p.getInterimFields()}
                     for p in prevs]
            ret[-1]['Previous Results'] = prevs
    return ret


def read(context, request):
    ret = {
        "url": router.url_for("read", force_external=True),
        "success": True,
        "error": False,
        "objects": [],
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
    for proxy in proxies:
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
            if obj.portal_type == 'AnalysisRequest' and fieldname == 'Analyses':
                val = ar_analysis_values(obj)
            else:
                val = field.get(obj)
                if val:
                    if field.type == 'reference':
                        if type(val) in (list, tuple):
                            val = [v.Title() for v in val]
                        else:
                            val = val.Title()
                else:
                    val = ''
                try:
                    json.dumps(val)
                except:
                    val = str(val)
            obj_data[fieldname] = val
        obj_data['path'] = "/".join(obj.getPhysicalPath())
        ret['objects'].append(obj_data)
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
