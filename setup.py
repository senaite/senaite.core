from setuptools import setup, find_packages

version = '3.0rc3.5.2'

setup(name='bika.lims',
      version=version,
      description="Bika LIMS",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
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
          'Products.ATExtensions>=1.1a3',
          'Products.CMFEditions',
          'Products.AdvancedQuery',
          'Products.TinyMCE',
          'collective.monkeypatcher',
          'collective.js.jqueryui',
          'plone.app.z3cform',
          'openpyxl==1.5.8',
          'plone.app.iterate',
          'xhtml2pdf',
          'magnitude',
          'gpw',
          'jarn.jsi18n==0.3',
      ],
      extras_require={
          'test': [
                  'plone.app.testing',
                  'plone.app.robotframework',
              ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
