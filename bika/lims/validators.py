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

import re
import string
import types
from time import strptime as _strptime

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api import APIError
from bika.lims.utils import t as _t
from bika.lims.utils import to_utf8
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from Products.ZCTextIndex.ParseTree import ParseError
from zope.interface import implements


class IdentifierTypeAttributesValidator:
    """Validate IdentifierTypeAttributes to ensure that attributes are
    not duplicated.
    """

    implements(IValidator)
    name = "identifiertypeattributesvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = instance.REQUEST
        form = request.get('form', {})
        fieldname = kwargs['field'].getName()
        form_value = form.get(fieldname, False)
        if form_value is False:
            # not required...
            return True
        if value == instance.get(fieldname):
            # no change.
            return True

        return True


validation.register(IdentifierTypeAttributesValidator())


class IdentifierValidator:
    """some actual validation should go here.
    I'm leaving this stub registered, but adding no extra validation.
    """

    implements(IValidator)
    name = "identifiervalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = instance.REQUEST
        form = request.get('form', {})
        fieldname = kwargs['field'].getName()
        form_value = form.get(fieldname, False)
        if form_value is False:
            # not required...
            return True
        if value == instance.get(fieldname):
            # no change.
            return True

        return True


validation.register(IdentifierValidator())


class UniqueFieldValidator:
    """Verifies if a field value is unique within the same container
    """
    implements(IValidator)
    name = "uniquefieldvalidator"

    def get_parent_objects(self, context):
        """Return all objects of the same type from the parent object
        """
        parent_object = api.get_parent(context)
        portal_type = api.get_portal_type(context)
        return parent_object.objectValues(portal_type)

    def query_parent_objects(self, context, query=None):
        """Return the objects of the same type from the parent object

        :param query: Catalog query to narrow down the objects
        :type query: dict
        :returns: Content objects of the same portal type in the parent
        """

        # return the object values if we have no catalog query
        if query is None:
            return self.get_parent_objects(context)

        # avoid undefined reference of catalog in except...
        catalog = None

        # try to fetch the results via the catalog
        try:
            catalogs = api.get_catalogs_for(context)
            catalog = catalogs[0]
            return map(api.get_object, catalog(query))
        except (IndexError, UnicodeDecodeError, ParseError, APIError) as e:
            # fall back to the object values of the parent
            logger.warn("UniqueFieldValidator: Catalog query {} failed "
                        "for catalog {} ({}) -> returning object values of {}"
                        .format(query, repr(catalog), str(e),
                                repr(api.get_parent(context))))
            return self.get_parent_objects(context)

    def make_catalog_query(self, context, field, value):
        """Create a catalog query for the field
        """

        # get the catalogs for the context
        catalogs = api.get_catalogs_for(context)
        # context not in any catalog?
        if not catalogs:
            logger.warn("UniqueFieldValidator: Context '{}' is not assigned"
                        "to any catalog!".format(repr(context)))
            return None

        # take the first catalog
        catalog = catalogs[0]

        # Check if the field accessor is indexed
        field_index = field.getName()
        accessor = field.getAccessor(context)
        if accessor:
            field_index = accessor.__name__

        # return if the field is not indexed
        if field_index not in catalog.indexes():
            return None

        # build a catalog query
        query = {
            "portal_type": api.get_portal_type(context),
            "path": {
                "query": api.get_parent_path(context),
                "depth": 1,
            }
        }
        query[field_index] = value
        logger.info("UniqueFieldValidator:Query={}".format(query))
        return query

    def __call__(self, value, *args, **kwargs):
        context = kwargs['instance']
        uid = api.get_uid(context)
        field = kwargs['field']
        fieldname = field.getName()
        translate = getToolByName(context, 'translation_service').translate

        # return directly if nothing changed
        if value == field.get(context):
            return True

        # Fetch the parent object candidates by catalog or by objectValues
        #
        # N.B. We want to use the catalog to speed things up, because using
        # `parent.objectValues` is very expensive if the parent object contains
        # many items and causes the UI to block too long
        catalog_query = self.make_catalog_query(context, field, value)
        parent_objects = self.query_parent_objects(
            context, query=catalog_query)

        for item in parent_objects:
            if hasattr(item, 'UID') and item.UID() != uid and \
               fieldname in item.Schema() and \
               str(item.Schema()[fieldname].get(item)) == str(value).strip():
                # We have to compare them as strings because
                # even if a number (as an  id) is saved inside
                # a string widget and string field, it will be
                # returned as an int. I don't know if it is
                # caused because is called with
                # <item.Schema()[fieldname].get(item)>,
                # but it happens...
                msg = _(
                    "Validation failed: '${value}' is not unique",
                    mapping={
                        'value': safe_unicode(value)
                    })
                return to_utf8(translate(msg))
        return True


