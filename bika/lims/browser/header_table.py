"""ARs and Samples use HeaderTable to display object fields in their custom
view and edit screens.
"""

from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p
from zope.component import getAdapter


class HeaderTableView(BrowserView):

    template = ViewPageTemplateFile('templates/header_table.pt')

    def __call__(self):
        self.errors = {}
        if 'header_table_submitted' in self.request:
            schema = self.context.Schema()
            fields = schema.fields()
            form = self.request.form
            for field in fields:
                fieldname = field.getName()
                if fieldname in form:
                    if fieldname + "_uid" in form:
                        # references (process_form would normally do *_uid trick)
                        field.getMutator(self.context)(form[fieldname + "_uid"])
                    else:
                        # other fields
                        field.getMutator(self.context)(form[fieldname])
            message = _p("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
        return self.template()

    def three_column_list(self, input_list):
        list_len = len(input_list)

        # Calculate the length of the sublists
        sublist_len = (list_len % 3 == 0 and list_len / 3 or list_len / 3 + 1)

        def _list_end(num):
            # Calculate the list end point given the list number
            return (num == 2 and list_len or (num + 1) * sublist_len)

        # Generate only filled columns
        final = []
        for i in range(3):
            column = input_list[i * sublist_len:_list_end(i)]
            if len(column) > 0:
                final.append(column)
        return final

    def sublists(self, mode):
        ret = []
        prominent = []
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        wv = adapter()
        edit = wv.get('edit', {}).get('visible', [])
        view = wv.get('view', {}).get('visible', [])

        fieldnames = wv.get('header_table', {}).get('prominent', [])
        for fieldname in fieldnames:
            if fieldname in view:
                prominent.append({'fieldName': fieldname, 'mode': 'view'})
            elif fieldname in edit:
                prominent.append({'fieldName': fieldname, 'mode': 'edit'})

        fieldnames = wv.get('header_table', {}).get('visible', [])
        for fieldname in fieldnames:
            if fieldname in edit:
                ret.append({'fieldName': fieldname, 'mode': 'edit'})
            elif fieldname in view:
                ret.append({'fieldName': fieldname, 'mode': 'view'})

        return prominent, self.three_column_list(ret)
