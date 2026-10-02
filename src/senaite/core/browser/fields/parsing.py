# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.

import ast


def parse_record_literal(value, normalize_records=False):
    """Safely parse stringified record values without executing code.

    Some record payloads are persisted as string representations of Python
    literals. Historically these were parsed with eval(), which allows
    arbitrary code execution. We only accept Python literals here.
    """
    if not isinstance(value, str):
        return value

    if normalize_records:
        value = value.replace('}\n', '},')

    return ast.literal_eval(value)
