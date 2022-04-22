Utility for extending Worksheet layouts
-----------------------------

First step: create utility for provide tuples custom layouts

.. code-block:: python

    from zope.interface import implements
    from bika.lims.interfaces import IWorksheetLayouts

    class MyClassForWorksheetLayouts(object):
        """ My worksheet layouts
        """
        implements(IWorksheetLayouts)

        def getLayoutsList(self):
            return (
                ('my_first_ws_layout', 'My first WS layout'),
            )

Second step: registration created utility in the `configure.zcml`

.. code-block:: xml

    <utility
        name="my_name_worksheet_layouts_utility"
        factory="my.module.some_module.MyClassForWorksheetLayouts"
        provides="bika.lims.interfaces.IWorksheetLayouts"
    />

Third step: create view for your layout

.. code-block:: python

    from bika.lims.browser.analyses import AnalysesView

    class MyFirstWSLayoutView(AnalysesView):
        """ My worksheet layout view
        """
        def __init__(self, context, request):
            super(MyFirstWSLayoutView, self).__init__(context, request)
            # some custom logic

Fourth step: registration your view in the `configure.zcml`

.. code-block:: xml

    <!-- use core layer or your addon layer -->
    <browser:page
        for="bika.lims.interfaces.IWorksheet"
        name="my_first_ws_layout"
        class="my.module.some_module.MyFirstWSLayoutView"
        permission="senaite.core.permissions.ViewResults"
        layer="bika.lims.interfaces.IBikaLIMS"
    />

