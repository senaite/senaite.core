# -*- coding: utf-8 -*-

from Persistence import PersistentMapping


def copyPermMap(old):
    """bullet proof copy
    """
    new = PersistentMapping()
    for k, v in old.items():
        new[k] = v
    return new
