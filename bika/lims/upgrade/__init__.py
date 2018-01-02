# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
    from bika.lims.upgrade.utils import UpgradeUtils
    ut = UpgradeUtils(portal)
    return ut.isOlderVersion('bika.lims', '315')


def upgradestep(upgrade_product, version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context, *args):
            p = getToolByName(context, 'portal_quickinstaller').get(upgrade_product)
            setattr(p, 'installedversion', version)
            return fn(context, *args)
        return wrap_func_args
    return wrap_func
