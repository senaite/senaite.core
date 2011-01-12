## Script (Python) "get_standardstock_results"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get standard stocks and their results
##
std_stocks = {}
std_titles = {}

this_date = DateTime()
today = DateTime(this_date.year(), this_date.month(), this_date.day(), 00, 00)
for st in context.portal_catalog(portal_type='StandardStock'):
    stock = st.getObject()
    if stock.getExpiryDate() and stock.getExpiryDate() < today:
        continue
    date = stock.getDateCreated()
    if date:
        created = date.strftime('%Y/%m/%d')
    else: 
        created = ''
    date = stock.getExpiryDate()
    if date:
        expiry = date.strftime('%Y/%m/%d')
    else:
        expiry = ''
    title = stock.Title()
    uid = stock.UID()
    std_stocks[uid] = {}
    i = 1 
    sort_title = title
    while std_titles.has_key(sort_title):
        sort_title += '(%u)' % i
    std_titles[sort_title] = uid
    # results in string for javascript manipulation
    results = ''
    services = []
    for item in stock.getStandardResults():
        services.append(item['service'])
        results += item['service']
        results += ';'
        if item.has_key('result'):
            results += item['result']
        results += ';'
        if item.has_key('min'):
            results += item['min']
        results += ';'
        if item.has_key('max'):
            results += item['max']
        results += ':'

    std_stocks[uid] = {
                    'uid': uid,
                    'id': stock.getId(),
                    'title': stock.Title(), 
                    'created': created,
                    'expiry': expiry,
                    'services': services,
                    'results': results
                    }

result_set = {}
titles = std_titles.keys()
titles.sort()
s_uids = []
for title in titles:
    s_uids.append(std_titles[title])
result_set['uids'] = s_uids
result_set['std_stocks'] = std_stocks
return result_set
