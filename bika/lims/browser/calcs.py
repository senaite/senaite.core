from Products.CMFCore.utils import getToolByName
import plone, json, sys, math

class AJAXCalculateAnalysisEntry():
    """ This view is called by javascript when an analysis' result or interim field value is
        entered. Returns a JSON dictionary, or None if no action is required or possible.
        - If the return has an 'error':string, it must also have a 'field' key, the value of which
          is the ID of the field which gets the (!).
        - If the return has a 'result' key, no other values are required.
    """

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)

        uid = self.request.get('uid')
        field = self.request.get('field')
        value = self.request.get('value')
        interim_fields = json.loads(self.request.get('item_data'))

        # all return values in here.
        # 'field' decides the position of the error (!) exclaimation
        ret = {'field':field}

        try:
            analysis = pc(portal_type='Analysis', UID=uid)[0].getObject()
        except:
            ret['error'] = 'Analysis %s does not exist (should not happen!)' % uid
            return json.dumps(ret)

        analyses = analysis.aq_parent.objectValues()
        service = analysis.getService()
        calculation = service.getCalculation()
        dependencies = calculation and calculation.getDependentServices() or []

        if calculation:
            # map keys to the names of services/fields in the calculation formula
            mapping = {}
            # modified interim_results gets returned to the html row's item_data
            item_data = []
            # check if all interim fields in the request have values
            for i in interim_fields:
                if i['id'] == field: i['value'] = value
                if str(i['value']) == '': return None # nop
                try:
                    i['value'] = float(i['value'])
                except:
                    ret['field'] = field
                    ret['error'] = 'The value specified is not a number'
                    return json.dumps(ret)
                mapping[i['id']] = i['value']
                item_data.append(i)
            ret['item_data'] = item_data
            # check if all dependent analyses in this AR have results
            for dep in dependencies:
                for a in analyses:
                    if a.getService().getUID() == dep.getUID():
                        if not a.getResult(): return None # nop
                        mapping[i['id']] = i['value']

            formula = calculation.getFormula()
            try:
                formula = eval("'%s'%%mapping"%formula,
                               {"__builtins__":None, 'math':math},
                               {'mapping': mapping})
                ret['formula'] = formula
                result = eval(formula)
            except ZeroDivisionError:
                ret['field'] = 'Result'
                ret['error'] = "Cannot divide by zero"
                return json.dumps(ret)
            except Exception, e:
                ret['field'] = 'Result'
                ret['error'] = e.msg
                return json.dumps(ret)

            # check if analyses that rely on this need to have their results
            # re-calculated now that this result is complete
            # back_dependencies = analysis.getBackReferences()

            ret['result'] = str(result)

        return json.dumps(ret)

