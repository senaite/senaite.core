# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.browser.add import DefaultAddForm as BaseAddForm
from plone.dexterity.browser.add import DefaultAddView as BaseAddView
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.container.interfaces import INameChooser


class DefaultAddForm(BaseAddForm):
    """Patched Add Form to handle renameAfterCreation of DX objects
    """

    #def add(self, object):
    #    """Patched add method to use our own addContentToContainer
    #    """
    #    fti = getUtility(IDexterityFTI, name=self.portal_type)
    #    new_object = addContentToContainer(self.container, object)

    #    if fti.immediate_view:
    #        self.immediate_view = "/".join(
    #            [self.container.absolute_url(), new_object.id, fti.immediate_view]
    #        )
    #    else:
    #        self.immediate_view = "/".join(
    #            [self.container.absolute_url(), new_object.id]
    #        )


class DefaultAddView(BaseAddView):
    form = DefaultAddForm


def addContentToContainer(container, object, checkConstraints=True):
    """Add an object to a container (patched)

    original code located in `plone.dexterity.utils module`

    The patched version of this function uses the object ID to get the object
    from the container instead of the return value of

    `container._setObject(name, object)`

    This ensures we have the generated ID the object was renamed to *after* the
    object was added to the container!
    """
    if not hasattr(aq_base(object), "portal_type"):
        raise ValueError("object must have its portal_type set")

    container = aq_inner(container)
    if checkConstraints:
        container_fti = container.getTypeInfo()

        fti = getUtility(IDexterityFTI, name=object.portal_type)
        if not fti.isConstructionAllowed(container):
            raise Unauthorized("Cannot create %s" % object.portal_type)

        if container_fti is not None and not container_fti.allowType(
            object.portal_type
        ):
            raise ValueError("Disallowed subobject type: %s" % object.portal_type)

    name = getattr(aq_base(object), "id", None)
    name = INameChooser(container).chooseName(name, object)
    object.id = name

    container._setObject(name, object)
    try:
        # PATCH HERE: Use object.id to ensure we have the renamed object ID
        return container._getOb(object.id)
    except AttributeError:
        uuid = IUUID(object)
        return uuidToObject(uuid)
