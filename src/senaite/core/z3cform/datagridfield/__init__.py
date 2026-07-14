# -*- coding: utf-8 -*-
#
# Vendored from collective.z3cform.datagridfield 1.5.3
# https://github.com/collective/collective.z3cform.datagridfield
#
# SENAITE.CORE ships its own copy of the datagrid widget machinery to avoid
# depending on the (largely unmaintained) upstream package. Only the parts
# consumed by senaite.core are kept; the block widget, demo, GenericSetup
# profiles and transmogrify/supermodel helpers were dropped.

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("senaite.core")
