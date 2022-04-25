Utility for extending Worksheet layouts
---------------------------------------

Use this tool if you want to create and use your own custom worksheet layout views.


1. Create class which implements ``IWorksheetLayouts`` marker interface and returns the list of your homemade layouts (as tuple of tuples) 

.. code-block:: python

    from zope.interface import implements
    from bika.lims.interfaces import IWorksheetLayouts

    class MyClassForWorksheetLayouts(object):
        """ My worksheet layouts
        """
        implements(IWorksheetLayouts)

        def getLayouts(self):
            return (
                ('my_first_ws_layout', 'My first WS layout'),
            )

Please note that each tuple which describes your layout has two elements: (``registered_view_name``, ``Title``). Title used in the drop-down menu.


2. Register your class as an utility in ``configure.zcml``

.. code-block:: xml

    <utility
        name="my_name_worksheet_layouts_utility"
        factory="my.module.some_module.MyClassForWorksheetLayouts"
        provides="bika.lims.interfaces.IWorksheetLayouts"
    />

3. Make a view for your new layout

.. code-block:: python

    from bika.lims.browser.analyses import AnalysesView

    class MyFirstWSLayoutView(AnalysesView):
        """ My worksheet layout view
        """
        def __init__(self, context, request):
            super(MyFirstWSLayoutView, self).__init__(context, request)
            # some custom logic

4. Register a fresh view file in the ``configure.zcml``

.. code-block:: xml

    <!-- use core layer or your addon layer -->
    <browser:page
        for="bika.lims.interfaces.IWorksheet"
        name="my_first_ws_layout"
        class="my.module.some_module.MyFirstWSLayoutView"
        permission="senaite.core.permissions.ViewResults"
        layer="bika.lims.interfaces.IBikaLIMS"
    />

