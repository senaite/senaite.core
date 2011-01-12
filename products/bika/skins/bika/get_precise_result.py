## Script (Python) "get_precise_result"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=result, precision
##title=Return result as a string with the correct precision
##
try:
    float_result = float(result)
except ValueError:
    return result

if precision == None or precision == '':
    precision == 0
if precision == 0:
    precise_result = '%.0f' %float_result 
if precision == 1:
    precise_result = '%.1f' %float_result 
if precision == 2:
    precise_result = '%.2f' %float_result 
if precision == 3:
    precise_result = '%.3f' %float_result 
if precision == 4:
    precise_result = '%.4f' %float_result 
if precision > 4:
    precise_result = '%.5f' %float_result 
return precise_result
