# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from setuptools import setup
from setuptools import find_packages

version = "2.1.0"

setup(
    name="senaite.core",
    version=version,
    description="SENAITE LIMS CORE",
    long_description=open("README.rst").read() + "\n" +
    open("RELEASE_NOTES.rst").read() + "\n" +
    open("CHANGES.rst").read() + "\n",
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
    ],
    keywords=["senaite", "lims", "opensource"],
    author="RIDING BYTES & NARALABS",
    author_email="senaite@senaite.com",
    url="https://github.com/senaite/senaite.core",
    license="GPLv2",
    package_dir={"": "src"},
    # packages=["bika", "bika.lims", "senaite", "senaite.core"],
    packages=find_packages(where="src", include=("senaite*", "bika*")),
    namespace_packages=["bika", "senaite"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "collective.monkeypatcher",
        "magnitude",
        "plone.api",
        "plone.app.dexterity",
        "plone.app.iterate",
        "plone.app.referenceablebehavior",
        "plone.app.relationfield",
        "plone.app.z3cform",
        "plone.jsonapi.core",
        "plone.resource",
        "plone.subrequest",
        "setuptools",
        # Products
        "Products.ATContentTypes",
        "Products.CMFEditions",
        "Products.DataGridField",
        "Products.TextIndexNG3",
        "Products.contentmigration",
        # XXX: Remove after 2.1.0
        "zopyx.txng3.ext==3.4.0",
        # tinycss2 >= 1.0.0 does not support Python 2.x anymore
        "tinycss2<1.0.0",
        # Python 2/3 compatibility library: https://six.readthedocs.io/
        "six",
        # Fix Scrutinizer (remove after we migrated to Python 3)
        # https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst#622-2020-01-02
        "Pillow<7.0.0",
        # https://pypi.org/project/more-itertools/
        "more-itertools<6.0.0",
        # cssselect2 0.3.0 does not support Python 2.x anymore
        "cssselect2<0.3.0",
        # beautifulsoup4 4.9.0 requires "soupsieve<2.0"
        "soupsieve<2.0.0",
        # TODO: better integrate just the JS files w/o this package
        "plone.app.jquerytools",
        # "collective.js.jqueryui",
        "archetypes.schemaextender",
        # SENAITE
        "senaite.lims",
        # openpyxl >= 3.0.0 does not support Python 2.x anymore
        "openpyxl==2.6.4",
        # Werkzeug >= 2.0.0 does not support Python 2.x anymore
        "Werkzeug<2.0.0",
        "collective.z3cform.datagridfield",
    ],
    extras_require={
        "test": [
            "unittest2",
            "plone.app.testing",
        ]
    },
    entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
