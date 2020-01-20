from operator import itemgetter

from Products.ATExtensions.field import RecordField
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IFieldDefaultProvider
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisSpecificationWidget
# A tuple of (subfield_id, subfield_label,)
from bika.lims.interfaces.analysis import IRequestAnalysis

SUB_FIELDS = (
    ("keyword", _("Analysis Service")),
    ("min_operator", _("Min operator")),
    ("min", _('Min')),
    ("max_operator", _("Max operator")),
    ("max", _('Max')),
    ("warn_min", _('Min warn')),
    ("warn_max", _('Max warn')),
    ("hidemin", _('< Min')),
    ("hidemax", _('> Max')),
    ("rangecomment", _('Range Comment')),
)


class ResultsRangeField(RecordField):
    """A field that stores a results range
    """
    _properties = RecordField._properties.copy()
    _properties.update({
        "type": "results_range_field",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
    })

    def get(self, instance, **kwargs):
        from bika.lims.content.analysisspec import ResultsRangeDict
        value = super(ResultsRangeField, self).get(instance, **kwargs)
        if value:
            return ResultsRangeDict(value)
        return None


registerField(ResultsRangeField, title="ResultsRange",
              description="Used for storing a results range",)


class SpecificationsField(RecordsField):
    """A field that stores a list of results ranges
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "type": "specifications",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
        "subfield_validators": {
            "min": "analysisspecs_validator",
            "max": "analysisspecs_validator",
        },
        "required_subfields": ("keyword", ),
        "widget": AnalysisSpecificationWidget,
    })

    def get(self, instance, **kwargs):
        from bika.lims.content.analysisspec import ResultsRangeDict
        values = super(SpecificationsField, self).get(instance, **kwargs)
        uid_keyword_service = kwargs.get("uid", kwargs.get("keyword", None))
        if uid_keyword_service:
            return self.getResultsRange(values, uid_keyword_service)
        if values:
            return map(lambda val: ResultsRangeDict(val), values)
        return []

    def getResultsRange(self, values, uid_keyword_service):
        from bika.lims.content.analysisspec import ResultsRangeDict
        if not uid_keyword_service:
            return None

        if api.is_object(uid_keyword_service):
            uid_keyword_service = api.get_uid(uid_keyword_service)

        key = "keyword"
        if api.is_uid(uid_keyword_service) and uid_keyword_service != "0":
            # We always assume a uid of "0" refers to portal
            key = "uid"

        # Find out the item for the given uid/keyword
        value = filter(lambda v: v.get(key) == uid_keyword_service, values)
        return value and ResultsRangeDict(value[0]) or None

    def _to_dict(self, value):
        """Convert the records to persistent dictionaries
        """
        value = super(SpecificationsField, self)._to_dict(value)

        # Bail out items without "uid" key (uid is used everywhere to know the
        # service the result range refers to)
        return filter(lambda result_range: "uid" in result_range, value)


class DefaultResultsRangeProvider(object):
    """Default Results Range provider for analyses
    This is used for backwards-compatibility for when the analysis' ResultsRange
    was obtained directly from Sample's ResultsRanges field, before this:
    https://github.com/senaite/senaite.core/pull/1506
    """
    implements(IFieldDefaultProvider)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Get the default value.
        """
        if not IRequestAnalysis.providedBy(self.context):
            return None

        keyword = self.context.getKeyword()
        sample = self.context.getRequest()
        field = sample.getField("ResultsRange")
        rr = field.get(sample, keyword=keyword)
        if rr:
            self.context.setResultsRange(rr)
            return self.context.getResultsRange()

        return None
