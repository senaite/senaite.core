from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from bika.lims.utils import sortable_title
from zope.interface import Interface, implements
from zope.site.hooks import getSite
from zExceptions import Redirect
import sys,re
from bika.lims import bikaMessageFactory as _

class UniqueFieldValidator:
    """ Verifies that a field value is unique for items
    if the same type in this location """

    implements(IValidator)
    name = "uniquefieldvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service').translate

        if value == instance.get(fieldname):
            return True

        for item in aq_parent(instance).objectValues():
            if hasattr(item, 'UID') and item.UID() != instance.UID() and \
               item.schema.get(fieldname).getAccessor(item)() == value:
                msg = _("Validation failed: '${value}' is not unique",
                        mapping = {'value': value})
                return ts(msg)
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
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service').translate

        if re.findall(r"[^A-Za-z\w\d\-\_]", value):
            return _("Validation failed: keyword contains invalid characters")

        # check the value against all AnalysisService keywords
        # this has to be done from catalog so we don't
        # clash with ourself
        bsc = getToolByName(instance, 'bika_setup_catalog')
        services = bsc(portal_type='AnalysisService', getKeyword = value)
        for service in services:
            if service.UID != instance.UID():
                msg = _("Validation failed: '${title}': "
                        "This keyword is already in use by service '${used_by}'",
                        mapping = {'title': value, 'used_by': service.Title})
                return ts(msg)

        calc = hasattr(instance, 'getCalculation') and \
             instance.getCalculation() or None
        our_calc_uid = calc and calc.UID() or ''

        # check the value against all Calculation Interim Field ids
        calcs = [c for c in bsc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['keyword'] == value and our_calc_uid != calc.UID():
                    msg = _("Validation failed: '${title}': " \
                            "This keyword is already in use by calculation '${used_by}'",
                            mapping = {'title': value, 'used_by': calc.Title()})
                    return ts(msg)
        return True

validation.register(ServiceKeywordValidator())

class InterimFieldsValidator:
    """Validating InterimField keywords.
        XXX Applied as a subfield validator but validates entire field.
        keyword must match isUnixLikeName
        keyword may not be the same as any service keyword.
        keyword must be unique in this InterimFields field
        keyword must be unique for all interimfields which share the same title.
        title must be unique for all interimfields which share the same keyword.
    """

    implements(IValidator)
    name = "interimfieldsvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get(fieldname, [])

        ts = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')

        if instance.REQUEST.get('validated', '') == fieldname:
            return True
        else:
            instance.REQUEST['validated'] = fieldname


        for x in range(len(interim_fields)):
            row = interim_fields[x]
            keys = row.keys()
            if 'title' not in keys:
                return ts(_("Validation failed: title is required"))
            if 'keyword' not in keys:
                return ts(_("Validation failed: keyword is required"))

        if not re.match(r"^[A-Za-z\w\d\-\_]+$", value):
            return _("Validation failed: keyword contains invalid characters")

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
                    mapping = {'keyword': k})
            return ts(msg)
        for t in [t for t in titles.keys() if titles[t] > 1]:
            msg = _("Validation failed: '${title}': duplicate title",
                    mapping = {'title': t})
            return ts(msg)

        # check all keywords against all AnalysisService keywords for dups
        services = bsc(portal_type='AnalysisService', getKeyword = value)
        if services:
            msg = _("Validation failed: '${title}': "\
                    "This keyword is already in use by service '${used_by}'",
                    mapping = {'title': value, 'used_by': services[0].Title})
            return ts(msg)

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
                        mapping={'title': field['title'],
                                 'keyword': title_keywords[field['title']]})
                return ts(msg)
            if 'keyword' in field and \
               field['keyword'] in keyword_titles.keys() and \
               keyword_titles[field['keyword']] != field['title']:
                msg = _("Validation failed: keyword '${keyword}' "
                        "must have column title '${title}'",
                        mapping={'keyword': field['keyword'],
                                 'title': keyword_titles[field['keyword']]})
                return ts(msg)

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
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get('InterimFields')

        ts = getToolByName(instance, 'translation_service').translate
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
                        mapping = {'keyword': keyword})
                return ts(msg)
        return True

validation.register(FormulaValidator())

