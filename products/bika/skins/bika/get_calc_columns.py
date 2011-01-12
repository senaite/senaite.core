## Script (Python) "get_calc_columns"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch
##title=Determine which calculation columns are required
##
vm = False # vessel mass
sm = False # sample mass
nm = False # nett mass
gm = False # nett mass
tv = False # titration vol
tf = False # titration factor

for analysis in batch:
    calc_type = analysis.getCalcType()
    if calc_type == None:
        continue
    if calc_type in ['wl', 'rw']:
        gm = True
        vm = True
        nm = True
    if calc_type in ['wlt', 'rwt']:
        vm = True
        sm = True
        nm = True
    if calc_type in ['t',]:
        tv = True
        tf = True
cols = []
if vm: cols.append('vm')
if sm: cols.append('sm')
if gm: cols.append('gm')
if nm: cols.append('nm')
if tv: cols.append('tv')
if tf: cols.append('tf')
    
return cols

