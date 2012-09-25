You can copy development-buildout.cfg into your zinstance folder, then run:

    $ bin/buildout -c development-buildout.cfg

Indent everything correctly (Especially TAL files!)

Strip trailing whitespace but leave one blank line at the end of each file.

If filestorage files have been deleted/recreated, you may need to re-create
the admin user:

    $ bin/plonectl adduser admin admin

If you don't have a mail server configured, you can use this command to start
a simple printing debug SMTP server:

    $ python -m smtpd -n -c DebuggingServer localhost:1025

In debug mode a copy of the HTML that is meant to be included in the email,
will be written to Plone/zinstance/parts/instance/var/[first_ar]_[action].html

Use the built-in Title and Description indexes and metadatas where possible!

    Modify using lowercase. e.g service.edit(title='Ash', description='blah')
    Access directly as attribute: service.title     service.description
    OR as method:                 service.Title()   service.Description()

    use override method to serve the title if it should be something other than
    the title - e.g the description:

    security.declarePublic('Title')
    def Title(self):
        t = self.Description()
        return t and t or ''

bika.lims package layout.
=========================

./bika/lims/configure.zcml - Main ZCML configuration file

    All other ZCML files are included forward from this one. Most folders
    have at least a configure.zcml file.

./bika/lims/profiles.zcml - Configure GenericSetup installation profile

    Registers the installation profile, and configures initial configuration.

./bika/lims/permissions.zcml - Configure ZCML permissions

    These are the permissions which can be used in ZCML files for limiting
    access to views.

./bika/lims/permissions.py - Configure Python permissions

    Configure Python variables for all permissions - these shoud be used when
    referring to permissions in Python code.

./bika/lims/barcode.py - Barcode logic

    his file decides what happens when a specific barcode is scanned. By
    default, the scanned object's View page is shown.

./bika/lims/catalog.py - Definition of bika catalogs

    Three search catalogs, with their indexes and metadata, are defined here.
    bika_setup_catalog - Contains items configured in Control Panel.
    bika_catalog - Transactional types: Samples, AnalysisRequests, Worksheets.
    bika_analysis_catalog - This indexes Analysis, Duplicate Analysis, and Reference Analysis objects.

./bika/lims/config.py - Global configuration variables

    Some parts of the system make certain assumptions about these values, and
    so they should be changed with great care.

./bika/lims/idserver.py - Create content IDs using external ID server

    If the external ID server is started and configured, this file will query
    and update the counters when creating new objects.

./bika/lims/navtree.py - Force translation of content titles in vavigation

    Content titles can not be translated with the default Plone i18n machine,
    so we do it manually, here.

./bika/lims/testing.py - Automated tests configuration

    This creates a test Plone site, installs Bika LIMS, loads setupdata from
    _testing.xlsx, and runs all tests.

./bika/lims/utils.py - Mixed Python utility functions

    Useful functions, or functions with no other sensible home, go here.

./bika/lims/validators.py - Archetypes field data validation

    All custom fields that require validation, have their validators
    in this file.

./bika/lims/content - Content type definitions (Archetypes)
===========================================================

    The base content types are all defined here.  They are not listed below.

    In some cases, a custom Folder type is used, example ClientFolder
    or WorksheetFolder.  These types provide only minor differences from the
    default Plone folder types, and are not listed below.

./bika/lims/content/configure.zcml

    Most of the items in this folder are not directly accessable via URL.  The
    one exception, so far, is the 'methods' folder.  This folder contains setup
    items, but it has been made accessable from the navigation tree. This ZCML
    file configures the /methods URL.

./bika/lims/content/bikaschema.py

    This is the base schema on top of which all Bika LIMS objects are created.

./bika/lims/content/organisation.py

    Organisation is the base type of Client, Laboratory, and ReferenceSupplier

./bika/lims/content/person.py

    Person is the base type of Client, Laboratory, and Supplier contacts

./bika/lims/content/bikasetup.

    This is the main Bika Settings control panel object

./bika/lims/browser - Browser views and static resources
========================================================

Browser views contain the logic behind the display templates.  These files
also contain the Workflow Action logic for each content type.

./bika/lims/browser/configure.zcml

    The URLs in this folder are configured in many separate ZCML files.
    This one brings them all together.

./bika/lims/browser/accreditation.py

    The Accreditation link on the front page, if it is configured, points
    to this view.

./bika/lims/browser/analyses.py

    This view is responsible for viewing or editing lists of analyses.

