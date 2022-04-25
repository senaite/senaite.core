Worksheet - Worksheet Layouts Utility
-------------------------------------

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t WorksheetLayoutUtility

Required Imports:

    >>> from bika.lims.browser.worksheet.tools import getWorksheetLayouts
    >>> from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
    >>> from Products.Archetypes.public import DisplayList

Check layouts:

    >>> layouts = set(getWorksheetLayouts().keys())
    >>> config_layouts = set(DisplayList(WORKSHEET_LAYOUT_OPTIONS).keys())
    >>> intersection = layouts.intersection(config_layouts)
    >>> len(intersection)
    2
