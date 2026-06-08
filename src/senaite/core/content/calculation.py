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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import importlib
import inspect
import math
import re
import string

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ICalculation
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.interimfields import InterimFields
from senaite.core.schema.uidreferencefield import UIDReferenceField
from senaite.core.validators.formula import FormulaValidator
from senaite.core.validators.imports import ImportsValidator
from senaite.core.validators.interimfields import \
    InterimFieldsValidationErrorView
from senaite.core.validators.interimfields import InterimFieldsValidator
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from z3c.form import error
from z3c.form import util
from z3c.form import validator
from zope import component
from zope import schema
from zope.interface import Interface
from zope.interface import implementer


def getGlobals(imports=None, **kwargs):
    """Return the globals dictionary for the formula calculation
    """
    # Default globals
    globs = {
        "__builtins__": None,
        "all": all,
        "any": any,
        "bool": bool,
        "chr": chr,
        "cmp": cmp,
        "complex": complex,
        "divmod": divmod,
        "enumerate": enumerate,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "hex": hex,
        "int": int,
        "len": len,
        "list": list,
        "long": long,
        "math": math,
        "max": max,
        "min": min,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "range": range,
        "reversed": reversed,
        "round": round,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "xrange": xrange,
    }
    # Update with keyword arguments
    globs.update(kwargs)
    # Update with additional Python libraries
    imports = imports or []
    for imp in imports:
        mod = imp["module"]
        func = imp["function"]
        member = getModuleMember(mod, func)
        if member is None:
            raise ImportError(
                "Could not find member {} of module {}".format(
                    func, mod))
        globs[func] = member
    return globs


def getModuleMember(dotted_name, member):
    """Get the member object of a module.

    :param dotted_name: The dotted name of the module, e.g. 'scipy.special'
    :type dotted_name: string
    :param member: The name of the member function, e.g. 'gammaincinv'
    :type member: string
    :returns: member object or None
    """
    try:
        mod = importlib.import_module(dotted_name)
    except ImportError:
        return None

    members = dict(inspect.getmembers(mod))
    return members.get(member)


class FormulaFormatter(string.Formatter):
    """Helper class to remove spaces, tabs and etc.

    Replaces square brackets and correctly substitute dotted parameters (e.g.
    AnalysisService wildcards)
    """

    def __init__(self):
        super(FormulaFormatter, self).__init__()
        self.trans = {ord(s): api.safe_unicode(d) for s, d in zip("[]", "{}")}
        for c in "\n\t\r":
            self.trans[ord(c)] = u""

    def format(self, formula, params):
        formula = api.safe_unicode(formula)
        formula = formula.translate(self.trans)
        return self.vformat(formula, [], params)

    def get_field(self, field_name, args, kwargs):
        return (self.get_value(field_name, args, kwargs), field_name)


f_formatter = FormulaFormatter()


def calculate_formula(formula="", parameters={}, imports=None):
    result = "Failure"

    try:
        formula = f_formatter.format(formula, parameters)
        result = eval(formula, getGlobals(imports))
    except TypeError as e:
        # non-numeric arguments in interim mapping?
        result = "TypeError: {}".format(str(e.args[0]))
    except ZeroDivisionError as e:
        result = "Division by 0: {}".format(str(e.args[0]))
    except KeyError as e:
        result = "Key Error: {}".format(str(e.args[0]))
    except ImportError as e:
        result = "Import Error: {}".format(str(e.args[0]))
    except SyntaxError as e:
        result = "Syntax Error: {}".format(str(e.args[0]))
    except Exception as e:
        result = "Unspecified exception: {}".format(str(e.args[0]))

    return result


class IImportRecord(Interface):
    """Record schema for python import module
    """
    module = schema.TextLine(
        title=_(
            u"label_calculation_import_module_name",
            default=u"Module"
        ),
        required=False)
    function = schema.TextLine(
        title=_(
            u"label_calculation_import_function_name",
            default=u"Function"
        ),
        required=False)


