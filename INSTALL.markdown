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

* 1. Download and install the Unified Installer from http://plone.org/products ::

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

* 2. Edit Plone/zinstance/buildout.conf

  Find the ``eggs`` section.  Add ``bika.lims``::

    eggs =
        Plone
        Pillow
        bika.lims

* 3. Run buildout::

    sudo bin/buildout

* 4 Start Plone

    # start in foreground (debug) mode:
    $ bin/plonectl fg

    # start normally:
    $ bin/plonectl start

* 5 Add Bika instance

    Add a new plone site.  Assign an ID of your choice, and select
    the checkbox to activate the Bika-LIMS extension profile.

    That's it.  You should be able to test the site now by visiting
    http://localhost:8080/SITE_ID

* 6. (Optional) Set up a domain name::

    Set up a domain name for the LIMS site URL and add the Apache mapping
    noting the Zope server port used by the instance (default 8080)

    Edit the apache configuration, adding a new virtual host

   ``sudo vim /etc/apache2/sites-enabled/000-default``

   Add directives, ensuring an existing port is not conflicted::

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

* 7. (Optional) Change the port in buildout.cfg if port 8080 is already used::

    http-address = 8080

* 8. (Optional) Change the ``effective-user`` if ``plone`` is not the one used.

* 9. (Optional) Add the environment-vars entry for the ID-server, noting port number::

    [instance]
    environment-vars =
           IDServerURL http://localhost:8081

The ID-Server is now by default automatically built
and started as part of the Zope/Plone instance but can
optionally still be deployed in a clustering setup.

See https://github.com/bikalabs for other install options, especially
https://github.com/bikalabs/Bika-3-Buildout which automates most
of the steps below and also installs the /Bika Plone instance.

* 10. (Optional) Test and reload apache config::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

* 11. Test run in foreground, noting error messages if any and taking
   corrective action if so ::

    sudo bin/plonectl fg
    ...
    2012-01-11 12:06:07 INFO Zope Ready to handle requests

* 12. Access the Zope instance via Apache::

    Via a web browser on public URL http://admin:admin@example.bikalabs.com/manage/ ::

    Or localhost address at http://admin:admin@localhost:8080/manage/ ::

* 13. Add the Plone instance with Bika LIMS extensions::

If not automatically created by the buildout process yet, add a Plone instance,
noting the instance name (default Plone, or Bika) and ensure that the Bika LIMS option is ticked.

* 14. (Optional) Modify Apache web server configuration to point to instance root::

Point to the instance "Plone" or "Bika" root instead of Zope root if required
by changing the Apache rewrite rule::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Bika/VirtualHostRoot/$1 [L,P]

* 15. Reload the Apache webserver's configuration::

    sudo apache2ctl graceful

* 16. (Optional) Stop the foreground instance (Control C), and restart it as a background process.

    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

    Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

* 17. To start with a completely fresh instance::

    Rename/move the Data.fs.* files in var/filestorage (after stopping instance).


Windows
=======

1. Install Bika LIMS
--------------------

Open the buildout.cfg file for your new Plone instance.

Update CHANGELOG
================
    $ cd src/bika.lims
    $ git log master --since=01/01/2010 --pretty=format:"%ad%n==========%n%s%+N" --date=short --no-merges >> CHANGELOG.rst

set --since parameter to reflect the date of the last update to the CHANGELOG.

Test Coverage reports
=====================

    $ cd zinstance
    $ bin/test --coverage=~/bika-test-coverage

Create a directory within your previously created coverage directory.  We call it reports.  Run the coveragereport.py module with the source being you coverage output and the destination, your newly created reports directory.  See the following:

$ svn co  svn://svn.zope.org/repos/main/z3c.coverage/trunk z3c.coverage
$ mkdir ~/bika-test-coverage/reports
$ python ~/z3c.coverage/src/z3c/coverage/coveragereport.py ~/bika-test-coverage ~/bika-test-coverage/reports

