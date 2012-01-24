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

Topic
=====

heading
-------

- list
- list

    example
    Example line 2




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

http://collective-docs.readthedocs.org/en/latest/ is your friend.

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

Plone 4 development setup
=========================

1. First follow normal Installation instructions.
2. Run ```cd /usr/local/Plone/zinstance```
3. Run ```cp ../buildout-cache/eggs/bika.lims-3.0a1/bika/lims/buildout/develop.cfg .```
4. Run ```bin/buildout -n -c develop.cfg```
5. Run ```bin/plonectl fg``` or ```bin\instance console``` (windows)

If filestorage files have been deleted, you may need to run:

    bin/plonectl adduser admin admin

Windows
=======

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

3.0 dev
=======

2012-01-23
----------

#### Changes

 - Sampler and Preserver roles, users and permissions
 - Sampling and Preservation workflows
 - Inactive and Cancellation Workflows
 - Pre-preserved Containers
 - Automatic versioning for some bika_setup types
 - Analyst and Instrument on Worksheet templates
 - XLSX setup data loader
 - Sample disposal date based on date sampled, not date received.
 - Internal ID Server by default
 - user defined calculations and interim fields
 - Dry Matter results option does not appear until enabled in Site Setup
 - Accreditation portlet disabled until enabled in Site Setup
 - BikaListingView
 - New icons
 - (mostly) usable at 800x600
 - Column display toggles
 - Future dated samples and ARs
 - Accreditation template: i18n in locales/manual.pot/accreditation_*
 - intermediate workflow state for analyses requiring attachments
 - Labmanager has Site Administrator role (not Manager)
 - 'Indeterminate' results
 - use portal_factory everywhere
 - working test suite
 - static resource directories
 - Merged BikaMembers types
 - CoordinateField/Widget
 - DurationField/Widget
 - CustomRecordsWidget

2.3.3 Bug fix release
=====================

#### Bugs fixed

 - Inclusion of BikaMembers 0.0.3. No changes to bika code, version bumped
   to facilitate release of new BikaMembers version.

2.3
===

#### Changes

 - Analysis categories introduced
 - Analysis service result restrictions - specification of possible results
 - Allow site and client specification of email and fax subject line content
 - Additional instrument/export formats:
   WinescanFT120, WinescanAuto, FIAStar and Bartelt's data-collector
 - Export worksheet analyses to instruments
 - PDF as a result output option
 - SMS result output option
 - Result publication options synchronized and signatures added to emails
 - Email batching of query results conforms to result mailing
 - IDServer batching of unique id request
 - Optmization of worksheet searching on selection criteria
 - Extract tab added with extract for analysis services or profiles
 - Batch update of analysis service prices
 - German translation module added
 - Added a light query form which excludes analysis category and service
 - Batch size setting in analysis request lists
 - BikaMembers replaces UpfrontContacts
 - ATSchemaEditor removed
 - Significant performance improvements

#### Bugs fixed

 - Resolve client action conflicts
 - Sampled date validation
 - Drymatter formatting on output corrected
 - Correct default none workflows
 - Review portlet optimization
 - Pricelist prints blank for analysis service with price not defined

2.2
===

#### Changes

 - Attachments permitted on analysis requests and analyses
 - Worksheet resequencing, and sort order for worksheet analysis selection
 - Worksheet deletion only available for open worksheets
 - Portlet to provide export of analysis services and analysis profiles
 - Requirement for unique analysis service names, analysis service keywords,
 - instrument import keywords and analysis profile keywords enforced.
 - Report headings and formats standardized accross different reports
 - AR import alternative layout provided with selection, including profiles
 - Progress bar introduced for long running processes

2.1.1
=====

#### Changes

 - Disposal Date for Samples and Retention Period per Sample Type added.
 - Various new search criteria added.
 - Standard Manufacturers introduced.
 - Labels for Standard Samples introduced.
 - "Print" and "Email" facilities introduced for lists of Standard Samples and Standard Stocks.
 - "Duplicate" facility for Analysis Services introduced.
 - Addresses added to top of emailed query results.
 - Labels for Samples and Analysis Requests changed.
 - Analysis Services can have multiple Methods.
 - Change log introduced for Methods.
 - Methods added to left navigation bar.
 - List of Methods included in pop-up for Analyses.
 - Documents may be uploaded for Methods.

2.1
===

#### Changes

 - Sample object and workflow introduced
 - Results specifications, lab and per client
 - Analysis profiles
 - Worksheet template engine
 - Interface to Bika Calendar
 - Import of analysisrequests from csv file
 -  Export of results to csv file
 - Print as publication option
 - Lab Departments, lab contacts, and department manager introduced
 - Quality Control calculations. Control, blank and duplicate analyses.
 - QC graphs, normal distribution, trends and duplicate variation
 - Various analysis calculations allowed. Described by Calculation Type
 - Dependant Calcs introduced. Where an analysis result is calculated from
 -  other analyses: e.g. AnalysisX = AnalysisY - Analysis Z
 - Dry matter result reporting. Results are reported on sample as received,
 -  and also as dry matter result on dried sample
 - Re-publication, Pre publication of individual results and per Client
 - Many reports including Turn around, analyses repeated and out of spec