validation.register(UniqueFieldValidator())


class InvoiceBatch_EndDate_Validator:
    """ Verifies that the End Date is after the Start Date """

    implements(IValidator)
    name = "invoicebatch_EndDate_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs.get('instance')
        request = kwargs.get('REQUEST')

        if request and request.form.get('BatchStartDate'):
            startdate = _strptime(request.form.get('BatchStartDate'), '%Y-%m-%d %H:%M')
        else:
            startdate = _strptime(instance.getBatchStartDate(), '%Y-%m-%d %H:%M')

        enddate = _strptime(value, '%Y-%m-%d %H:%M')

        translate = api.get_tool('translation_service', instance).translate
        if not enddate >= startdate:
            msg = _("Start date must be before End Date")
            return to_utf8(translate(msg))
        return True


validation.register(InvoiceBatch_EndDate_Validator())


class ServiceKeywordValidator:
    """Validate AnalysisService Keywords
    must match isUnixLikeName
    may not be the same as another service keyword
    may not be the same as any InterimField id.
    """

    implements(IValidator)
    name = "servicekeywordvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})

        translate = getToolByName(instance, 'translation_service').translate

        if re.findall(r"[^A-Za-z\w\d\-\_]", value):
            return _("Validation failed: keyword contains invalid characters")

        # check the value against all AnalysisService keywords
        # this has to be done from catalog so we don't
        # clash with ourself
        bsc = getToolByName(instance, 'bika_setup_catalog')
        services = bsc(portal_type='AnalysisService', getKeyword=value)
        for service in services:
            if service.UID != instance.UID():
                msg = _(
                    "Validation failed: '${title}': This keyword "
                    "is already in use by service '${used_by}'",
                    mapping={
                        'title': safe_unicode(value),
                        'used_by': safe_unicode(service.Title)
                    })
                return to_utf8(translate(msg))

        calc = hasattr(instance, 'getCalculation') and \
            instance.getCalculation() or None
        our_calc_uid = calc and calc.UID() or ''

        # check the value against all Calculation Interim Field ids
        calcs = [c for c in bsc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields:
                continue
            for field in interim_fields:
                if field['keyword'] == value and our_calc_uid != calc.UID():
                    msg = _(
                        "Validation failed: '${title}': This keyword "
                        "is already in use by calculation '${used_by}'",
                        mapping={
                            'title': safe_unicode(value),
                            'used_by': safe_unicode(calc.Title())
                        })
                    return to_utf8(translate(msg))
        return True


validation.register(ServiceKeywordValidator())


class InterimFieldsValidator:
    """Validating InterimField keywords.
        XXX Applied as a subfield validator but validates entire field.
        keyword must match isUnixLikeName
        keyword may not be the same as any service keyword.
        keyword must be unique in this InterimFields field
        keyword must be unique for interimfields which share the same title.
        title must be unique for interimfields which share the same keyword.
    """

    implements(IValidator)
    name = "interimfieldsvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get(fieldname, [])

        translate = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')

        # We run through the validator once per form submit, and check all
        # values
        # this value in request prevents running once per subfield value.
        key = instance.id + fieldname
        if instance.REQUEST.get(key, False):
            return True

        for x in range(len(interim_fields)):
            row = interim_fields[x]
            keys = row.keys()
            if 'title' not in keys:
                instance.REQUEST[key] = to_utf8(
                    translate(_("Validation failed: title is required")))
                return instance.REQUEST[key]
            if 'keyword' not in keys:
                instance.REQUEST[key] = to_utf8(
                    translate(_("Validation failed: keyword is required")))
                return instance.REQUEST[key]
            if not re.match(r"^[A-Za-z\w\d\-\_]+$", row['keyword']):
                instance.REQUEST[key] = _(
                    "Validation failed: keyword contains invalid characters")
                return instance.REQUEST[key]

        # keywords and titles used once only in the submitted form
        keywords = {}
        titles = {}
        for field in interim_fields:
            if 'keyword' in field:
                if field['keyword'] in keywords:
                    keywords[field['keyword']] += 1
                else:
                    keywords[field['keyword']] = 1
            if 'title' in field:
                if field['title'] in titles:
                    titles[field['title']] += 1
                else:
                    titles[field['title']] = 1
        for k in [k for k in keywords.keys() if keywords[k] > 1]:
            msg = _(
                "Validation failed: '${keyword}': duplicate keyword",
                mapping={
                    'keyword': safe_unicode(k)
                })
            instance.REQUEST[key] = to_utf8(translate(msg))
            return instance.REQUEST[key]
        for t in [t for t in titles.keys() if titles[t] > 1]:
            msg = _(
                "Validation failed: '${title}': duplicate title",
                mapping={
                    'title': safe_unicode(t)
                })
            instance.REQUEST[key] = to_utf8(translate(msg))
            return instance.REQUEST[key]

        # check all keywords against all AnalysisService keywords for dups
        services = bsc(portal_type='AnalysisService', getKeyword=value)
        if services:
            msg = _(
                "Validation failed: '${title}': "
                "This keyword is already in use by service '${used_by}'",
                mapping={
                    'title': safe_unicode(value),
                    'used_by': safe_unicode(services[0].Title)
                })
            instance.REQUEST[key] = to_utf8(translate(msg))
            return instance.REQUEST[key]

        # any duplicated interimfield titles must share the same keyword
        # any duplicated interimfield keywords must share the same title
        calcs = bsc(portal_type='Calculation')
        keyword_titles = {}
        title_keywords = {}
        for calc in calcs:
            if calc.UID == instance.UID():
                continue
            calc = calc.getObject()
            for field in calc.getInterimFields():
                keyword_titles[field['keyword']] = field['title']
                title_keywords[field['title']] = field['keyword']
        for field in interim_fields:
            if field['keyword'] != value:
                continue
            if 'title' in field and \
               field['title'] in title_keywords.keys() and \
               title_keywords[field['title']] != field['keyword']:
                msg = _(
                    "Validation failed: column title '${title}' "
                    "must have keyword '${keyword}'",
                    mapping={
                        'title': safe_unicode(field['title']),
                        'keyword': safe_unicode(title_keywords[field['title']])
                    })
                instance.REQUEST[key] = to_utf8(translate(msg))
                return instance.REQUEST[key]
            if 'keyword' in field and \
               field['keyword'] in keyword_titles.keys() and \
               keyword_titles[field['keyword']] != field['title']:
                msg = _(
                    "Validation failed: keyword '${keyword}' "
                    "must have column title '${title}'",
                    mapping={
                        'keyword': safe_unicode(field['keyword']),
                        'title': safe_unicode(keyword_titles[field['keyword']])
                    })
                instance.REQUEST[key] = to_utf8(translate(msg))
                return instance.REQUEST[key]

        # Check if choices subfield is valid
        for interim in interim_fields:
            message = self.validate_choices(interim)
            if message:
                # Not a valid choice
                instance.REQUEST[key] = message
                return message

        instance.REQUEST[key] = True
        return True

    def validate_choices(self, interim):
        """Checks whether the choices are valid for the given interim
        """
        choices = interim.get("choices")
        if not choices:
            # No choices set, nothing to do
            return

        # Choices are expressed like "value0:text0|value1:text1|..|valuen:textn"
        choices = choices.split("|") or []
        try:
            choices = dict(map(lambda ch: ch.strip().split(":"), choices))
        except ValueError:
            return _t(_(
                "No valid format in choices field. Supported format is: "
                "<value-0>:<text>|<value-1>:<text>|<value-n>:<text>"))

        # Empty keys (that match with the result value) are not allowed
        keys = map(lambda k: k.strip(), choices.keys())
        empties = filter(None, keys)
        if len(empties) != len(keys):
            return _t(_("Empty keys are not supported"))

        # No duplicate keys allowed
        unique_keys = list(set(keys))
        if len(unique_keys) != len(keys):
            return _t(_("Duplicate keys in choices field"))

        # We need at least 2 choices
        if len(keys) < 2:
            return _t(_("At least, two options for choices field are required"))


validation.register(InterimFieldsValidator())


class FormulaValidator:
    """ Validate keywords in calculation formula entry
    """
    implements(IValidator)
    name = "formulavalidator"

    def __call__(self, value, *args, **kwargs):
        if not value:
            return True
        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get('InterimFields')

        translate = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')
        interim_keywords = interim_fields and \
            [f['keyword'] for f in interim_fields] or []
        keywords = re.compile(r"\[([^\.^\]]+)\]").findall(value)

        for keyword in keywords:
            # Check if the service keyword exists and is active.
            dep_service = bsc(getKeyword=keyword, is_active=True)
            if not dep_service and keyword not in interim_keywords:
                msg = _(
                    "Validation failed: Keyword '${keyword}' is invalid",
                    mapping={
                        'keyword': safe_unicode(keyword)
                    })
                return to_utf8(translate(msg))

        # Wildcards
        # LIMS-1769 Allow to use LDL and UDL in calculations
        # https://jira.bikalabs.com/browse/LIMS-1769
        allowedwds = ['LDL', 'UDL', 'BELOWLDL', 'ABOVEUDL']
        keysandwildcards = re.compile(r"\[([^\]]+)\]").findall(value)
        keysandwildcards = [k for k in keysandwildcards if '.' in k]
        keysandwildcards = [k.split('.', 1) for k in keysandwildcards]
        errwilds = [k[1] for k in keysandwildcards if k[0] not in keywords]
        if len(errwilds) > 0:
            msg = _(
                "Wildcards for interims are not allowed: ${wildcards}",
                mapping={
                    'wildcards': safe_unicode(', '.join(errwilds))
                })
            return to_utf8(translate(msg))

        wildcards = [k[1] for k in keysandwildcards if k[0] in keywords]
        wildcards = [wd for wd in wildcards if wd not in allowedwds]
        if len(wildcards) > 0:
            msg = _(
                "Invalid wildcards found: ${wildcards}",
                mapping={
                    'wildcards': safe_unicode(', '.join(wildcards))
                })
            return to_utf8(translate(msg))

        return True


validation.register(FormulaValidator())


class CoordinateValidator:
    """ Validate latitude or longitude field values
    """
    implements(IValidator)
    name = "coordinatevalidator"

    def __call__(self, value, **kwargs):
        if not value:
            return True

        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = instance.REQUEST

        form = request.form
        form_value = form.get(fieldname)

        translate = getToolByName(instance, 'translation_service').translate

        try:
            degrees = int(form_value['degrees'])
        except ValueError:
            return to_utf8(
                translate(_("Validation failed: degrees must be numeric")))

        try:
            minutes = int(form_value['minutes'])
        except ValueError:
            return to_utf8(
                translate(_("Validation failed: minutes must be numeric")))

        try:
            seconds = int(form_value['seconds'])
        except ValueError:
            return to_utf8(
                translate(_("Validation failed: seconds must be numeric")))

        if not 0 <= minutes <= 59:
            return to_utf8(
                translate(_("Validation failed: minutes must be 0 - 59")))

        if not 0 <= seconds <= 59:
            return to_utf8(
                translate(_("Validation failed: seconds must be 0 - 59")))

        bearing = form_value['bearing']

        if fieldname == 'Latitude':
            if not 0 <= degrees <= 90:
                return to_utf8(
                    translate(_("Validation failed: degrees must be 0 - 90")))
            if degrees == 90:
                if minutes != 0:
                    return to_utf8(
                        translate(
                            _("Validation failed: degrees is 90; "
                              "minutes must be zero")))
                if seconds != 0:
                    return to_utf8(
                        translate(
                            _("Validation failed: degrees is 90; "
                              "seconds must be zero")))
            if bearing.lower() not in 'sn':
                return to_utf8(
                    translate(_("Validation failed: Bearing must be N/S")))

        if fieldname == 'Longitude':
            if not 0 <= degrees <= 180:
                return to_utf8(
                    translate(_("Validation failed: degrees must be 0 - 180")))
            if degrees == 180:
                if minutes != 0:
                    return to_utf8(
                        translate(
                            _("Validation failed: degrees is 180; "
                              "minutes must be zero")))
                if seconds != 0:
                    return to_utf8(
                        translate(
                            _("Validation failed: degrees is 180; "
                              "seconds must be zero")))
            if bearing.lower() not in 'ew':
                return to_utf8(
                    translate(_("Validation failed: Bearing must be E/W")))

        return True


validation.register(CoordinateValidator())


class ResultOptionsValueValidator(object):
    """Validator for the subfield "ResultValue" of ResultOptions field
    """

    implements(IValidator)
    name = "result_options_value_validator"

    def __call__(self, value, *args, **kwargs):
        # Result Value must be floatable
        if not api.is_floatable(value):
            return _t(_("Result Value must be a number"))

        # Get all records
        instance = kwargs['instance']
        field_name = kwargs['field'].getName()
        request = instance.REQUEST
        records = request.form.get(field_name)

        # Result values must be unique
        value = api.to_float(value)
        values = map(lambda ro: ro.get("ResultValue"), records)
        values = filter(api.is_floatable, values)
        values = map(api.to_float, values)
        duplicates = filter(lambda val: val == value, values)
        if len(duplicates) > 1:
            return _t(_("Result Value must be unique"))

        return True


validation.register(ResultOptionsValueValidator())


class ResultOptionsTextValidator(object):
    """Validator for the subfield "ResultText" of ResultsOption field
    """

    implements(IValidator)
    name = "result_options_text_validator"

    def __call__(self, value, *args, **kwargs):
        # Result Text is required
        if not value or not value.strip():
            return _t(_("Display Value is required"))

        # Get all records
        instance = kwargs['instance']
        field_name = kwargs['field'].getName()
        request = instance.REQUEST
        records = request.form.get(field_name)

        # Result Text must be unique
        original_texts = map(lambda ro: ro.get("ResultText"), records)
        duplicates = filter(lambda text: text == value, original_texts)
        if len(duplicates) > 1:
            return _t(_("Display Value must be unique"))

        return True


validation.register(ResultOptionsTextValidator())


class RestrictedCategoriesValidator:
    """ Verifies that client Restricted categories include all categories
    required by service dependencies. """

    implements(IValidator)
    name = "restrictedcategoriesvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})

        translate = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')
        # uc = getToolByName(instance, 'uid_catalog')

        failures = []

        for category in value:
            if not category:
                continue
            services = bsc(portal_type="AnalysisService", category_uid=category)
            for service in services:
                service = service.getObject()
                calc = service.getCalculation()
                deps = calc and calc.getDependentServices() or []
                for dep in deps:
                    if dep.getCategoryUID() not in value:
                        title = dep.getCategoryTitle()
                        if title not in failures:
                            failures.append(title)
        if failures:
            msg = _(
                "Validation failed: The selection requires the following "
                "categories to be selected: ${categories}",
                mapping={
                    'categories': safe_unicode(','.join(failures))
                })
            return to_utf8(translate(msg))

        return True


validation.register(RestrictedCategoriesValidator())


class PrePreservationValidator:
    """ Validate PrePreserved Containers.
        User must select a Preservation.
    """
    implements(IValidator)
    name = "container_prepreservation_validator"

    def __call__(self, value, *args, **kwargs):
        # If not prepreserved, no validation required.
        if not value:
            return True

        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        preservation = form.get('Preservation')

        if type(preservation) in (list, tuple):
            preservation = preservation[0]

        if preservation:
            return True

        translate = getToolByName(instance, 'translation_service').translate
        # bsc = getToolByName(instance, 'bika_setup_catalog')

        if not preservation:
            msg = _("Validation failed: PrePreserved containers "
                    "must have a preservation selected.")
            return to_utf8(translate(msg))


validation.register(PrePreservationValidator())


class StandardIDValidator:
    """Matches against regular expression:
       [^A-Za-z\w\d\-\_]
    """

    implements(IValidator)
    name = "standard_id_validator"

    def __call__(self, value, *args, **kwargs):

        regex = r"[^A-Za-z\w\d\-\_]"

        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})

        translate = getToolByName(instance, 'translation_service').translate

        # check the value against all AnalysisService keywords
        if re.findall(regex, value):
            msg = _("Validation failed: keyword contains invalid "
                    "characters")
            return to_utf8(translate(msg))

        return True


