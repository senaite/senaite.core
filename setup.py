# This file is part of Bika LIMS Evo
#
# Copyright 2017 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from setuptools import setup, find_packages

version = '1.1.8'

setup(name='bika.lims',
      version=version,
      description="Bika LIMS Evo",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read() + "\n",
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
          "Programming Language :: Python",
      ],
      keywords=['lims', 'bika', 'opensource'],
      author='Naralabs',
      author_email='support@naralabs.com',
      url='https://github.com/naralabs/bika.lims',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
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
          'jarn.jsi18n==0.3',
          'WeasyPrint==0.19.2',
          'collective.progressbar',
          'z3c.unconfigure==1.0.1',
          'plone.app.dexterity',
          'plone.app.relationfield',
          'plone.app.referenceablebehavior',
          'five.pt',
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
