## Script (Python) "date_components_support"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=date=None, use_ampm=0, starting_year=None, ending_year=None, future_years=None
##title=
##

try:
    from DateTime.DateTime import DateTimeError
except ImportError:
    DateTimeError = 'DateTimeError'

# 'id' is what shows up.  December for month 12. 
# 'value' is the value for the form.
# 'selected' is whether or not it is selected.

default=0
years=[]
days=[]
months=[]
hours=[]
minutes=[]
ampm=[]
now=DateTime()

# from CMFDefault.DublinCore
CEILING=DateTime(9999, 0)
FLOOR=DateTime(1970, 0)
PLONE_CEILING=DateTime(2021,0) # 2020-12-31

def month_names():
    names={}
    for x in range(1,13):
        faux=DateTime(2004, x, 1)
        names[x]=faux.Month()
    return names

month_dict=month_names()

# XXX This debacle is because the date that is usually passed in ends with GMT
#     and of course DateTime is too stupid to handle it.  So we strip it off.

if same_type(date, ''):
    date=date.strip()
    if not date:
        date=None
    elif date.split(' ')[-1].startswith('GMT'):
        date=' '.join(date.split(' ')[:-1])

if date is None:
    date=now
    default=1
elif not same_type(date, now):
    try:
        date=DateTime(date)
    except (TypeError, DateTimeError):
        date=now
        default=1

# Anything above PLONE_CEILING should be PLONE_CEILING
if date.greaterThan(PLONE_CEILING):
    date = PLONE_CEILING

# Get portal year range
site_properties = context.portal_properties.site_properties
if starting_year is None:
    min_year = site_properties.getProperty('calendar_starting_year', 1999)
else:
    min_year = starting_year
if ending_year is None:
    if future_years is None:
        max_year = site_properties.getProperty('calendar_future_years_available', 5) + now.year()
    else:
        max_year = future_years + now.year()
else:
    max_year = ending_year

year=int(date.strftime('%Y'))

if min_year != max_year:
    years.append({'id': '----', 'value': '0000', 'selected': None})

for x in range(min_year, max_year+1):
    d={'id': x, 'value': x, 'selected': None}
    if x==year:
        d['selected']=1
    years.append(d)

month=int(date.strftime('%m'))

if default:
    months.append({'id': '----', 'value': '00', 'selected': 1})
else:
    months.append({'id': '----', 'value': '00', 'selected': None})

for x in range(1, 13):
    d={'id': month_dict[x], 'value': '%02d' % x, 'selected': None}
    if x==month and not default:
        d['selected']=1
    months.append(d)

day=int(date.strftime('%d'))

if default:
    days.append({'id': '----', 'value': '00', 'selected': 1})
else:
    days.append({'id': '----', 'value': '00', 'selected': None})

for x in range(1, 32):
    d={'id': x, 'value': '%02d' % x, 'selected': None}
    if x==day and not default:
        d['selected']=1
    days.append(d)

if use_ampm:
    hours_range=[12]+range(1,12)
    hour_default='12'
    hour=int(date.strftime('%I'))
else:
    hours_range=range(0,24)
    hour_default='00'
    hour=int(date.strftime('%H'))

if default:
    hours.append({'id': '----', 'value': hour_default, 'selected': 1})
else:
    hours.append({'id': '----', 'value': hour_default, 'selected': None})

for x in hours_range:
    d={'id': '%02d' % x, 'value': '%02d' % x, 'selected': None }
    if x==hour and not default:
        d['selected']=1
    hours.append(d)

minute=int(date.strftime('%M'))

if default:
    minutes.append({'id': '----', 'value': '00', 'selected': 1})
else:
    minutes.append({'id': '----', 'value': '00', 'selected': None})

for x in range(0, 60):
    d={'id': '%02d' % x, 'value': '%02d' % x, 'selected': None}
    if (x==minute or minute < x < minute+5) and not default:
        d['selected']=1
    minutes.append(d)

if use_ampm:
    p=date.strftime('%p')

    if default:
        ampm.append({'id': '----', 'value': 'AM', 'selected': 1})
    else:
        ampm.append({'id': '----', 'value': 'AM', 'selected': None})

    for x in ('AM', 'PM'):
        d={'id': x, 'value': x, 'selected': None}
        if x==p and not default:
            d['selected']=1
        ampm.append(d)

return {'years': years, 'months': months, 'days': days,
        'hours': hours, 'minutes': minutes, 'ampm': ampm}
