##parameters=xvalues, mean, stdev

import math

data = []
for x in xvalues:
    y = (  math.exp(-0.5*(math.pow((x-mean)/stdev, 2)) ) /
           (stdev*math.sqrt(2*math.pi))
        )
    data.append( (x, y) )
return data
