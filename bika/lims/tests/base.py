"""
"""

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
from bika.lims.browser.load_setup_data import LoadSetupData
import bika.lims

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', bika.lims)
    ztc.installPackage('bika.lims')

setup_product()
ptc.setupPloneSite(products=['bika.lims'])

class BikaTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit
    test cases.
    """

class BikaFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