validation.register(StandardIDValidator())


def get_record_value(request, uid, keyword, default=None):
    """Returns the value for the keyword and uid from the request"""
    value = request.get(keyword)
    if not value:
        return default
    if not isinstance(value, list):
        return default
    return value[0].get(uid, default) or default


class AnalysisSpecificationsValidator:
    """Min value must be below max value
       Warn min value must be below min value or empty
       Warn max value must above max value or empty
       Percentage value must be between 0 and 100
       Values must be numbers
    """

    implements(IValidator)
    name = "analysisspecs_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        fieldname = kwargs['field'].getName()

        # This value in request prevents running once per subfield value.
        # self.name returns the name of the validator. This allows other
        # subfield validators to be called if defined (eg. in other add-ons)
        key = '{}-{}-{}'.format(self.name, instance.getId(), fieldname)
        if instance.REQUEST.get(key, False):
            return True

        # Walk through all AS UIDs and validate each parameter for that AS
        service_uids = request.get("uids", [])
        for uid in service_uids:
            err_msg = self.validate_service(request, uid)
            if not err_msg:
                continue

            # Validation failed
            service = api.get_object_by_uid(uid)
            title = api.get_title(service)

            err_msg = "{}: {}".format(title, _(err_msg))
            translate = api.get_tool('translation_service').translate
            instance.REQUEST[key] = to_utf8(translate(safe_unicode(err_msg)))
            return instance.REQUEST[key]

        instance.REQUEST[key] = True
        return True

    def validate_service(self, request, uid):
        """Validates the specs values from request for the service uid. Returns
        a non-translated message if the validation failed.
        """
        spec_min = get_record_value(request, uid, "min")
        spec_max = get_record_value(request, uid, "max")
        error = get_record_value(request, uid, "error", "0")
        warn_min = get_record_value(request, uid, "warn_min")
        warn_max = get_record_value(request, uid, "warn_max")

        if not spec_min and not spec_max:
            # Neither min nor max values have been set, dismiss
            return None

        if not api.is_floatable(spec_min):
            return "'Min' value must be numeric"
        if not api.is_floatable(spec_max):
            return "'Max' value must be numeric"
        if api.to_float(spec_min) > api.to_float(spec_max):
            return "'Max' value must be above 'Min' value"
        if not api.is_floatable(error) or 0.0 < api.to_float(error) > 100:
            return "% Error must be between 0 and 100"

        if warn_min:
            if not api.is_floatable(warn_min):
                return "'Warn Min' value must be numeric or empty"
            if api.to_float(warn_min) > api.to_float(spec_min):
                return "'Warn Min' value must be below 'Min' value"

        if warn_max:
            if not api.is_floatable(warn_max):
                return "'Warn Max' value must be numeric or empty"
            if api.to_float(warn_max) < api.to_float(spec_max):
                return "'Warn Max' value must be above 'Max' value"
        return None


