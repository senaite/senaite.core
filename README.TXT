Bika3 SVN buildout
==================

1.  Install Plone 4.
2.  Edit base.cfg, changing the eggs-directory and download-cache directives to
    point to the location of your Plone installation
3.  Run `path-to-plone4/Python-2.6/bin/python bootstrap.py`
4.  Run `bin/buildout -c develop.cfg`
5.  Run `bin/plonectl fg`

