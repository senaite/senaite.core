Linux Installation
------------------

1. Install Dependencies:

    $ sudo apt-get install gcc g++ tar bzip2 gzip build-essential autoconf libtool pkg-config zlib1g-dev libssl-dev libexpat1-dev libreadline6-dev libxslt1.1 gnuplot 

2. Download and install Plone

    $ sudo wget https://launchpad.net/plone/4.2/4.2/+download/Plone-4.2-UnifiedInstaller-update-1.tgz
    $ tar xzf Plone-4.2-UnifiedInstaller-update-1.tgz
    $ cd Plone-4.2-UnifiedInstaller/
    $ sudo ./install.sh --target=/opt/Plone --password=Password standalone

This takes a while...

7. Edit buildout.cfg

    $ cd /opt/Plone/zinstance
    $ editor buildout.cfg

9. Add "bika.lims" to the eggs section

    eggs =
        Plone
        Pillow
        bika.lims

10. Run buildout:

    $ bin/buildout

It's important that the buildout.cfg is in the current directory when you run
this command.

The buildout will download all dependencies.  If the downloads are interrupted,
they will resume when bin/buildout is run again.

You'll see some SyntaxErrors like:  "Return outside function" etc.  Ignore them.

11. Start Plone:

    $ bin/plonectl fg

12. Add a new site:

Visit http://localhost:8080 and add a new site.  Be sure to select the
checkbox for the Bika LIMS extension profile.  No other add-ons need to
be installed - dependencies are installed automatically.

"bika" is a reserved word, and cannot be used for a site id.

13. Test:

Visit http://localhost:8080 and view your site.


