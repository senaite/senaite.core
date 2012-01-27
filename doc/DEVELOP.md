Edit zinstance/develop.cfg
--------------------------

### In the [sources] section:

###### For readonly access

    bika.lims = git git://github.com/bikalabs/Bika-LIMS.git

Use this if you'd like to have the latest code installed, but don't have a
Github account.  The package will be updated each time you run buildout.

###### Read & write access

    bika.lims = git git@github.com:bikalabs/Bika-LIMS.git

### In the [buildout] section:

    develop =
        src/bika.lims

### i18ndude

The i18ndude tool is required only if you intend to add strings that need to
be translated.  Run locales/updatelocales.sh to update the POT/PO files.

update parts= to include i18ndude:

    parts +=
        test
        omelette
        i18ndude

And add the [i18ndude] section below it:

    [i18ndude]
    recipe = zc.recipe.egg
    eggs = i18ndude

### testing

Modify the [test] section to look like this:

    [test]
    recipe = zc.recipe.testrunner
    eggs =
        bika.lims [test]
    defaults = ['--auto-color', '--auto-progress']

You can then run bin/test to execute all tests in bika.lims

### Run buildout

    $ bin/buildout -c develop.cfg

### Start Plone in debug mode.

    $ bin/plonectl fg

Miscellaneous issues
--------------------

Indent everything (Especially TAL files!)

If filestorage files have been deleted, you may need to run:

    $ bin/plonectl adduser admin admin

If you don't have a mail server configured, you can use this command to start
a simple debug SMTP server:

    $ python -m smtpd -n -c DebuggingServer localhost:1025

Use the built-in Title and Description indexes and metadatas where possible!

    Modify using lowercase. e.g service.edit(title='Ash', description='blah')
    Access directly as attribute: service.title     service.description
    OR as method:                 service.Title()   service.Description()

    use override method to serve the title if it should be something other than
    the title - e.g the description:

    security.declarePublic('Title')
    def Title(self):
        t = self.Description()
        return t and t or ''

Adding a new Content Type
-------------------------

Adding a "Container" type, and a site-setup configlet:

The following files are modified (search them for "Container"):

    * modified:   bika/lims/__init__.py
    * modified:   bika/lims/catalog.py
    * modified:   bika/lims/controlpanel/configure.zcml
    * modified:   bika/lims/interfaces/__init__.py
    * modified:   bika/lims/profiles/default/controlpanel.xml
    * modified:   bika/lims/profiles/default/cssregistry.xml
    * modified:   bika/lims/profiles/default/factorytool.xml
    * modified:   bika/lims/profiles/default/propertiestool.xml
    * modified:   bika/lims/profiles/default/structure/bika_setup/.objects
    * modified:   bika/lims/profiles/default/types.xml
    * modified:   bika/lims/profiles/default/workflows.xml
    * modified:   bika/lims/setuphandlers.py

The following files were created:

    * bika/lims/browser/images/container.png
    * bika/lims/browser/images/container_big.png
    * bika/lims/profiles/default/structure/bika_setup/bika_containers
    * bika/lims/profiles/default/structure/bika_setup/bika_containers/.properties
    * bika/lims/profiles/default/structure/bika_setup/bika_containers/.objects
    * bika/lims/content/container.py
    * bika/lims/controlpanel/bika_containers.py
    * bika/lims/profiles/default/types/Container.xml
    * bika/lims/profiles/default/types/Containers.xml
