# -*- coding: utf-8 -*-

from bika.lims.api import user as userapi
from DateTime import DateTime


def user_added_to_group(principal, event):
    user = userapi.get_user(principal)
    user.setModificationDate(DateTime())


def user_removed_from_group(principal, event):
    user = userapi.get_user(principal)
    user.setModificationDate(DateTime())
