## Controller Python Script "analysisspec_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify analysis spec
##
req = context.REQUEST.form.items()
rc = context.reference_catalog

analysisspecs = []
analysisspec = {}

came_from = context.REQUEST.form['came_from']

st_titles = []
for key, value in req:
    if came_from == "add":
        if key.startswith('sampletypes'):
            st_uids = value
            for s in st_uids:
                st = rc.lookupObject(s)
                st_titles.append(st.Title())
    else:
        if key.startswith('SampleType'):
            st_uid = value
            st = rc.lookupObject(st_uid)
            st_title = st.Title()
            continue

    if not key.startswith('analysisspec'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    uid = key.split('.')[-1]
    analysisspec = {}
    analysisspec = value
    analysisspec['service'] = uid
    analysisspecs.append(analysisspec)

if came_from == 'edit':
    uid = context.REQUEST.form['AnalysisSpecUID']
    as = rc.lookupObject(uid)
    as.edit(
        SampleType=st_uid,
        ResultsRange=analysisspecs,
        )
else:
    existing_specs = {}
    for spec_proxy in context.portal_catalog(portal_type='AnalysisSpec',
                                   getClientUID=context.UID()):
        spec = spec_proxy.getObject()
        existing_specs[spec.getSampleTypeUID()] = spec.UID()
        
    for uid in st_uids:
        if existing_specs.has_key(uid):
            as = rc.lookupObject(existing_specs[uid])
        else:
            as_id = context.generateUniqueId('AnalysisSpec')
            context.invokeFactory(id=as_id, type_name='AnalysisSpec')
            as = context[as_id]
        as.edit(
            SampleType=uid,
            ResultsRange=analysisspecs,
            )
        as.reindexObject()



from Products.CMFPlone import transaction_note
if came_from == 'edit':
    transaction_note('Analysis Spec modified successfully')
    message=context.translate('message_order_edited', default='${st} successfully modified', mapping={'st': st_title}, domain='bika')
else:
    display_titles = ''
    for title in st_titles:
        if display_titles:
            display_titles += ', '
            display_titles += title
            display_obj = 'Analysis Specs'
        else:
            display_titles = title
            display_obj = 'Analysis Spec'

    transaction_note('Analysis Spec created successfully')
    message=context.translate('message_order_created', default='${obj} ${st} successfully created or modified', mapping={'obj': display_obj, 'st': display_titles}, domain='bika')


return state.set(portal_status_message=message)
