from setuptools import setup, find_packages

version = '3.1.4.1'

setup(name='bika.lims',
      version=version,
      description="Bika LIMS",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Development Status :: 5 - Production/Stable",
      "Environment :: Web Environment",
      "Intended Audience :: Information Technology",
      "Intended Audience :: Science/Research",
      "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
      ],
      keywords='Bika Open Source LIMS',
      author='Bika Laboratory Systems',
      author_email='support@bikalabs.com',
      url='www.bikalabs.com',
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
          'collective.wtf',
          'WeasyPrint==0.19.2',
          'collective.progressbar',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'robotsuite',
              'robotframework',
              'robotframework-selenium2library',
              'plone.app.robotframework',
              'Products.PloneTestCase',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
