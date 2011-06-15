README for the 'browser/images/' directory
==========================================

This folder is a Zope 3 Resource Directory acting as a repository for images.

Its declaration is located in 'browser/configure.zcml':

    <!-- Resource directory for images -->
    <browser:resourceDirectory
        name="bika.lims.images"
        directory="images"
        layer=".interfaces.IThemeSpecific"
        />

An image placed in this directory (e.g. 'logo.png') can be accessed from
this relative URL:

    "++resource++bika.lims.images/logo.png"

Note that it might be better to register each of these resources separately if
you want them to be overridable from zcml directives.

The only way to override a resource in a resource directory is to override the
entire directory (all elements have to be copied over).

A Zope 3 browser resource declared like this in 'browser/configure.zcml':

    <browser:resource
        name="logo.png"
        file="images/logo.png"
        layer=".interfaces.IThemeSpecific"
        />

can be accessed from this relative URL:

    "++resource++logo.png"

Notes
-----

* Whatever the way they are declared (in bulk inside a resource directory or
  as separate resources), images registered as Zope 3 browser resources don't
  have all the attributes that Zope 2 image objects have (i.e. the 'title'
  property and the 'tag()' and 'get_size()' methods).
  This means that if you want the html tag of your image to be auto-generated
  (this is the case by default for the portal logo), you should store it in a
  directory that is located in the 'skins/' folder of your package, registered
  as a File System Directory View in the 'portal_skins' tool, and added to the
  layers of your skin.

* Customizing/overriding images that are originally accessed from the
  'portal_skins' tool (e.g. Plone default logo and icons) can be done inside
  that tool only. There is no known way to do it with Zope 3 browser
  resources.
  Vice versa, there is no known (easy) way to override a Zope 3 browser
  resource from a skin layer in 'portal_skins'.
