## Controller Python Script "worksheet_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Add worksheet
##
req = context.REQUEST.form
ws_id = context.generateUniqueId('Worksheet')
context.invokeFactory(id=ws_id, type_name='Worksheet')
ws = context[ws_id]
ws.edit(
    Number=ws_id
    )

analyses = []
analysis_uids = []
if req.has_key('WorksheetTemplate'):
    if not req['WorksheetTemplate'] == 'None':
        uid = req['WorksheetTemplate']
        rc = context.reference_catalog
        wst = rc.lookupObject(uid)
        rows = wst.getRow()
        count_a = 0
        count_b = 0
        count_c = 0
        count_d = 0
        for row in rows:
            if row['type'] == 'a': count_a = count_a + 1
            if row['type'] == 'b': count_b = count_b + 1
            if row['type'] == 'c': count_c = count_c + 1
            if row['type'] == 'd': count_d = count_d + 1
        services = wst.getService()
        service_uids = [s.UID() for s in services]
        selected = {}
        ars = []
        analysis_services = []
        # get the oldest analyses first
        for a in context.portal_catalog(
                        portal_type='Analysis',
                        review_state = 'sample_received',
                        getServiceUID=service_uids,
                        sort_on='getDueDate'):
            analysis = a.getObject()
            ar_id = analysis.getRequestID()
            ar_uid = analysis.aq_parent.UID()
            if selected.has_key(ar_id):
                a_uids = selected[ar_id]['a']
                s_uids = selected[ar_id]['c']
            else:
                if len(selected) < count_a:
                    selected[ar_id] = {}
                    selected[ar_id]['a'] = []
                    selected[ar_id]['c'] = []
                    selected[ar_id]['uid'] = ar_uid
                    a_uids = []
                    s_uids = []
                    ars.append(ar_id)            
                else:
                    continue
            a_uids.append(analysis.UID())
            s_uids.append(analysis.getServiceUID())
            selected[ar_id]['a'] = a_uids
            selected[ar_id]['c'] = s_uids

        used_ars = {}
        for row in rows:
            position = int(row['pos'])
            if row['type'] == 'a':
                if ars:
                    ar = ars.pop(0)
                    used_ars[position] = {}
                    used_ars[position]['ar'] = selected[ar]['uid']
                    used_ars[position]['serv'] = selected[ar]['c']
                    for analysis in selected[ar]['a']:
                        analyses.append((position, analysis)) 
            if row['type'] in ['b', 'c']: 
                sampletype_uid = row['sub']
                standards = {}
                standard_found = False
                for s in context.portal_catalog(
                        portal_type='StandardSample',
                        review_state='current',
                        getStandardStockUID=sampletype_uid):
                    standard = s.getObject()
                    standard_uid = standard.UID()
                    standards[standard_uid] = {}
                    standards[standard_uid]['services'] = []
                    standards[standard_uid]['count'] = 0
                    specs = standard.getResultsRangeDict()
                    for service_uid in service_uids:
                        if specs.has_key(service_uid):
                            standards[standard_uid]['services'].append(service_uid)
                            count = standards[standard_uid]['count']
                            count += 1
                            standards[standard_uid]['count'] = count
                    if standards[standard_uid]['count'] == len(service_uids):
                        # this standard has all the services
                        standard_found = True
                        break
                if standard_found:
                    ws.assignStandard(Standard=standard_uid, Position=position, Type=row['type'], Service=service_uids)
                else:
                    # find the standard with the most services
                    these_services = service_uids
                    standard_keys = standards.keys()
                    no_of_services = 0
                    mostest = None
                    for key in standard_keys:
                        if standards[key]['count'] > no_of_services:
                            no_of_services = standards[key]['count']
                            mostest = key
                    if mostest:
                        ws.assignStandard(Standard=mostest, Position=position, Type=row['type'], Service=standards[mostest]['services'])
            
        if analyses:
            ws.assignNumberedAnalyses(Analyses=analyses)
            
        if count_d:
            for row in rows:
                if row['type'] == 'd':
                    position = int(row['pos'])
                    dup_pos = int(row['sub'])
                    if used_ars.has_key(dup_pos):
                        ws.assignDuplicate(AR=used_ars[dup_pos]['ar'], Position=position, Service=used_ars[dup_pos]['serv'])

        ws.setMaxPositions(len(rows))

ws.reindexObject()

dest = ws.absolute_url()
context.REQUEST.RESPONSE.redirect(dest)

