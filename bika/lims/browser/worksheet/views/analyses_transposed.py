# coding=utf-8
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser.bika_listing import BikaListingTable
from bika.lims.browser.worksheet.views.analyses import AnalysesView


class AnalysesTransposedView(AnalysesView):
    """ The view for displaying the table of manage_results transposed.
        Analysis Requests are displayed in columns and analyses in rows.
        Uses most of the logic provided by BikaListingView through
        bika.lims.worksheet.views.AnalysesView to generate the items,
        but renders its own template, which is highly specific for
        display analysis results. Because of this, some generic
        BikaListing functionalities, such as sorting, pagination,
        contextual menus for columns, etc. will not work in this view.
    """

    def contents_table(self, table_only = True):
        """ Overrides contents_table method from the parent class
            BikaListingView, using the transposed template instead
            of the classic template.
        """
        table = AnalysesTransposedTable(bika_listing = self, table_only = True)
        return table.render(self)


class AnalysesTransposedTable(BikaListingTable):
    """ The BikaListingTable that uses a transposed template for
        displaying the results.
    """
    render = ViewPageTemplateFile("../templates/analyses_transposed.pt")
    render_cell = ViewPageTemplateFile("../templates/analyses_transposed_cell.pt")

    def rendered_items(self, cat=None, **kwargs):
        return ''

    def get_rows_headers(self):
        cached = []
        rows = []
        index = 0
        ignore = ['Analysis', 'Service', 'Result']
        for col in self.bika_listing.review_state['columns']:
            if col == 'Result':
                # Further interims will be inserted in this position
                resindex = index
            if col in ignore:
                continue
            lcol = self.bika_listing.columns[col]
            rows.append({'id': col,
                         'title': lcol['title'],
                         'type': lcol.get('type',''),
                         'row_type': 'field',
                         'hidden': not lcol.get('toggle', True),
                         'input_class': lcol.get('input_class',''),
                         'input_width': lcol.get('input_width','')})
            cached.append(col)
            index += 1

        for item in self.items:
            for interim in item.get('interim_fields', []):
                if interim['keyword'] not in cached:
                    rows.insert(resindex,
                                {'id': interim['keyword'],
                                 'title': interim['title'],
                                 'type': interim.get('type'),
                                 'row_type': 'interim',
                                 'hidden': interim.get('hidden', False)})
                    cached.append(interim['keyword'])
                    resindex += 1

            if item['id'] not in cached:
                rows.insert(resindex,
                            {'id': item['id'],
                             'title': item['title'],
                             'type': item.get('type',''),
                             'row_type': 'analysis',
                             'index': index})
                resindex += 1
                cached.append(item['id'])
        return rows

    def render_row_cell(self, rowheader, item):
        self.current_rowhead = rowheader
        self.current_item = item
        return self.render_cell()


