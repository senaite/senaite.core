Bika LIMS
============
This document describes the installation of Bika LIMS 
(Laboratory Information Management System) on a Unix server.
The ID-Server is now by default automatically built
and started as part of the Zope/Plone instance but can
optionally still be deployed in a clustering setup. 

See https://github.com/bikalabs for other install options, especially 
https://github.com/bikalabs/Bika-3-Buildout which automates most
of the steps below and also installs the /Bika Plone instance.

Installation
------------
This document details the installation steps for Bika LIMS version 3 
from the Plone Unified Installer package for Linux, as well as the 
setup for Apache as web proxy to make the LIMS available on the 
standard http port 80. The process should be similar for MacOSX and
other Unix-type operating systems. The gcc compiler, python2.6, 
the python-dev library and git is required and you could use that
already installed on your operating system.

#. Download the Unified Installer from plone.org::

    http://plone.org/products (tested with any version >= 4.1)

#. Untar the archive an run the installer::

    $ tar xzf Plone-4.1.3-UnifiedInstaller.tgz
    $ cd Plone-4.1.3-UnifiedInstaller

    $ sudo ./install.sh --password=admin standalone

    or (ubuntu):
    
    $ sudo ./install.sh --password=admin --libz=yes --lxml=yes standalone

#. (Optional) Set up a domain name::

    Set up a domain name for the LIMS site URL and add the Apache mapping
    noting the Zope server port used by the instance (default 8080) 

    Edit the apache configuration, adding a new virtual host 

   ``sudo vim /etc/apache2/sites-enabled/000-default``

   Add directives, ensuring an existing port is not conflicted::

    <VirtualHost *:80>
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

#. Verify successful build from the output of the installer script. Refer to http://plone.org if installation fails::

    ######################  Installation Complete  ######################

    Plone successfully installed at /home/example
    See /home/example/zinstance/README.html
    for startup instructions

    Use the account information below to log into the Zope Management Interface
    The account has full 'Manager' privileges.

    Username: admin
    Password: xyz
    ...

#. Edit the buildout configuration, eg ``/home/example/zinstance/buildout.cfg``::

   a.) Find the ``eggs`` section.  Add ``bika.lims``::

       eggs =
           Plone
           Pillow
           bika.lims

   b.) (Optional) Change the Zope instance port if the default 8080 is not used::

       http-address = 8080

   c.) (Optional) Change the ``effective-user`` if ``plone`` is not the one used. 

   d.) (Optional) Add the environment-vars entry for the ID-server, noting port number::

       [instance]
       environment-vars =
           IDServerURL http://localhost:8081

#. Run buildout::

    sudo bin/buildout

#. (Optional) Test and reload apache config::

    sudo apache2ctl configtest
    dig example.bikalabs.com
    sudo apachectl graceful

#. Test run in foreground, noting error messages if any and taking corrective action if so::

    sudo bin/plonectl fg

    ...

    2012-01-11 12:06:07 INFO Zope Ready to handle requests

#. Access the Zope instance::

   a.) via a web browser on public URL http://admin:admin@example.bikalabs.com/manage/ ::

   b.) or if on localhost at  http://admin:admin@localhost:8080/manage/ ::

#. Add the Plone instance with Bika LIMS extensions::

    If not automatically created by the buildout process yet, add a Plone instance,
    noting the instance name (default Plone, or Bika) and ensure that the Bika LIMS option is ticked.

#. (Optional) Modify Apache web server configuration to point to instance root::

    Point to the instance "Plone" or "Bika" root instead of Zope root if required
    by changing the Apache rewrite rule::

    #RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/VirtualHostRoot/$1 [L,P]
    RewriteRule ^/(.*) http://localhost:8080/VirtualHostBase/http/example.bikalabs.com:80/Bika/VirtualHostRoot/$1 [L,P]

     Reload the Apache webserver's configuration::

     sudo apache2ctl graceful

#. (Optional) Stop the foreground instance (Control C), and restart it as a background process. 
    Add it to server startup scripts to start Plone on reboot::

    sudo bin/plonectl start

    Add similar as below to ``/etc/rc.local`` or equivalent::

    /home/example/zinstance/bin/plonectl start

#. To start with a completely fresh instance::

    Rename/move the Data.fs.* files in var/filestorage (after stopping instance).


    Windows
    -------

2. Install Bika LIMS
--------------------

Open the buildout.cfg file for your new Plone instance.

    Ubuntu
    ------
    /usr/local/Plone/zeocluster/buildout.cfg
    or
    /usr/local/Plone/zinstance/buildout.cfg

    Windows
    -------

modify the find-links section to include the Bika LIMS egg URL.

    find-links += 
        https://github.com/bikalabs/Bika-LIMS/downloads


re-run buildout:

    bin/buildout

Select "Bika-LIMS extension profile" when adding a new site, or activate
it in the site-setup->Addons area of an existing site.

Plone 4 development setup
=========================

http://collective-docs.readthedocs.org/en/latest/ is your friend.

1. Install Plone 4
2. Download the bika3 repository to a folder called bika.lims
3. Edit instance/buildout.cfg:
   - Add "src/bika.lims" in the "develop=" section
   - (Optional) Add the following configuration to the [instance] section:

    environment-vars =
        IDServerURL http://localhost:8081

5. Run bin/buildout -n -c develop.cfg
6. Run bin/plonectl fg or bin\instance console
7. Load sample data with url/load_setup_data
8. Make sure the idserver is running
9. Load sample data with url/load_setup_data

If filestorage files have been deleted, 
run bin\plonectl adduser admin admin to create the admin user

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


Updating the demo
==================

on bika2 in usr/local/Plone
run in zinstance: sudo bin/svnupdate_and_rebuild
Which will clear db, get fresh copy from svn and rebuild, and start in fg
If all ok, break, and restart with sudo plone -c "bin/plonectl start"
Then recreate plone site 'Plone'

Miscellaneous testing issues
============================
python -m smtpd -n -c DebuggingServer localhost:1025


Add a new AT Content Type
=========================

example: Container (and bika_containers site-setup folder)

Modified files: (search for "container"):
#       modified:   bika/lims/__init__.py
#       modified:   bika/lims/catalog.py
#       modified:   bika/lims/controlpanel/configure.zcml
#       modified:   bika/lims/interfaces/__init__.py
#       modified:   bika/lims/profiles/default/controlpanel.xml
#       modified:   bika/lims/profiles/default/cssregistry.xml
#       modified:   bika/lims/profiles/default/factorytool.xml
#       modified:   bika/lims/profiles/default/propertiestool.xml
#       modified:   bika/lims/profiles/default/structure/bika_setup/.objects
#       modified:   bika/lims/profiles/default/types.xml
#       modified:   bika/lims/profiles/default/workflows.xml
#       modified:   bika/lims/setuphandlers.py

Newly added files:
#       bika/lims/browser/images/container.png
#       bika/lims/browser/images/container_big.png
#       bika/lims/profiles/default/structure/bika_setup/bika_containers
#       bika/lims/profiles/default/structure/bika_setup/bika_containers/.properties
#       bika/lims/profiles/default/structure/bika_setup/bika_containers/.objects
#       bika/lims/content/container.py
#       bika/lims/controlpanel/bika_containers.py
#       bika/lims/profiles/default/types/Container.xml
#       bika/lims/profiles/default/types/Containers.xml

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






