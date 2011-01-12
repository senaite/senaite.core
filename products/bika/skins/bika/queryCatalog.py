## Script (Python) "queryCatalog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,show_all=0,quote_logic=0,quote_logic_indexes=['SearchableText','Description','Title'],use_types_blacklist=False,show_inactive=False
##title=wraps the portal_catalog with a rules qualified query
##
from ZODB.POSException import ConflictError
from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFCore.utils import getToolByName

results=[]
catalog=context.portal_catalog
indexes=catalog.indexes()
query={}
show_query=show_all
second_pass = {}

if REQUEST is None:
    REQUEST = context.REQUEST

def quotestring(s):
    return '"%s"' % s

def quotequery(s):
    if not s:
        return s
    try:
        terms = s.split()
    except ConflictError:
        raise
    except:
        return s
    tokens = ('OR', 'AND', 'NOT')
    s_tokens = ('OR', 'AND')
    check = (0, -1)
    for idx in check:
        if terms[idx].upper() in tokens:
            terms[idx] = quotestring(terms[idx])
    for idx in range(1, len(terms)):
        if (terms[idx].upper() in s_tokens and
            terms[idx-1].upper() in tokens):
            terms[idx] = quotestring(terms[idx])
    return ' '.join(terms)

# We need to quote parentheses when searching text indices (we use
# quote_logic_indexes as the list of text indices)
def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

def ensureFriendlyTypes(query):
    ploneUtils = getToolByName(context, 'plone_utils')
    portal_type = query.get('portal_type', [])
    if not same_type(portal_type, []):
        portal_type = [portal_type]
    Type = query.get('Type', [])
    if not same_type(Type, []):
        Type = [Type]
    typesList = portal_type + Type
    if not typesList:
        friendlyTypes = ploneUtils.getUserFriendlyTypes(typesList)
        query['portal_type'] = friendlyTypes

for k, v in REQUEST.items():
    if v and k in indexes:
        if k in quote_logic_indexes:
            v = quote_bad_chars(v)
            if quote_logic:
                v = quotequery(v)
        query.update({k:v})
        show_query=1
    elif k.endswith('_usage'):
        key = k[:-6]
        param, value = v.split(':')
        second_pass[key] = {param:value}
    elif k=='sort_on' or k=='sort_order' or k=='sort_limit':
        if k=='sort_limit' and not same_type(v, 0):
            query.update({k:int(v)})
        else:
            query.update({k:v})

for k, v in second_pass.items():
    qs = query.get(k)
    if qs is None:
        continue
    query[k] = q = {'query':qs}
    q.update(v)

# doesn't normal call catalog unless some field has been queried
# against. if you want to call the catalog _regardless_ of whether
# any items were found, then you can pass show_all=1.

if not context.portal_membership.isAnonymousUser() and \
        context.member_is_client():
    client = context.get_client_for_member()
    path_query = ['/'.join(client.getPhysicalPath())+'/']
    query['path'] = path_query

if show_query:
    try:
        if use_types_blacklist:
            ensureFriendlyTypes(query)
        results=catalog(query,show_inactive=show_inactive)
    except ParseError:
        pass

return results
