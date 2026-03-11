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

import re
import six
from functools import partial

from . import ValidatedData, success, fail, flatten_dict
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.analysisservice import get_by_keyword
from senaite.core import logger
from senaite.core.i18n import translate
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import Invalid
from z3c.form.error import ErrorViewSnippet
from z3c.form.error import MultipleErrorViewSnippet
from z3c.form.error import MultipleErrors
from z3c.form import validator


TYPES_WITH_CHOICES = (
    "select",
    "multiselect",
    "multiselect_duplicates",
    "multichoice",
)


def non_blank_validator():
    """ check the field value is a string and non-zero length
    """
    def validate(field):
        k, v = next(iter(field.items()))
        if not isinstance(v, six.string_types) or len(v) == 0:
            return fail("non_blank_validator",
                        translate(_(u"non_blank_validator_error",
                                    default=u"'${field_name}' is required",
                                    mapping={"field_name": k}))
                        )
        return success(field)
    return validate


def invalid_characters_validator():
    def validate(field):
        k, v = next(iter(field.items()))
        if v and not re.match(r"^[A-Za-z\w\d\-\_]+$", v):
            return fail("invalid_characters_validator",
                        translate(
                            _(u"invalid_characters_validator_error",
                                default=u"'${field_name}' "
                                        u"contains invalid characters",
                                mapping={"field_name": k}))
                        )
        return success(field)
    return validate


def no_dup_value_validator(rows):
    def validate(field):
        k, v = next(iter(field.items()))
        dups = filter(lambda r: r[k] == v, rows)
        if len(dups) > 1:
            return fail("no_dups_values_validator",
                        translate(_(u"no_dups_values_validator_error",
                                    default=u"'${duplicate}' duplicates found",
                                    mapping={"duplicate": k}))
                        )
        return success(field)
    return validate


def no_dup_service_keyword_validator(services):
    def validate(field):
        k, v = next(iter(field.items()))
        dups = filter(lambda s: s.getKeyword == v, services)
        if len(dups) > 0:
            return fail("no_dup_service_keyword_validator",
                        translate(_(u"no_dup_service_keyword_validator_error",
                                    default=u"Keyword '${duplicate}' duplicate found for a Analysis Service",
                                    mapping={"duplicate": v}))
                        )
        return success(field)
    return validate


def choices_and_restype_validator():
    def validate(row):
        r_type = row.get("result_type", "")
        choices = row.get("choices")
        if not choices and r_type in TYPES_WITH_CHOICES:
            return fail("choices_and_restype_validator",
                        translate(_(
                            u"choices_and_restype_validator_no_choices_error",
                            default=u"Control type is not supported for empty choices"))
                        )
        if choices and r_type not in TYPES_WITH_CHOICES:
            return fail("choices_and_restype_validator",
                        translate(_(
                            u"choices_and_restype_validator_not_supported_choices_error",
                            default=u"Chosen control type not supporting choices"))
                        )
        return success(row)
    return validate


def calcs_interims_validator(calcs):
    """Validate interim field keywords against other active calculations.

    A keyword used in multiple calculations must have the same column title
    in all of them, since it identifies a shared interim value.

    Deactivated calculations and the calculation being edited are excluded.
    """
    def validate(row):
        keyword = api.safe_unicode(row.get("keyword", ""))
        title = api.safe_unicode(row.get("title"))
        dup_keyword_title = None
        dup_calc_title = None
        for calc in calcs:
            for i in calc.getInterimFields():
                int_keyword = api.safe_unicode(i.get("keyword", ""))
                int_title = api.safe_unicode(i.get("title", ""))
                if int_keyword == keyword and int_title != title:
                    dup_keyword_title = int_title
                    dup_calc_title = api.safe_unicode(api.get_title(calc))
                    break
            else:
                continue
            break
        if dup_keyword_title:
            return fail("calcs_interims_validator",
                        translate(_(
                            u"calcs_interims_validator_dup_keyword_error",
                            default=u"keyword '${keyword}' must have column title '${title}' (defined in '${calc}')",
                            mapping={
                                "keyword": keyword,
                                "title": dup_keyword_title,
                                "calc": dup_calc_title}))
                        )
        return success(row)
    return validate


def choices_empty_keys_validator():
    def validate(choices):
        keys = map(lambda k: k.strip(), choices.keys())
        empties = filter(None, keys)
        if choices and len(empties) != len(keys):
            return fail("choices_empty_keys_validator",
                        translate(_(
                            u"choices_empty_keys_validator_error",
                            default=u"Empty keys are not supported"))
                        )
        return success(choices)
    return validate


