from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
from hashlib import sha1
import hmac
import json
import plone.protect
import unittest
import os

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def _authenticator(self, user):
        manager = getUtility(IKeyManager)
        secret=manager.secret()
        auth=hmac.new(secret, user, sha1).hexdigest()
        return auth

    def test_is_unicode(self):
        from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
        path = os.path.join(os.path.dirname(__file__), '..', 'locales')
        langs = os.listdir(path)
        for lang in langs:
            lc_path = os.path.join(path, lang, 'LC_MESSAGES')
            if os.path.isdir(lc_path):
                files = os.listdir(lc_path)
                for f in files:
                    if f.endswith('.mo'):
                        mcatalog = GettextMessageCatalog(lang, 'zope',
                                           os.path.join(lc_path, f))
                        catalog = mcatalog._catalog
                        self.failUnless(catalog._charset,
            u"""Charset value for the Message catalog is missing.
                The language is %s (zope.po).
                Value of the message catalog should be in unicode""" % (lang,)
                                        )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
