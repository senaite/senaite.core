## Script (Python) "get_uncertainty"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=result, service
##title=Get result uncertainty
##
if result is None:
    return None

uncertainties = service.getUncertainties()
if uncertainties:
    try:
        result = float(result)
    except ValueError:
        # if it is not an float we assume no measure of uncertainty
        return None

    for d in uncertainties:
        if float(d['intercept_min']) <= result < float(d['intercept_max']):
            return d['errorvalue']
    return None
else:
    return None