./bika/lims/browser/analysisrequest.py

    The main AnalysisRequest view, edit and popup screens. Also contains the
    root /analysisrequests folder view.

./bika/lims/browser/analysisservice.py

    AnalysisService information popup, and other utility views for
    AnalysisService contexts.

./bika/lims/browser/attachment.py

    AJAX views for handling attachments.

./bika/lims/browser/bika_listing.py

    Contains BikaListingView, used for nearly all content listings.

./bika/lims/browser/calcs.py

    AJAX calculations are done here.

./bika/lims/browser/client.py

    All client views:

    AR Templates
    Analysis Profiles
    Analysis Requests
    Analysis Specifications
    Attachments
    Contacts
    Orders
    Samples

./bika/lims/browser/contact.py

    Contact login details are created here.

./bika/lims/browser/late_analyses.py

    Shows a full list of late Analyses.

./bika/lims/browser/load_setup_data.py

    This view reads XLSX files from the setupdata folder, and loads their
    content into the LIMS.

./bika/lims/browser/log.py

    Used to show workflow history for all types.

./bika/lims/browser/menu.py

    By default, Plone's interface shows only the states and transitions from
    the context object's primary workflow. This is a utility to modify
    Plone's editable border and include Inactive or Disabled states.

./bika/lims/browser/publish.py

    When they are published, Analysis Requests are compiled to HTML and sent
    to all contacts.

./bika/lims/browser/referencesample.py

    Views to display each Reference Sample, and to view it's Reference
    Analyses.

./bika/lims/browser/referencesupplier.py

    When viewing a Reference Supplier, this code shows Reference Samples and
    Reference Supplier Contacts.

./bika/lims/browser/remarks.py

    This is the AJAX request handler for setting Remarks fields.

./bika/lims/browser/sample.py

    Display all Sample screens:

    Sample Edit
    Sample View
    Sample Partitions table
    Sample Analyses

    Also contains the main /samples folder listing view.

./bika/lims/browser/stickers.py

    Invoked via URL on an object, we render a sticker for that object. Used
    manually with a list of objects, renders stickers for all provided
    objects, and invokes a print dialog.

./bika/lims/browser/viewlets.py

    All viewlets are defined here. The "Load setup data" message for new
    instances is one such.

./bika/lims/browser/worksheetfolder.py

    The main /worksheets folder listing.  This file also contains the code
    to add new worksheets.

./bika/lims/browser/worksheet.py

    All worksheet screens:

    Add Analyses
    Add Blank Reference
    Add Control Referencve
    Add Duplicate Analysis
    Manage Results - Renders the table for editing analyses.
    Export - If an instrument is selected, this exports the worksheet

./bika/lims/browser/templates
=============================

    Nearly all the TAL templates used in the system live here.

./bika/lims/browser/mailtemplates
=================================

    These are used for publishing ARs. Now, there is only one template here:
    analysisrequest_results.pt

./bika/lims/browser/css - Static CSS files
==========================================

    This is the "correct" place to put CSS files. Bika still follows old
    practices, and does most of it's CSS customisations in the
    skins/ploneCustom.css file.

    The files in this folder should be served by a caching proxy server. The
    files are accessed using a URL similar to the following:

    ++resource++bika.lims.css/file.css

./bika/lims/browser/css/hide_contentmenu.css

    Hides the 'Actions', 'Display' and 'Add New' menus for specific types.
    Configured in profiles/cssregistry.xml.

./bika/lims/browser/css/hide_editable_border.css

    Completely hides the editable border for specified types.
    Configured in profiles/cssregistry.xml.

./bika/lims/browser/fields - Custom Archetypes field definitions
================================================================

./bika/lims/browser/fields/addressfield.py

    All Organisation and Person Address fields.

./bika/lims/browser/fields/aranalysesfield.py

    This contains the methods relating to the AnalysisRequest 'Analyses'
    field.  The field does not contain any data, but is used to get and set
    the values of Analyses inside an AnalysisRequest.

./bika/lims/browser/fields/coordinatefield.py

    Used for Location Coordinates: Latitude and Longitude.

./bika/lims/browser/fields/durationfield.py

    Used for all Durations. Stores Days, Hours, and Minutes.

./bika/lims/browser/fields/historyawarereferencefield.py

    This works just like the Archetypes Reference Field, except that it
    'remembers' the version of the referenced object, and always returns that
    same version.

