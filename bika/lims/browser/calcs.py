from Products.CMFCore.utils import getToolByName
import json, sys, math

class AJAXCalculateAnalysisEntry():
    """ This view is called by javascript when an analysis' result or interim field value is
        entered.
    """
    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')

        uid = self.request.get('uid')
        field = self.request.get('field')
        value = self.request.get('value')
        interim_fields = json.loads(self.request.get('item_data'))

        # all return values are JSON objects; this is the variable that is encoded.
        # uid and field are included to let javascript know where to place error messages.
        ret = {'uid':uid, 'field':field}

        try:
            analysis = pc(portal_type='Analysis', UID=uid)[0].getObject()
        except:
            ret['field'] = 'Result'
            ret['error'] = 'The analysis does not exist (should not happen!)'
            return json.dumps(ret)

        analyses = analysis.aq_parent.objectValues()
        service = analysis.getService()
        calculation = service.getCalculation()
        dependencies = calculation and calculation.getDependentServices() or []

        if calculation:
            # map keys to the names of services/fields in the calculation formula.
            mapping = {}
            # check if all interim fields in the request have values
            for i in interim_fields:
                if i['id'] == field: i['value'] = value
                try:
                    i['value'] = float(i['value'])
                except:
                    ret['error'] = 'The value specified is not a number'
                    return json.dumps(ret)
                mapping[i['id']] = i['value']
            # check if all dependent analyses in this AR have results
            for dep in dependencies:
                for a in analyses:
                    if a.getService().getUID() == dep.getUID():
                        if not a.getResult(): return None # nop, not error
                        mapping[i['id']] = i['value']
            formula = calculation.getFormula()
            try:
                formula = eval("'%s'%%mapping"%formula,
                               {"__builtins__":None, 'math':math},
                               {'mapping': mapping})
                result = eval(formula)
            except ZeroDivisionError:
                ret['field'] = 'Result'
                ret['error'] = "Cannot divide by zero"
            except Exception, e:
                ret['field'] = 'Result'
                ret['error'] = e.msg
                return json.dumps(ret)

            # check if analyses that rely on this need to have their results
            # re-calculated now that this result is complete
#        back_dependencies = analysis.getBackReferences()

            ret['result'] = str(result)
            return json.dumps(ret)

