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

    def __init__(self, bika_listing = None, table_only = False):
        BikaListingTable.__init__(self, bika_listing, True)
        self.rows_headers = []
        self.trans_items = {}
        self.positions = []
        self._transpose_data()

    def _transpose_data(self):
        cached = []
        index = 0
        #ignore = ['Analysis', 'Service', 'Result', 'ResultDM']
        include = ['Attachments', 'DetectionLimit', 'DueDate','Pos', 'ResultDM']
        for col in self.bika_listing.review_state['columns']:
            if col == 'Result':
                # Further interims will be inserted in this position
                resindex = index
            if col not in include:
                continue
            lcol = self.bika_listing.columns[col]
            self.rows_headers.append({'id': col,
                         'title': lcol['title'],
                         'type': lcol.get('type',''),
                         'row_type': 'field',
                         'hidden': not lcol.get('toggle', True),
                         'input_class': lcol.get('input_class',''),
                         'input_width': lcol.get('input_width','')})
            cached.append(col)
            index += 1

        for item in self.items:
            if item['Service'] not in cached:
                self.rows_headers.insert(resindex,
                            {'id': item['Service'],
                             'title': item['title'],
                             'type': item.get('type',''),
                             'row_type': 'analysis',
                             'index': index})
                resindex += 1
                cached.append(item['Service'])

            pos = item['Pos']
            if pos in self.trans_items:
                self.trans_items[pos][item['Service']] = item
            else:
                self.trans_items[pos] = {item['Service']: item}
            if pos not in self.positions:
                self.positions.append(pos)

    def rendered_items(self, cat=None, **kwargs):
        return ''

    def render_row_cell(self, rowheader, position = ''):
        self.current_rowhead = rowheader
        self.current_position = position
        if rowheader['row_type'] == 'field':
            # Only the first item for this position contains common
            # data for all the analyses with the same position
            its = [i for i in self.items if i['Pos'] == position]
            self.current_item = its[0] if its else {}

        elif position in self.trans_items \
            and rowheader['id'] in self.trans_items[position]:
            self.current_item = self.trans_items[position][rowheader['id']]

        else:
            return ''

        return self.render_cell()
