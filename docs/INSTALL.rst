Installing Bika LIMS
====================

The process should be similar for all systems on which Plone is supported.

Linux Installation Steps
------------------------

1. Plone and Bika LIMS have some system dependencies

    The following list of packages need to be installed.  The package list is valid
    for Ubuntu 14.04. If you use a different distribution, you may need to find the
    versions of these packages which are provided with your system. ::

       sudo apt-get install python-dev build-essential libffi-dev libpcre3-dev gcc
       sudo apt-get install autoconf libtool pkg-config zlib1g-dev git-core libssl-dev
       sudo apt-get install libexpat1-dev libxslt1.1 gnuplot libpcre3 libcairo2
       sudo apt-get install libpango1.0-0 libgdk-pixbuf2.0-0

2. Install Plone

    Download the latest stable version of the
    `Plone Unified Installer <http://plone.org/products/plone/releases>`_.
    You should also read the
    `Plone Installation Documentation <http://docs.plone.org/manage/installing/index.html>`_.

    A basic command for installing a development environment in Linux::

        ./install.sh --target=/path/to/Plone --build-python --static-lxml zeo

3. Add Bika LIMS to your buildout.cfg

    Change directory to ``Plone/zeocluster``, and edit ``buildout.cfg``.

    Find the section beginning with ``eggs =``, and add ``bika.lims`` to the existing
    entries::

        eggs =
            Plone
            Pillow
            bika.lims

    Indentation in buildout.cfg is important, and should be kept uniform for all lines.

    Save the file, and then run bin/buildout again.  Buildout will download and install
    all remaining dependencies.

    If the download is interrupted, simply run bin/buildout again.  The process will
    be resumed.

    Spurious errors may occur while running buildout, and may be safely ignored. Verify
    successful build from the output of the buildout script, which should  include a
    list of found versions like this::

        *************** PICKED VERSIONS ****************
        [versions]
        Babel = 1.3
        CairoSVG = 1.0.7
        Products.ATExtensions = 1.1
        Products.AdvancedQuery = 3.0.3
        PyYAML = 3.11
        Pygments = 1.6
        Pyphen = 0.9.1
        Werkzeug = 0.9.4
        argh = 0.24.1
        bpython = 0.13
        cairocffi = 0.5.3
        cffi = 0.8.2
        collective.progressbar = 0.5
        collective.wtf = 1.0b9
        cssselect = 0.9.1
        gpw = 0.2
        i18ndude = 3.3.3
        magnitude = 0.9.3
        pathtools = 0.1.2
        plone.api = 1.1.0
        plone.jsonapi.core = 0.4
        *************** /PICKED VERSIONS ***************

    If the buildout finished successfully, an 'adminPassword.txt' will have been
    created automatically inside the Plone instance folder. It contains the super-user
    credentials you'll need to create the Bika site.

4. Test your setup

    First, start the ZEO Server::

        bin/plonectl zeoserver start

    Then you must start one ZEO Client in the foreground, noting error messages if any
    and taking corrective action if so::

        bin/plonectl client1 fg

    If you see ``INFO Zope Ready to handle requests`` then the server is running.
    Press Control+C to stop the foreground client.

    To start the Plone server normally, use the following command::

        bin/plonectl start

5. Add a new Plone/Bika instance.

    Open a browser and go to http://localhost:8080/.  Select "Add Plone Site",
    and ensure that the Bika LIMS option is checked, then submit the form.

Windows Installation Steps
--------------------------

1. Download and Install Plone

    Currently Bika LIMS for Windows requires a Plone 4.3.1 installation.

    * Download the `Windows Installer <http://plone.org/products/plone/releases/4.3.1>`_
    * Execute the installer and follow through the steps

    For this guide we will assume the default location of `C:\Plone43`

    For more information visit: http://docs.plone.org/manage/installing/index.html

2. Installing Bika LIMS

    1. Open ``C:\Plone43\buildout.cfg`` in a text editor

    2. Find the section beginning with ``eggs =``, and add ``bika.lims`` to the existing
       entries::

        eggs =
            Plone
            Pillow
            bika.lims

    3. Run buildout from cmd (press ``⊞ Win``, type ``cmd``, press ``↵ Enter``)::

        C:> cd C:\Plone43
        C:\Plone43> bin\buildout.exe

    4. A successful buildout should output::

        Updating run-instance.
        Updating service.
        *************** PICKED VERSIONS ****************
        [versions]
        bika.lims = 3.0
        cairocffi = 0.5.4
        cairosvg = 1.0.7
        cssselect = 0.9.1
        gpw = 0.2
        magnitude = 0.9.3
        products.advancedquery = 3.0.3
        products.atextensions = 1.1
        pycparser = 2.10
        pyphen = 0.9.1
        *************** /PICKED VERSIONS ***************

    If you see the following errors: ``Error: Couldn't install: cffi 0.8.2`` or
    ``Error 5: Access is denied`` refer to Troubleshooting below.