validation.register(AnalysisSpecificationsValidator())


class UncertaintiesValidator:
    """Uncertainties may be specified as numeric values or percentages.
    Min value must be below max value.
    Uncertainty must not be < 0.
    """

    implements(IValidator)
    name = "uncertainties_validator"

    def __call__(self, subf_value, *args, **kwargs):

        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        fieldname = kwargs['field'].getName()
        translate = getToolByName(instance, 'translation_service').translate

        # We run through the validator once per form submit, and check all
        # values
        # this value in request prevents running once per subfield value.
        key = instance.id + fieldname
        if instance.REQUEST.get(key, False):
            return True

        for i, value in enumerate(request[fieldname]):

            # Values must be numbers
            try:
                minv = float(value['intercept_min'])
            except ValueError:
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Min values must be numeric")))
                return instance.REQUEST[key]
            try:
                maxv = float(value['intercept_max'])
            except ValueError:
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Max values must be numeric")))
                return instance.REQUEST[key]

            # values may be percentages; the rest of the numeric validation must
            # still pass once the '%' is stripped off.
            err = value['errorvalue']
            perc = False
            if err.endswith('%'):
                perc = True
                err = err[:-1]
            try:
                err = float(err)
            except ValueError:
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Error values must be numeric")))
                return instance.REQUEST[key]

            if perc and (err < 0 or err > 100):
                # Error percentage must be between 0 and 100
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Error percentage must be between 0 "
                          "and 100")))
                return instance.REQUEST[key]

            # Min value must be < max
            if minv > maxv:
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Max values must be greater than Min "
                          "values")))
                return instance.REQUEST[key]

            # Error values must be >-1
            if err < 0:
                instance.REQUEST[key] = to_utf8(
                    translate(
                        _("Validation failed: Error value must be 0 or greater"
                          )))
                return instance.REQUEST[key]

        instance.REQUEST[key] = True
        return True


