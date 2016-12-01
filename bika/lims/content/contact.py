# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""The contact person at an organisation.
"""
import types

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import DisplayList

from zope.interface import implements

from plone import api

from bika.lims.utils import isActive
from bika.lims.interfaces import IContact
from bika.lims.content.person import Person
from bika.lims.config import PROJECTNAME
from bika.lims.config import ManageClients
from bika.lims import logger
from bika.lims import bikaMessageFactory as _


schema = Person.schema.copy() + atapi.Schema((
    atapi.LinesField('PublicationPreference',
                     vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
                     schemata='Publication preference',
                     widget=atapi.MultiSelectionWidget(
                         label=_("Publication preference"),
                     )),
    atapi.BooleanField('AttachmentsPermitted',
                       default=False,
                       schemata='Publication preference',
                       widget=atapi.BooleanWidget(
                           label=_("Results attachments permitted"),
                           description=_(
                               "File attachments to results, e.g. microscope "
                               "photos, will be included in emails to recipients "
                               "if this option is enabled")
                       )),
    atapi.ReferenceField('CCContact',
                         schemata='Publication preference',
                         vocabulary='getContacts',
                         multiValued=1,
                         allowed_types=('Contact',),
                         relationship='ContactContact',
                         widget=atapi.ReferenceWidget(
                             checkbox_bound=0,
                             label=_("Contacts to CC"),
                         )),
))


schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
schema.moveField('CCContact', before='AttachmentsPermitted')


class Contact(Person):
    """A Contact of a Client which can be linked to a System User
    """
    implements(IContact)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """Return the contact's Fullname as title
        """
        return safe_unicode(self.getFullname()).encode('utf-8')

    security.declareProtected(ManageClients, 'getUser')
    def getUser(self):
        """Returns the linked Plone User or None
        """
        username = self.getUsername()
        if not username:
            return None
        user = api.user.get(userid=username)
        return user

    security.declareProtected(ManageClients, 'getUser')
    def setUser(self, user_or_username):
        """Link the user to the Contact
        """
        user = None
        userid = None

        # Handle User IDs (strings)
        if isinstance(user_or_username, types.StringTypes):
            userid = user_or_username
            user = api.user.get(userid)
        # Handle User Objects (MemberData/PloneUser)
        if hasattr(user_or_username, "getId"):
            userid = user_or_username.getId()
            user = user_or_username

        # Not a valid user
        if user is None:
            return False

        # Set the Username
        self.setUsername(userid)
        return True

    security.declareProtected(ManageClients, 'unlinkUser')
    def unlinkUser(self, delete=False):
        """Unlink the user to the Contact
        """
        userid = self.getUsername()
        if self.hasUser():
            logger.debug("Unlinking User '{}' from Contact '{}'".format(
                userid, self.Title()))
            self.setUsername(None)
            # Also remove the Plone User (caution)
            if delete:
                logger.debug("Removing Plone User '{}'".format(userid))
                api.user.delete(username=userid)
            return True
        return False

    security.declareProtected(ManageClients, 'hasUser')
    def hasUser(self):
        """Check if Contact has a linked a System User
        """
        user = self.getUser()
        if user is None:
            return False
        return True

    def getContacts(self, dl=True):
        pairs = []
        objects = []
        for contact in self.aq_parent.objectValues('Contact'):
            if isActive(contact) and contact.UID() != self.UID():
                pairs.append((contact.UID(), contact.Title()))
                if not dl:
                    objects.append(contact)
        pairs.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return dl and DisplayList(pairs) or objects

    def getParentUID(self):
        return self.aq_parent.UID()

atapi.registerType(Contact, PROJECTNAME)
