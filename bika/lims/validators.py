from Acquisition import aq_parent
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

import re


class IdentifierTypeAttributesValidator:
    """Validate IdentifierTypeAttributes to ensure that attributes are
    not duplicated.
    """

    implements(IValidator)
    name = "identifiertypeattributesvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        bsc = getToolByName(instance, "bika_setup_catalog")
        translate = getToolByName(instance, 'translation_service').translate
        request = instance.REQUEST
        form = request.get('form', {})
        fieldname = kwargs['field'].getName()
        form_value = form.get(fieldname, False)
        if form_value == False:
            # not required...
            return True
        if value == instance.get(fieldname):
            # no change.
            return True

        import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()

        return True


validation.register(IdentifierTypeAttributesValidator())


class IdentifierValidator:
    """some actual validation should go here.
    I'm leaving this stub registered, but adding no extra validation
    until someone asks me to do so.
    """

    implements(IValidator)
    name = "identifiervalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        bsc = getToolByName(instance, "bika_setup_catalog")
        translate = getToolByName(instance, 'translation_service').translate
        request = instance.REQUEST
        form = request.get('form', {})
        fieldname = kwargs['field'].getName()
        form_value = form.get(fieldname, False)
        if form_value == False:
            # not required...
            return True
        if value == instance.get(fieldname):
            # no change.
            return True

        return True

validation.register(IdentifierValidator())


class UniqueFieldValidator:
    """ Verifies that a field value is unique for items
    if the same type in this location """

    implements(IValidator)
    name = "uniquefieldvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        # request = kwargs.get('REQUEST', {})
        # form = request.get('form', {})

        translate = getToolByName(instance, 'translation_service').translate

        if value == instance.get(fieldname):
            return True

        for item in aq_parent(instance).objectValues():
            if hasattr(item, 'UID') and item.UID() != instance.UID() and \
                            item.schema.get(fieldname).getAccessor(
                                    item)() == value:
                msg = _("Validation failed: '${value}' is not unique",
                        mapping={'value': safe_unicode(value)})
                return to_utf8(translate(msg))
        return True