validation.register(UncertaintiesValidator())


class DurationValidator:
    """Simple stuff - just checking for integer values.
    """

    implements(IValidator)
    name = "duration_validator"

    def __call__(self, value, *args, **kwargs):

        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        fieldname = kwargs['field'].getName()
        translate = getToolByName(instance, 'translation_service').translate

        value = request[fieldname]
        for v in value.values():
            try:
                int(v)
            except:
                return to_utf8(
                    translate(_("Validation failed: Values must be numbers")))
        return True


validation.register(DurationValidator())


class ReferenceValuesValidator:
    """Min value must be below max value
       Percentage value must be between 0 and 100
       Values must be numbers
       Expected values must be between min and max values
    """

    implements(IValidator)
    name = "referencevalues_validator"

    def __call__(self, value, *args, **kwargs):
        request = kwargs.get('REQUEST', {})
        # Retrieve all AS uids
        services = request.get('service', [{}])[0]
        for uid, service_name in services.items():
            err_msg = self.validate_service(request, uid)
            if not err_msg:
                continue

            # Validation failed
            err_msg = "{}: {}".format(_("Validation for '{}' failed"),
                                      _(err_msg))
            err_msg = err_msg.format(service_name)
            translate = api.get_tool('translation_service').translate
            return to_utf8(translate(safe_unicode(err_msg)))

        return True

    def validate_service(self, request, uid):
        """Validates the specs values from request for the service uid. Returns
        a non-translated message if the validation failed."""

        result = get_record_value(request, uid, 'result')
        if not result:
            # No result set for this service, dismiss
            return None

        if not api.is_floatable(result):
            return "Expected result value must be numeric"

        spec_min = get_record_value(request, uid, "min", result)
        spec_max = get_record_value(request, uid, "max", result)
        error = get_record_value(request, uid, "error", "0")
        if not api.is_floatable(spec_min):
            return "'Min' value must be numeric"
        if not api.is_floatable(spec_max):
            return "'Max' value must be numeric"
        if api.to_float(spec_min) > api.to_float(result):
            return "'Min' value must be below the expected result"
        if api.to_float(spec_max) < api.to_float(result):
            return "'Max' value must be above the expected result"
        if not api.is_floatable(error) or 0.0 < api.to_float(error) > 100:
            return "% Error must be between 0 and 100"
        return None