./bika/lims/browser/fields/interimfieldsfield.py

    In Calculation objects, Interim Fields indicate the ID, Title, and type
    of all values that an Analysis will require, before a result can be
    calculated. The Calculation Interim fields is a "template" for any
    Analysis created using this Calculation.

    In Analysis objects Interim Fields uses the same field type, but the
    "value" key is populated with the field value, and a result is
    calculated.

./bika/lims/browser/fields/referenceresultsfield.py

    Reference Definitions and Reference Samples use this field to define
    the results expected from reference samples, for each analysis service.

./bika/lims/browser/images - Static image files

    All images should be placed here. The files in this folder should be
    served by a caching proxy server. The files are accessed using a URL
    similar to the following:

    ++resource++bika.lims.images/image_name.png

./bika/lims/browser/js - Static javascript files

    All javascriptfiles should be placed here. The files in this folder
    should be served by a caching proxy server. The files are accessed using
    a URL similar to the following:

    ++resource++bika.lims.js/file.js

./bika/lims/browser/queries - UI and implementation of Queries
==============================================================

__init__.py
analysisrequests.py
invoices.py
orders.py
queries.pt
queries_query.pt
query_frame.pt
query_out.pt

./bika/lims/browser/reports - UI and implementation of Reports
==============================================================

__init__.py
analysesattachments.py
analysesoutofrange.py
analysesperclient.py
analysespersampletype.py
analysesperservice.py
analysesrepeated.py
analysestats.py
analysestats_overtime.py
arsnotinvoiced.py
report_frame.pt
report_out.pt
reports.pt
reports_administration.pt
reports_history.pt
reports_productivity.pt
reports_qualitycontrol.pt
resultspersamplepoint.py

./bika/lims/browser/widgets
===========================

    Custom form widgets

./bika/lims/controlpanel
========================

    Folders and Views for Control Panel configuration.

./bika/lims/exportimport
========================

    CSV data interfaces for worksheets, and views for selecting an Instrument
    and CSV file to be imported. The Import and Export routines for each
    instrument interface are stored in the 'instruments' folder, along with a
    TAL template for collecting parameters.

./bika/lims/locales - Translations
==================================

bika.pot

    i18ndude places strings from the bika domain in this file. Any strings
    which i18ndude does not find when scanning the bika source, are removed
    from the file.

bika-manual.pot

    The strings that i18ndude does not find, go here. They are merged into
    the bika.PO files when they are compiled by i18ndude.

plone.pot

    Overwrite plone domain strings here.

plone-manual.pot

    Some of bika's strings must be translated in the plone domain. These need
    to be added here, and will be merged into the plone.po overrides.

./bika/lims/interfaces - ZCA Interfaces (markers)
=================================================

    These are used to "mark" content objects, so that ZCML statements can be
    targeted to certain types of content.

./bika/lims/profiles/default
============================

    Generic Setup installation profile

    actions.xml
        Site actions (portal tabs)

    browserlayer.xml
        Used to ensure customisations only appear when Bika is installed.

    catalog.xml
        Default Plone portal_catalog indexes and metadata.

    componentregistry.xml
        Configure Zope utilities - For now, this is only the ID Server.

    controlpanel.xml
        Link views into the Plone control panel

    cssregistry.xml
        Configure Plone's portal_stylesheets Resource Registry

    factorytool.xml
        List of types who's creation is handled with the portal_factory tool

    jsregistry.xml
        Configure Plone's portal_javascripts Resource Registry

    metadata.xml
        Configure dependencies.

    portal_languages.xml
        Configure the supported content languages

    portlets.xml
        Configure the location of the Login, Navigation and worklist portlets

    propertiestool.xml, properties.xml
        site properties

    repositorytool.xml
        Configure types to be versioned (Plone < 4.1 uses setuphandlers for this).

    skins.xml
        Configure legacy skin layers

    toolset.xml
        Activate the catalog tools for Bika catalogs

    types.xml
        Complete list of Archetypes content types

    viewlets.xml
        Modify default viewlet configuration

    workflows.xml
        Links workflows to specific portal types

./bika/lims/scripts
===================

    external utility scripts (ID Server)

./bika/lims/setupdata
=====================

    Pre-configured setup data and associated files

./bika/lims/skins
=================

    Skin layers are a legacy Plone 2 technology for adding overridable
    templates and media resources to Plone packages.

    Some parts of Archetypes are hard-coded to use skin layers, and so while
    the system continues to use Archetypes, the skins folder will remain.

