Windows Installation
--------------------

#### 1. Download and run the Plone Unified Installer:

    https://launchpad.net/plone/4.2/4.2/+download/setup-plone42-4.2.0-5363-win32.exe

#### 2. Install Gnuplot:

Visit http://gnuplot.sourceforge.net/

#### 3. Install Bika LIMS:

Edit c:\Plone4\buildout.cfg and add "bika.lims" to the eggs section:

    eggs =
        ...
        bika.lims

#### 4. Run buildout:

First, start an administrator command prompt: Click Start, locate the
"Command Prompt" entry, right click on it, and select "Run as
Administrator" from the dropdown menu

Then type the following commands:

    C:\> cd \Plone41
    C:\Plone41> bin\buildout.exe

It's important that the buildout.cfg is in the current directory when you run
this command.

The buildout will download all dependencies.  If the downloads are interrupted,
they will resume when bin\buildout is run again.

You'll see some SyntaxErrors like:  "Return outside function" etc.  Ignore them.

#### 5. Start Plone:

    Plone is configured as a Windows Service by default - restart it.

    If you want to run Plone in the foreground (debug mode), then you need
    to stop the Plone service first.  Then, run:

    C:\Plone4> bin\plonectl fg

#### 6. Add a new site:

Visit http://localhost:8080 and add a new site.  Be sure to select the
checkbox for the Bika LIMS extension profile.  No other add-ons need to
be installed - dependencies are installed automatically.

"bika" is a reserved word, and cannot be used for a site id.

#### 7. Test:

Visit http://localhost:8080 and view your site.

Issues:
-------

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

