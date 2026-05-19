# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.

import os
import tempfile
import unittest

from senaite.core.browser.fields.parsing import parse_record_literal


class TestRecordParsing(unittest.TestCase):

    def test_parse_record_literal_parses_python_literals(self):
        parsed = parse_record_literal("{'key': 'value'}")
        self.assertEqual(parsed, {'key': 'value'})

    def test_parse_record_literal_normalizes_multiline_records(self):
        payload = "{'a': 1}\n{'b': 2}"
        parsed = parse_record_literal(payload, normalize_records=True)
        self.assertEqual(parsed, ({'a': 1}, {'b': 2}))

    def test_parse_record_literal_rejects_code_execution_payload(self):
        fd, marker = tempfile.mkstemp(prefix="senaite_eval_")
        os.close(fd)
        os.unlink(marker)
        payload = "__import__('os').system('touch %s')" % marker

        with self.assertRaises((ValueError, SyntaxError)):
            parse_record_literal(payload)

        self.assertFalse(os.path.exists(marker))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRecordParsing))
    return suite
