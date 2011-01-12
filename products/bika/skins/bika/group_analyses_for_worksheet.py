## Script (Python) "group_analyses_for_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

def checkCalcType(calctype):
    cols = []
    if calctype in ['wl', 'rw']:
        cols.append('gm')
        cols.append('vm')
        cols.append('nm')
        return cols
    if calctype in ['wlt', 'rwt']:
        cols.append('vm')
        cols.append('sm')
        cols.append('nm')
        return cols
    if calctype in ['t',]:
        cols.append('tv')
        cols.append('tf')
        return cols
    return cols

plone_view = context.restrictedTraverse('@@plone')
analyses = context.getAnalyses()
sort_on = (('Title', 'nocase', 'asc'),)
analyses = sequence.sort(analyses, sort_on)

duplicates = context.objectValues('DuplicateAnalysis')
standards_and_blanks = context.getStandardAnalyses()
rejects = context.objectValues('RejectAnalysis')

any_cols = []
any_published = False

seq = {}
keys = {}
for item in context.getWorksheetLayout():
    seq[item['uid']] = item['pos']
    keys[item['uid']] = item['key']

results = {}
sub_results = {}

for analysis in duplicates:
    ws = analysis.aq_parent
    ar = analysis.getRequest()
    copy_analysis = ar[analysis.getService().getId()]
    due_date = copy_analysis.getDueDate()
    sample = ar.getSample()
    sampletype = sample.getSampleType()
    copy_id = '(%s)' %(ar.getId())
    pos = seq[analysis.UID()]
    calctype = analysis.getCalcType()
    cols = checkCalcType(calctype)
    if cols:
        any_cols.extend(cols)
    if len(cols) > 0 or calctype == 'dep':
        calcd = True
    else:
        calcd = False
    parent_link = "%s/base_edit" %(ar.aq_parent.absolute_url())
    sub_results = {
                 'RequestID': copy_id,
                 'OrderID': ar.getClientOrderNumber(),
                 'absolute_url': ar.absolute_url(),
                 'ParentTitle': ar.aq_parent.Title(),
                 'ParentLink': parent_link,
                 'ParentUID': ' ',
                 'sampletype_uid': sampletype.UID(),
                 'DueDate': plone_view.toLocalizedTime(
                     due_date, long_format=1
                     ),
                 'DatePublished': '',  
                 'Analysis': analysis,
                 'Cols': cols,
                 'Calcd': calcd,
                 'Type': 'd',
                 'Key': '',
                 'Pos': pos,
               }
    if not results.has_key(pos):
        results[pos] = []
    results[pos].append(sub_results)

for analysis in rejects:
    ws = analysis.aq_parent
    ar = analysis.getRequest()
    real_analysis = ar[analysis.getService().getId()]
    due_date = real_analysis.getDueDate()
    sample = ar.getSample()
    sampletype = sample.getSampleType()
    copy_id = '(%s)' %(ar.getId())
    pos = seq[analysis.UID()]
    calctype = analysis.getCalcType()
    cols = checkCalcType(calctype)
    if cols:
        any_cols.extend(cols)
    if len(cols) > 0 or calctype == 'dep':
        calcd = True
    else:
        calcd = False
    parent_link = "%s/base_edit" %(ar.aq_parent.absolute_url())
    sub_results = {
                 'RequestID': copy_id,
                 'OrderID': ar.getClientOrderNumber(),
                 'absolute_url': ar.absolute_url(),
                 'ParentTitle': ar.aq_parent.Title(),
                 'ParentLink': parent_link,
                 'ParentUID': ar.aq_parent.UID(),
                 'sampletype_uid': sampletype.UID(),
                 'DueDate': plone_view.toLocalizedTime(
                     due_date, long_format=1
                     ),
                 'DatePublished': '',  
                 'Analysis': analysis,
                 'Cols': cols,
                 'Calcd': calcd,
                 'Type': 'r',
                 'Key': '',
                 'Pos': pos,
               }
    if not results.has_key(pos):
        results[pos] = []
    results[pos].append(sub_results)

for analysis in standards_and_blanks:
    std_sample = analysis.aq_parent
    ss_id = std_sample.getId()
    stock = std_sample.getStandardStock()
    if stock:
        stock_uid = std_sample.getStandardStock().UID()
    else:
        stock_uid = None;
    pos = seq[analysis.UID()]
    calctype = analysis.getCalcType()
    cols = checkCalcType(calctype)
    if cols:
        any_cols.extend(cols)
    if len(cols) > 0 or calctype == 'dep':
        calcd = True
    else:
        calcd = False
    ss_id = analysis.aq_parent.getStandardID()
    parent_link = "%s/base_edit" %(std_sample.aq_parent.absolute_url())
    sub_results = {
                 'RequestID': analysis.aq_parent.getStandardID(),
                 'OrderID': '',
                 'absolute_url': std_sample.absolute_url(),
                 'ParentTitle': std_sample.aq_parent.Title(),
                 'ParentLink': parent_link,
                 'ParentUID': std_sample.aq_parent.UID(),
                 'sampletype_uid': stock_uid,
                 'DueDate': '',
                 'DatePublished': '',
                 'Analysis': analysis,
                 'Cols': cols,
                 'Calcd': calcd,
                 'Type': analysis.getStandardType(),
                 'Key': '',
                 'Pos': pos,
               }
    if not results.has_key(pos):
        results[pos] = []
    results[pos].append(sub_results)

for analysis in analyses:
    ar = analysis.aq_parent
    ar_id = ar.getId()
    sample = ar.getSample()
    sampletype = sample.getSampleType()
    due_date = analysis.getDueDate()
    date_published = analysis.getDateAnalysisPublished()
    if date_published:
        date_published = plone_view.toLocalizedTime(date_published, long_format=1)
        any_published = True
    pos = seq[analysis.UID()]
    key = keys[analysis.UID()]
    calctype = analysis.getCalcType()
    cols = checkCalcType(calctype)
    if cols:
        any_cols.extend(cols)
    if len(cols) > 0 or calctype == 'dep':
        calcd = True
    else:
        calcd = False
    parent_link = "%s/base_edit" %(ar.aq_parent.absolute_url())
    sub_results = {
                 'RequestID': ar.getRequestID(),
                 'OrderID': ar.getClientOrderNumber(),
                 'absolute_url': ar.absolute_url(),
                 'ParentTitle': ar.aq_parent.Title(),
                 'ParentLink': parent_link,
                 'ParentUID': ar.aq_parent.UID(),
                 'sampletype_uid': sampletype.UID(),
                 'DueDate': plone_view.toLocalizedTime(
                     due_date, long_format=1
                     ),
                 'DatePublished': date_published,
                 'Analysis': analysis,
                 'Cols': cols,
                 'Calcd': calcd,
                 'Type': 'a',
                 'Key': key,
                 'Pos': pos,
               }
    if not results.has_key(pos):
        results[pos] = []
    results[pos].append(sub_results)

l = results.keys()
l.sort()
result_set = {}
all_results = []
for pos in l:
    all_results = all_results + results[pos]
any_cols.sort()
final_cols = []
for col in any_cols:
    if col not in final_cols: final_cols.append(col)

result_set['results'] = all_results
result_set['any_cols'] = final_cols
result_set['published'] = any_published
return result_set
