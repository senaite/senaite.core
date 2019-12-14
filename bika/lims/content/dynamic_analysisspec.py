# -*- coding: utf-8 -*-

from StringIO import StringIO

from bika.lims import _
from bika.lims.catalog import SETUP_CATALOG
from openpyxl.reader.excel import load_workbook
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import implementer


class IDynamicAnalysisSpec(model.Schema):
    """Dynamic Analysis Specification
    """

    specs_file = namedfile.NamedBlobFile(
        title=_(u"Specification File"),
        description=_(u"Only Excel files supported"),
        required=True)


@implementer(IDynamicAnalysisSpec)
class DynamicAnalysisSpec(Item):
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
        ps = self.get_primary_sheet()
        if ps is None:
            return []
        return map(lambda cell: cell.value, ps.rows[0])

    def get_specs(self):
        ps = self.get_primary_sheet()
        if ps is None:
            return []
        keys = self.get_header()
        specs = []
        for num, row in enumerate(ps.rows):
            # skip the header
            if num == 0:
                continue
            values = map(lambda cell: cell.value, row)
            data = dict(zip(keys, values))
            specs.append(data)
        return specs
