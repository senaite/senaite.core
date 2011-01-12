from Products.bika.stats import lz
from Products.bika.stats import lzs
from Products.bika.stats import lmean
from Products.bika.stats import lstdev
from Products.bika.stats import lmedianscore
from reportlab.lib.colors import getAllNamedColors, HexColor
from reportlab.graphics.widgets.markers import makeMarker

def find_coords(value):
# since graph depicts all sorts of granularity, binary search for closest
    start = 0
    end = len(nc_dtuple) + 1
    i = end // 2
    value_found = False
    while not value_found:
        if nc_dtuple[i][0] < value:
            start = i
        else:
            end = i
        if (end - start) == 1:
            value_found = True
            # choose one of the 2 numbers
            if (value - start) > (end - value):
                i = end
            else:
                i = start
        else:
            i = start + ((end - start)//2)
    return  [(value, 0), (value, nc_dtuple[i][1])]

chart = 'NormalCurve'
xvalues = context.REQUEST.get('xvalues')
expected_result = context.REQUEST.get('expected', 0)
selected_result = context.REQUEST.get('selected', 0)
selected_id = context.REQUEST.get('selected_id', '')
try:
    expected = float(expected_result)
except ValueError:
    expected = None
try:
    selected = float(selected_result)
except ValueError:
    selected = None

xvalues = [float(v) for v in xvalues.split(',')]
#xvalues = [float(v) for v in xvalues]

xmin = min(xvalues)
xmax = max(xvalues)
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

# append median, expected and selected result if they are in range
mean_coord = find_coords(mean)
data.append(mean_coord)
mean_found = True

if expected >= nc_loop_xmin and expected <=nc_loop_xmax:
    expected_coord = find_coords(expected)
    data.append(expected_coord)
    expected_found = True
else:
    expected_found = False

if selected >= nc_loop_xmin and selected <=nc_loop_xmax:
    selected_coord = find_coords(selected)
    data.append(selected_coord)
    selected_found = True
else:
    selected_found = False

#***************************************************************************
#Set attributes of the graph

colors = getAllNamedColors()

attrs = {}

#********************* values displayed on x-axis **************

r = xmax - xmin
step = r / 4.0
reduce_count = 0
increase_count = 0
if step < 1:
    while step < 1:
        step = step * 10.0
        increase_count += 1
elif step >= 10:
    while step >= 10:
        step = step / 10.0
        reduce_count += 1

# step is now between 1 and 10
step_bumped = False
if step < 2.5:
    step = 1
else:
    if step < 7.5:
        step = 5
    else:
        step = 10
        step_bumped = True


for i in range(increase_count):
    step = step / 10.0
for i in range(reduce_count):
    step = step * 10.0
if step == 0:
    if xxx == yyy: xxxx = 1

x_axis_values = []

# find the step value below the lowest value
x = (nc_loop_xmin // step) * step

while x < nc_loop_xmax:
    x_axis_values.append(x)
    x += step

if step_bumped:
    increase_count -= 1
if increase_count <= 0:
    for value in x_axis_values:
        attrs['%s.xValueAxis.labelTextFormat' % chart] = '%.0f' 
        l_mean = '%0.1f' %mean
        l_exp = '%0.1f' %expected
        if selected: l_sel = '%0.1f' %selected
elif increase_count == 1:
    for value in x_axis_values:
        attrs['%s.xValueAxis.labelTextFormat' % chart] = '%.1f'
        l_mean = '%0.2f' %mean
        l_exp = '%0.2f' %expected
        if selected: l_sel = '%0.2f' %selected
elif increase_count == 2:
    for value in x_axis_values:
        attrs['%s.xValueAxis.labelTextFormat' % chart] = '%.2f'
        l_mean = '%0.3f' %mean
        l_exp = '%0.3f' %expected
        if selected: l_sel = '%0.3f' %selected
else:
    for value in x_axis_values:
        attrs['%s.xValueAxis.labelTextFormat' % chart] = '%.3f'
        l_mean = '%0.4f' %mean
        l_exp = '%0.4f' %expected
        if selected: l_sel = '%0.4f' %selected


label = 'Mean (%s)' %l_mean
attrs['LegendMean.x'] = 80
attrs['LegendMean.y'] = 10
attrs['LegendMean.fontSize'] = 10
attrs['LegendMean.fontName'] = 'Helvetica'
attrs['LegendMean.colorNamePairs'] = ( (colors['orange'], label),)

label = 'Expected (%s)' %l_exp
attrs['LegendExpected.x'] = 180
attrs['LegendExpected.y'] = 10
attrs['LegendExpected.fontSize'] = 10
attrs['LegendExpected.fontName'] = 'Helvetica'
attrs['LegendExpected.colorNamePairs'] = ( (colors['darkolivegreen'], label),)

attrs['LegendSelected.x'] = 280
attrs['LegendSelected.y'] = 10
attrs['LegendSelected.fontSize'] = 10
attrs['LegendSelected.fontName'] = 'Helvetica'
if selected_found:
    label = '%s (%s)' %(selected_id, l_sel)
    attrs['LegendSelected.colorNamePairs'] = ( (colors['blue'], label),)
else:
    label = ' '
    attrs['LegendSelected.strokeColor'] = colors['white']
    attrs['LegendSelected.colorNamePairs'] = ( (colors['white'], label),)

attrs['%s.lines[0].symbol' % chart] = makeMarker('FilledCircle', size=8)
attrs['%s.lines[0].strokeWidth' % chart] = -1 #remove line, so only markers can be seen
attrs['%s.lines[0].strokeColor' % chart] = colors['lightblue']

# Add mean dataset
if mean_found:
    attrs['%s.lines[2].strokeColor' % chart] = colors['orange']
    expected_line = 3
else:
    expected_line = 2

# Add expected dataset
if expected_found:
    attrs['%s.lines[%s].strokeColor' % (chart, expected_line)] = colors['darkolivegreen']
    selected_line = expected_line + 1
else:
    selected_line = expected_line

# Add selected dataset
if selected_found:
    attrs['%s.lines[%s].strokeColor' % (chart, selected_line)] = colors['blue']

attrs['%s.yValueAxis.valueMin' % chart] = 0             
attrs['%s.yValueAxis.valueMax' % chart] = ymaxval        

attrs['%s.yValueAxis.visible' % chart] = False       
attrs['%s.yValueAxis.visibleGrid' % chart] = True
attrs['%s.yValueAxis.gridStrokeColor' % chart] = colors['ReportLabFidBlue']
attrs['%s.yValueAxis.gridEnd' % chart] = None
attrs['%s.yValueAxis.gridStart' % chart] = None

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
