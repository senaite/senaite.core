## Controller Python Script "analysisservice_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify analysis service
##

req = context.REQUEST.form
service = context

calcdependancy=context.REQUEST.get('CalcDependancy', [])
method=context.REQUEST.get('Method', [])
new_uncertainties = []
old_uncertainties=context.REQUEST.get('Uncertainties', [])
for uncertainty in old_uncertainties:
    if uncertainty.has_key('delete'):
        continue
    new_uncertainties.append(uncertainty)

resultoptions = []
options = context.REQUEST.get('ResultOptions',{})
option_keys = options.keys()
option_keys.sort()
for key in option_keys:
    resultoptions.append({'Seq': key, 
                          'Result': options[key]})

service.edit(
    title=req['Title'].strip(),
    ServiceDescription=req['ServiceDescription'],
    Instructions=req['Instructions'],
    ReportDryMatter=req['ReportDryMatter'],
    AttachmentOption=req['AttachmentOption'],
    Unit=req['Unit'],
    Precision=req['Precision'],
    Price=req['Price'],
    CorporatePrice=req['CorporatePrice'],
    VAT=req['VAT'],
    InstrumentKeyword=req['InstrumentKeyword'].strip(),
    AnalysisKey=req['AnalysisKey'].strip(),
    CalcDependancy=calcdependancy,
    Instrument=req['Instrument'],
    Method=method,
    MaxHoursAllowed=req['MaxHoursAllowed'],
    CalculationType=req['CalculationType'],
    TitrationUnit=req['TitrationUnit'],
    DuplicateVariation=req['DuplicateVariation'],
    Department=req['Department'],
    AnalysisCategory=req['AnalysisCategory'],
    Accredited=req['Accredited'],
    ResultOptions=resultoptions,
    Uncertainties=new_uncertainties,
    )

service.reindexObject()


from Products.CMFPlone import transaction_note
transaction_note('Analysis Service modified successfully')

return state
