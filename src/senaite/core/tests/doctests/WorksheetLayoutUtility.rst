Worksheet - Worksheet Layouts Utility
-------------------------------------

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t WorksheetLayoutUtility

Required Imports:

    >>> from senaite.core.config.worksheet import WORKSHEET_LAYOUT_OPTIONS
    >>> from senaite.core.vocabularies.worksheet import WorksheetLayoutsFactory
    >>> from Products.Archetypes.public import DisplayList

Check layouts:

    >>> layouts = set(WorksheetLayoutsFactory.keys())
    >>> config_layouts = set(DisplayList(WORKSHEET_LAYOUT_OPTIONS).keys())
    >>> intersection = layouts.intersection(config_layouts)
    >>> len(intersection)
    2