class ITestParameterRecord(Interface):
    """Record schema for python test params
    """

    directives.widget("keyword", style=u"max-width: 120px;")
    keyword = schema.TextLine(
        title=_(
            u"label_calculation_test_param_keyword",
            default=u"Keyword"
        ),
        required=False,
        default=u"")

    directives.widget("value", style=u"max-width: 100px;")
    value = schema.TextLine(
        title=_(
            u"label_calculation_test_param_value",
            default=u"Value"
        ),
        required=False,
        default=u"")


class ICalculationSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_calculation_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_calculation_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget(
        "interim_fields",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    interim_fields = InterimFields(
        title=_(u"label_calculation_interims",
                default=u"Calculation Interim Fields"),
        description=_(u"description_calculation_interims",
                      default=u"Define interim fields such as vessel mass, "
                      u"dilution factors, should your calculation require "
                      u"them. The field title specified here will be used "
                      u"as column headers and field descriptors where "
                      u"the interim fields are displayed. If 'Apply wide' "
                      u"is enabled the field will be shown in a selection "
                      u"box on the top of the worksheet, allowing to "
                      u"apply a specific value to all the corresponding "
                      u"fields on the sheet."),
        required=False,
    )

    directives.widget(
        "imports",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    imports = DataGridField(
        title=_(u"label_calculation_imports",
                default=u"Additional Python Libraries"),
        description=_(u"description_calculation_imports",
                      default=u"If your formula needs a special function "
                      u"from an external Python library, you can import "
                      u"it here. E.g. if you want to use the 'floor' "
                      u"function from the Python 'math' module, you "
                      u"add 'math' to the Module field and 'floor' "
                      u"to the function field. The equivalent in "
                      u"Python would be 'from math import floor'. "
                      u"In your calculation you could use then "
                      u"'floor([Ca] + [Mg])'."),
        value_type=DataGridRow(schema=IImportRecord),
        required=False,
        default=[
            {"module": "math", "function": "floor"},
            {"module": "math", "function": "ceil"},
        ]
    )

    formula = schema.Text(
        title=_(
            u"label_calculation_formula",
            default=u"Calculation Formula"
        ),
        description=_(
            u"description_calculation_formula",
            default=u"<p>The formula you type here will be "
                    u"dynamically calculated be dynamically calculated when "
                    u"an analysis using this calculation is displayed.</p>"
                    u"<p>To enter a Calculation, use standard maths "
                    u"operators, + - * / ( ), and all keywords available, "
                    u"both from other Analysis Services and the Interim "
                    u"Fields specified here, as variables. Enclose them "
                    u"in square brackets [ ].</p><p>E.g, the calculation "
                    u"for Total Hardness, the total of Calcium (ppm) and "
                    u"Magnesium (ppm) ions in water, is entered as [Ca] "
                    u"+ [Mg], where Ca and Mg are the keywords for "
                    u"those two Analysis Services.</p>"
        ),
        required=True,
    )

    directives.widget(
        "test_parameters",
        DataGridWidgetFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=True)
    test_parameters = DataGridField(
        title=_(
            u"label_calculation_test_params",
            default=u"Test Parameters"
        ),
        description=_(
            u"description_calculation_test_params",
            default=u"To test the calculation, enter values here "
                    u"for all calculation parameters.  This includes "
                    u"Interim fields defined above, as well as any services "
                    u"that this calculation depends on to "
                    u"calculate results."
        ),
        value_type=DataGridRow(schema=ITestParameterRecord),
        required=False,
        default=[]
    )

    directives.mode(raw_test_keywords="hidden")
    raw_test_keywords = schema.TextLine(
        title=_(u"label_calculation_raw_test_keywords",
                default=u"Raw Test Result"),
        required=False,
        default=u"",
    )

    test_result = schema.TextLine(
        title=_(u"label_calculation_test_result",
                default=u"Test Result"),
        description=_(u"description_calculation_test_result",
                      default=u"The result after the calculation has taken "
                      u"place with test values.")
    )

    directives.mode(dependent_services="hidden")
    dependent_services = UIDReferenceField(
        title=_(
            u"label_calculation_dependent_services",
            default=u"DependentServices"
        ),
        allowed_types=("AnalysisService", ),
        relationship="CalculationDependentServices",
        multi_valued=True,
        required=False,
    )


@implementer(ICalculation, ICalculationSchema, IDeactivable)
class Calculation(Container):
    """Calculation
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    def _getGlobals(self):
        return getGlobals(self.getPythonImports())

    def _getModuleMember(self, dotted_name, member):
        return getModuleMember(dotted_name, member)

    @security.protected(permissions.View)
    def getInterimFields(self):
        accessor = self.accessor("interim_fields")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setInterimFields(self, value):
        new_value = []

        for x in range(len(value)):
            row = dict(value[x])
            keys = row.keys()
            if "value" not in keys:
                row["value"] = ""
            # convert None values to empty string to avoid value conversion
            # to "None"
            if row["value"] is None:
                row["value"] = ""
            # normalize old AT 'type' field to new DX 'result_type'
            if "result_type" not in keys:
                old_type = row.pop("type", "")
                row["result_type"] = "string" if old_type == "string" \
                    else "numeric"
            if "choices" not in keys:
                row["choices"] = u""
            new_value.append(row)

        mutator = self.mutator("interim_fields")
        mutator(self, new_value)

    def getCalculationDependencies(self, flat=False, deps=None):
        """ Recursively calculates all dependencies of this calculation.
            The return value is dictionary of dictionaries (of dictionaries...)

            {service_UID1:
                {service_UID2:
                    {service_UID3: {},
                     service_UID4: {},
                    },
                },
            }

            set flat=True to get a simple list of AnalysisService objects
        """
        if deps is None:
            deps = [] if flat is True else {}

        def get_fetched(deps):
            if isinstance(deps, list):
                return map(api.get_uid, deps)
            if isinstance(deps, dict):
                fetched = deps.keys()
                for value in deps.values():
                    fetched.extend(get_fetched(value))
                return fetched
            return []

        # List of service uids that have been grabbed already. This is used to
        # prevent an infinite recursion error when the formula includes the
        # Keyword of the Service that includes the Calculation
        fetched = get_fetched(deps)

        for service in self.getDependentServices():
            if api.get_uid(service) in fetched:
                # Processed already. Omit to prevent recursion
                continue

            if flat:
                deps.append(service)
            else:
                deps[service.UID()] = {}

            calc = service.getCalculation()
            if calc:
                calc.getCalculationDependencies(flat, deps)

        if flat:
            # Remove duplicates
            deps = list(set(deps))

        return deps

    def getCalculationDependents(self, deps=None):
        """Return a flat list of services who depend on this calculation.

        This refers only to services who's Calculation UIDReferenceField have
        the value set to point to this calculation.

        It has nothing to do with the services referenced in the calculation's
        Formula.
        """
        if deps is None:
            deps = []
        # TODO: when AnalysisService migrate to Dexterity replace w/ get_backrefs method
        # from senaite.core.schema.uidreferencefield
        backrefs = get_backreferences(self, 'AnalysisServiceCalculation')
        services = map(api.get_object_by_uid, backrefs)
        for service in services:
            calc = service.getCalculation()
            if calc and calc.UID() != self.UID():
                calc.getCalculationDependents(deps)
            deps.append(service)
        return deps

    # BBB: alternate spelling used in older code
    def getCalculationDependants(self, deps=None):
        return self.getCalculationDependents(deps=deps)

    # BBB: AT schema field property
    InterimFields = property(getInterimFields, setInterimFields)

    @security.protected(permissions.View)
    def getPythonImports(self):
        accessor = self.accessor("imports")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setPythonImports(self, value):
        mutator = self.mutator("imports")
        mutator(self, value)

    # BBB: AT schema field property
    PythonImports = property(getPythonImports, setPythonImports)

    @security.protected(permissions.View)
    def getFormula(self):
        accessor = self.accessor("formula")
        value = accessor(self) or ""
        return api.to_utf8(value)

    def getMinifiedFormula(self):
        """Return the current formula value as text.
        The result will have newlines and additional spaces stripped out.
        """
        value = " ".join(self.getFormula().splitlines())
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setFormula(self, value):
        """Set the Dependent Services from the text of the calculation Formula
        """
        sc = api.get_tool(SETUP_CATALOG)
        if not value:
            self.setDependentServices(None)
        else:
            keywords = re.compile(r"\[([^.^\]]+)\]").findall(value)
            brains = sc(portal_type='AnalysisService', getKeyword=keywords)
            services = [brain.getObject() for brain in brains]
            self.setDependentServices(services)

        mutator = self.mutator("formula")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Formula = property(getFormula, setFormula)

    @security.protected(permissions.View)
    def getTestParameters(self):
        accessor = self.accessor("test_parameters")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setTestParameters(self, value):
        """This is called from the objectmodified subscriber, to ensure
        correct population of the test-parameters field.
        It collects Keywords for all services that are direct dependencies of
        this calculatioin, and all of this calculation's InterimFields,
        and gloms them together.
        """
        params = []

        # Set default/existing values for InterimField keywords
        for interim in self.getInterimFields():
            keyword = interim.get("keyword")
            ex = [x.get("value") for x in value if
                  x.get("keyword") == keyword]
            params.append({"keyword": keyword,
                           "value": ex[0] if ex else interim.get("value")})
        # Set existing/blank values for service keywords
        for service in self.getDependentServices():
            keyword = service.getKeyword()
            ex = [x.get("value") for x in value if
                  x.get("keyword") == keyword]
            params.append({"keyword": keyword,
                           "value": ex[0] if ex else ""})

        mutator = self.mutator("test_parameters")
        mutator(self, params)

    # BBB: AT schema field property
    TestParameters = property(getTestParameters, setTestParameters)

    @security.protected(permissions.View)
    def getTestResult(self):
        accessor = self.accessor("test_result")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setTestResult(self, value):
        """Calculate formula with TestParameters and enter result into
        TestResult field.
        """
        # Create mapping from TestParameters
        mapping = {x['keyword']: x['value'] for x in self.getTestParameters()}
        # Gather up and parse formula
        formula = self.getMinifiedFormula()
        mutator = self.mutator("test_result")
        result = ""

        if formula:
            imports = self.getPythonImports()
            result = str(calculate_formula(formula, mapping, imports))

        mutator(self, result)

    # BBB: AT schema field property
    TestResult = property(getTestResult, setTestResult)

    @security.protected(permissions.View)
    def getDependentServices(self):
        accessor = self.accessor("dependent_services")
        return accessor(self) or []

    @security.protected(permissions.View)
    def getRawDependentServices(self):
        accessor = self.accessor("dependent_services", raw=True)
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setDependentServices(self, value):
        mutator = self.mutator("dependent_services")
        mutator(self, value)

    # BBB: AT schema field property
    DependentServices = property(getDependentServices, setDependentServices)


validator.WidgetsValidatorDiscriminators(
    FormulaValidator,
    schema=util.getSpecification(ICalculationSchema,
                                 force=True))
component.provideAdapter(FormulaValidator)

validator.WidgetValidatorDiscriminators(
    InterimFieldsValidator,
    field=ICalculationSchema["interim_fields"],
)
component.provideAdapter(InterimFieldsValidator)

validator.WidgetValidatorDiscriminators(
    ImportsValidator,
    field=ICalculationSchema["imports"],
)
component.provideAdapter(ImportsValidator)

error.ErrorViewDiscriminators(
    InterimFieldsValidationErrorView,
    error=error.MultipleErrors,
    field=ICalculationSchema["interim_fields"],
)
component.provideAdapter(InterimFieldsValidationErrorView)