./bika/lims/subscribers
=======================

    Functions that subscribe to Zope events. Mainly, these are used for
    "workflow cascades". For example, when a Sample is received, the sample's
    AR and all it's analyses will also be transitioned to "received" state.
    Similarly, an Analysis Request's state is always equal to the 'lowest'
    workflow state of all it's analyses. This is managed here.

    Other, more specialised event handlers are listed below.

    after_transition_log.py

        In debug mode, this shows workflow events after the transition is
        complete.

    analysis.py

        Newly added analyses will have their workflow state set according to
        the state of the parent AR.  Deleting analyses could modify the state
        of the parent AR.

    analysiscategory.py

        This handler fires after Transition events, to prevent Categories
        from being disabled when they contain Analysis Services.

    analysisservice.py

        A service cannot be deactivated if "active" calculations list it as a
        dependency. A service cannot be activated if it's calculation is
        inactive.

    calculation.py

        A calculation cannot be re-activated if services it depends on are
        deactivated. A calculation cannot be deactivated if active services
        are using it.

    objectmodified.py

        This is used to update the versioned reference between Calculations
        and Services. When a calculation is modified, all AnalysisService
        objects are updated so that they refer to the new version of this
        calculation.

./bika/lims/profiles/default/types
==================================

    Includes an XML file for every custom content type. These files must be
    referenced in types.xml to be initiated.

./bika/lims/profiles/default/workflows
======================================

    Define the states, transitions and variables for all workflows.

    bika_ar_workflow
    ----------------

    Workflow for Analysis Requests

    * sample_registered  Initial object state.
    * to_be_sampled      To Be Sampled (Sampling Workflow enabled).
    * sampled            Sampling workflow completed - sample collected.
    * sample_due         Sample has not yet been received at the laboratory.
    * sample_received    The laboratory has received the sample.
    * to_be_preserved    The sample requires preservation.
    * to_be_verified     Results have been entered, but not verified.
    * verified           Results have been verified as correct.
    * not_requested      This analysis was not requested by the client.
    * published          The results have been sent to the client.

    bika_analysis_workflow
    ----------------------

    Workflow for Analysis objects

    Analyses follow the AR workflow, but an additional automatic workflow
    step has been added to allow results to be submitted without an
    attachment, if an attachment is required. The verification workflow
    transition will not be available until the atttachment has been added.

    * sample_registered  Initial object state.
    * to_be_sampled      To Be Sampled (Sampling Workflow enabled).
    * sampled            Sampling workflow completed - sample collected.
    * sample_due         Sample has not yet been received at the laboratory.
    * sample_received    The laboratory has received the sample.
    * to_be_preserved    The sample requires preservation.
    * to_be_verified     Results have been entered, but not verified.
    * attachment_due     Attachment Outstanding
    * verified           Results have been verified as correct.
    * not_requested      This analysis was not requested by the client.
    * published          The results have been sent to the client.

    bika_duplicateanalysis_workflow
    -------------------------------

    Duplicate analyses are located inside Worksheets, and do not follow the
    AR/Analysis workflow.

    * unassigned         Default state of new Duplicate Analyses
    * assigned           Assigned to worksheet
    * attachment_due     Attachment Outstanding
    * to_be_verified     To be verified
    * rejected           Rejected
    * verified           Verified

    bika_referenceanalysis_workflow
    -------------------------------

    For flexibility purposes, this is a separate workflow, but it is identical
    to Duplicate Analysis workflow

    bika_referencesample_workflow
    -----------------------------
    * current           The sample is current and usable.
    * expired           The sample has reached it's expiry date.
    * disposed          The sample has been disposed of.

    bika_worksheetanalysis_workflow
    -------------------------------

    A secondary workflow, to indicate if an analysis is Assigned to a worksheet,
    or not.

    bika_worksheet_workflow
    -----------------------

    Workflow for Worksheets

    * open             Default state for Worksheets.
    * to_be_verified   All analysis results have been submitted
    * attachment_due   Attachment Outstanding (for one or more analyses)
    * verified         Results have been verified as correct.
    * rejected         The worksheet has been rejected (too many errors)

    bika_one_state_workflow
    -----------------------

    Some objects have no workflow, but some views require a primary workflow.
    To simply these views, objects without workflow should specify this as
    their primary workflow.

    bika_cancellation_workflow
    --------------------------

    Active/Cancelled states for objects which can be cancelled.

    Indexed as cancellation_review_state in the catalogs.

    bika_inactive_workflow
    ----------------------

    Active/Inactive states for objects which can be deactivated

    Indexed as inactive_state in the catalogs.

