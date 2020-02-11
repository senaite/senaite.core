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

from setuptools import setup, find_packages

version = '1.3.3'

setup(
    name='senaite.core',
    version=version,
    description="SENAITE Core",
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
    keywords=['senaite', 'lims', 'opensource'],
    author="RIDING BYTES & NARALABS",
    author_email="senaite@senaite.com",
    url='https://github.com/senaite/senaite.core',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bika'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.api',
        'plone.subrequest',
        'plone.jsonapi.core',
        'Products.ATExtensions>=1.1a3',
        'Products.CMFEditions',
        'Products.DataGridField',
        'Products.TinyMCE',
        'Products.TextIndexNG3',
        'collective.monkeypatcher',
        'collective.js.jqueryui',
        'plone.app.z3cform',
        'openpyxl==1.5.8',
        'plone.app.iterate',
        'magnitude',
        'jarn.jsi18n',
        'collective.progressbar',
        'plone.app.dexterity',
        'plone.app.relationfield',
        'plone.app.referenceablebehavior',
        'five.pt==2.2.4',
        'z3c.jbot',
        'plone.resource',
        'CairoSVG==1.0.20',
        'cairocffi<1.0.0',
        'zopyx.txng3.ext==3.4.0',
        "senaite.core.supermodel>=1.2.0",
        "senaite.core.listing>=1.1.0",
        "senaite.core.spotlight",
        # Python 2.x is not supported by WeasyPrint v43
        'WeasyPrint==0.42.3',
        # tinycss2 >= 1.0.0 does not support Python 2.x anymore
        'tinycss2<1.0.0',
        # Add this line *after* senaite.impress 1.2.0 was realeased!
        'senaite.impress>=1.2.0',
        # Python 2/3 compatibility library: https://six.readthedocs.io/
        'six',
        # Needed for `IPortalCatalogQueueProcessor`, which will be included in
        # `Products.CMFCore` in Plone 5. Remove after we are on Plone 5!
        'collective.indexing',
        # Fix Scrutinizer (remove after we migrated to Python 3)
        # https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst#622-2020-01-02
        'Pillow<7.0.0',
        # https://pypi.org/project/more-itertools/
        'more-itertools<6.0.0'
    ],
    extras_require={
        'test': [
            'unittest2',
            'plone.app.testing',
        ]
    },
    entry_points="""
          # -*- Entry points: -*-
          [z3c.autoinclude.plugin]
          target = plone
          """,
)