1.2.1
=====

#### Bugs fixed

 - Removed invoice line item descriptions from core code to allow skin
   integration
 - Create dummy titration values for analyses imported from instrument
 - More language translations

1.2.0
=====

#### Changes

 - Statements renamed to Invoices
 - Jobcards renamed to Worksheets
 - New identification fields added to analysis request
 - Client Reference, Sample Type and Sample Point
 - Welcome page introduced
 - Late analyses list linked from late analyses portlet
 - Icon changes
 - Accreditation body logo and details added to laboratory info
 - Accreditation logo, disclaimers added throughout web site
 - Laboratory confidence level value data driven from laboratory info
 - Analyses methods provided as pop-up where analyses are listed
 - Titration factors and titration volumes added to analyses and worksheets
 - Measure of uncertainties introduced per analysis and intercept
 - Two new specialist roles created - verifier and publisher
 - Sample test data load script - load_sample_data.py
 - Implement generic instrument data import tool
 - Login portlet added
 - Modifications required to support interlab
   Permit analysis parent (sample) to be in 'released' state.
   Reference SampleID on AnalysisRequest-

#### Bugs fixed

 - 1566324: Logged in page redirected to welcome page.
 - 1573299: LiveSearch - Added permissions to InvoiceLineItem.
 - 1573083: Status Drop Down - Invoicing
 - 1551957: Contacts not visible to other contacts. Correct local owner role
 - 1566334: position of 'add new ar' button changed to conform to other forms
 - 1532008: query results sort order most recent first
 - 1532770: Order default listing correction
 - 1558458: Member discount data driven in messages on AR forms
 - 1538354: SubTotal and VAT calculation on edit AR
 - 1532796: AR edit - allow change of contact

1.1.3
=====

 This is a bug fix release. Migration from older versions has also
 been improved greatly.

 Please note that AnalysisRequest now has a custom mutator that
 expects the title of the Cultivar, not the UID. This will impact
 anybode that customised the *analysisrequed_add.cpy* controller
 script and the *validate_analysisrequest_add_form.vpy* validation
 script.

#### Bugs fixed

 - 1423182: IndexError on surfing to LIMS pages without being logged on
 - 1423238: Orders - Dispatch date
 - 1429992: AR edit tab - Cultivar uneditable
 - 1429996: Cultivar names to allow numbers
 - 1429999: Late analysis alert - 'More...' URL
 - 1430002: Sample due alerts - 'More...' URL
 - 1433787: Security - Clients
 - 1434100: Search - Index & Attribute errors
 - 1418473: Updated start-id-server.bat for Win2K & Win XP

1.1.2
=====

#### Features added

 - 1423205: Show logs to labmanager set-up
 - 1291750: Added default ID prefixes for Order and Statement

#### Bugs fixed

 - 1424589: Late analysis alert to be calulated on date received

1.1.1
=====

#### Changes

 - Updated portlets with Plone 2.1 style definition list markup

#### Bugs fixed:

 - 1423179: Clients must not see JobCard links on Analysis Requests
 - 1423182: IndexError on surfing to LIMS pages without being logged on
 - 1423188: Site map - Clients should not have access to ...
 - 1423191: Link rot - 'logged in' page
 - 1423193: Groups folder should not be shown
 - 1423194: No 'More...' if there are less than 5
 - 1423204: AR view - Missing tabs and status drop down
 - 1423209: Schema Editor - Drop Down List Issue (Select)
 - 1423234: Late Analysis alert shows for anonymous visitors
 - 1423363: Report Analysis Totals
 - 1423386: Email publication error

1.1.0
=====

#### Changes
 - Made Bika compatibable with Plone 2.1
 - Added Spanish translation contributed by Luis Espinoza
 - Added Italian translation contributed by Pierpaolo Baldan
 - Added Dutch translation contributed by Joris Goudriaan
 - Added Portugese translation contributed by Nuno R. Pinhão
 - The schemas of Client, Contact, AnalysisRequest and Order can be
   edited in the through-the-web schema editor, ATSchemaEditorNG.
 - The maximum time allowed for the publication of results can now be
   set per analysis service. The portlet
   'skins/bika/portlet_late_analysis.pt' has been added to alert lab
   users when analyses are late.
 - Analyses on an AnalysisRequest have a reference to a Jobcard,
   rendered as a hyperlink on the AnalysisRequest view.
 - A bug has been fixed where 'not_requested' analyses were checked
   on the AnalysisRequest edit form.
 - Enabled 'changed_state' folder button globally and disabled on
   AnalysisRequest and Jobcard.

1.0.1
=====

#### Changes

 - Updated 'skins/bika/date_components_support.py' with latest
   version of script in Plone 2.0.5
 - Modified access to transitions in workflow scripts, normal
   attribute access seems to guarded since Zope 2.7.5.
 - Added CHANGES.txt and README.txt
 - Added windows batch script for ID server
   (scripts/start-id-server.bat)

