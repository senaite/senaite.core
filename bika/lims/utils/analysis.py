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

import copy
import math

import zope.event
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from archetypes.schemaextender.interfaces import IExtensionField

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import to_unicode


def duplicateAnalysis(analysis):
    """
    Duplicate an analysis consist on creating a new analysis with
    the same analysis service for the same sample. It is used in
    order to reduce the error procedure probability because both
    results must be similar.
    :base: the analysis object used as the creation base.
    """
    ar = analysis.aq_parent
    kw = analysis.getKeyword()
    # Rename the analysis to make way for it's successor.
    # Support multiple duplicates by renaming to *-0, *-1, etc
    cnt = [x for x in ar.objectValues("Analysis") if x.getId().startswith(kw)]
    a_id = "{0}-{1}".format(kw, len(cnt))
    dup = create_analysis(ar, analysis, id=a_id, Retested=True)
    return dup


def copy_analysis_field_values(source, analysis, **kwargs):
    src_schema = source.Schema()
    dst_schema = analysis.Schema()
    # Some fields should not be copied from source!
    # BUT, if these fieldnames are present in kwargs, the value will
    # be set accordingly.
    IGNORE_FIELDNAMES = [
        'UID', 'id', 'allowDiscussion', 'subject', 'location', 'contributors',
        'creators', 'effectiveDate', 'expirationDate', 'language', 'rights',
        'creation_date', 'modification_date', 'IsReflexAnalysis',
        'OriginalReflexedAnalysis', 'ReflexAnalysisOf', 'ReflexRuleAction',
        'ReflexRuleLocalID', 'ReflexRuleActionsTriggered', 'Hidden']
    for field in src_schema.fields():
        fieldname = field.getName()
        if fieldname in IGNORE_FIELDNAMES and fieldname not in kwargs:
            continue
        if fieldname not in dst_schema:
            continue
        value = kwargs.get(fieldname, field.get(source))
        if value:
            # Campbell's mental note:never ever use '.set()' directly to a
            # field. If you can't use the setter, then use the mutator in order
            # to give the value. We have realized that in some cases using
            # 'set' when the value is a string, it saves the value
            # as unicode instead of plain string.
            field = analysis.getField(fieldname)
            if IExtensionField.providedBy(field):
                # SchemaExtender fields don't auto-generate the accessor/mutator
                field.set(analysis, value)
            else:
                mutator_name = field.mutator
                mutator = getattr(analysis, mutator_name)
                mutator(value)


def create_analysis(context, source, **kwargs):
    """Create a new Analysis.  The source can be an Analysis Service or
    an existing Analysis, and all possible field values will be set to the
    values found in the source object.
    :param context: The analysis will be created inside this object.
    :param source: The schema of this object will be used to populate analysis.
    :param kwargs: The values of any keys which match schema fieldnames will
    be inserted into the corresponding fields in the new analysis.
    :returns: Analysis object that was created
    :rtype: Analysis
    """
    an_id = kwargs.get('id', source.getKeyword())
    analysis = _createObjectByType("Analysis", context, an_id)
    copy_analysis_field_values(source, analysis, **kwargs)

    # AnalysisService field is not present on actual AnalysisServices.
    if IAnalysisService.providedBy(source):
        analysis.setAnalysisService(source)
    else:
        analysis.setAnalysisService(source.getAnalysisService())

    # Set the interims from the Service
    service_interims = analysis.getAnalysisService().getInterimFields()
    # Avoid references from the analysis interims to the service interims
    service_interims = copy.deepcopy(service_interims)
    analysis.setInterimFields(service_interims)

    analysis.unmarkCreationFlag()
    zope.event.notify(ObjectInitializedEvent(analysis))
    return analysis

