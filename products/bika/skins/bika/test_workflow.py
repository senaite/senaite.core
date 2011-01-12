## Script (Python) "test_workflow"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=login
##
context.load_testdata()
context.load_testdata2()

client = context.clients.objectValues()[0]
contact = client.objectValues('Contact')[0]

service_uids = [a.UID() for a in 
                 context.bika_services.objectValues('AnalysisService')]

selected_services = service_uids[:4]
samplepoints = ('pointa', 'pointb', 'pointc', 'pointd')

l = [
('analysisrequest.0',
    {'Analyses': selected_services,
     'SamplePoint': samplepoints[0],
     'ClientReference': 'R001',
     'ClientSampleID': 'S001'}),
 ('analysisrequest.1',
    {'Analyses': selected_services,
     'SampleType': sampletypes[1],
     'ClientReference': 'R002',
     'ClientSampleID': 'S002'}),
('analysisrequest.2',
    {'Analyses': selected_services,
     'SampleType': sampletypes[2],
     'ClientReference': 'R003',
     'ClientSampleID': 'S003'}),
('analysisrequest.3',
    {'Analyses': selected_services,
     'SampleType': sampletypes[3],
     'ClientReference': 'R004',
     'ClientSampleID': 'S004'}),
('Contact', contact.UID())]

for key, value in dict(l).items()
    context.REQUEST.form[key] = value

client.analysisrequest_add()
wf = context.portal_workflow

######################################################################
# Test 1: receive all ARs, assign them to Worksheet, promote equally to
# verified state
######################################################################
context.plone_log('TEST 1')
# receive ARs
analyses_uids = []
for ar in client.objectValues('AnalysisRequest'):
    wf.doActionFor(ar, 'receive')
    assert wf.getInfoFor(ar, 'review_state', '') == 'sample_received'
    for a in ar.getAnalyses():
        analyses_uids.append(a.UID())
        assert wf.getInfoFor(a, 'review_state', '') == 'sample_received'
# create worksheet
worksheet_id = context.generateUniqueId('Worksheet')
context.Worksheets.invokeFactory(id=worksheet_id, type_name='Worksheet')
worksheet = context.Worksheets[worksheet_id]
worksheet.assignAnalyses(Analyses=analyses_uids)
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'assigned'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'assigned'
# submit results, no state change should occur
results = dict([(uid, 5) for uid in analyses_uids])
worksheet.submitResults(results)
# submit worksheet
wf.doActionFor(worksheet, 'submit')
assert wf.getInfoFor(worksheet, 'review_state', '') == 'to_be_verified'
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'to_be_verified'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'to_be_verified'
# verify worksheet
wf.doActionFor(worksheet, 'verify')
assert wf.getInfoFor(worksheet, 'review_state', '') == 'verified'
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'verified'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'verified'


######################################################################
# Test 2: receive all ARs, assign them to Worksheet, delete analyses
# from worksheet, and promote equally to verified state
######################################################################
context.plone_log('TEST 2')
# receive ARs
analyses_uids = []
for ar in client.objectValues('AnalysisRequest'):
    wf.doActionFor(ar, 'receive')
    assert wf.getInfoFor(ar, 'review_state', '') == 'sample_received'
    for a in ar.getAnalyses():
        analyses_uids.append(a.UID())
        assert wf.getInfoFor(a, 'review_state', '') == 'sample_received'
# create worksheet
worksheet_id = context.generateUniqueId('Worksheet')
context.Worksheets.invokeFactory(id=worksheet_id, type_name='Worksheet')
worksheet = context.Worksheets[worksheet_id]
worksheet.assignAnalyses(Analyses=analyses_uids)
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'assigned'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'assigned'
# delete 
# XXX

# submit results, no state change should occur
results = dict([(uid, 5) for uid in analyses_uids])
worksheet.submitResults(results)
# submit worksheet
wf.doActionFor(worksheet, 'submit')
assert wf.getInfoFor(worksheet, 'review_state', '') == 'to_be_verified'
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'to_be_verified'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'to_be_verified'
# verify worksheet
wf.doActionFor(worksheet, 'verify')
assert wf.getInfoFor(worksheet, 'review_state', '') == 'verified'
for ar in client.objectValues('AnalysisRequest'):
    assert wf.getInfoFor(ar, 'review_state', '') == 'verified'
    for a in ar.getAnalyses():
        assert wf.getInfoFor(a, 'review_state', '') == 'verified'