class CoordinateValidator:
    """ Validate latitude or longitude field values
    """
    implements(IValidator)
    name = "coordinatevalidator"

    def __call__(self, value, *args, **kwargs):
        if not value:
            return True

        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = instance.REQUEST

        if request.get('validated', '') == fieldname:
            return True
        else:
            request['validated'] = fieldname

        form = request.form
        form_value = form.get(fieldname)

        ts = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')

        try:
            degrees = int(form_value['degrees'])
        except:
            return ts(_("Validation failed: degrees must be numeric"))

        try:
            minutes = int(form_value['minutes'])
        except:
            return ts(_("Validation failed: minutes must be numeric"))

        try:
            seconds = int(form_value['seconds'])
        except:
            return ts(_("Validation failed: seconds must be numeric"))

        if not 0 <= minutes <= 59:
            return ts(_("Validation failed: minutes must be 0 - 59"))

        if not 0 <= seconds <= 59:
            return ts(_("Validation failed: seconds must be 0 - 59"))

        bearing = form_value['bearing']

        if fieldname == 'Latitude':
            if not 0 <= degrees <= 90:
                return ts(_("Validation failed: degrees must be 0 - 90"))
            if degrees == 90:
                if minutes != 0:
                    return ts(_("Validation failed: degrees is 90; minutes must be zero"))
                if seconds != 0:
                    return ts(_("Validation failed: degrees is 90; seconds must be zero"))
            if bearing.lower() not in 'sn':
                return ts(_("Validation failed: Bearing must be N/S"))

        if fieldname == 'Longitude':
            if not 0 <= degrees <= 180:
                return ts(_("Validation failed: degrees must be 0 - 180"))
            if degrees == 180:
                if minutes != 0:
                    return ts(_("Validation failed: degrees is 180; minutes must be zero"))
                if seconds != 0:
                    return ts(_("Validation failed: degrees is 180; seconds must be zero"))
            if bearing.lower() not in 'ew':
                return ts(_("Validation failed: Bearing must be E/W"))

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

        ts = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')

        # ResultValue must always be a number
        for field in form_value:
            try:
                f = float(field['ResultValue'])
            except:
                return ts(_("Validation failed: Result Values must be numbers"))

        return True

validation.register(ResultOptionsValidator())

class RestrictedCategoriesValidator:
    """ Verifies that client Restricted categories include all categories
    required by service dependencies. """

    implements(IValidator)
    name = "restrictedcategoriesvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')
        uc = getToolByName(instance, 'uid_catalog')

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
                    mapping={'categories': ','.join(failures)})
            return ts(msg)

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
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        preservation = form.get('Preservation')

        if type(preservation) in (list,tuple):
            preservation = preservation[0]

        if preservation:
            return True

        ts = getToolByName(instance, 'translation_service').translate
        bsc = getToolByName(instance, 'bika_setup_catalog')

        if not preservation:
            msg = _("Validation failed: PrePreserved containers "
                    "must have a preservation selected.")
            return ts(msg)

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
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service').translate

        # check the value against all AnalysisService keywords
        if re.findall(regex, value):
            msg = _("Validation failed: keyword contains invalid "
                    "characters")
            return ts(msg)

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
            fieldname = kwargs['field'].getName()
            request = kwargs.get('REQUEST', {})
                        
            if instance.REQUEST.get('validated', '') == self.name:
                return True
            else:
                instance.REQUEST['validated'] = self.name    
                
            ts = getToolByName(instance, 'translation_service').translate
                            
            mins   = request.get('min',{})[0]
            maxs   = request.get('max',{})[0]
            errors = request.get('error',{})[0]
                        
            # Retrieve all AS uids
            uids = mins.keys()
            for uid in uids:
                
                # Foreach AS, check spec. input values
                min = mins[uid]
                max = maxs[uid]
                err = errors[uid]
                
                min = min == '' and '0' or min
                max = max == '' and '0' or max
                err = err == '' and '0' or err
                
                # Values must be numbers
                try: min = float(min)
                except: return ts(_("Validation failed: Min values must be numeric"))  
                try: max = float(max)
                except: return ts(_("Validation failed: Max values must be numeric"))                
                try: err = float(err)
                except: return ts(_("Validation failed: Percentage error values must be numeric"))    
                            
                # Min value must be < max
                if min > max :
                    return ts(_("Validation failed: Max values must be greater than Min values"))   
                
                # Error percentage must be between 0 and 100
                if err < 0 or err > 100 :
                    return ts(_("Validation failed: Error percentage must be between 0 and 100"))
                                
            return True
    
validation.register(AnalysisSpecificationsValidator())   


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
            fieldname = kwargs['field'].getName()
            request = kwargs.get('REQUEST', {})
                        
            if instance.REQUEST.get('validated', '') == self.name:
                return True
            else:
                instance.REQUEST['validated'] = self.name    
                
            ts = getToolByName(instance, 'translation_service').translate
            
            ress   = request.get('result',{})[0]
            mins   = request.get('min',{})[0]
            maxs   = request.get('max',{})[0]
            errors = request.get('error',{})[0]
                        
            # Retrieve all AS uids
            uids = ress.keys()
            for uid in uids:
                
                # Foreach AS, check spec. input values
                res = ress[uid]
                min = mins[uid]
                max = maxs[uid]
                err = errors[uid]
                
                res = res == '' and '0' or res
                min = min == '' and '0' or min
                max = max == '' and '0' or max
                err = err == '' and '0' or err
                
                # Values must be numbers
                try: res = float(res)
                except: return ts(_("Validation failed: Expected values must be numeric"))
                try: min = float(min)
                except: return ts(_("Validation failed: Min values must be numeric"))  
                try: max = float(max)
                except: return ts(_("Validation failed: Max values must be numeric"))                
                try: err = float(err)
                except: return ts(_("Validation failed: Percentage error values must be numeric"))    
                
                # Min value must be < max
                if min > max :
                    return ts(_("Validation failed: Max values must be greater than Min values"))   
                
                # Expected result must be between min and max
                if res < min or res > max:
                    return ts(_("Validation failed: Expected values must be between Min and Max values"))
                                
                # Error percentage must be between 0 and 100
                if err < 0 or err > 100 :
                    return ts(_("Validation failed: Percentage error values must be between 0 and 100"))
                                
            return True
    
validation.register(ReferenceValuesValidator()) 