""" View utilities.
"""
class utils:

    def categories_in_poc(self, poc, full_objects = False):
        pc = getToolByName(self, 'portal_catalog')
        res = pc(portal_type = 'AnalysisCategory', getPointOfCapture = poc)
        if full_objects:
            res = [r.getObject() for r in res]
        return res

    def services_in_category(self, cat, full_objects = False):
        pc = getToolByName(self, 'portal_catalog')
        res = pc(portal_type = 'AnalysisCategory', getCategory = cat)
        if full_objects:
            res = [r.getObject() for r in res]
        return res

