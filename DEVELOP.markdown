1.  Title and Description
    Use the built-in title and description fields as much as possible. 
    Modify using lowercase. e.g service.edit(title='Ash', description='blah')
    Access directly as attribute: service.title     service.description
    OR as method:                 service.Title()   service.Description()
    
    use override method to serve the title if it should be something other than
    the title - e.g the description

    security.declarePublic('Title')
    def Title(self):
        t = self.Description()
        return t and t or ''

2.  Indent tal files!

Plone 4 development setup
=========================

1. First follow normal Installation instructions.
2. Run ```cd /usr/local/Plone/zinstance```
3. Run ```bin/buildout -n -c ../eggs/bika.lims-3.0a1/bika/lims/buildout/develop.cfg```
4. Run ```bin/plonectl fg``` or ```bin\instance console```


If filestorage files have been deleted, you may need to run:

    bin/plonectl adduser admin admin

Windows Installer Issue
=======================

If the Zope/Plone instance fails to start (you get a message
saying "Please stop the service first"):

    1. Find the running process id by opening the .pid file within 
    your instance's var/ directory.
    2. Open the Windows Task Manager and stop the running process with
    the above identifier.
    3. Delete all .pid and .lock files in your instance's var/ directory.
    4, Start your instance.

Running in foreground will by default set debug mode to be on for
resource registries.  This is tragically slow; Turn off registry
debugging in ZMI at /portal_css  and at /portal_javascripts (must 
be done after every server start).

You could also do the following to boost Windows performance radically:

    In file: Products/CMFCore.DirectoryView:
    In function: DirectoryInformation._changed():
    comment out the whole whole block that begins with:
        if platform == 'win32':

    (this workaround will no longer be needed in Plone 4.2, i.e. CMF 2.3)

