# This file is part of Bika LIMS Evo
#
# Copyright 2017 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from setuptools import setup, find_packages

version = '1.2.2'

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
    author='SENAITE Foundation',
    author_email='support@senaite.com',
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
        'Products.AdvancedQuery',
        'Products.TinyMCE',
        'collective.monkeypatcher',
        'collective.js.jqueryui',
        'plone.app.z3cform',
        'openpyxl==1.5.8',
        'plone.app.iterate',
        'magnitude',
        'gpw',
        'jarn.jsi18n',
        'WeasyPrint==0.42',
        'collective.progressbar',
        'z3c.unconfigure==1.0.1',
        'plone.app.dexterity',
        'plone.app.relationfield',
        'plone.app.referenceablebehavior',
        'five.pt==2.2.4',
        'z3c.jbot',
        'plone.resource',
        'CairoSVG==1.0.20',
        'collective.taskqueue',
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
