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

from . import ValidatedData, success, fail
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.analysisservice import get_by_keyword
from senaite.core import logger
from senaite.core.i18n import translate
from zope.interface import Invalid
from z3c.form import validator


def no_wildcards_for_interims():
    def validate(data):
        interim_keywords = filter(
            None, map(lambda i: i.get("keyword"), data['interim_fields'] or []))
        keysandwildcards = map(
            lambda k: k.split(".", 1),
            filter(
                lambda k: "." in k,
                re.compile(r"\[([^\]]+)\]").findall(data['formula'])))
        errwilds = [k[1] for k in keysandwildcards if k[0] in interim_keywords]
        if len(errwilds) > 0:
            return fail("no_wildcards_",
                        translate(
                            _(u"no_wildcards__error",
                                default=u"Wildcards for  are not "
                                        u"allowed: ${wildcards}",
                                mapping={"wildcards": ", ".join(errwilds)}))
                        )
        return success(data)
    return validate


def invalid_wildcards_check():
    def validate(data):
        interim_keywords = filter(
            None, map(lambda i: i.get("keyword"), data['interim_fields'] or []))
        keysandwildcards = map(
            lambda k: k.split(".", 1),
            filter(
                lambda k: "." in k,
                re.compile(r"\[([^\]]+)\]").findall(data['formula'])))
        allowedwds = ("LDL", "UDL", "BELOWLDL", "ABOVEUDL",
                      "LOQ", "LLOQ", "BELOWLOQ", "BELOWLLOQ",
                      "ULOQ", "ABOVEULOQ",)
        wildcards = [k[1] for k in keysandwildcards if k[0]
                     not in interim_keywords and k[1] not in allowedwds]
        if len(wildcards) > 0:
            return fail("invalid_wildcards_check",
                        translate(
                            _(u"invalid_wildcards_check_error",
                                default=u"Invalid wildcards "
                                        u"found: ${wildcards}",
                                mapping={"wildcards":  ", ".join(wildcards)}))
                        )
        return success(data)
    return validate


def invalid_keyword():
    def validate(data):
        keywords = re.compile(r"\[([^\.^\]]+)\]").findall(data['formula'])
        interim_keywords = filter(
            None, map(lambda i: i.get("keyword"), data['interim_fields'] or []))
        as_keywords = list(set([k for k in keywords if k not in interim_keywords]))
        services = get_by_keyword(as_keywords)
        if len(as_keywords) != len(services):
            err_keywords = [k for k in as_keywords if k not in [
                s.getKeyword for s in services]]
            return fail("invalid_keyword",
                        translate(
                            _(u"invalid_keyword_error",
                                default=u"AnalysesServices not found "
                                        u"for keywords: ${keywords}",
                                mapping={"keywords": ", ".join(err_keywords)}))
                        )
        return success(data)
    return validate


class FormulaValidator(validator.InvariantsValidator):
    """ Validate keywords in calculation formula entry
    """

    _validators = (
        no_wildcards_for_interims(),
        invalid_wildcards_check(),
        invalid_keyword()
    )

    def validateObject(self, obj):
        errors = super(FormulaValidator, self).validateObject(obj)
        formula = obj.formula if hasattr(obj, 'formula') else ""
        ifields = obj.interim_fields if hasattr(obj, 'interim_fields') else []
        data = dict(formula=formula, interim_fields=ifields)

        try:
            result = ValidatedData(data).run(*self._validators)
        except Exception as err:
            logger.error("ERROR FORMULA VALIDATION CHAIN: {}".format(err))
            errors += (Invalid(translate(_(u"formula_validation_chain_error",
                                           default=u"Validation chain "
                                                   u"internal error: ${error}",
                                           mapping={"error": err}))),)
            return errors

        for err in result['errors'].values():
            errors += (Invalid(err),)

        return errors
