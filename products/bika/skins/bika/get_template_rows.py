## Script (Python) "get_template_rows"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=num_positions, template_rows
##title=
##
try:
    num_pos = int(num_positions)
except ValueError:
    num_pos = 0
rows = []
i = 1
if template_rows:
    for t_row in template_rows:
        if num_pos > 0:
            if i > num_pos:
                break
        rows.append(t_row)
        i = i+1
else:
    if num_pos == 0:
        num_pos = 10        
for i in range(i,(num_pos + 1)):
    row = { 
        'pos': i,
        'type': 'a',
        'sub': 1}
    rows.append(row)

return rows