def get_significant_digits(numeric_value):
    """
    Returns the precision for a given floatable value.
    If value is None or not floatable, returns None.
    Will return positive values if the result is below 1 and will
    return 0 values if the result is above or equal to 1.
    :param numeric_value: the value to get the precision from
    :returns: the numeric_value's precision
            Examples:
            numeric_value     Returns
            0               0
            0.22            1
            1.34            0
            0.0021          3
            0.013           2
            2               0
            22              0
    """
    try:
        numeric_value = float(numeric_value)
    except (TypeError, ValueError):
        return None
    if numeric_value == 0:
        return 0
    significant_digit = int(math.floor(math.log10(abs(numeric_value))))
    return 0 if significant_digit > 0 else abs(significant_digit)


def _format_decimal_or_sci(result, precision, threshold, sciformat):
    # Current result's precision is above the threshold?
    sig_digits = get_significant_digits(result)

    # Note that if result < 1, sig_digits > 0. Otherwise, sig_digits = 0
    # Eg:
    #       result = 0.2   -> sig_digit = 1
    #                0.002 -> sig_digit = 3
    #                0     -> sig_digit = 0
    #                2     -> sig_digit = 0
    # See get_significant_digits signature for further details!
    #
    # Also note if threshold is negative, the result will always be expressed
    # in scientific notation:
    # Eg.
    #       result=12345, threshold=-3, sig_digit=0 -> 1.2345e4 = 1.2345·10⁴
    #
    # So, if sig_digits is > 0, the power must be expressed in negative
    # Eg.
    #      result=0.0012345, threshold=3, sig_digit=3 -> 1.2345e-3=1.2345·10-³
    sci = sig_digits >= threshold and abs(
        threshold) > 0 and sig_digits <= precision
    sign = '-' if sig_digits > 0 else ''
    if sig_digits == 0 and abs(threshold) > 0 and abs(int(float(result))) > 0:
        # Number >= 1, need to check if the number of non-decimal
        # positions is above the threshold
        sig_digits = int(math.log(abs(float(result)), 10)) if abs(
            float(result)) >= 10 else 0
        sci = sig_digits >= abs(threshold)

    formatted = ''
    if sci:
        # First, cut the extra decimals according to the precision
        prec = precision if precision and precision > 0 else 0
        nresult = str("%%.%sf" % prec) % result

        if sign:
            # 0.0012345 -> 1.2345
            res = float(nresult) * (10 ** sig_digits)
        else:
            # Non-decimal positions
            # 123.45 -> 1.2345
            res = float(nresult) / (10 ** sig_digits)
        res = int(res) if res.is_integer() else res

        # Scientific notation
        if sciformat == 2:
            # ax10^b or ax10^-b
            formatted = "%s%s%s%s" % (res, "x10^", sign, sig_digits)
        elif sciformat == 3:
            # ax10<super>b</super> or ax10<super>-b</super>
            formatted = "%s%s%s%s%s" % (
                res, "x10<sup>", sign, sig_digits, "</sup>")
        elif sciformat == 4:
            # ax10^b or ax10^-b
            formatted = "%s%s%s%s" % (res, "·10^", sign, sig_digits)
        elif sciformat == 5:
            # ax10<super>b</super> or ax10<super>-b</super>
            formatted = "%s%s%s%s%s" % (
                res, "·10<sup>", sign, sig_digits, "</sup>")
        else:
            # Default format: aE^+b
            sig_digits = "%02d" % sig_digits
            formatted = "%s%s%s%s" % (res, "e", sign, sig_digits)
    else:
        # Decimal notation
        prec = precision if precision and precision > 0 else 0
        formatted = str("%%.%sf" % prec) % result
        if float(formatted) == 0 and '-' in formatted:
            # We don't want things like '-0.00'
            formatted = formatted.replace('-', '')
    return formatted


