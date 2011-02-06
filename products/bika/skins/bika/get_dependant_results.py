## Script (Python) "get_dependant_results"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=this_child
##title=Get analysis results dependant on other analyses results
##
results = {}

def test_reqs(reqd_calcs):
    all_results = True
    for reqd in reqds:
        if results[reqd] == None:
            all_results = False
            break
    return all_results

def update_data(parent, result_in):
    if result_in == None:
        result = None
    else:
        result = '%.2f' % result_in
    service = parent.getService()

    uncertainty = context.get_uncertainty(result, service)
    parent.edit(
        Result = result,
        Uncertainty = uncertainty,
        Unit = service.getUnit()
    )
    return


rc = context.reference_catalog
parents = [uid for uid in
    rc.getBackReferences(this_child, 'AnalysisAnalysis')]
for p in parents:
    parent = rc.lookupObject(p.sourceUID)

    parent_keyword = parent.getAnalysisKey()
    for child in parent.getDependantAnalysis():
        keyword = child.getAnalysisKey()
        try:
            results[keyword] = float(child.getResult())
        except:
            results[keyword] = None

    result = None
    if parent_keyword[0:3] == 'AME':
        protein_type = parent_keyword[3:len(parent_keyword)]
        protein_keyword = 'ProteinCrude%s' % protein_type
        reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'Starch', 'Sugars']
        if  test_reqs(reqds):
            ProteinCrude = results[protein_keyword]
            FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
            Starch = results['Starch']
            Sugars = results['Sugars']
            result = (0.1551 * ProteinCrude) + \
                     (0.3431 * FatCrudeEtherExtraction) + \
                     (0.1669 * Starch) + (0.1301 * Sugars)
        else:
            result = None
        update_data(parent, result)

    if parent_keyword[0:2] == 'ME':
        protein_type = parent_keyword[2:len(parent_keyword)]
        protein_keyword = 'ProteinCrude%s' % protein_type
        reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
        if test_reqs(reqds):
            ProteinCrude = results[protein_keyword]
            FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
            FibreCrude = results['FibreCrude']
            Ash = results['Ash']
            result = 12 + (0.008 * ProteinCrude) + \
                     (0.023 * FatCrudeEtherExtraction) - (0.018 * FibreCrude) + \
                     (0.012 * Ash)
        else:
            result = None
        update_data(parent, result)

    if parent_keyword[0:3] == 'TDN':
        ME_type = parent_keyword[3:len(parent_keyword)]
        ME_keyword = 'ME%s' % ME_type
        reqds = [ME_keyword, ]
        if test_reqs(reqds):
            ME = results[ME_keyword]
            result = 6.67 * ME
        else:
            result = None
        update_data(parent, result)

    if parent_keyword[0:3] == 'NSC':
        protein_type = parent_keyword[3:len(parent_keyword)]
        protein_keyword = 'ProteinCrude%s' % protein_type
        reqds = ['FibreNDF', protein_keyword, 'FatCrudeEtherExtraction', 'Ash']
        if test_reqs(reqds):
            FibreNDF = results['FibreNDF']
            ProteinCrude = results[protein_keyword]
            FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
            Ash = results['Ash']
            result = 100 - (FibreNDF + ProteinCrude + \
                     FatCrudeEtherExtraction + Ash)
        else:
            result = None
        update_data(parent, result)

    if parent_keyword[0:2] == 'DE':
        protein_type = parent_keyword[2:len(parent_keyword)]
        protein_keyword = 'ProteinCrude%s' % protein_type
        reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
        if test_reqs(reqds):
            ProteinCrude = results[protein_keyword]
            FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
            FibreCrude = results['FibreCrude']
            Ash = results['Ash']
            result = 17.38 + (0.105 * ProteinCrude) + \
                     (0.114 * FatCrudeEtherExtraction) - (0.317 * FibreCrude) - \
                     (0.402 * Ash)
        else:
            result = None
        update_data(parent, result)
        update_data(parent, result)

    drymatter = context.bika_settings.getDryMatterService()
    if parent.getServiceUID() == drymatter.UID():
        moisture = context.bika_settings.getMoistureService()
        moisture_key = moisture.getAnalysisKey()
        reqds = [moisture_key, ]
        if test_reqs(reqds):
            Moisture = results[moisture_key]
            result = 100 - Moisture
        else:
            result = None
        update_data(parent, result)

    if parent.checkHigherDependancies():
        parent.get_dependant_results(parent)

return
