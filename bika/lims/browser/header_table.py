"""ARs and Samples use HeaderTable to display object fields in their custom
view and edit screens.
"""

from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HeaderTableView(BrowserView):

    template = ViewPageTemplateFile('templates/header_table.pt')

    def __call__(self):
        self.errors = {}
        if 'header_table_submitted' in self.request:
            pass
        else:
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
            column = input_list[i*sublist_len:_list_end(i)]
            if len(column) > 0:
                final.append(column)
        return final

    def sublists(self, mode):
        ret = []
        schema = self.context.Schema()
        fields = list(schema.fields())
        for field in fields:
            fieldname = field.getName()
            widget = field.widget
            visible = schema[fieldname].widget.visible
            if visible and isinstance(visible, dict):
                if 'edit' in visible and visible['edit'] == 'visible':
                    ret.append({'field': field,
                                'widget': widget,
                                'mode': 'edit'})
                    continue
                if 'view' in visible and visible['view'] == 'visible':
                    ret.append({'field': field,
                                'widget': widget,
                                'mode': 'view'})
                    continue
        return self.three_column_list(ret)
