"""The lab staff
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.content.person import Person
from bika.lims.config import PUBLICATION_PREFS, PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from zope.interface import implements
from bika.lims.interfaces import ILabContact
import sys

schema = Person.schema.copy() + Schema((
    LinesField('PublicationPreference',
        vocabulary = PUBLICATION_PREFS,
        default = 'email',
        schemata = 'Publication preference',
        widget = MultiSelectionWidget(
            label=_("Publication preference"),
        ),
    ),
    ImageField('Signature',
        widget = ImageWidget(
            label=_("Signature"),
            description = _(
                "Upload a scanned signature to be used on printed analysis "
                "results reports. Ideal size is 250 pixels wide by 150 high"),
        ),
    ),
    ReferenceField('Department',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        relationship = 'LabContactDepartment',
        vocabulary = 'getDepartments',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Department"),
            description=_("The laboratory department"),
        ),
    ),
    ComputedField('DepartmentTitle',
        expression = "context.getDepartment() and context.getDepartment().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False

class LabContact(Person):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    implements(ILabContact)

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the contact's Fullname as title """
        return safe_unicode(self.getFullname()).encode('utf-8')

    def hasUser(self):
        """ check if contact has user """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in
                               bsc(portal_type='Department',
                                   inactive_state = 'active')]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

registerType(LabContact, PROJECTNAME)
