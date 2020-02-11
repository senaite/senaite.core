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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import importlib
import inspect
import math
import re

import transaction
from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api import get_object_by_uid
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields.uidreferencefield import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces.calculation import ICalculation
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import ReferenceWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import registerType
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.field import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements


schema = BikaSchema.copy() + Schema((

    InterimFieldsField(
        'InterimFields',
        widget=BikaRecordsWidget(
            label=_("Calculation Interim Fields"),
            description=_(
                "Define interim fields such as vessel mass, dilution factors, "
                "should your calculation require them. The field title "
                "specified here will be used as column headers and field "
                "descriptors where the interim fields are displayed. If "
                "'Apply wide' is enabled the field will be shown in a "
                "selection box on the top of the worksheet, allowing to apply "
                "a specific value to all the corresponding fields on the "
                "sheet."),
        )
    ),

    UIDReferenceField(
        'DependentServices',
        required=1,
        multiValued=1,
        allowed_types=('AnalysisService',),
        widget=ReferenceWidget(
            checkbox_bound=0,
            visible=False,
            label=_("Dependent Analyses"),
        ),
    ),

    RecordsField(
        'PythonImports',
        required=False,
        subfields=('module', 'function'),
        subfield_labels={'module': _('Module'), 'function': _('Function')},
        subfield_readonly={'module': False, 'function': False},
        subfield_types={'module': 'string', 'function': 'string'},
        default=[
            {'module': 'math', 'function': 'ceil'},
            {'module': 'math', 'function': 'floor'},
        ],
        subfield_validators={
            'module': 'importvalidator',
        },
        widget=BikaRecordsWidget(
            label=_("Additional Python Libraries"),
            description=_(
                "If your formula needs a special function from an external "
                "Python library, you can import it here. E.g. if you want to "
                "use the 'floor' function from the Python 'math' module, "
                "you add 'math' to the Module field and 'floor' to the "
                "function field. The equivalent in Python would be 'from math "
                "import floor'. In your calculation you could use then "
                "'floor([Ca] + [Mg])'. "
            ),
            allowDelete=True,
        ),
    ),

    TextField(
        'Formula',
        required=True,
        validators=('formulavalidator',),
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            label=_("Calculation Formula"),
            description=_(
                "<p>The formula you type here will be dynamically calculated "
                "when an analysis using this calculation is displayed.</p>"
                "<p>To enter a Calculation, use standard maths operators,  "
                "+ - * / ( ), and all keywords available, both from other "
                "Analysis Services and the Interim Fields specified here, "
                "as variables. Enclose them in square brackets [ ].</p>"
                "<p>E.g, the calculation for Total Hardness, the total of "
                "Calcium (ppm) and Magnesium (ppm) ions in water, is entered "
                "as [Ca] + [Mg], where Ca and MG are the keywords for those "
                "two Analysis Services.</p>"),
        )
    ),

    RecordsField(
        'TestParameters',
        required=False,
        subfields=('keyword', 'value'),
        subfield_labels={'keyword': _('Keyword'), 'value': _('Value')},
        subfield_readonly={'keyword': True, 'value': False},
        subfield_types={'keyword': 'string', 'value': 'float'},
        default=[{'keyword': '', 'value': 0}],
        widget=BikaRecordsWidget(
            label=_("Test Parameters"),
            description=_("To test the calculation, enter values here for all "
                          "calculation parameters.  This includes Interim "
                          "fields defined above, as well as any services that "
                          "this calculation depends on to calculate results."),
            allowDelete=False,
        ),
    ),

    TextField(
        'TestResult',
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            label=_('Test Result'),
            description=_("The result after the calculation has taken place "
                          "with test values.  You will need to save the "
                          "calculation before this value will be calculated."),
        )
    ),

))

schema['title'].widget.visible = True
schema['description'].widget.visible = True