def format_uncertainty(analysis, result, decimalmark='.', sciformat=1):
    """
    Returns the formatted uncertainty according to the analysis, result
    and decimal mark specified following these rules:

    If the "Calculate precision from uncertainties" is enabled in
    the Analysis service, and

    a) If the the non-decimal number of digits of the result is above
       the service's ExponentialFormatPrecision, the uncertainty will
       be formatted in scientific notation. The uncertainty exponential
       value used will be the same as the one used for the result. The
       uncertainty will be rounded according to the same precision as
       the result.

       Example:
       Given an Analysis with an uncertainty of 37 for a range of
       results between 30000 and 40000, with an
       ExponentialFormatPrecision equal to 4 and a result of 32092,
       this method will return 0.004E+04

    b) If the number of digits of the integer part of the result is
       below the ExponentialFormatPrecision, the uncertainty will be
       formatted as decimal notation and the uncertainty will be
       rounded one position after reaching the last 0 (precision
       calculated according to the uncertainty value).

       Example:
       Given an Analysis with an uncertainty of 0.22 for a range of
       results between 1 and 10 with an ExponentialFormatPrecision
       equal to 4 and a result of 5.234, this method will return 0.2

    If the "Calculate precision from Uncertainties" is disabled in the
    analysis service, the same rules described above applies, but the
    precision used for rounding the uncertainty is not calculated from
    the uncertainty neither the result. The fixed length precision is
    used instead.

    For further details, visit
    https://jira.bikalabs.com/browse/LIMS-1334

    If the result is not floatable or no uncertainty defined, returns
    an empty string.

    The default decimal mark '.' will be replaced by the decimalmark
    specified.

    :param analysis: the analysis from which the uncertainty, precision
                     and other additional info have to be retrieved
    :param result: result of the analysis. Used to retrieve and/or
                   calculate the precision and/or uncertainty
    :param decimalmark: decimal mark to use. By default '.'
    :param sciformat: 1. The sci notation has to be formatted as aE^+b
                  2. The sci notation has to be formatted as ax10^b
                  3. As 2, but with super html entity for exp
                  4. The sci notation has to be formatted as a·10^b
                  5. As 4, but with super html entity for exp
                  By default 1
    :returns: the formatted uncertainty
    """
    try:
        result = float(result)
    except ValueError:
        return ""

    objres = None
    try:
        objres = float(analysis.getResult())
    except ValueError:
        pass

    if result == objres:
        # To avoid problems with DLs
        uncertainty = analysis.getUncertainty()
    else:
        uncertainty = analysis.getUncertainty(result)

    if uncertainty is None or uncertainty == 0:
        return ""

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = analysis.getExponentialFormatPrecision()
    precision = analysis.getPrecision(result)
    formatted = _format_decimal_or_sci(uncertainty, precision, threshold,
                                       sciformat)
    return formatDecimalMark(formatted, decimalmark)


def format_numeric_result(analysis, result, decimalmark='.', sciformat=1):
    """
    Returns the formatted number part of a results value.  This is
    responsible for deciding the precision, and notation of numeric
    values in accordance to the uncertainty. If a non-numeric
    result value is given, the value will be returned unchanged.

    The following rules apply:

    If the "Calculate precision from uncertainties" is enabled in
    the Analysis service, and

    a) If the non-decimal number of digits of the result is above
       the service's ExponentialFormatPrecision, the result will
       be formatted in scientific notation.

       Example:
       Given an Analysis with an uncertainty of 37 for a range of
       results between 30000 and 40000, with an
       ExponentialFormatPrecision equal to 4 and a result of 32092,
       this method will return 3.2092E+04

    b) If the number of digits of the integer part of the result is
       below the ExponentialFormatPrecision, the result will be
       formatted as decimal notation and the resulta will be rounded
       in accordance to the precision (calculated from the uncertainty)

       Example:
       Given an Analysis with an uncertainty of 0.22 for a range of
       results between 1 and 10 with an ExponentialFormatPrecision
       equal to 4 and a result of 5.234, this method will return 5.2

    If the "Calculate precision from Uncertainties" is disabled in the
    analysis service, the same rules described above applies, but the
    precision used for rounding the result is not calculated from
    the uncertainty. The fixed length precision is used instead.

    For further details, visit
    https://jira.bikalabs.com/browse/LIMS-1334

    The default decimal mark '.' will be replaced by the decimalmark
    specified.

    :param analysis: the analysis from which the uncertainty, precision
                     and other additional info have to be retrieved
    :param result: result to be formatted.
    :param decimalmark: decimal mark to use. By default '.'
    :param sciformat: 1. The sci notation has to be formatted as aE^+b
                      2. The sci notation has to be formatted as ax10^b
                      3. As 2, but with super html entity for exp
                      4. The sci notation has to be formatted as a·10^b
                      5. As 4, but with super html entity for exp
                      By default 1
    :result: should be a string to preserve the decimal precision.
    :returns: the formatted result as string
    """
    try:
        result = float(result)
    except ValueError:
        return result

    # continuing with 'nan' result will cause formatting to fail.
    if math.isnan(result):
        return result

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = analysis.getExponentialFormatPrecision()
    precision = analysis.getPrecision(result)
    formatted = _format_decimal_or_sci(result, precision, threshold, sciformat)
    return formatDecimalMark(formatted, decimalmark)


