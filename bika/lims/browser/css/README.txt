README for the 'browser/css/' directory
===============================================

This folder is a Zope 3 Resource Directory acting as a repository for
css.

Its declaration is located in 'browser/configure.zcml':

    <!-- Resource directory for css -->
    <browser:resourceDirectory
        name="bika.lims.css"
        directory="css"
        layer=".interfaces.IThemeSpecific"
        />

A stylesheet placed in this directory (e.g. 'main.css') can be accessed from
this relative URL:

    "++resource++bika.lims.css/main.css"

Note that it might be better to register each of these resources separately if
you want them to be overridable from zcml directives.

The only way to override a resource in a resource directory is to override the
entire directory (all elements have to be copied over).

A Zope 3 browser resource declared like this in 'browser/configure.zcml':

    <browser:resource
        name="main.css"
        file="css/main.css"
        layer=".interfaces.IThemeSpecific"
        />

can be accessed from this relative URL:

    "++resource++main.css"

Notes
-----

* Stylesheets registered as Zope 3 resources might be flagged as not found in
  the 'portal_css' tool if the layer they are registered for doesn't match the
  default skin set in 'portal_skins'.
  This can be confusing but it must be considered as a minor bug in the CSS
  registry instead of a lack in the way Zope 3 resources are handled in
  Zope 2.

* There might be a way to interpret DTML from a Zope 3 resource view.
  Although, if you need to use DTML for setting values in a stylesheet (the
  same way as in default Plone css where values are read from
  'base_properties'), it is much easier to store it in a directory that is
  located in the 'skins/' folder of your package, registered as a File System
  Directory View in the 'portal_skins' tool, and added to the layers of your
  skin.

* Customizing/overriding css that are originally accessed from the
  'portal_skins' tool (e.g. Plone default css) can be done inside that
  tool only. There is no known way to do it with Zope 3 browser resources.
  Vice versa, there is no known way to override a Zope 3 browser resource from
  a skin layer in 'portal_skins'.
