Development setup
-----------------

### develop.cfg - in the [sources] section:

###### For readonly access add the following line:

    bika.lims = git git://github.com/bikalabs/Bika-LIMS.git branch=dev

Use this if you'd like to have the latest code installed, but don't have a
Github account.  The package will be updated each time you run buildout.

###### For read/write access add the following line:

    bika.lims = git git@github.com:bikalabs/Bika-LIMS.git branch=dev

Use this if you have a github account configured, and will be pushing your
changes back to the server.

### develop.cfg - in the [buildout] section:

Add bika.lims:

    develop =
        src/bika.lims

### Run buildout

Specify develop.cfg on the command line like this:

    $ bin/buildout -c develop.cfg

### Start Plone in debug mode.

    $ bin/plonectl fg

Miscellaneous issues
--------------------

Indent everything (Especially TAL files!)

If filestorage files have been deleted/recreated, you may get an
admin password prompt which never succeeds.  You need to run:

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

### i18ndude

The i18ndude tool is required only if you intend to add strings that need to
be translated.

To Automatically recompile .mo files during development, edit your
buildout.cfg to include the zope_i18n_compile_mo_files variable.

    [buildout]
    environment-vars =
        zope_i18n_compile_mo_files true

Update your develop.cfg:

    parts =
        ...
        i18ndude

    [i18ndude]
    unzip = true
    recipe = zc.recipe.egg
    eggs = i18ndude

After this you can use locales/updatelocales.sh to update the POT/PO files.

### testing

Modify the [test] section to look like this:

    [test]
    recipe = zc.recipe.testrunner
    eggs =
        bika.lims [test]
    defaults = ['--auto-color', '--auto-progress']

You can then run bin/test to execute all tests in bika.lims
