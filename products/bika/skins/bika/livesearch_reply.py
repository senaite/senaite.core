## Script (Python) "livescript_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10
##title=Determine whether to show an id in an edit form

from Products.CMFCore.utils import getToolByName

ploneUtils = getToolByName(context, 'plone_utils')
pretty_title_or_id = ploneUtils.pretty_title_or_id

portalProperties = getToolByName(context, 'portal_properties')
siteProperties = getattr(portalProperties, 'site_properties', None)
useViewAction = []
if siteProperties is not None:
    useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

# SIMPLE CONFIGURATION
USE_ICON = True
USE_RANKING = False
MAX_TITLE = 29
MAX_DESCRIPTION = 93

# generate a result set for the query
catalog = context.portal_catalog

friendly_types = ploneUtils.getUserFriendlyTypes()

def quotestring(s):
    return '"%s"' % s

def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

# for now we just do a full search to prove a point, this is not the
# way to do this in the future, we'd use a in-memory probability based
# result set.
# convert queries to zctextindex
r=q.split(' ')
r = " AND ".join(r)
r = quote_bad_chars(r)+'*'
searchterms = r.replace(' ','+')

query = {'SearchableText': r, 'portal_types': friendly_types}
if not context.portal_membership.isAnonymousUser() and \
        context.member_is_client():
    client = context.get_client_for_member()
    path_query = ['/'.join(client.getPhysicalPath())+'/']
    query['path'] = path_query

results = catalog(SearchableText=r, portal_type=friendly_types)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml;charset=%s' % context.plone_utils.getSiteEncoding())

_ = context.translate
legend_livesearch = _('legend_livesearch', default='LiveSearch &darr;')
label_no_results_found = _('label_no_results_found', default='No matching results found.')

if not results:
    print '''<fieldset class="livesearchContainer">'''
    print '''<legend id="livesearchLegend">%s</legend>''' % legend_livesearch
    print '''<div class="LSIEFix">'''
    print '''<div id="LSNothingFound">%s</div>''' % label_no_results_found
    print '''<li class="LSRow">'''
    print '<a href="search_form" style="font-weight:normal">Advanced Search&hellip;</a>'
    print '''</li>'''
    print '''</div>'''
    print '''</fieldset>'''

else:
    print '''<fieldset class="livesearchContainer">'''
    print '''<legend id="livesearchLegend">%s</legend>''' % legend_livesearch
    print '''<div class="LSIEFix">'''
    print '''<ul class="LSTable">'''
    for result in results[:limit]:

        itemUrl = result.getURL()
        if result.portal_type in useViewAction:
            itemUrl += '/view'

        print '''<li class="LSRow">''',
        print '''<img src="%s"/>''' % result.getIcon,
        full_title = pretty_title_or_id(result)
        if len(full_title) >= MAX_TITLE:
            display_title = ''.join((full_title[:MAX_TITLE],'...'))
        else:
            display_title = full_title
        print '''<a href="%s" title="%s">%s</a>''' % (itemUrl, full_title, display_title)
        print '''<span class="discreet">[%s%%]</span>''' % result.data_record_normalized_score_
        display_description = result.Description
        if len(display_description) >= MAX_DESCRIPTION:
            display_description = ''.join((display_description[:MAX_DESCRIPTION],'...'))
        print '''<div class="discreet" style="margin-left: 2.5em;">%s</div>''' % (display_description)
        print '''</li>'''
        full_title, display_title, display_description = None, None, None

    print '''<li class="LSRow">'''
    print '<a href="search_form" style="font-weight:normal">Advanced Search&hellip;</a>'
    print '''</li>'''

    if len(results)>limit:
        # add a more... row
        print '''<li class="LSRow">'''
        print '<a href="%s" style="font-weight:normal">Show all&hellip;</a>' % ('search?SearchableText=' + searchterms)
        print '''</li>'''
    print '''</ul>'''
    print '''</div>'''
    print '''</fieldset>'''

return printed

