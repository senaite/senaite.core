# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from DateTime import DateTime

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import ComputedField
from Products.Archetypes.atapi import ComputedWidget
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import ReferenceWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.workflow import getCurrentState

from plone.app.blob.field import FileField

from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME
from bika.lims.config import ATTACHMENT_REPORT_OPTIONS
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import DateTimeWidget


schema = BikaSchema.copy() + Schema((

    ComputedField(
        'RequestID',
        expression='here.getRequestID()',
        widget=ComputedWidget(
            visible=True,
        ),
    ),

    FileField(
        'AttachmentFile',
        widget=FileWidget(
            label=_("Attachment"),
        ),
    ),

    ReferenceField(
        'AttachmentType',
        required=0,
        allowed_types=('AttachmentType',),
        relationship='AttachmentAttachmentType',
        widget=ReferenceWidget(
            label=_("Attachment Type"),
        ),
    ),

    StringField(
        'ReportOption',
        searchable=True,
        vocabulary="ATTACHMENT_REPORT_OPTIONS",
        widget=SelectionWidget(
            label=_("Report Options"),
            checkbox_bound=0,
            format='select',
            visible=True,
            default='a',
        ),
    ),

    StringField(
        'AttachmentKeys',
        searchable=True,
        widget=StringWidget(
            label=_("Attachment Keys"),
        ),
    ),

    DateTimeField(
        'DateLoaded',
        required=1,
        default_method='current_date',
        widget=DateTimeWidget(
            label=_("Date Loaded"),
        ),
    ),

    ComputedField(
        'AttachmentTypeUID',
        expression="context.getAttachmentType().UID() if context.getAttachmentType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    ComputedField(
        'ClientUID',
        expression='here.aq_parent.UID()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
))

schema['id'].required = False
schema['title'].required = False


class Attachment(BaseFolder):
    """Attachments live inside a client and can be linked to ARs or Analyses
    """
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the Id
        """
        return safe_unicode(self.getId()).encode('utf-8')

    def getTextTitle(self):
        """Return the request and possibly analayis title as title
        """
        request_id = self.getRequestID()
        if not request_id:
            return ''

        analysis = self.getAnalysis()
        if not analysis:
            return request_id

        return '%s - %s' % (request_id, analysis.Title())

    def getRequest(self):
        """Return the AR to which this is linked there is a short time between
        creation and linking when it is not linked
        """
        # Attachment field in AnalysisRequest is still a ReferenceField, not
        # an UIDReferenceField yet.
        tool = getToolByName(self, REFERENCE_CATALOG)
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisRequestAttachment')]

        if len(uids) > 1:
            logger.warn("Attachment assigned to more than one Analysis Request."
                        "This should never happen!. The first Analysis Request"
                        "will be returned.")

        if len(uids) > 0:
            reference = uids[0]
            ar = tool.lookupObject(reference.sourceUID)
            return ar

        # This Attachment is not linked directly to an Analysis Request, but
        # probably linked to an Analysis, so try to get the Analysis Request
        # from there.
        analysis = self.getAnalysis()
        if IRequestAnalysis.providedBy(analysis):
            return analysis.getRequest()

        return None

    def getRequestID(self):
        """Return the ID of the request to which this is linked
        """
        ar = self.getRequest()
        if ar:
            return ar.getId()
        else:
            return None

    def getAnalysis(self):
        """Return the analysis to which this is linked it may not be linked to
        an analysis
        """
        analysis = get_backreferences(self, 'AnalysisAttachment',
                                      as_brains=True)
        if not analysis:
            return None

        if len(analysis) > 1:
            logger.warn("Single attachment assigned to more than one Analysis")

        analysis = api.get_object(analysis[0])
        return analysis

    security.declarePublic('current_date')

    def current_date(self):
        """return current date
        """
        return DateTime()


registerType(Attachment, PROJECTNAME)
