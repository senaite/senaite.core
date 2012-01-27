Installation
------------

This document describes the installation of Bika LIMS using the Plone Unified
Installer package

### Download and install Plone

The latest Unified Installer can be found at http://plone.org/products

    $ tar xzf Plone-4.1.3-UnifiedInstaller.tgz
    $ cd Plone-4.1.3-UnifiedInstaller
    $ sudo ./install.sh --target=Plone --libz=yes --password=admin standalone

### Edit Plone/zinstance/buildout.conf.

Find the "eggs" section and add "bika.lims"

    eggs =
        Plone
        Pillow
        bika.lims

### Run buildout

    sudo bin/buildout

### Start Plone

    # Start in foreground (debug) mode, noting error
    # messages if any and taking corrective action
    $ bin/plonectl fg

    # start normally:
    $ bin/plonectl start

### Add a new plone site.

Assign an ID of your choice, and select the checkbox to activate the
Bika-LIMS extension profile.  To add Bika LIMS to an existing Plone site,
visit the Addons page of Site Setup.

That's it!

You should be able to test the site now by visiting
http://localhost:8080/SITE_ID
