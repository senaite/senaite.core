Plone 4 development setup
=========================

Edit Plone/zinstance/develop.cfg

- In [sources], add one of the following:

    # readonly access
    bika.lims = git git://github.com/bikalabs/Bika-LIMS.git branch=master

    # normal access
    bika.lims = git git@github.com:bikalabs/Bika-LIMS.git branch=master

You can replace "master" with "dev" if you'd like to test the latest
(unstable) code.

- In [buildout], add or edit the develop= section:

    develop =
        src/bika.lims

- Run buildout

    bin/buildout -c develop.cfg

Start Plone as normal.

Miscallanious issues
--------------------
- If filestorage files have been deleted, you may need to run:

    bin/plonectl adduser admin admin

- If you don't have a mail server configured, you can use this command
to start a simple debug SMTP server:

    python -m smtpd -n -c DebuggingServer localhost:1025

- To update the CHANGELOG use `git log`.  Set the --since parameter to
reflect the date of the previous most recent update to the CHANGELOG.

    $ cd Plone/zinstance/src/bika.lims
    $ git log master --since=01/01/2010 --pretty=format:"%ad%n==========%n%s%+N" --date=short --no-merges > CHANGELOG.tmp

Then merge the new information from CHANGELOG.tmp into the existing CHANGELOG.markdown,
and remove the temporary file.

- Title and Description - Use the built-in indexes and metadatas where possible.

    Modify using lowercase. e.g service.edit(title='Ash', description='blah')
    Access directly as attribute: service.title     service.description
    OR as method:                 service.Title()   service.Description()

    use override method to serve the title if it should be something other than
    the title - e.g the description

    security.declarePublic('Title')
    def Title(self):
        t = self.Description()
        return t and t or ''

- Indent TAL files!

Add a new AT Content Type
=========================

example: Container (and bika_containers site-setup folder)

Modified files: (search for "container"):

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

Newly added files:

    * bika/lims/browser/images/container.png
    * bika/lims/browser/images/container_big.png
    * bika/lims/profiles/default/structure/bika_setup/bika_containers
    * bika/lims/profiles/default/structure/bika_setup/bika_containers/.properties
    * bika/lims/profiles/default/structure/bika_setup/bika_containers/.objects
    * bika/lims/content/container.py
    * bika/lims/controlpanel/bika_containers.py
    * bika/lims/profiles/default/types/Container.xml
    * bika/lims/profiles/default/types/Containers.xml
