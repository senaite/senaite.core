from AccessControl import ModuleSecurityInfo
"""
fixSchema.py module

A standard utility module for applying schema changes
"""

import pstat               # required 3rd party module
import math, string, copy  # required python modules
from types import *

__version__ = 0.6

############# DISPATCH CODE ##############


class Dispatch:
    """
The Dispatch class, care of David Ascher, allows different functions to
be called depending on the argument types.  This way, there can be one
function name regardless of the argument type.  To access function doc
in stats.py module, prefix the function with an 'l' or 'a' for list or
array arguments, respectively.  That is, print stats.lmean.__doc__ or
print stats.amean.__doc__ or whatever.
"""

    def __init__(self, *tuples):
        self._dispatch = {}
        for func, types in tuples:
            for t in types:
                if t in self._dispatch.keys():
                    raise ValueError, "can't have two dispatches on "+str(t)
                self._dispatch[t] = func
        self._types = self._dispatch.keys()

    def __call__(self, arg1, *args, **kw):
        if type(arg1) not in self._types:
            raise TypeError, "don't know how to dispatch %s arguments" %  type(arg1)
        return apply(self._dispatch[type(arg1)], (arg1,) + args, kw)


##########################################################################
########################   LIST-BASED FUNCTIONS   ########################
##########################################################################


ModuleSecurityInfo('Products.bika.fixSchema').declarePublic('fixStandards')
def fixStandards (self):
    import traceback
    from Globals import package_home
    from Products.bika.config import *
    from Products.bika.configlets import bika_configlets
    from StringIO import StringIO
    from Products.bika.StandardSample import schema as ss_schema
    from Products.CMFCore.utils import getToolByName
    from Products.Archetypes.public import *
    from Products.Archetypes.Extensions.utils import installTypes, install_subskin
    portal = getToolByName(self, 'portal_url').getPortalObject()
    # Add fields to StandardSamplej

    # Add a field SampleType, with dropdown of types
    field = StringField('StandardID',
        required=1,
        index='FieldIndex',
        searchable=True,
        widget=StringWidget(
            label='Standard ID',
            label_msgid='label_standardid',
            description='The ID assigned to the standard sample by the lab',
            description_msgid='help_standardid',
            i18n_domain=I18N_DOMAIN,
            visible={'edit':'hidden'},
        ),
    )
    ss_schema.addField(field )

    if not 'getStandardID' in portal.portal_catalog.indexes():
        portal.portal_catalog.manage_addIndex('getStandardID',
        'FieldIndex')

    field = StringField('StandardDescription',
        searchable=True,
        widget=StringWidget(
            label='Standard description',
            label_msgid='label_standarddescription',
            description='The standard description',
            description_msgid='help_standarddescription',
            i18n_domain=I18N_DOMAIN,
        ),
    )
    ss_schema.addField(field)

    return



