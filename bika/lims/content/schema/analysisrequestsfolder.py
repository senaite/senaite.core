# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Schema import Schema
from plone.app.folder import folder

schema = folder.ATFolderSchema.copy() + Schema(())
