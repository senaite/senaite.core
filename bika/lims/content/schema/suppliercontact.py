# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""The contact person at a reference supplier organisation.
"""
from bika.lims.content.person import Person

schema = Person.schema.copy()

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'

schema['id'].schemata = 'default'
schema['id'].widget.visible = False
# Don't make title required - it will be computed from the Person's
# Fullname
schema['title'].schemata = 'default'
schema['title'].required = 0
schema['title'].widget.visible = False
