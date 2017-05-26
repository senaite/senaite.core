from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed


def _promote_transition(obj, transaction_id):
    """ Promotes the transition passed in to the object's parent
    :param obj: Analysis Request for which the transition has to be promoted
    :param transaction_id: Unique id of the transaction
    """
    sample = obj.getSample()
    if sample:
        doActionFor(sample, transaction_id)


def after_no_sampling_workflow(obj):
    """Method triggered after a 'no_sampling_workflow' transition for the
    Analysis Request passed inis performed. Performs the same transition to the
    parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'no_sampling' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'no_sampling_workflow')


def after_sampling_workflow(obj):
    """Method triggered after a 'sampling_workflow' transition for the
    Analysis Request passed in is performed. Performs the same transition to
    the parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'sampling' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'sampling_workflow')


def after_preserve(obj):
    """Method triggered after a 'preserve' transition for the Analysis Request
    passed in is performed. Promotes the same transition to parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'preserve' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'preserve')


def after_sample(obj):
    """Method triggered after a 'sample' transition for the Analysis Request
    passed in is performed. Promotes sample transition to parent's sample
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Do note that the 'sample' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'sample')


def after_receive(obj):
    """Method triggered after a 'receive' transition for the Analysis Request
    passed in is performed. Responsible of triggering cascade actions such as
    transitioning the container (sample), as well as associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    obj.setDateReceived(DateTime())
    obj.reindexObject(idxs=["getDateReceived", ])

    # Do note that the 'sample' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'receive')


def after_attach(obj):
    """Method triggered after an 'attach' transition for the Analysis Request
    passed in is performed.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Don't cascade. Shouldn't be attaching ARs for now (if ever).
    pass


def after_verify(obj):
    """Method triggered after a 'verify' transition for the Analysis Request
    passed in is performed. Responsible of triggering cascade actions to
    associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Verify all analyses from this Analysis Request
    for analysis in analyses:
        success, message = doActionFor(analysis, 'verify')
        if not success:
            # If failed, delete last verificator
            analysis.deleteLastVerificator()