def get_method_instrument_constraints(context, uids):
    """
        Returns a dictionary with the constraints and rules for
        methods, instruments and results to be applied to each of the
        analyses specified in the param uids (an array of uids).
        See docs/imm_results_entry_behaviour.png for further details
    """
    constraints = {}
    uc = getToolByName(context, 'uid_catalog')
    analyses = uc(portal_type=['Analysis', 'ReferenceAnalysis'],
                  UID=uids)
    cached_servs = {}
    for analysis in analyses:
        if not analysis:
            continue
        analysis = analysis.getObject()
        auid = analysis.UID()
        suid = analysis.getServiceUID()
        refan = analysis.portal_type == 'ReferenceAnalysis'
        cachedkey = "qc" if refan else "re"
        if suid in cached_servs.get(cachedkey, []):
            constraints[auid] = cached_servs[cachedkey][suid]
            continue

        if not cached_servs.get(cachedkey, None):
            cached_servs[cachedkey] = {suid: {}}
        else:
            cached_servs[cachedkey][suid] = {}
        constraints[auid] = {}

        allowed_instruments = analysis.getAllowedInstruments()

        # Analysis allows manual/instrument entry?
        s_mentry = analysis.getManualEntryOfResults()
        s_ientry = analysis.getInstrumentEntryOfResults()
        s_instrums = allowed_instruments if s_ientry else []
        s_instrums = [instr.UID() for instr in s_instrums]
        a_dinstrum = analysis.getInstrument() if s_ientry else None
        s_methods = analysis.getAllowedMethods()
        s_dmethod = analysis.getMethod()
        dmuid = s_dmethod.UID() if s_dmethod else ''
        diuid = a_dinstrum.UID() if a_dinstrum else ''

        # To take into account ASs with no method assigned by default or
        # ASs that have an instrument assigned by default that doesn't have
        # a method associated.
        if s_mentry or not s_dmethod:
            s_methods += [None]

        for method in s_methods:
            # Method manual entry?
            m_mentry = method.isManualEntryOfResults() if method else True

            instrs = []
            if method:
                # Instruments available for this method and analysis?
                instrs = [i for i in method.getInstruments()
                          if i.UID() in s_instrums]
            else:
                # What about instruments without a method assigned?
                instrs = [i for i in allowed_instruments
                          if i.UID() in s_instrums and not i.getMethods()]

            instuids = [i.UID() for i in instrs]
            v_instrobjs = [i for i in instrs if i.isValid()]
            v_instrs = [i.UID() for i in v_instrobjs]
            muid = method.UID() if method else ''

            # PREMISES
            # p1: Analysis allows manual entry?
            # p2: Analysis allows instrument entry?
            # p3: Method selected and non empty?
            # p4: Method allows manual entry?
            # p5: At least one instrument available for this method?
            # p6: Valid instruments available?
            # p7: All instruments valid?
            # p8: Methods allow the service's default instrument?
            # p9: Default instrument valid?
            premises = [
                "R" if not refan else 'Q',
                "Y" if s_mentry else "N",
                "Y" if s_ientry else "N",
                "Y" if method else "N",
                "Y" if m_mentry else "N",
                "Y" if instrs else "N",
                "Y" if v_instrs or not instrs else "N",
                "Y" if len(v_instrs) == len(instrs) else "N",
                "Y" if diuid in instuids else "N",
                "Y" if a_dinstrum and a_dinstrum.isValid() else "N",
            ]
            tprem = ''.join(premises)

            fiuid = v_instrs[0] if v_instrs else ''
            instrtitle = to_unicode(a_dinstrum.Title()) if a_dinstrum else ''
            iinstrs = ', '.join([to_unicode(i.Title()) for i in instrs
                                 if i.UID() not in v_instrs])
            dmeth = to_unicode(method.Title()) if method else ''
            m1 = _("Invalid instruments are not displayed: %s") % iinstrs
            m2 = _("Default instrument %s is not valid") % instrtitle
            m3 = _("No valid instruments available: %s ") % iinstrs
            m4 = _("Manual entry of results for method %s is not allowed "
                   "and no valid instruments found: %s") % (dmeth, iinstrs)
            m5 = _("The method %s is not valid: no manual entry allowed "
                   "and no instrument assigned") % dmeth
            m6 = _("The method %s is not valid: only instrument entry for "
                   "this analysis is allowed, but the method has no "
                   "instrument assigned") % dmeth
            m7 = _("Only instrument entry for this analysis is allowed, "
                   "but there is no instrument assigned")

            """
            Matrix dict keys char positions: (True: Y, False: N)
              0: (R)egular analysis or (Q)C analysis
              1: Analysis allows manual entry?
              2: Analysis allows instrument entry?
              3: Method is not None?
              4: Method allows manual entry?
              5: At least one instrument avialable for the method?
              6: Valid instruments available?
              7: All instruments valid?
              8: Method allows the service's default instrument?
              9: Default instrument valid?

            Matrix dict values array indexes:
              0: Method list visible? YES:1, NO:0, YES(a):2, YES(r):3
              1: Add "None" in methods list? YES:1, NO:0, NO(g):2
              2: Instr. list visible? YES:1, NO:0
              3: Add "None" in instrums list? YES: 1, NO:0
              4: UID of the selected instrument or '' if None
              5: Results field editable? YES: 1, NO:0
              6: Alert message string

            See docs/imm_results_entry_behaviour.png for further details
            """
            matrix = {
                # Regular analyses
                'RYYYYYYYY': [1, 1, 1, 1, diuid, 1, ''],  # B1
                'RYYYYYYYN': [1, 1, 1, 1, '', 1, ''],  # B2
                'RYYYYYYNYY': [1, 1, 1, 1, diuid, 1, m1],  # B3
                'RYYYYYYNYN': [1, 1, 1, 1, '', 1, m2],  # B4
                'RYYYYYYNN': [1, 1, 1, 1, '', 1, m1],  # B5
                'RYYYYYN': [1, 1, 1, 1, '', 1, m3],  # B6
                'RYYYYN': [1, 1, 1, 1, '', 1, ''],  # B7
                'RYYYNYYYY': [1, 1, 1, 0, diuid, 1, ''],  # B8
                'RYYYNYYYN': [1, 1, 1, 0, fiuid, 1, ''],  # B9
                'RYYYNYYNYY': [1, 1, 1, 0, diuid, 1, m1],  # B10
                'RYYYNYYNYN': [1, 1, 1, 1, '', 0, m2],  # B11
                'RYYYNYYNN': [1, 1, 1, 0, fiuid, 1, m1],  # B12
                'RYYYNYN': [1, 1, 1, 1, '', 0, m4],  # B13
                'RYYYNN': [1, 1, 1, 1, '', 0, m5],  # B14
                'RYYNYYYYY': [1, 1, 1, 1, diuid, 1, ''],  # B15
                'RYYNYYYYN': [1, 1, 1, 1, '', 1, ''],  # B16
                'RYYNYYYNYY': [1, 1, 1, 1, diuid, 1, m1],  # B17
                'RYYNYYYNYN': [1, 1, 1, 1, '', 1, m2],  # B18
                'RYYNYYYNN': [1, 1, 1, 1, '', 1, m1],  # B19
                'RYYNYYN': [1, 1, 1, 1, '', 1, m3],  # B20
                'RYYNYN': [1, 1, 1, 1, '', 1, ''],  # B21
                'RYNY': [2, 0, 0, 0, '', 1, ''],  # B22
                'RYNN': [0, 0, 0, 0, '', 1, ''],  # B23
                'RNYYYYYYY': [3, 2, 1, 1, diuid, 1, ''],  # B24
                'RNYYYYYYN': [3, 2, 1, 1, '', 1, ''],  # B25
                'RNYYYYYNYY': [3, 2, 1, 1, diuid, 1, m1],  # B26
                'RNYYYYYNYN': [3, 2, 1, 1, '', 1, m2],  # B27
                'RNYYYYYNN': [3, 2, 1, 1, '', 1, m1],  # B28
                'RNYYYYN': [3, 2, 1, 1, '', 1, m3],  # B29
                'RNYYYN': [3, 2, 1, 1, '', 0, m6],  # B30
                'RNYYNYYYY': [3, 2, 1, 0, diuid, 1, ''],  # B31
                'RNYYNYYYN': [3, 2, 1, 0, fiuid, 1, ''],  # B32
                'RNYYNYYNYY': [3, 2, 1, 0, diuid, 1, m1],  # B33
                'RNYYNYYNYN': [3, 2, 1, 1, '', 0, m2],  # B34
                'RNYYNYYNN': [3, 2, 1, 0, fiuid, 1, m1],  # B35
                'RNYYNYN': [3, 2, 1, 1, '', 0, m3],  # B36
                'RNYYNN': [3, 2, 1, 1, '', 0, m6],  # B37
                'RNYNYYYYY': [3, 1, 1, 0, diuid, 1, ''],  # B38
                'RNYNYYYYN': [3, 1, 1, 0, fiuid, 1, ''],  # B39
                'RNYNYYYNYY': [3, 1, 1, 0, diuid, 1, m1],  # B40
                'RNYNYYYNYN': [3, 1, 1, 1, '', 0, m2],  # B41
                'RNYNYYYNN': [3, 1, 1, 0, fiuid, 1, m1],  # B42
                'RNYNYYN': [3, 1, 1, 0, '', 0, m3],  # B43
                'RNYNYN': [3, 1, 1, 0, '', 0, m7],  # B44
                # QC Analyses
                'QYYYYYYYY': [1, 1, 1, 1, diuid, 1, ''],  # C1
                'QYYYYYYYN': [1, 1, 1, 1, '', 1, ''],  # C2
                'QYYYYYYNYY': [1, 1, 1, 1, diuid, 1, ''],  # C3
                'QYYYYYYNYN': [1, 1, 1, 1, diuid, 1, ''],  # C4
                'QYYYYYYNN': [1, 1, 1, 1, '', 1, ''],  # C5
                'QYYYYYN': [1, 1, 1, 1, '', 1, ''],  # C6
                'QYYYYN': [1, 1, 1, 1, '', 1, ''],  # C7
                'QYYYNYYYY': [1, 1, 1, 0, diuid, 1, ''],  # C8
                'QYYYNYYYN': [1, 1, 1, 0, fiuid, 1, ''],  # C9
                'QYYYNYYNYY': [1, 1, 1, 0, diuid, 1, ''],  # C10
                'QYYYNYYNYN': [1, 1, 1, 0, diuid, 1, ''],  # C11
                'QYYYNYYNN': [1, 1, 1, 0, fiuid, 1, ''],  # C12
                'QYYYNYN': [1, 1, 1, 0, fiuid, 1, ''],  # C13
                'QYYYNN': [1, 1, 1, 1, '', 0, m5],  # C14
                'QYYNYYYYY': [1, 1, 1, 1, diuid, 1, ''],  # C15
                'QYYNYYYYN': [1, 1, 1, 1, '', 1, ''],  # C16
                'QYYNYYYNYY': [1, 1, 1, 1, diuid, 1, ''],  # C17
                'QYYNYYYNYN': [1, 1, 1, 1, diuid, 1, ''],  # C18
                'QYYNYYYNN': [1, 1, 1, 1, fiuid, 1, ''],  # C19
                'QYYNYYN': [1, 1, 1, 1, diuid, 1, ''],  # C20
                'QYYNYN': [1, 1, 1, 1, '', 1, ''],  # C21
                'QYNY': [2, 0, 0, 0, '', 1, ''],  # C22
                'QYNN': [0, 0, 0, 0, '', 1, ''],  # C23
                'QNYYYYYYY': [3, 2, 1, 1, diuid, 1, ''],  # C24
                'QNYYYYYYN': [3, 2, 1, 1, '', 1, ''],  # C25
                'QNYYYYYNYY': [3, 2, 1, 1, diuid, 1, ''],  # C26
                'QNYYYYYNYN': [3, 2, 1, 1, diuid, 1, ''],  # C27
                'QNYYYYYNN': [3, 2, 1, 1, '', 1, ''],  # C28
                'QNYYYYN': [3, 2, 1, 1, '', 1, ''],  # C29
                'QNYYYN': [3, 2, 1, 1, '', 0, m6],  # C30
                'QNYYNYYYY': [3, 2, 1, 0, diuid, 1, ''],  # C31
                'QNYYNYYYN': [3, 2, 1, 0, fiuid, 1, ''],  # C32
                'QNYYNYYNYY': [3, 2, 1, 0, diuid, 1, ''],  # C33
                'QNYYNYYNYN': [3, 2, 1, 0, diuid, 1, ''],  # C34
                'QNYYNYYNN': [3, 2, 1, 0, fiuid, 1, ''],  # C35
                'QNYYNYN': [3, 2, 1, 0, fiuid, 1, ''],  # C36
                'QNYYNN': [3, 2, 1, 1, '', 0, m5],  # C37
                'QNYNYYYYY': [3, 1, 1, 0, diuid, 1, ''],  # C38
                'QNYNYYYYN': [3, 1, 1, 0, fiuid, 1, ''],  # C39
                'QNYNYYYNYY': [3, 1, 1, 0, diuid, 1, ''],  # C40
                'QNYNYYYNYN': [3, 1, 1, 0, diuid, 1, ''],  # C41
                'QNYNYYYNN': [3, 1, 1, 0, fiuid, 1, ''],  # C42
                'QNYNYYN': [3, 1, 1, 0, fiuid, 1, ''],  # C43
                'QNYNYN': [3, 1, 1, 1, '', 0, m7],  # C44
            }
            targ = [v for k, v in matrix.items() if tprem.startswith(k)]
            if not targ:
                targ = [[1, 1, 1, 1, '', 0, 'Key not found: %s' % tprem], ]
            targ = targ[0]
            atitle = analysis.Title() if analysis else "None"
            mtitle = method.Title() if method else "None"
            instdi = {}
            if refan and instrs:
                instdi = {i.UID(): i.Title() for i in instrs}
            elif not refan and v_instrobjs:
                instdi = {i.UID(): i.Title() for i in v_instrobjs}
            targ += [instdi, mtitle, atitle, tprem]
            constraints[auid][muid] = targ
            cached_servs[cachedkey][suid][muid] = targ
    return constraints


def create_retest(analysis):
    """Creates a retest of the given analysis
    """
    if not IRequestAnalysis.providedBy(analysis):
        raise ValueError("Type not supported: {}".format(repr(type(analysis))))

    # Support multiple retests by prefixing keyword with *-0, *-1, etc.
    parent = api.get_parent(analysis)
    keyword = analysis.getKeyword()

    # Get only those analyses with same keyword as original
    analyses = parent.getAnalyses(full_objects=True)
    analyses = filter(lambda an: an.getKeyword() == keyword, analyses)
    new_id = '{}-{}'.format(keyword, len(analyses))

    # Create a copy of the original analysis
    an_uid = api.get_uid(analysis)
    retest = create_analysis(parent, analysis, id=new_id, RetestOf=an_uid)
    retest.setResult("")
    retest.setResultCaptureDate(None)

    # Add the retest to the same worksheet, if any
    worksheet = analysis.getWorksheet()
    if worksheet:
        worksheet.addAnalysis(retest)

    retest.reindexObject()
    return retest