validation.register(ReferenceValuesValidator())


class PercentValidator:
    """ Floatable, >=0, <=100. """

    implements(IValidator)
    name = "percentvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})

        translate = getToolByName(instance, 'translation_service').translate

        try:
            value = float(value)
        except:
            msg = _("Validation failed: percent values must be numbers")
            return to_utf8(translate(msg))

        if value < 0 or value > 100:
            msg = _(
                "Validation failed: percent values must be between 0 and 100")
            return to_utf8(translate(msg))

        return True


validation.register(PercentValidator())


def _toIntList(numstr, acceptX=0):
    """
    Convert ans string to a list removing all invalid characters.
    Receive: a string as a number
    """
    res = []
    # Converting and removing invalid characters
    for i in numstr:
        if i in string.digits and i not in string.letters:
            res.append(int(i))

    # Converting control number into ISBN
    if acceptX and (numstr[-1] in 'Xx'):
        res.append(10)
    return res


def _sumLists(a, b):
    """
    Algorithm to check validity of NBI and NIF.
    Receives string with a umber to validate.
    """
    val = 0
    for i in map(lambda a, b: a * b, a, b):
        val += i
    return val


class NIBvalidator:
    """
    Validates if the introduced NIB is correct.
    """

    implements(IValidator)
    name = "NIBvalidator"

    def __call__(self, value, *args, **kwargs):
        """
        Check the NIB number
        value:: string with NIB.
        """
        instance = kwargs['instance']
        translate = getToolByName(instance, 'translation_service').translate
        LEN_NIB = 21
        table = (73, 17, 89, 38, 62, 45, 53, 15, 50, 5, 49, 34, 81, 76, 27, 90,
                 9, 30, 3)

        # convert to entire numbers list
        nib = _toIntList(value)

        # checking the length of the number
        if len(nib) != LEN_NIB:
            msg = _('Incorrect NIB number: %s' % value)
            return to_utf8(translate(msg))
        # last numbers algorithm validator
        return nib[-2] * 10 + nib[-1] == 98 - _sumLists(table, nib[:-2]) % 97


