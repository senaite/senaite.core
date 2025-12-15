Worksheet - Worksheet Layouts Utility
-------------------------------------

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t WorksheetLayoutUtility

Required Imports:

    >>> from senaite.core.config.worksheet import WORKSHEET_LAYOUT_OPTIONS
    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility

Check layouts:

    >>> vocab_key = "senaite.core.vocabularies.worksheet_layout"
    >>> vocab_factory = getUtility(IVocabularyFactory, vocab_key)
    >>> vocab = vocab_factory()
    >>> layout_names = set([term.token for term in vocab])
    >>> config_layouts = set([i[0] for i in WORKSHEET_LAYOUT_OPTIONS])
    >>> intersection = layout_names.intersection(config_layouts)
    >>> len(intersection)
    2
