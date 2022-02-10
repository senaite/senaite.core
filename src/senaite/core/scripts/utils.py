# -*- coding: utf-8 -*-

from zope.component.hooks import setSite
from zope.event import notify
from zope.globalrequest import setRequest
from zope.traversing.interfaces import BeforeTraverseEvent


def setup_site(site):
    setSite(site)
    site.clearCurrentSkin()
    site.setupCurrentSkin(site.REQUEST)
    notify(BeforeTraverseEvent(site, site.REQUEST))
    setRequest(site.REQUEST)
