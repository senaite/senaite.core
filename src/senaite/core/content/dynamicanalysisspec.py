# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import defaultdict

from bika.lims import senaiteMessageFactory as _
from bika.lims import api
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IDynamicAnalysisSpec
from openpyxl.reader.excel import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from plone.namedfile import field as namedfile
from plone.supermodel import model
from six import StringIO
from z3c.form.interfaces import NOT_CHANGED
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant

REQUIRED_COLUMNS = [
    "Keyword",  # The Analysis Keyword
    "min",  # Lower Limit
    "max",  # Upper Limit
]

# Optional columns whose values are operators: each operator with the values
# it is written as, either its key, its symbol or its HTML entity (`&ge;`)
OPERATOR_COLUMNS = {
    "min_operator": {
        "geq": ["geq", "ge", ">=", u"\u2265"],
        "gt": ["gt", ">"],
    },
    "max_operator": {
        "leq": ["leq", "le", "<=", u"\u2264"],
        "lt": ["lt", "<"],
    },
}


def to_operator(column, value):
    """Returns the operator key (e.g. `geq`) of the value of an operator
    column, written as the key, the symbol (`>=`) or the HTML entity (`&ge;`,
    `geq;`), with any surrounding whitespace

    :param column: the operator column, `min_operator` or `max_operator`
    :param value: the value of the cell
    :returns: the operator key, or None if the value is not an operator
    """
    if not api.is_string(value):
        return None
    value = value.strip().lower()
    if value.startswith("&"):
        value = value[1:]
    if value.endswith(";"):
        value = value[:-1]
    for key, values in OPERATOR_COLUMNS[column].items():
        if value in values:
            return key
    return None


def is_empty(value):
    """Returns whether the value of a cell is empty or blank
    """
    if api.is_string(value):
        return not value.strip()
    return value is None


class IDynamicAnalysisSpecSchema(model.Schema):
    """Dynamic Analysis Specification
    """

    specs_file = namedfile.NamedBlobFile(
        title=_(u"Specification File"),
        description=_(u"Only Excel files supported"),
        required=True)

    @invariant
    def validate_specs_file(data):
        """Checks the Excel file contains the required header columns
        """
        # return immediately if not changed
        if data.specs_file == NOT_CHANGED:
            return True
        fd = StringIO(data.specs_file.data)
        try:
            xls = load_workbook(fd)
        except (InvalidFileException, TypeError):
            raise Invalid(_(
                "Invalid specifications file detected. "
                "Please upload an Excel spreadsheet with at least "
                "the following columns defined: '{}'"
                .format(", ".join(REQUIRED_COLUMNS))))
        try:
            header_row = xls.worksheets[0].rows.next()
            header = map(lambda c: c.value, header_row)
        except (IndexError, AttributeError):
            raise Invalid(
                _("First sheet does not contain a valid column definition"))
        # Strip trailing empty header cells (Excel pads the used range with
        # blank cells when otherwise-empty columns carry any formatting).
        while header and (header[-1] is None or
                          (api.is_string(header[-1])
                           and not header[-1].strip())):
            header.pop()
        # Every remaining header must be a usable column name, since the
        # dynamic results-range adapter looks up sample attributes through
        # getattr(obj, column) -- a non-string column raises TypeError at
        # sample creation time.
        for idx, col in enumerate(header):
            if not api.is_string(col) or not col.strip():
                raise Invalid(_(
                    "Column {} of the header row has no name. "
                    "Please remove empty columns from the spreadsheet "
                    "and upload it again.".format(idx + 1)))
        for col in REQUIRED_COLUMNS:
            if col not in header:
                raise Invalid(_("Column '{}' is missing".format(col)))
        # Operators must be valid, or the range would be applied inclusive
        rows = xls.worksheets[0].iter_rows(min_row=2, values_only=True)
        for num, row in enumerate(rows, start=2):
            for col, value in zip(header, row):
                if col not in OPERATOR_COLUMNS or is_empty(value):
                    continue
                if not to_operator(col, value):
                    operators = OPERATOR_COLUMNS[col]
                    valid = ", ".join(sorted(operators.keys()))
                    raise Invalid(_(
                        u"Invalid {} '{}' in row {}. Valid values are: {}, "
                        u"or their symbols".format(col, value, num, valid)))


@implementer(IDynamicAnalysisSpec, IDynamicAnalysisSpecSchema)
class DynamicAnalysisSpec(Container):
    """Dynamic Analysis Specification
    """
    _catalogs = [SETUP_CATALOG]

    def get_workbook(self):
        specs_file = self.specs_file
        if not specs_file:
            return None
        data = StringIO(specs_file.data)
        return load_workbook(data)

    def get_worksheets(self):
        wb = self.get_workbook()
        if wb is None:
            return []
        return wb.worksheets

    def get_primary_sheet(self):
        sheets = self.get_worksheets()
        if len(sheets) == 0:
            return None
        return sheets[0]

    def get_header(self):
        header = []
        ps = self.get_primary_sheet()
        if ps is None:
            return header
        for num, row in enumerate(ps.rows):
            if num > 0:
                break
            header = [cell.value for cell in row]
        # Excel often pads the used range with trailing empty cells; drop them
        # so downstream getattr(obj, column) calls don't blow up on a None
        # column name. Empty cells in the middle of the header are left as-is
        # because removing them would shift the column/value alignment used
        # by get_specs (zip(keys, row_cells)).
        while header and not (api.is_string(header[-1]) and header[-1].strip()):
            header.pop()
        return header

    def get_specs(self):
        ps = self.get_primary_sheet()
        if ps is None:
            return []
        keys = self.get_header()
        specs = []

        def get_cell_string_value(cell):
            value = cell.value
            if api.is_string(value):
                return value
            elif value is None:
                return None
            return str(value)

        for num, row in enumerate(ps.rows):
            # skip the header
            if num == 0:
                continue
            values = map(get_cell_string_value, row)
            data = dict(zip(keys, values))
            # operators are written as keys, symbols or HTML entities
            for column in OPERATOR_COLUMNS:
                if column in data:
                    data[column] = to_operator(column, data[column])
            specs.append(data)
        return specs

    def get_by_keyword(self):
        specs = self.get_specs()
        groups = defaultdict(list)
        for spec in specs:
            groups[spec.get("Keyword")].append(spec)
        return groups
