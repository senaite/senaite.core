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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import copy
from datetime import timedelta

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DecimalWidget
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import IInternalUse
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.workflow import getTransitionDate
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import FixedPointField
from Products.Archetypes.Schema import Schema
from Products.ATContentTypes.utils import DT2dt
from Products.ATContentTypes.utils import dt2DT
from Products.CMFCore.permissions import View
from senaite.core.catalog.indexer.baseanalysis import sortable_title
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides

# The actual uncertainty for this analysis' result, populated when the result
# is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    read_permission=View,
    write_permission="Field: Edit Result",
    precision=10,
    widget=DecimalWidget(
        label=_("Uncertainty")
    )
)
# This field keep track if the field hidden has been set manually or not. If
# this value is false, the system will assume the visibility of this analysis
# in results report will depend on the value set at AR, Profile or Template
# levels (see AnalysisServiceSettings fields in AR). If the value for this
# field is set to true, the system will assume the visibility of the analysis
# will only depend on the value set for the field Hidden (bool).
HiddenManually = BooleanField(
    'HiddenManually',
    default=False,
)


schema = schema.copy() + Schema((
    Uncertainty,
    HiddenManually,
))


class AbstractRoutineAnalysis(AbstractAnalysis, ClientAwareMixin):
    implements(IAnalysis, IRequestAnalysis, IRoutineAnalysis, ICancellable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getRequest(self):
        """Returns the Analysis Request this analysis belongs to.
        Delegates to self.aq_parent
        """
        ar = self.aq_parent
        return ar

    @security.public
    def getRequestID(self):
        """Used to populate catalog values.
        Returns the ID of the parent analysis request.
        """
        ar = self.getRequest()
        if ar:
            return ar.getId()

    @security.public
    def getRequestUID(self):
        """Returns the UID of the parent analysis request.
        """
        ar = self.getRequest()
        if ar:
            return ar.UID()

    @security.public
    def getRequestURL(self):
        """Returns the url path of the Analysis Request object this analysis
        belongs to. Returns None if there is no Request assigned.
        :return: the Analysis Request URL path this analysis belongs to
        :rtype: str
        """
        request = self.getRequest()
        if request:
            return request.absolute_url_path()

    def getClient(self):
        """Returns the Client this analysis is bound to, if any
        """
        request = self.getRequest()
        return request and request.getClient() or None

    @security.public
    def getClientOrderNumber(self):
        """Used to populate catalog values.
        Returns the ClientOrderNumber of the associated AR
        """
        request = self.getRequest()
        if request:
            return request.getClientOrderNumber()

    @security.public
    def getDateReceived(self):
        """Used to populate catalog values.
        Returns the date the Analysis Request this analysis belongs to was
        received. If the analysis was created after, then returns the date
        the analysis was created.
        """
        request = self.getRequest()
        if request:
            ar_date = request.getDateReceived()
            if ar_date and self.created() > ar_date:
                return self.created()
            return ar_date
        return None

    @security.public
    def isSampleReceived(instance):
        """Returns whether if the Analysis Request this analysis comes from has
        been received or not
        """
        return instance.getDateReceived() and True or False

    @security.public
    def getDatePublished(self):
        """Used to populate catalog values.
        Returns the date on which the "publish" transition was invoked on this
        analysis.
        """
        return getTransitionDate(self, 'publish', return_as_datetime=True)

    @security.public
    def getDateSampled(self):
        """Returns the date when the Sample was Sampled
        """
        request = self.getRequest()
        if request:
            return request.getDateSampled()
        return None

    @security.public
    def isSampleSampled(self):
        """Returns whether if the Analysis Request this analysis comes from has
        been received or not
        """
        return self.getDateSampled() and True or False

    @security.public
    def getStartProcessDate(self):
        """Returns the date time when the analysis request the analysis belongs
        to was received. If the analysis request hasn't yet been received,
        returns None
        Overrides getStartProcessDateTime from the base class
        :return: Date time when the analysis is ready to be processed.
        :rtype: DateTime
        """
        return self.getDateReceived()

    @security.public
    def getSamplePoint(self):
        request = self.getRequest()
        if request:
            return request.getSamplePoint()
        return None

    @security.public
    def getDueDate(self):
        """Used to populate getDueDate index and metadata.
        This calculates the difference between the time the analysis processing
        started and the maximum turnaround time. If the analysis has no
        turnaround time set or is not yet ready for proces, returns None
        """
        tat = self.getMaxTimeAllowed()
        if not tat:
            return None
        start = self.getStartProcessDate()
        if not start:
            return None

        # delta time when the first analysis is considered as late
        delta = timedelta(minutes=api.to_minutes(**tat))

        # calculated due date
        end = dt2DT(DT2dt(start) + delta)

        # delta is within one day, return immediately
        if delta.days == 0:
            return end

        # get the laboratory workdays
        setup = api.get_setup()
        workdays = setup.getWorkdays()

        # every day is a workday, no need for calculation
        if workdays == tuple(map(str, range(7))):
            return end

        # reset the due date to the received date, and add only for configured
        # workdays another day
        due_date = end - delta.days

        days = 0
        while days < delta.days:
            # add one day to the new due date
            due_date += 1
            # skip if the weekday is a non working day
            if str(due_date.asdatetime().weekday()) not in workdays:
                continue
            days += 1

        return due_date

    @security.public
    def getSampleType(self):
        request = self.getRequest()
        if request:
            return request.getSampleType()
        return None

    @security.public
    def getSampleTypeUID(self):
        """Used to populate catalog values.
        """
        sample_type = self.getSampleType()
        if sample_type:
            return api.get_uid(sample_type)

    @security.public
    def getResultsRange(self):
        """Returns the valid result range for this routine analysis

        A routine analysis will be considered out of range if it result falls
        out of the range defined in "min" and "max". If there are values set
        for "warn_min" and "warn_max", these are used to compute the shoulders
        in both ends of the range. Thus, an analysis can be out of range, but
        be within shoulders still.

        :return: A dictionary with keys "min", "max", "warn_min" and "warn_max"
        :rtype: dict
        """
        return self.getField("ResultsRange").get(self)

    @security.public
    def getSiblings(self, with_retests=False):
        """
        Return the siblings analyses, using the parent to which the current
        analysis belongs to as the source
        :param with_retests: If false, siblings with retests are dismissed
        :type with_retests: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        raise NotImplementedError("getSiblings is not implemented.")

    @security.public
    def getCalculation(self):
        """Return current assigned calculation
        """
        field = self.getField("Calculation")
        calculation = field.get(self)
        if not calculation:
            return None
        return calculation

    @security.public
    def getDependents(self, with_retests=False, recursive=False):
        """
        Returns a list of siblings who depend on us to calculate their result.
        :param with_retests: If false, dependents with retests are dismissed
        :param recursive: If true, returns all dependents recursively down
        :type with_retests: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        def is_dependent(analysis):
            # Never consider myself as dependent
            if analysis.UID() == self.UID():
                return False

            # Never consider analyses from same service as dependents
            self_service_uid = self.getRawAnalysisService()
            if analysis.getRawAnalysisService() == self_service_uid:
                return False

            # Without calculation, no dependency relationship is possible
            calculation = analysis.getCalculation()
            if not calculation:
                return False

            # Calculation must have the service I belong to
            services = calculation.getRawDependentServices()
            return self_service_uid in services
        
        request = self.getRequest()
        if request.isPartition():
            parent = request.getParentAnalysisRequest()
            siblings = parent.getAnalyses(full_objects=True)
        else:
            siblings = self.getSiblings(with_retests=with_retests)

        dependents = filter(lambda sib: is_dependent(sib), siblings)
        if not recursive:
            return dependents

        # Return all dependents recursively
        deps = dependents
        for dep in dependents:
            down_dependencies = dep.getDependents(with_retests=with_retests,
                                                  recursive=True)
            deps.extend(down_dependencies)
        return deps

    @security.public
    def getDependencies(self, with_retests=False, recursive=False):
        """
        Return a list of siblings who we depend on to calculate our result.
        :param with_retests: If false, siblings with retests are dismissed
        :param recursive: If true, looks for dependencies recursively up
        :type with_retests: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        calc = self.getCalculation()
        if not calc:
            return []

        # If the calculation this analysis is bound does not have analysis
        # keywords (only interims), no need to go further
        service_uids = calc.getRawDependentServices()

        # Ensure we exclude ourselves
        service_uid = self.getRawAnalysisService()
        service_uids = filter(lambda serv: serv != service_uid, service_uids)
        if len(service_uids) == 0:
            return []

        dependencies = []
        for sibling in self.getSiblings(with_retests=with_retests):
            # We get all analyses that depend on me, also if retracted (maybe
            # I am one of those that are retracted!)
            deps = map(api.get_uid, sibling.getDependents(with_retests=True))
            if self.UID() in deps:
                dependencies.append(sibling)
                if recursive:
                    # Append the dependencies of this dependency
                    up_deps = sibling.getDependencies(with_retests=with_retests,
                                                      recursive=True)
                    dependencies.extend(up_deps)

        # Exclude analyses of same service as me to prevent max recursion depth
        return filter(lambda dep: dep.getRawAnalysisService() != service_uid,
                      dependencies)

    @security.public
    def getPrioritySortkey(self):
        """
        Returns the key that will be used to sort the current Analysis, from
        most prioritary to less prioritary.
        :return: string used for sorting
        """
        analysis_request = self.getRequest()
        if analysis_request is None:
            return None
        ar_sort_key = analysis_request.getPrioritySortkey()
        ar_id = analysis_request.getId().lower()
        title = sortable_title(self)
        if callable(title):
            title = title()
        return '{}.{}.{}'.format(ar_sort_key, ar_id, title)

    @security.public
    def getHidden(self):
        """ Returns whether if the analysis must be displayed in results
        reports or not, as well as in analyses view when the user logged in
        is a Client Contact.

        If the value for the field HiddenManually is set to False, this function
        will delegate the action to the method getAnalysisServiceSettings() from
        the Analysis Request.

        If the value for the field HiddenManually is set to True, this function
        will return the value of the field Hidden.
        :return: true or false
        :rtype: bool
        """
        if self.getHiddenManually():
            return self.getField('Hidden').get(self)
        request = self.getRequest()
        if request:
            service_uid = self.getServiceUID()
            ar_settings = request.getAnalysisServiceSettings(service_uid)
            return ar_settings.get('hidden', False)
        return False

    @security.public
    def setHidden(self, hidden):
        """ Sets if this analysis must be displayed or not in results report and
        in manage analyses view if the user is a lab contact as well.

        The value set by using this field will have priority over the visibility
        criteria set at Analysis Request, Template or Profile levels (see
        field AnalysisServiceSettings from Analysis Request. To achieve this
        behavior, this setter also sets the value to HiddenManually to true.
        :param hidden: true if the analysis must be hidden in report
        :type hidden: bool
        """
        self.setHiddenManually(True)
        self.getField('Hidden').set(self, hidden)

    @security.public
    def setInternalUse(self, internal_use):
        """Applies the internal use of this Analysis. Analyses set for internal
        use are not accessible to clients and are not visible in reports
        """
        if internal_use:
            alsoProvides(self, IInternalUse)
        else:
            noLongerProvides(self, IInternalUse)

    def getConditions(self):
        """Returns the conditions of this analysis. These conditions are usually
        set on sample registration and are stored at sample level
        """
        sample = self.getRequest()
        service_uid = self.getRawAnalysisService()

        def is_valid(condition):
            uid = condition.get("uid")
            if api.is_uid(uid) and uid == service_uid:
                value = condition.get("value", None)
                if value:
                    return "title" in condition
            return False

        conditions = sample.getServiceConditions()
        conditions = filter(is_valid, conditions)
        return copy.deepcopy(conditions)
