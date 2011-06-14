from setuptools import setup, find_packages
import os

version = '3.0pre-alpha'

setup(name='bika.lims',
      version=version,
      description="Bika LIMS",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='bika lims',
      author='Bika Lab Systems',
      author_email='support@bikalabs.com',
      url='www.bikalabs.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.ATExtensions',
#          'five.grok',
          'reportlab',
      ],
      entry_points="""
      # -*- Entry points: -*-
	[z3c.autoinclude.plugin]
        target = plone
      """,
      )
