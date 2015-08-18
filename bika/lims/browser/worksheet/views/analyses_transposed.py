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

    def contents_table(self, table_only = False):
        """ Overrides contents_table method from the parent class
            BikaListingView, using the transposed template instead
            of the classic template.
        """
        table = AnalysesTransposedTable(bika_listing = self, table_only = table_only)
        return table.render(self)


class AnalysesTransposedTable(BikaListingTable):
    """ The BikaListingTable that uses a transposed template for
        displaying the results.
    """
    render = ViewPageTemplateFile("../templates/analyses_transposed.pt")

    def rendered_items(self, cat=None, **kwargs):
        return ''
