# coding=utf-8

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims.browser.bika_listing import BikaListingTable
from bika.lims.browser.worksheet.views.analyses import AnalysesView
from bika.lims.utils import t


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
        self.bika_listing = bika_listing

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

    def get_workflow_actions(self):
        """ Compile a list of possible workflow transitions for items
            in this Table.
        """

        # cbb return empty list if we are unable to select items
        if not self.bika_listing.show_select_column:
            return []

        if self.bika_listing.workflow is None:
            self.bika_listing.workflow = getToolByName(self.context, 'portal_workflow')
        # get all transitions for all items.
        transitions = {}
        actions = []
        for obj in [i.get('obj', '') for i in self.items]:
            obj = hasattr(obj, 'getObject') and obj.getObject() or obj
            for it in self.bika_listing.workflow.getTransitionsFor(obj):
                transitions[it['id']] = it

        # the list is restricted to and ordered by these transitions.
        if 'transitions' in self.bika_listing.review_state:
            for transition_dict in self.bika_listing.review_state['transitions']:
                if transition_dict['id'] in transitions:
                    actions.append(transitions[transition_dict['id']])
        else:
            actions = transitions.values()

        new_actions = []
        # remove any invalid items with a warning
        for a,action in enumerate(actions):
            if isinstance(action, dict) \
                    and 'id' in action:
                new_actions.append(action)
            else:
                logger.warning("bad action in custom_actions: %s. (complete list: %s)."%(action,actions))
        actions = new_actions
        # and these are removed
        if 'hide_transitions' in self.bika_listing.review_state:
            actions = [a for a in actions
                       if a['id'] not in self.bika_listing.review_state['hide_transitions']]

        # cheat: until workflow_action is abolished, all URLs defined in
        # GS workflow setup will be ignored, and the default will apply.
        # (that means, WorkflowAction-bound URL is called).
        for i, action in enumerate(actions):
            actions[i]['url'] = ''

        # if there is a self.review_state['some_state']['custom_actions'] attribute
        # on the BikaListingView, add these actions to the list.
        if 'custom_actions' in self.bika_listing.review_state:
            for action in self.bika_listing.review_state['custom_actions']:
                if isinstance(action, dict) \
                        and 'id' in action:
                    actions.append(action)

        for a,action in enumerate(actions):
            actions[a]['title'] = t(PMF(actions[a]['id'] + "_transition_title"))
        return actions
