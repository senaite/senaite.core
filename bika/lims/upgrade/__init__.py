# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

# see https://gist.github.com/malthe/704910
import imp
import sys
from Products.CMFCore.utils import getToolByName

def create_modules(module_path):
    path = ""
    module = None
    for element in module_path.split('.'):
        path += element

        try:
            module = __import__(path)
        except ImportError:
            new = imp.new_module(path)
            if module is not None:
                setattr(module, element, new)
            module = new

        sys.modules[path] = module
        __import__(path)

        path += "."

    return module


def stub(module_path, class_name, base_class, meta_class=type):
    module = create_modules(module_path)
    cls = meta_class(class_name, (base_class, ), {})
    setattr(module, class_name, cls)


def skip_pre315(portal):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    qi = portal.portal_quickinstaller
    info = qi.upgradeInfo('bika.lims')
    if info['installedVersion'] > '315':
        return True
    return False


def upgradestep(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            p = getToolByName(context, 'portal_quickinstaller').get(upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func