validation.register(NIBvalidator())


class IBANvalidator:
    """
    Validates if the introduced NIB is correct.
    """

    implements(IValidator)
    name = "IBANvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        translate = getToolByName(instance, 'translation_service').translate

        # remove spaces from formatted
        IBAN = ''.join(c for c in value if c.isalnum())

        IBAN = IBAN[4:] + IBAN[:4]
        country = IBAN[-4:-2]

        if country not in country_dic:
            msg = _('Unknown IBAN country %s' % country)
            return to_utf8(translate(msg))

        length_c, name_c = country_dic[country]

        if len(IBAN) != length_c:
            diff = len(IBAN) - length_c
            msg = _('Wrong IBAN length by %s: %s' %
                    (('short by %i' % -diff)
                     if diff < 0 else ('too long by %i' % diff), value))
            return to_utf8(translate(msg))
        # Validating procedure
        elif int("".join(str(letter_dic[x]) for x in IBAN)) % 97 != 1:
            msg = _('Incorrect IBAN number: %s' % value)
            return to_utf8(translate(msg))

        else:
            # Accepted:
            return True


validation.register(IBANvalidator())

# Utility to check the integrity of an IBAN bank account No.
# based on https://www.daniweb.com/software-development/python/code/382069
# /iban-number-check-refreshed
# Dictionaries - Refer to ISO 7064 mod 97-10
letter_dic = {
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
    "G": 16,
    "H": 17,
    "I": 18,
    "J": 19,
    "K": 20,
    "L": 21,
    "M": 22,
    "N": 23,
    "O": 24,
    "P": 25,
    "Q": 26,
    "R": 27,
    "S": 28,
    "T": 29,
    "U": 30,
    "V": 31,
    "W": 32,
    "X": 33,
    "Y": 34,
    "Z": 35,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9
}