def choices_unique_keys_validator():
    def validate(choices):
        keys = map(lambda k: k.strip(), choices.keys())
        unique_keys = list(set(keys))
        if choices and len(unique_keys) != len(keys):
            return fail("choices_unique_keys_validator",
                        translate(_(
                            u"choices_unique_keys_validator_error",
                            default=u"Duplicate keys in choices field")))
        return success(choices)
    return validate


def choices_min_items_validator():
    def validate(choices):
        keys = map(lambda k: k.strip(), choices.keys())
        if choices and len(keys) < 2:
            return fail("choices_min_items_validator",
                        translate(_(
                            u"choices_min_items_validator_error",
                            default=u"At least, two options for choices field are required"))
                        )
        return success(choices)
    return validate


def choices_syntax_validator():
    def validate(field):
        k, v = next(iter(field.items()))
        choices = v.split("|") if v else []
        try:
            choices = dict(
                map(lambda ch: map(str.strip, str(ch).split(":")), choices))
        except ValueError:
            return fail(k, translate(_(u"choice_syntax_validation_error",
                                       default=u"No valid format in choices field. Supported format is: "
                                       "<value-0>:<text>|<value-1>:<text>|<value-n>:<text>")))
        choices_nested_validators = [
            choices_empty_keys_validator(),
            choices_unique_keys_validator(),
            choices_min_items_validator()
        ]
        result = ValidatedData(choices).run(*choices_nested_validators)
        if len(result['errors']) > 0:
            return fail('choices', result['errors'])
        return success(field)
    return validate


def field_wrapper(field_name, validators):
    def validate(row):
        result = ValidatedData(
            {field_name: row.get(field_name)}).run(*validators)
        if len(result['errors']) > 0:
            return fail(field_name, result['errors'])
        return success(row)
    return validate


def row_wrapper(row_idx, validators):
    def validate(data):
        result = ValidatedData(data[row_idx]).run(*validators)
        if len(result['errors']) > 0:
            return fail(row_idx, result['errors'])
        return success(data)
    return validate


class InterimFieldsValidator(validator.SimpleFieldValidator):

    def validate(self, value):

        data = {str(idx): dict({'row_idx': idx}, **v)
                for idx, v in enumerate(value or [], start=1)}
        rows = data.values()
        services = get_by_keyword([v['keyword'] for v in rows])
        ctx_uid = api.get_uid(self.context)
        calcs = [api.get_object(c) for c in api.search(
            {"portal_type": "Calculation", "is_active": True},
            SETUP_CATALOG) if c.UID != ctx_uid]

        _validators = [
            field_wrapper('keyword',
                          [
                              non_blank_validator(),
                              invalid_characters_validator(),
                              no_dup_value_validator(rows),
                              no_dup_service_keyword_validator(services),
                          ]),
            field_wrapper('title', [non_blank_validator(),
                          no_dup_value_validator(rows)]),
            calcs_interims_validator(calcs),
            choices_and_restype_validator(),
            field_wrapper('choices', [choices_syntax_validator()])
        ]
        row_validators = [row_wrapper(k, _validators)
                          for k in data.keys()]
        try:
            result = ValidatedData(data).run(*row_validators)
        except Exception as err:
            logger.error("ERROR INTERIMS VALIDATION CHAIN: {}".format(err))
            raise Invalid(translate(_(u"interims_validation_chain_error",
                                      default=u"Validation chain internal error: ${error}",
                                      mapping={"error": err})))
        errors = {k: flatten_dict(v) for k, v in result['errors'].items() if v}
        if errors:
            # TODO: when ZOPE version will reach 5.0 replace w/ MultipleInvalid
            # - no special Error views required then
            # https://github.com/zopefoundation/zope.interface/blob/7e0be48d15c594cc592537da2da98311017b19ab/src/zope/interface/exceptions.py#L235C7-L235C22
            errors_list = []
            for k, v in errors.items():
                for val_name, error_message in v.items():
                    errors_list.append((k, val_name, error_message))
            raise MultipleErrors(sorted(errors_list, key=lambda e: e[0]))


class InterimErrorViewSnippet(ErrorViewSnippet):

    def __init__(self, error, request, widget, field, form, content):
        super(InterimErrorViewSnippet, self).__init__(
            error, request, widget, field, form, content)
        self.message = translate(
            _(u"interim_field_error",
              default=u"Interim field ${row_num}: ${message}",
              mapping={
                  "row_num": self.content[0],
                  "message": api.safe_unicode(self.content[2])
              }))

    def update(self):
        pass


class InterimFieldsValidationErrorView(MultipleErrorViewSnippet):

    def __init__(self, error, request, widget, field, form, content):
        super(InterimFieldsValidationErrorView, self).__init__(
            error, request, widget, field, form, content)
        err_snippet = partial(InterimErrorViewSnippet,
                              error, request, widget, field, form)
        self.error.errors = (err_snippet(err) for err in self.error.errors)
