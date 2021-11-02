# -*- coding: utf-8 -*-

import re

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import api
from Products.Archetypes.utils import shasattr
from senaite.core import logger

TMP_RX = re.compile("[a-z0-9]{32}$")


def is_tmp_id(id):
    return TMP_RX.match(id)


def isTemporary(self):
    parent = aq_parent(aq_inner(self))
    # Fix indexing of temporary objects resulting in orphan entries in catalog
    # https://github.com/senaite/senaite.core/pull/1865
    if is_tmp_id(self.id) or is_tmp_id(parent.id):
        logger.debug("Object %s is temporary!" % api.get_path(self))
        return True
    # Checks to see if we are created as temporary object by
    # portal factory.
    tmp = shasattr(parent, "meta_type") and parent.meta_type == "TempFolder"
    return tmp


