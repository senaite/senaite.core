Bika LIMS
=========

Bika Laboratory Information Management System.

Installation
============

This document describes the installation of Bika LIMS
from the Plone Unified Installer package for Unix/Linux
servers, as well as the setup for Apache as web proxy to
make the LIMS available on the standard http port 80.
The process should be similar for MacOSX and other Unix-type
operating systems.

Prerequisites
-------------

    Plone >= 4.1

Quick Installation
------------------

Download and install the Unified Installer from http://plone.org/products

    $ tar xzf Plone-4.1.3-UnifiedInstaller.tgz
    $ cd Plone-4.1.3-UnifiedInstaller

    # normal install:

    $ sudo ./install.sh --password=admin standalone

    # Ubuntu users need to run the installer like this ::

    $ sudo ./install.sh --password=admin --libz=yes --lxml=yes standalone

You should see text like this:

    ######################  Installation Complete  ######################
    Plone successfully installed at /usr/local/Plone
    See /usr/local/Plone/zinstance/README.html
    for startup instructions

    Use the account information below to log into the Zope Management Interface
    The account has full 'Manager' privileges.

    Username: admin
    Password: admin
    ...

Edit Plone/zinstance/buildout.conf

    Find the `eggs` section.  Add `bika.lims`

    eggs =
        Plone
        Pillow
        lxml
        bika.lims

Run buildout

    sudo bin/buildout

Start Plone

    # start in foreground (debug) mode:
    $ bin/plonectl fg

    # start normally:
    $ bin/plonectl start

Add Bika instance

    Add a new plone site.  Assign an ID of your choice, and select
    the checkbox to activate the Bika-LIMS extension profile.

    That's it!
    
    You should be able to test the site now by visiting
    http://localhost:8080/SITE_ID

(Optional) Set up a domain name

    Set up a domain name for the LIMS site URL and add the Apache mapping
    noting the Zope server port used by the instance (default 8080)

    Edit the apache configuration, adding a new virtual host

   `sudo vim /etc/apache2/sites-enabled/000-default`

(Optional) Add directives, ensuring an existing port is not conflicted::

    <VirtualHost*:80>
      ServerName  example.bikalabs.com
      ServerAdmin webmaster@bikalabs.com
      ErrorLog /var/log/apache2/example.bikalabs.com.error.log
      LogLevel warn
      CustomLog /var/log/apache2/example.bikalabs.com.access.log combined
      RewriteEngine On
      RewriteRule ^/robots.txt -  [L]
      RewriteRule ^/manage(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80 /VirtualHostRoot/manage$1 [L,P]
      RewriteRule ^/(.\*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    </VirtualHost>

(Optional) Change the port in buildout.cfg if port 8080 is already used

    http-address = 8080

(Optional) Change the `effective-user` if `plone` is not the one used.

    effective-user = cb

(Optional) Add the environment-vars entry for the ID-server, noting port number

    [instance]
    environment-vars =
           IDServerURL http://localhost:8081

    The ID-Server is now by default automatically built
    and started as part of the Zope/Plone instance but can
    optionally still be deployed in a clustering setup.

    See https://github.com/bikalabs for other install options, especially
    https://github.com/bikalabs/Bika-3-Buildout which automates most
    of the steps below and also installs the /Bika Plone instance.

(Optional) Test and reload apache config

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

Test run in foreground, noting error messages if any and taking corrective action 

    sudo bin/plonectl fg

Access the Zope instance via Apache

    Via a web browser on public URL http://admin:admin@example.bikalabs.com/manage/

Or via Zope:

    Or localhost address at http://admin:admin@localhost:8080/manage/

And add a Plone instance with Bika LIMS extensions pre-activated

If it hasn't been automatically created by the buildout process yet, add a Plone instance,
noting the instance name (default Plone, or Bika) and ensure that the Bika LIMS option is ticked.

(Optional) Modify Apache web server configuration to point to instance root

    Point to the instance "Plone" or "Bika" root instead of Zope root if required
    by changing the Apache rewrite rule::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Bika/VirtualHostRoot/$1 [L,P]

Reload the Apache webserver's configuration::

    sudo apache2ctl graceful

(Optional) Stop the foreground instance (Control C), and restart it as a background process.

    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

    Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

To start with a completely fresh instance::

    Rename/move the Data.fs.* files in var/filestorage (after stopping instance).

Windows
=======

If the Zope/Plone instance fails to start (you get a message
saying "Please stop the service first"):

    1. Find the running process id by opening the .pid file within
    your instance's var/ directory.
    2. Open the Windows Task Manager and stop the running process with
    the above identifier.
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

    (this workaround will no longer be needed in Plone 4.2, i.e. CMF 2.3)