# ISO 3166-1 alpha-2 country code
country_dic = {
    "AL": [28, "Albania"],
    "AD": [24, "Andorra"],
    "AT": [20, "Austria"],
    "BE": [16, "Belgium"],
    "BA": [20, "Bosnia"],
    "BG": [22, "Bulgaria"],
    "HR": [21, "Croatia"],
    "CY": [28, "Cyprus"],
    "CZ": [24, "Czech Republic"],
    "DK": [18, "Denmark"],
    "EE": [20, "Estonia"],
    "FO": [18, "Faroe Islands"],
    "FI": [18, "Finland"],
    "FR": [27, "France"],
    "DE": [22, "Germany"],
    "GI": [23, "Gibraltar"],
    "GR": [27, "Greece"],
    "GL": [18, "Greenland"],
    "HU": [28, "Hungary"],
    "IS": [26, "Iceland"],
    "IE": [22, "Ireland"],
    "IL": [23, "Israel"],
    "IT": [27, "Italy"],
    "LV": [21, "Latvia"],
    "LI": [21, "Liechtenstein"],
    "LT": [20, "Lithuania"],
    "LU": [20, "Luxembourg"],
    "MK": [19, "Macedonia"],
    "MT": [31, "Malta"],
    "MU": [30, "Mauritius"],
    "MC": [27, "Monaco"],
    "ME": [22, "Montenegro"],
    "NL": [18, "Netherlands"],
    "NO": [15, "Northern Ireland"],
    "PO": [28, "Poland"],
    "PT": [25, "Portugal"],
    "RO": [24, "Romania"],
    "SM": [27, "San Marino"],
    "SA": [24, "Saudi Arabia"],
    "RS": [22, "Serbia"],
    "SK": [24, "Slovakia"],
    "SI": [19, "Slovenia"],
    "ES": [24, "Spain"],
    "SE": [24, "Sweden"],
    "CH": [21, "Switzerland"],
    "TR": [26, "Turkey"],
    "TN": [24, "Tunisia"],
    "GB": [22, "United Kingdom"]
}


class SortKeyValidator:
    """ Check for out of range values.
    """

    implements(IValidator)
    name = "SortKeyValidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        translate = getToolByName(instance, 'translation_service').translate
        try:
            value = float(value)
        except:
            msg = _("Validation failed: value must be float")
            return to_utf8(translate(msg))

        if value < 0 or value > 1000:
            msg = _("Validation failed: value must be between 0 and 1000")
            return to_utf8(translate(msg))

        return True


validation.register(SortKeyValidator())


class InlineFieldValidator:
    """ Inline Field Validator

    calls a field function for validation
    """

    implements(IValidator)
    name = "inline_field_validator"

    def __call__(self, value, *args, **kwargs):
        field = kwargs['field']
        request = kwargs['REQUEST']
        instance = kwargs['instance']

        # extract the request values
        data = request.get(field.getName())

        # check if the field contains a callable
        validator = getattr(field, self.name, None)

        # validator is a callable
        if callable(validator):
            return validator(instance, request, field, data)

        # validator is a string, check if the instance has a method with this name
        if type(validator) in types.StringTypes:
            instance_validator = getattr(instance, validator, None)
            if callable(instance_validator):
                return instance_validator(request, field, data)

        return True


validation.register(InlineFieldValidator())


class ReflexRuleValidator:
    """
    - The analysis service have to be related to the method
    """

    implements(IValidator)
    name = "reflexrulevalidator"

    def __call__(self, value, *args, **kwargs):

        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})
        method = instance.getMethod()
        bsc = getToolByName(instance, 'bika_setup_catalog')
        query = {
            'portal_type': 'AnalysisService',
            'method_available_uid': method.UID()
        }
        method_ans_uids = [b.UID for b in bsc(query)]
        rules = instance.getReflexRules()
        error = ''
        pc = getToolByName(instance, 'portal_catalog')
        for rule in rules:
            as_uid = rule.get('analysisservice', '')
            as_brain = pc(
                UID=as_uid,
                portal_type='AnalysisService',
                is_active=True)
            if as_brain[0] and as_brain[0].UID in method_ans_uids:
                pass
            else:
                error += as_brain['title'] + ' '
        if error:
            translate = getToolByName(instance,
                                      'translation_service').translate
            msg = _("The following analysis services don't belong to the"
                    "current method: " + error)
            return to_utf8(translate(msg))
        return True


validation.register(ReflexRuleValidator())


class NoWhiteSpaceValidator:
    """ String, not containing space(s). """

    implements(IValidator)
    name = "no_white_space_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        translate = getToolByName(instance, 'translation_service').translate

        if value and " " in value:
            msg = _("Invalid value: Please enter a value without spaces.")
            return to_utf8(translate(msg))

        return True


validation.register(NoWhiteSpaceValidator())


class ImportValidator(object):
    """Checks if a dotted name can be imported or not
    """
    implements(IValidator)
    name = "importvalidator"

    def __call__(self, mod, **kwargs):

        # some needed tools
        instance = kwargs['instance']
        translate = getToolByName(instance, 'translation_service').translate

        try:
            # noinspection PyUnresolvedReferences
            import importlib
            importlib.import_module(mod)
        except ImportError:
            msg = _("Validation failed: Could not import module '%s'" % mod)
            return to_utf8(translate(msg))

        return True


validation.register(ImportValidator())