class Calculation(BaseFolder, HistoryAwareMixin):
    """Calculation for Analysis Results
    """
    implements(ICalculation, IDeactivable)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def setInterimFields(self, value):
        new_value = []

        for x in range(len(value)):
            row = dict(value[x])
            keys = row.keys()
            if 'value' not in keys:
                row['value'] = 0
            new_value.append(row)

        # extract the keywords from the new calculation interims
        calculation_interim_keys = map(lambda i: i.get("keyword"), value)

        # update all service interims
        for service in self.getCalculationDependants():
            # get the interims of the dependant service
            service_interims = service.getInterimFields()
            # extract the keywords from the service interims
            service_interim_keys = map(lambda i: i.get("keyword"),
                                       service_interims)
            # sync new interims from the calculation -> service
            new_interims = set(calculation_interim_keys).difference(
                set(service_interim_keys))
            for key in new_interims:
                new_interim = value[calculation_interim_keys.index(key)]
                service_interims.append(new_interim)
            if new_interims:
                service.setInterimFields(service_interims)

        self.getField('InterimFields').set(self, new_value)

    def setFormula(self, Formula=None):
        """Set the Dependent Services from the text of the calculation Formula
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        if Formula is None:
            self.setDependentServices(None)
            self.getField('Formula').set(self, Formula)
        else:
            keywords = re.compile(r"\[([^.^\]]+)\]").findall(Formula)
            brains = bsc(portal_type='AnalysisService',
                         getKeyword=keywords)
            services = [brain.getObject() for brain in brains]
            self.getField('DependentServices').set(self, services)
            self.getField('Formula').set(self, Formula)

    def getMinifiedFormula(self):
        """Return the current formula value as text.
        The result will have newlines and additional spaces stripped out.
        """
        value = " ".join(self.getFormula().splitlines())
        return value

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

    def getCalculationDependants(self, deps=None):
        """Return a flat list of services who depend on this calculation.

        This refers only to services who's Calculation UIDReferenceField have
        the value set to point to this calculation.

        It has nothing to do with the services referenced in the calculation's
        Formula.
        """
        if deps is None:
            deps = []
        backrefs = get_backreferences(self, 'AnalysisServiceCalculation')
        services = map(get_object_by_uid, backrefs)
        for service in services:
            calc = service.getCalculation()
            if calc and calc.UID() != self.UID():
                calc.getCalculationDependants(deps)
            deps.append(service)
        return deps

    def setTestParameters(self, form_value):
        """This is called from the objectmodified subscriber, to ensure
        correct population of the test-parameters field.
        It collects Keywords for all services that are direct dependencies of
        this calculatioin, and all of this calculation's InterimFields,
        and gloms them together.
        """
        params = []

        # Set default/existing values for InterimField keywords
        for interim in self.getInterimFields():
            keyword = interim.get('keyword')
            ex = [x.get('value') for x in form_value if
                  x.get('keyword') == keyword]
            params.append({'keyword': keyword,
                           'value': ex[0] if ex else interim.get('value')})
        # Set existing/blank values for service keywords
        for service in self.getDependentServices():
            keyword = service.getKeyword()
            ex = [x.get('value') for x in form_value if
                  x.get('keyword') == keyword]
            params.append({'keyword': keyword,
                           'value': ex[0] if ex else ''})
        self.Schema().getField('TestParameters').set(self, params)

    # noinspection PyUnusedLocal
    def setTestResult(self, form_value):
        """Calculate formula with TestParameters and enter result into
         TestResult field.
        """
        # Create mapping from TestParameters
        mapping = {x['keyword']: x['value'] for x in self.getTestParameters()}
        # Gather up and parse formula
        formula = self.getMinifiedFormula()
        test_result_field = self.Schema().getField('TestResult')

        # Flush the TestResult field and return
        if not formula:
            return test_result_field.set(self, "")

        formula = formula.replace('[', '{').replace(']', '}').replace('  ', '')
        result = 'Failure'

        try:
            # print "pre: {}".format(formula)
            formula = formula.format(**mapping)
            # print "formatted: {}".format(formula)
            result = eval(formula, self._getGlobals())
            # print "result: {}".format(result)
        except TypeError as e:
            # non-numeric arguments in interim mapping?
            result = "TypeError: {}".format(str(e.args[0]))
        except ZeroDivisionError as e:
            result = "Division by 0: {}".format(str(e.args[0]))
        except KeyError as e:
            result = "Key Error: {}".format(str(e.args[0]))
        except ImportError as e:
            result = "Import Error: {}".format(str(e.args[0]))
        except Exception as e:
            result = "Unspecified exception: {}".format(str(e.args[0]))
        test_result_field.set(self, str(result))

    def _getGlobals(self, **kwargs):
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
        for imp in self.getPythonImports():
            mod = imp["module"]
            func = imp["function"]
            member = self._getModuleMember(mod, func)
            if member is None:
                raise ImportError(
                    "Could not find member {} of module {}".format(
                        func, mod))
            globs[func] = member
        return globs

    def _getModuleMember(self, dotted_name, member):
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

    def workflow_script_activate(self):
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = self.getDependentServices()
        inactive_services = []
        for service in services:
            if not api.is_active(service):
                inactive_services.append(service.Title())
        if inactive_services:
            msg = _("Cannot activate calculation, because the following "
                    "service dependencies are inactive: ${inactive_services}",
                    mapping={'inactive_services': safe_unicode(
                        ", ".join(inactive_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_script_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be deactivated if active services are using it.
        services = bsc(portal_type="AnalysisService", is_active=True)
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == self.UID():
                calc_services.append(service.Title())
        if calc_services:
            msg = _(
                'Cannot deactivate calculation, because it is in use by the '
                'following services: ${calc_services}',
                mapping={
                    'calc_services': safe_unicode(", ".join(calc_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException


registerType(Calculation, PROJECTNAME)
