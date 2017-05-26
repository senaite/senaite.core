from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed


def after_no_sampling_workflow(obj):
    """Method triggered after a 'no_sampling_workflow' transition for the
    current Analysis Request is performed. Performs the same transition
    to the parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    sample = obj.getSample()
    doActionFor(sample, 'no_sampling_workflow')


def after_sampling_workflow(obj):
    """Method triggered after a 'sampling_workflow' transition for the
    current Analysis Request is performed. Performs the same transition
    to the parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    sample = obj.getSample()
    doActionFor(sample, 'sampling_workflow')


def after_sample(obj):
    """Method triggered after a 'sample' transition for the current
    AR is performed. Promotes sample transition to parent's sample
    bika.lims.workflow.AfterTransitionEventHandler
    """
    sample = obj.getSample()
    doActionFor(sample, 'sample')


def after_receive(obj):
    """Method triggered after a 'receive' transition for the current
    Analysis Request is performed. Responsible of triggering cascade
    actions such as transitioning the container (sample), as well as
    associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    obj.setDateReceived(DateTime())
    obj.reindexObject(idxs=["getDateReceived", ])

    # receive the AR's sample
    # Do note that the 'receive' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition the analyses here again
    sample = obj.getSample()
    doActionFor(sample, 'receive')
