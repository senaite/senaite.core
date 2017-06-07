# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.public import Schema
from bika.lims.content.abstractroutineanalysis import schema

schema = schema.copy() + Schema(())
