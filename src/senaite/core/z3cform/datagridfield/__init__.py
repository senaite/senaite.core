# -*- coding: utf-8 -*-
#
# Vendored from collective.z3cform.datagridfield 1.5.3
# https://github.com/collective/collective.z3cform.datagridfield
#
# SENAITE.CORE ships its own copy of the datagrid widget machinery to avoid
# depending on the (largely unmaintained) upstream package. Only the parts
# consumed by senaite.core are kept; the block widget, demo, GenericSetup
# profiles and transmogrify/supermodel helpers were dropped.

# The vendored modules use `_` for their message ids; reuse the existing
# senaite.core message factory instead of registering another one.
from bika.lims import senaiteMessageFactory as _  # noqa: F401
