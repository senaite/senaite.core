from Products.bika.stats import lz
from Products.bika.stats import lzs
from Products.bika.stats import lmean
from Products.bika.stats import lstdev
from Products.bika.stats import lmedianscore
from reportlab.lib.colors import getAllNamedColors, HexColor
from reportlab.graphics.widgets.markers import makeMarker

chart = 'NormalCurve'
xvalues = [1.0, 2.0, 3.0, 3.0, 4.0, 4.0, 5.0, 5.0, 6.0, 7.0, ]
result = 5.0


xmin =  1.0
xmax = 7.0
xmean = lmean(xvalues)
diffleft = xmean - xmin
diffright = xmax - xmean
maxdiff = diffleft > diffright and diffleft or diffright
# Change the value of xvalues to be able to plot the whole curve. Call
# it nc_xvalues.

# To do: Get the values only for the results supplied (as above), and
# then plot them on the curve 

nc_loop_xmin = (xmin - maxdiff)
nc_loop_xmax = (xmax + maxdiff)

nc_xvalues = []
nc_loop_xvalues = []

i = nc_loop_xmin
increment = maxdiff*2/1000.0
while i < nc_loop_xmax:
    nc_xvalues.append(i)
    i += increment

nc_xvalues.sort()

nc_xmin = min(nc_xvalues)
nc_xmax = max(nc_xvalues)

nc_yvalues =[]

#******** new normal curve ********* 
r_stdev = lstdev(xvalues)
r_mean = lmean(xvalues)
nc_rdata = context.normal_curve(nc_xvalues, r_mean, r_stdev)
#***********************************

#Get max value for y-axis
for item in nc_rdata:
    pair = list(item)
    nc_yvalues.append(pair[1])

nc_ymaxval = max(nc_yvalues)

nc_dtuple = tuple(nc_rdata)

#******************************************

xvalues.sort()
stdev = lstdev(xvalues)

mean = lmean(xvalues)

yvalues =[]

rdata = context.normal_curve(xvalues, mean, stdev)

#Get max value for y-axis
for item in rdata:
    pair = list(item)
    yvalues.append(pair[1])

ymaxval = max(yvalues)

dtuple = tuple(rdata) 

data = [dtuple]

data.append(nc_dtuple)  #Uncomment this to get the whole normal curve
#data.append(dtuple)    #Use this to extend the curve?

# append median and analysis result if they are in range
mean_coord = None
result_coord = None
for x,y in nc_dtuple:
    if '%.2f' % x == '%.2f' % mean:
        mean_coord = [ (mean, 0), (mean, y) ]
    if '%.2f' % x == '%.2f' % result:
        result_coord = [ (result, y) ]

if mean_coord is not None:
    data.append(mean_coord)
if result_coord is not None:
    data.append(result_coord)

#***************************************************************************
#Set attributes of the graph

colors = getAllNamedColors()

attrs = {}

attrs['LegendMean.x'] = 180
attrs['LegendMean.y'] = 10
attrs['LegendMean.fontSize'] = 10
attrs['LegendMean.fontName'] = 'Helvetica'
attrs['LegendMean.colorNamePairs'] = ( (colors['green'], 'Mean'),)

attrs['LegendMember.x'] = 240
attrs['LegendMember.y'] = 10
attrs['LegendMember.fontSize'] = 10
attrs['LegendMember.fontName'] = 'Helvetica'
attrs['LegendMember.colorNamePairs'] = ( (colors['red'], 'Member'),)

attrs['%s.lines[0].symbol' % chart] = makeMarker('FilledCircle', size=8)
attrs['%s.lines[0].strokeWidth' % chart] = -1 #remove line, so only markers can be seen
attrs['%s.lines[0].strokeColor' % chart] = colors['lightblue']

# Add mean dataset
if len(data) >= 3:
    attrs['%s.lines[2].strokeColor' % chart] = colors['green']

# Add result dataset
if len(data) == 4:
    attrs['%s.lines[3].symbol' % chart] = makeMarker(
        'FilledCircle', size=10)
    attrs['%s.lines[3].strokeWidth' % chart] = -1 #remove line, so only markers can be seen
    attrs['%s.lines[3].strokeColor' % chart] = colors['red']

attrs['%s.yValueAxis.valueMin' % chart] = 0             
attrs['%s.yValueAxis.valueMax' % chart] = ymaxval        

attrs['%s.yValueAxis.visible' % chart] = False       
attrs['%s.yValueAxis.visibleGrid' % chart] = True
attrs['%s.yValueAxis.gridStrokeColor' % chart] = colors['ReportLabFidBlue']
attrs['%s.yValueAxis.gridEnd' % chart] = None
attrs['%s.yValueAxis.gridStart' % chart] = None

attrs['%s.xValueAxis.labelTextFormat' % chart] = '%0.2f' 
attrs['%s.xValueAxis.labels.fontSize' % chart] = 9
attrs['%s.xValueAxis.labels.fontName' % chart] = 'Helvetica'
attrs['%s.xValueAxis.visibleGrid' % chart] = True
attrs['%s.xValueAxis.gridStrokeColor' % chart] = colors['ReportLabFidBlue']
attrs['%s.xValueAxis.gridEnd' % chart] = None
attrs['%s.xValueAxis.gridStart' % chart] = None

attrs['%s.height' % chart] = 200
attrs['%s.width' % chart] = 400

# Get max and for x axis
diff = xmean - xmin
new_xmin = xmin - diff           
new_xmax = xmax + diff

attrs['%s.xValueAxis.valueMin' % chart] = new_xmin
attrs['%s.xValueAxis.valueMax' % chart] = new_xmax

#********************* values displayed on x-axis **************

r = xmax - xmin

step = r / 4.0

x_axis_values = []

median = lmedianscore(nc_xvalues)
xl_diff = median - xmin
xr_diff = xmax - median

max_diff = max([xl_diff, xr_diff])

x = median - max_diff - step*5
while x < median + max_diff + step*5:
    value = float('%.2f' % x)
    if value not in x_axis_values:
        x_axis_values.append(value)
    x += step

attrs['%s.xValueAxis.valueSteps' % chart] = x_axis_values       
attrs['%s.y' % chart] = 30

if data[0]:
    dict_list = [{'%s.data' % chart : data}, attrs]     #y-axis, x-axis
else:
    dict_list = [attrs]

dict = {}
for d in dict_list:
    for k in d.keys():
        dict[k] = d[k]
return dict

