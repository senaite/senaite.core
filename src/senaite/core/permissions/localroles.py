# -*- coding: utf-8 -*-

from zope.interface import implementer
from plone.app.workflow.interfaces import ISharingPageRole
from senaite.core.permissions import ManageSenaite
from bika.lims import senaiteMessageFactory as _


@implementer(ISharingPageRole)
class AnalystRole(object):

    title = _(u"title_analyst_role", default=u"Analyst")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class OwnerRole(object):
    title = _(u"title_owner_role", default=u"Owner")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class LabClerkRole(object):
    title = _(u"title_lab_clerk_role", default=u"Lab Clerk")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class PreserverRole(object):
    title = _(u"title_preserver_role", default=u"Preserver")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class PublisherRole(object):
    title = _(u"title_publisher_role", default=u"Publisher")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class SamplerRole(object):
    title = _(u"title_sampler_role", default=u"Sampler")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class VerifierRole(object):
    title = _(u"title_verifier_role", default=u"Verifier")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class LabManagerRole(object):
    title = _(u"title_lab_manager_role", default=u"Lab Manager")
    required_permission = ManageSenaite
    required_interface = None


@implementer(ISharingPageRole)
class ManagerRole(object):
    title = _(u"title_manager_role", default=u"Manager")
    required_permission = ManageSenaite
    required_interface = None