validation.register(UniqueFieldValidator())


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
                msg = _("Validation failed: '${title}': This keyword "
                        "is already in use by service '${used_by}'",
                        mapping={'title': safe_unicode(value),
                                 'used_by': safe_unicode(service.Title)})
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
                    msg = _("Validation failed: '${title}': This keyword "
                            "is already in use by calculation '${used_by}'",
                            mapping={'title': safe_unicode(value),
                                     'used_by': safe_unicode(calc.Title())})
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

        # We run through the validator once per form submit, and check all values
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
            msg = _("Validation failed: '${keyword}': duplicate keyword",
                    mapping={'keyword': safe_unicode(k)})
            instance.REQUEST[key] = to_utf8(translate(msg))
            return instance.REQUEST[key]
        for t in [t for t in titles.keys() if titles[t] > 1]:
            msg = _("Validation failed: '${title}': duplicate title",
                    mapping={'title': safe_unicode(t)})
            instance.REQUEST[key] = to_utf8(translate(msg))
            return instance.REQUEST[key]

        # check all keywords against all AnalysisService keywords for dups
        services = bsc(portal_type='AnalysisService', getKeyword=value)
        if services:
            msg = _("Validation failed: '${title}': "
                    "This keyword is already in use by service '${used_by}'",
                    mapping={'title': safe_unicode(value),
                             'used_by': safe_unicode(services[0].Title)})
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
                msg = _("Validation failed: column title '${title}' "
                        "must have keyword '${keyword}'",
                        mapping={'title': safe_unicode(field['title']),
                                 'keyword': safe_unicode(
                                     title_keywords[field['title']])})
                instance.REQUEST[key] = to_utf8(translate(msg))
                return instance.REQUEST[key]
            if 'keyword' in field and \
                            field['keyword'] in keyword_titles.keys() and \
                            keyword_titles[field['keyword']] != field['title']:
                msg = _("Validation failed: keyword '${keyword}' "
                        "must have column title '${title}'",
                        mapping={'keyword': safe_unicode(field['keyword']),
                                 'title': safe_unicode(
                                     keyword_titles[field['keyword']])})
                instance.REQUEST[key] = to_utf8(translate(msg))
                return instance.REQUEST[key]

        instance.REQUEST[key] = True
        return True


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
        keywords = re.compile(r"\[([^\]]+)\]").findall(value)

        for keyword in keywords:
            # Check if the service keyword exists and is active.
            dep_service = bsc(getKeyword=keyword, inactive_state="active")
            if not dep_service and \
                    not keyword in interim_keywords:
                msg = _("Validation failed: Keyword '${keyword}' is invalid",
                        mapping={'keyword': safe_unicode(keyword)})
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
                        translate(_("Validation failed: degrees is 90; "
                                    "minutes must be zero")))
                if seconds != 0:
                    return to_utf8(
                        translate(_("Validation failed: degrees is 90; "
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
                        translate(_("Validation failed: degrees is 180; "
                                    "minutes must be zero")))
                if seconds != 0:
                    return to_utf8(
                        translate(_("Validation failed: degrees is 180; "
                                    "seconds must be zero")))
            if bearing.lower() not in 'ew':
                return to_utf8(
                    translate(_("Validation failed: Bearing must be E/W")))

        return True


validation.register(CoordinateValidator())


class ResultOptionsValidator:
    """Validating AnalysisService ResultOptions field.
        XXX Applied as a subfield validator but validates
        for x in range(len(interim_fields)):
            row = interim_fields[x]
            keys = row.keys()
            if 'title' not in keys:entire field.
    """

    implements(IValidator)
    name = "resultoptionsvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        form_value = form.get(fieldname)

        translate = getToolByName(instance, 'translation_service').translate
        # bsc = getToolByName(instance, 'bika_setup_catalog')

        # ResultValue must always be a number
        for field in form_value:
            try:
                float(field['ResultValue'])
            except:
                return to_utf8(translate(_("Validation failed: "
                                           "Result Values must be numbers")))
            if 'ResultText' not in field:
                return to_utf8(translate(
                    _("Validation failed: Result Text cannot be blank")))

        return True


validation.register(ResultOptionsValidator())


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
            services = bsc(portal_type="AnalysisService",
                           getCategoryUID=category)
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
            msg = _("Validation failed: The selection requires the following "
                    "categories to be selected: ${categories}",
                    mapping={'categories': safe_unicode(','.join(failures))})
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


class AnalysisSpecificationsValidator:
    """Min value must be below max value
       Percentage value must be between 0 and 100
       Values must be numbers
    """

    implements(IValidator)
    name = "analysisspecs_validator"

    def __call__(self, value, *args, **kwargs):

        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        fieldname = kwargs['field'].getName()

        translate = getToolByName(instance, 'translation_service').translate

        mins = request.get('min', {})[0]
        maxs = request.get('max', {})[0]
        errors = request.get('error', {})[0]

        # We run through the validator once per form submit, and check all values
        # this value in request prevents running once per subfield value.
        key = instance.id + fieldname
        if instance.REQUEST.get(key, False):
            return True

        # Retrieve all AS uids
        for uid in mins.keys():

            # Foreach AS, check spec. input values
            minv = mins.get(uid, '') == '' and '0' or mins[uid]
            maxv = maxs.get(uid, '') == '' and '0' or maxs[uid]
            err = errors.get(uid, '') == '' and '0' or errors[uid]

            # Values must be numbers
            try:
                minv = float(minv)
            except ValueError:
                instance.REQUEST[key] = to_utf8(translate(
                    _("Validation failed: Min values must be numeric")))
                return instance.REQUEST[key]
            try:
                maxv = float(maxv)
            except ValueError:
                instance.REQUEST[key] = to_utf8(translate(
                    _("Validation failed: Max values must be numeric")))
                return instance.REQUEST[key]
            try:
                err = float(err)
            except ValueError:
                instance.REQUEST[key] = to_utf8(translate(_(
                    "Validation failed: Percentage error values must be numeric")))
                return instance.REQUEST[key]

            # Min value must be < max
            if minv > maxv:
                instance.REQUEST[key] = to_utf8(translate(_(
                    "Validation failed: Max values must be greater than Min values")))
                return instance.REQUEST[key]

            # Error percentage must be between 0 and 100
            if err < 0 or err > 100:
                instance.REQUEST[key] = to_utf8(translate(_(
                    "Validation failed: Error percentage must be between 0 and 100")))
                return instance.REQUEST[key]

        instance.REQUEST[key] = True
        return True


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

        # We run through the validator once per form submit, and check all values
        # this value in request prevents running once per subfield value.
        key = instance.id + fieldname
        if instance.REQUEST.get(key, False):
            return True

        for i, value in enumerate(request[fieldname]):

            # Values must be numbers
            try:
                minv = float(value['intercept_min'])
            except ValueError:
                instance.REQUEST[key] = to_utf8(translate(
                    _("Validation failed: Min values must be numeric")))
                return instance.REQUEST[key]
            try:
                maxv = float(value['intercept_max'])
            except ValueError:
                instance.REQUEST[key] = to_utf8(translate(
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
                instance.REQUEST[key] = to_utf8(translate(
                    _("Validation failed: Error values must be numeric")))
                return instance.REQUEST[key]

            if perc and (err < 0 or err > 100):
                # Error percentage must be between 0 and 100
                instance.REQUEST[key] = to_utf8(translate(_(
                    "Validation failed: Error percentage must be between 0 and 100")))
                return instance.REQUEST[key]

            # Min value must be < max
            if minv > maxv:
                instance.REQUEST[key] = to_utf8(translate(_(
                    "Validation failed: Max values must be greater than Min values")))
                return instance.REQUEST[key]

            # Error values must be >-1
            if err < 0:
                instance.REQUEST[key] = to_utf8(translate(
                    _("Validation failed: Error value must be 0 or greater")))
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

        instance = kwargs['instance']
        # fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        fieldname = kwargs['field'].getName()

        translate = getToolByName(instance, 'translation_service').translate

        ress = request.get('result', {})[0]
        mins = request.get('min', {})[0]
        maxs = request.get('max', {})[0]
        errs = request.get('error', {})[0]

        # Retrieve all AS uids
        uids = ress.keys()
        for uid in uids:

            # Foreach AS, check spec. input values
            res = ress[uid] if ress[uid] else '0'
            min = mins[uid] if mins[uid] else '0'
            max = maxs[uid] if maxs[uid] else '0'
            err = errs[uid] if errs[uid] else '0'

            # Values must be numbers
            try:
                res = float(res)
            except ValueError:
                return to_utf8(translate(
                    _("Validation failed: Expected values must be numeric")))
            try:
                min = float(min)
            except ValueError:
                return to_utf8(translate(
                    _("Validation failed: Min values must be numeric")))
            try:
                max = float(max)
            except ValueError:
                return to_utf8(translate(
                    _("Validation failed: Max values must be numeric")))
            try:
                err = float(err)
            except ValueError:
                return to_utf8(translate(_(
                    "Validation failed: Percentage error values must be numeric")))

            # Min value must be < max
            if min > max:
                return to_utf8(translate(_(
                    "Validation failed: Max values must be greater than Min values")))

            # Expected result must be between min and max
            if res < min or res > max:
                return to_utf8(translate(_(
                    "Validation failed: Expected values must be between Min and Max values")))

            # Error percentage must be between 0 and 100
            if err < 0 or err > 100:
                return to_utf8(translate(_(
                    "Validation failed: Percentage error values must be between 0 and 100")))

        return True


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
