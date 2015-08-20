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
        self.partitions = []
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
            """for interim in item.get('interim_fields', []):
                if interim['keyword'] not in cached:
                    self.rows_headers.insert(resindex,
                                {'id': interim['keyword'],
                                 'title': interim['title'],
                                 'type': interim.get('type'),
                                 'row_type': 'interim',
                                 'hidden': interim.get('hidden', False)})
                    cached.append(interim['keyword'])
                    resindex += 1
            """
            if item['id'] not in cached:
                self.rows_headers.insert(resindex,
                            {'id': item['id'],
                             'title': item['title'],
                             'type': item.get('type',''),
                             'row_type': 'analysis',
                             'index': index})
                resindex += 1
                cached.append(item['id'])

            part = item['Partition']
            if part in self.trans_items:
                self.trans_items[part][item['id']] = item
            else:
                self.trans_items[part] = {item['id']: item}
            if part not in self.partitions:
                self.partitions.append(part)

    def rendered_items(self, cat=None, **kwargs):
        return ''

    def render_row_cell(self, rowheader, partition = ''):
        self.current_rowhead = rowheader
        self.current_partition = partition
        if rowheader['row_type'] == 'field':
            # Only the first item for this partition contains common
            # data for all the analyses with the same partition
            its = [i for i in self.items if i['Partition'] == partition]
            self.current_item = its[0] if its else {}

        elif partition in self.trans_items \
            and rowheader['id'] in self.trans_items[partition]:
            self.current_item = self.trans_items[partition][rowheader['id']]

        else:
            return ''

        return self.render_cell()
