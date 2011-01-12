from Products.bika.stats import llinregress
from Products.bika.stats import lstdev
from Products.bika.stats import lmean
from reportlab.lib.colors import getAllNamedColors, HexColor
from reportlab.graphics.widgets.markers import makeMarker
from DateTime import DateTime

def num2date(i):
    if i // 1 == i:
        this_date = earliest_date + i
        return this_date.strftime('%Y %m %d')
    else:
        return ''

chart = 'LinePlot'
yvalues = context.REQUEST.get('yvalues')
xdates = context.REQUEST.get('xdates')
expected_result = context.REQUEST.get('expected', 0)
expected_min = context.REQUEST.get('min', 0)
expected_max = context.REQUEST.get('max', 0)
selected_id = context.REQUEST.get('selected_id', '')
try:
    expected = float(expected_result)
except ValueError:
    expected = None

try:
    e_min = float(expected_min)
except ValueError:
    e_min = None
try:
    e_max = float(expected_max)
except ValueError:
    e_max = None

yvalues = [float(v) for v in yvalues.split(',')]
xdatevalues = [DateTime(x) for x in xdates.split(',')]
earliest_date = min(xdatevalues) - 1
y_min = min(yvalues)
y_max = max(yvalues)

# xvalues must match yvalues for co-ordinates to be correct
# x_axis_values are unique xvalues
xvalues = []
x_axis_values = [0,]
for vdate in xdatevalues:
    xvalue = vdate - earliest_date
    xvalues.append(xvalue)
    if xvalue not in x_axis_values:
        x_axis_values.append(xvalue)
x_min = min(xvalues)
x_max = max(xvalues)
x_axis_values.append(xvalue + 1)


all_data = []
# result data
result_data = []
for i in range(len(yvalues)):
    result_data.append((xvalues[i], yvalues[i]))
all_data.append(tuple(result_data))

#
# expected result line
data = []
for i in range(len(x_axis_values)):
    data.append((x_axis_values[i], expected))
all_data.append(tuple(data))

#
# min and max result lines
min_data = []
max_data = []
for i in range(len(x_axis_values)):
    min_data.append((x_axis_values[i], e_min))
    max_data.append((x_axis_values[i], e_max))
all_data.append(tuple(min_data))
all_data.append(tuple(max_data))

#
# regression line - trend
# cannot be plotted if only one xvalue
trend_plotted = False
if x_min != x_max:
    trend_data = []
    trend_line = llinregress(xvalues, yvalues)
    point = trend_line[1]
    slope = trend_line[0]
    start_y = point + slope
    end_y = point + (slope * xvalues[-1])
    trend_data.append((xvalues[0], start_y))
    trend_data.append((xvalues[-1], end_y))
    all_data.append(tuple(trend_data))
    trend_plotted = True

#
# stdev lines 
# cannot be plotted if less than min results
stdev_plotted = False
r_stdev = 0
if len(yvalues) >= 5:
    r_stdev = lstdev(yvalues)
    r_mean = lmean(yvalues)
    stdev_high = r_mean + r_stdev
    stdev_low = r_mean - r_stdev
    min_data = []
    max_data = []
    for i in range(len(x_axis_values)):
        min_data.append((x_axis_values[i], stdev_low))
        max_data.append((x_axis_values[i], stdev_high))
    all_data.append(tuple(min_data))
    all_data.append(tuple(max_data))
    stdev_plotted = True

#
#********************* values displayed on y-axis **************
if y_min < e_min:
    abs_min = y_min
else:
    abs_min = e_min
if y_max > e_max:
    abs_max = y_max
else:
    abs_max = e_max
r = abs_max - abs_min

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

y_axis_values = []

