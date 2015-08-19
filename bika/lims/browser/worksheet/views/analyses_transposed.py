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

    def rendered_items(self, cat=None, **kwargs):
        return ''

    def get_rows_headers(self):
        cached = []
        rows = []
        index = 0
        for col in self.bika_listing.review_state['columns']:
            lcol = self.bika_listing.columns[col]
            rows.append({'title': lcol['title'],
                         'input_class': lcol.get('input_class',''),
                         'input_width': lcol.get('input_width',''),
                         'type': lcol.get('type',''),
                         'toggle': lcol.get('toggle', True),
                         'row_type': 'field'})
            index += 1
        for item in self.items:
            for interim in item.get('interim_fields', []):
                if interim['title'] not in cached:
                    rows.append({'title': interim['title'],
                                 'row_type': 'interim',
                                 'index': index})
                    index += 1
                    cached.append(interim['title'])
            if item['title'] not in cached:
                rows.append({'title': item['title'],
                             'row_type': 'analysis',
                             'index': index})
                index += 1
                cached.append(item['title'])
        return rows

