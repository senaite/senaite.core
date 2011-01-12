## Script (Python) "get_dups_for_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
dups = []
dupanalyses = context.objectValues('DuplicateAnalysis')
for analysis in dupanalyses:
    dups.append(analysis)

seq = {}
keys = {}
for item in context.getWorksheetLayout():
    seq[item['uid']] = item['pos']

ars = {}
positions = {}
for analysis in dups:
    ar_id = analysis.getRequest().getId()
    pos = seq[analysis.UID()]
    
    # use ; delimited string for java decode
    if not positions.has_key(pos):
        positions[pos] = {}
        services = analysis.getServiceUID() 
    else:
        services = services + ';' + analysis.getServiceUID()
    positions[pos] = {
              'pos': pos,
              'ar_id': ar_id,
              'services':services
              }
ps = positions.keys()
ps.sort()
sorted_pos = []
for pos in ps:
    if not ars.has_key(positions[pos]['ar_id']):
        ars[positions[pos]['ar_id']] = []
    ars[positions[pos]['ar_id']].append(positions[pos]['pos'])
    sorted_pos.append(positions[pos])
    

result_set = {}
result_set['dups'] = ars
result_set['pos'] = sorted_pos
return result_set
