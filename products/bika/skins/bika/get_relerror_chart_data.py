from reportlab.lib.colors import getAllNamedColors, HexColor
from reportlab.graphics.widgets.markers import makeMarker
from DateTime import DateTime

chart = 'LinePlot'
yvalues = context.REQUEST.get('yvalues')
xvalues = context.REQUEST.get('xvalues')
dupvar = context.REQUEST.get('dupvar')
if dupvar == 'None':
    dupvar = 0
dupvar = float(dupvar)


yvalues = [float(v) for v in yvalues.split(',')]
xvalues = [float(v) for v in xvalues.split(',')]
y_min = min(yvalues)
y_max = max(yvalues)
x_min = min(xvalues) - 1
x_max = max(xvalues) + 1

all_data = []
# result data
result_data = []
for i in range(len(yvalues)):
    result_data.append((xvalues[i], yvalues[i]))
all_data.append(tuple(result_data))

# acceptable error lines
min_data = []
max_data = []
for i in range(len(yvalues)):
    min_data.append((xvalues[i], -(dupvar)))
    max_data.append((xvalues[i], dupvar))
all_data.append(tuple(min_data))
all_data.append(tuple(max_data))

#
#********************* values displayed on y-axis **************
if dupvar > y_max:
    abs_max = dupvar
else:
    abs_max = y_max
if -(dupvar) < y_min:
    abs_min = -(dupvar)
else:
    abs_min = y_min
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
elif increase_count == 1:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.1f'
elif increase_count == 2:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.2f'
else:
    for value in y_axis_values:
        attrs['%s.yValueAxis.labelTextFormat' % chart] = '%.3f'


attrs['%s.x' %chart]= 50
attrs['%s.y' %chart] = 30
attrs['%s.height' %chart] = 300
attrs['%s.width' %chart] = 500
attrs['%s.data' %chart] = all_data
attrs['%s.joinedLines' %chart] = 1



attrs['LegendActual.x'] = 200
attrs['LegendActual.y'] = 10
attrs['LegendActual.fontSize'] = 10
attrs['LegendActual.fontName'] = 'Helvetica'
attrs['LegendActual.colorNamePairs'] = ( (colors['blue'], 'Actual'),)
attrs['%s.lines[0].symbol' %chart] = makeMarker('FilledCircle', size=8)
attrs['%s.lines[0].strokeColor' %chart] = colors['lightblue']
attrs['%s.lines[0].strokeWidth' %chart] = -1

label = 'Acceptable Variation (%s)' %(dupvar)
attrs['LegendMinMax.x'] = 300
attrs['LegendMinMax.y'] = 10
attrs['LegendMinMax.fontSize'] = 10
attrs['LegendMinMax.fontName'] = 'Helvetica'
attrs['LegendMinMax.colorNamePairs'] = ( (colors['red'], label),)
attrs['%s.lines[1].strokeColor' % chart] = colors['red']
attrs['%s.lines[2].strokeColor' % chart] = colors['red']

attrs['%s.xValueAxis.valueMin' %chart] = x_min
attrs['%s.xValueAxis.valueMax' %chart] = x_max
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