# find the step value below the lowest value
y = (abs_min // step) * step
if y == abs_min:
    y = abs_min - step

while y < abs_max:
    y_axis_values.append(y)
    y += step
y_axis_values.append(y)
if y == abs_max:
    y += step
    y_axis_values.append(y)


##***************************************************************************
#Set attributes of the graph

colors = getAllNamedColors()
attrs = {}


if step_bumped:
    increase_count -= 1
if increase_count <= 0:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.0f'
        l_min = '%0.1f' %e_min
        l_max = '%0.1f' %e_max
        l_exp = '%0.1f' %expected
        l_sd = '%0.2f' %r_stdev
elif increase_count == 1:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.1f'
        l_min = '%0.2f' %e_min
        l_max = '%0.2f' %e_max
        l_exp = '%0.2f' %expected
        l_sd = '%0.3f' %r_stdev
elif increase_count == 2:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.2f'
        l_min = '%0.3f' %e_min
        l_max = '%0.3f' %e_max
        l_exp = '%0.3f' %expected
        l_sd = '%0.4f' %r_stdev
else:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.3f'
        l_min = '%0.4f' %e_min
        l_max = '%0.4f' %e_max
        l_exp = '%0.4f' %expected
        l_sd = '%0.5f' %r_stdev


attrs['%s.x' %chart]= 50
attrs['%s.y' %chart] = 50
attrs['%s.height' %chart] = 300
attrs['%s.width' %chart] = 500
attrs['%s.data' %chart] = all_data
attrs['%s.joinedLines' %chart] = 1



attrs['LegendActual.x'] = 80
attrs['LegendActual.y'] = 10
attrs['LegendActual.fontSize'] = 10
attrs['LegendActual.fontName'] = 'Helvetica'
attrs['LegendActual.colorNamePairs'] = ( (colors['blue'], 'Actual'),)
attrs['%s.lines[0].symbol' %chart] = makeMarker('FilledCircle', size=8)
attrs['%s.lines[0].strokeColor' %chart] = colors['lightblue']
attrs['%s.lines[0].strokeWidth' %chart] = -1

label = 'Expected (%s)' %l_exp
attrs['LegendExpected.x'] = 160
attrs['LegendExpected.y'] = 10
attrs['LegendExpected.fontSize'] = 10
attrs['LegendExpected.fontName'] = 'Helvetica'
attrs['LegendExpected.colorNamePairs'] = ( (colors['darkolivegreen'], label),)
attrs['%s.lines[1].strokeColor' % chart] = colors['darkolivegreen']

label = 'Min (%s) Max(%s)' %(l_min, l_max)
attrs['LegendMinMax.x'] = 260
attrs['LegendMinMax.y'] = 10
attrs['LegendMinMax.fontSize'] = 10
attrs['LegendMinMax.fontName'] = 'Helvetica'
attrs['LegendMinMax.colorNamePairs'] = ( (colors['red'], label),)
attrs['%s.lines[2].strokeColor' % chart] = colors['red']
attrs['%s.lines[3].strokeColor' % chart] = colors['red']

if trend_plotted:
    label = 'Trend'
    attrs['LegendTrend.x'] = 480
    attrs['LegendTrend.y'] = 10
    attrs['LegendTrend.fontSize'] = 10
    attrs['LegendTrend.fontName'] = 'Helvetica'
    attrs['LegendTrend.colorNamePairs'] = ( (colors['orange'], label),)
    attrs['%s.lines[4].strokeColor' % chart] = colors['orange']

if stdev_plotted:
    label = 'StdDev (%s)' %(l_sd)
    attrs['LegendStDev.x'] = 380
    attrs['LegendStDev.y'] = 10
    attrs['LegendStDev.fontSize'] = 10
    attrs['LegendStDev.fontName'] = 'Helvetica'
    attrs['LegendStDev.colorNamePairs'] = ( (colors['yellow'], label),)
    if trend_plotted:
        attrs['%s.lines[5].strokeColor' % chart] = colors['yellow']
        attrs['%s.lines[6].strokeColor' % chart] = colors['yellow']
    else:
        attrs['%s.lines[4].strokeColor' % chart] = colors['yellow']
        attrs['%s.lines[5].strokeColor' % chart] = colors['yellow']

attrs['%s.xValueAxis.valueMin' %chart] = 0
attrs['%s.xValueAxis.valueStep' %chart] = 1
attrs['%s.xValueAxis.labelTextFormat' %chart] = num2date
attrs['%s.xValueAxis.visible' %chart] = True
attrs['%s.xValueAxis.visibleGrid' %chart] = True

attrs['%s.yValueAxis.valueMin' %chart] = y_axis_values[0]
attrs['%s.yValueAxis.valueMax' %chart] = value
attrs['%s.yValueAxis.valueSteps' %chart] = y_axis_values
attrs['%s.yValueAxis.visibleGrid' %chart] = True
attrs['%s.yValueAxis.gridStrokeColor' %chart] = colors['ReportLabFidBlue']
attrs['%s.yValueAxis.gridStart' %chart] = None
attrs['%s.yValueAxis.gridEnd' %chart] = None


dict_list = [attrs]     #y-axis, x-axis

dict = {}
for d in dict_list:
    for k in d.keys():
        dict[k] = d[k]
return dict