3. Setting up Plone Services

    1. Run cmd as Administrator (press ``⊞ Win``, type: ``cmd``, press ``CTRL``+``⇧ Shift``+``↵ Enter``)

    2. Navigate to the Plone root directory::

        C:\> cd C:\Plone43

    3. Install, Start and bring your newly created instance to the Foreground
       This should stop the default Plone 4.3 Service::

           C:\Plone43> bin\instance.exe install
           C:\Plone43> bin\instance.exe start
           C:\Plone43> bin\instance.exe fg

       If you see ``INFO Zope Ready to handle requests`` then the server is running

4. Add a new Plone/Bika instance.

    Open a browser and go to http://localhost:8080/.  Select "Add Plone Site",
    and ensure that the Bika LIMS option is checked, then submit the form.

Upgrading Bika LIMS
-------------------

If a new release of the LIMS is made available, the following procedure will
upgrade your existing installation to use the new packages.

1. Backup

    Stop Plone, and make a full backup of your instance before continuing::

        bin/plonectl stop
        bin/fullbackup

2. Buildout

    Run buildout with the "-n" option, to retreive the latest version of Bika
    LIMS and it's dependencies::

        bin/buildout -n

3. Restart Plone

    Just as during the installation, it's useful to start a single zeo client
    in the foreground to check for errors:

        bin/plonectl client1 stop
        bin/plonectl client1 fg

    To restart Plone issue a command like this:

        bin/plonectl restart

4. Migrate

    Go to site-setup, and click ``Add-ons``.  Find Bika LIMS in the list of
    activated addons, and click the ``bika.lims`` upgrade button.

Installing Bika-LIMS source
---------------------------

You should already have Plone and Bika LIMS installed.  The paths and commands
below are for Linux, but following along in windows is simple.

1. Download source::

    cd Plone/zeocluster/src
    git clone https://github.com/bikalabs/Bika-LIMS.git bika.lims

2. Select a git branch::

    We use git-flow to manage the git repository, with some quirks.  The ``next``
    branch contains code for the next hotfix or release, and ``develop`` contains
    unreleased code merged from ``feature/*`` branches. ::

        git checkout develop

3. Edit ``buildout.cfg``::

    develop =
        src/bika.lims

4. Restart Plone

    bin/plonectl restart all

The Bika LIMS distribution in Plone/buildout-cache/eggs/bika.lims* will now be
ignored by Plone, and the copy in src/bika.lims is used instead.

Troubleshooting
---------------

    (Windows) Dependencies ::

        You need to install some dependencies manually
        Download and install _bika_dependencies(Plone 4.3.1).exe_ from https://github.com/zylinx/bika.dependencies
        This fixes the fact that Plone's buildout cannot compile the libraries required by weasyprint.
        It installs the pre-compiled binaries into System32 and Plone's installation folder instead.

    (Windows) Privileges ::

        Open ``Explorer`` >> Navigate to ``C:\`` >> Right-Click on the ``Plone43`` directory >> select ``roperties``
        Select the ``Security`` Tab >>  Click ``Edit``  >> Check ``Full Control`` Allow for necessary User / Group
        Click  ``Apply``

    (Windows) If you are having trouble starting ``bin\instance.exe fg`` as follows::

        The program seems already to be running. If you believe not,
        check for dangling .pid and .lock files in var/.

        * You can try the following steps:

            -Find the running process id by opening the .pid file within your instance's var/ directory.
            -Open the Windows Task Manager and stop the running process with the above identifier.
            -Delete all .pid and .lock files in your instance's var/ directory.
            -Start your instance.

        * OR::

            -Run services.msc
            -Search for Plone 4.3
            -Try Starting or Stopping it along with your instance

    To empty/reset the database, run the following::

        rm -rf var/filestorage
        bin/buildout

    If your admin user does not exist or you forget the password::

        bin/plonectl adduser admin admin

    AttributeError: type object 'IIdServer' has no attribute '__iro__' ::

        * The code for "bika.lims" not installed or not included
        * Running buildout again usually fixes this


Log errors to sentry.bikalabs.com
---------------------------------

Add raven to your buildout.cfg in the ``eggs =`` section::

    eggs =
        ...
        raven

Then add the following snippet to your [instance] section.  If you are using a
ZEO configuration, add this to all [clientX] sections::

    event-log-custom =
        %import raven.contrib.zope
        <logfile>
          path ${buildout:directory}/var/client1/event.log
          level INFO
          max-size 5 MB
          old-files 5
        </logfile>
        <sentry>
          dsn http://90723864025d4520b084acee225ddb8a:f9f7dd0163a74fbeac4e24a5123b3d39@sentry.bikalabs.com/2
          level ERROR
        </sentry>

Add raven 4.0.4 into [versions] section::

    [versions]
        ...
        raven = 4.0.4

Run bin/buildout, and restart Plone.
