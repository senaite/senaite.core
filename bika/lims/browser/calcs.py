from Products.CMFCore.utils import getToolByName
import json

class CalculateAnalysisEntry():

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):

        uid = self.request.get('uid')
        field = self.request.get('field')
        value = self.request.get('value')

        pc = getToolByName(self.context, 'portal_catalog')

        try: analysis = pc(portal_type='Analysis', UID=uid)[0].getObject()
        except: return None

        interim_fields = analysis.getInterimFields()
        service = analysis.getService()
        calculation = service.getCalculation()
        dependencies = calculation.getDependentServices()
        back_dependencies = service.getBackReferences()

        # filter dependencies to permit only those present in this AR's context.
#        for dep in dependencies:





        return json.dumps({'helloworld':'yes.'})