from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseContent
from Products.Archetypes import atapi
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import ReferenceField
from zope.interface import implements
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReflexRule
import sys

schema = BikaSchema.copy() + Schema((
    # Methods associated to the Reflex rule
    # In the first place the user has to choose from a drop-down list the
    # method which the rules for the analysis service will be bind to. After
    # selecting the method, the system will display another list in order to
    # choose the analysis service to add the rules when using the selected
    # method.
    ReferenceField(
        'Method',
        required=1,
        multiValued=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary='_getAvailableMethodsDisplayList',
        allowed_types=('Method',),
        relationship='ReflexRuleMethod',
        referenceClass=HoldingReference,
        widget=SelectionWidget(
            label=_("Methods"),
            format='select',
            description=_(
                "Select the method which the rules for the analysis "
                "service will be bind to."),
        )
    ),

))
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")


class ReflexRule(BaseContent):
    """
    When results become available, some samples may have to be added to the
    next available worksheet for reflex testing. These situations are caused by
    the indetermination of the result or by a failed test.
    """
    implements(IReflexRule)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getAvailableMethodsDisplayList(self):
        """ Returns a DisplayList with the available Methods
            registered in Bika-Setup. Only active Methods are fetched.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method', inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

atapi.registerType(ReflexRule, PROJECTNAME)
