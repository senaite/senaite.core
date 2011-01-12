## Script (Python) "get_invoice_item_description"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ar
##title=Get invoice line item description
##

sample = ar.getSample()
sampleID = sample.Title()
clientref = sample.getClientReference()
clientsid = sample.getClientSampleID()
samplepoint = sample.getSamplePoint()
samplepoint = samplepoint and samplepoint.Title() or '' 
sampletype = sample.getSampleType()
sampletype = sampletype and sampletype.Title() or ''
orderno = ar.getClientOrderNumber() or ''
item_description = orderno + ' ' + clientref + ' ' + clientsid + ' ' + sampleID + ' ' + sampletype + ' ' + samplepoint
return item_description
