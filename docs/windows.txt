If the Zope/Plone instance fails to start (you get a message saying
"Please stop the service first"):

1. Find the running process id by opening the .pid file within your instance's var/ directory.
2. Open the Windows Task Manager and stop the running process with the above identifier.
3. Delete all .pid and .lock files in your instance's var/ directory.
4. Start your instance.

Running in foreground will by default set debug mode to be on for
resource registries.  This is tragically slow; Turn off registry
debugging in ZMI at /portal_css  and at /portal_javascripts (must
be done after every server start).

You could also do the following to boost Windows performance:

In file: Products/CMFCore.DirectoryView:
In function: DirectoryInformation._changed():

comment out the whole whole block that begins with:

    if platform == 'win32':
