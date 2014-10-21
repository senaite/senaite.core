*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

*** Test Cases ***


Repetitive Bika Setup stuff

    Log in                      test_labmanager  test_labmanager
    go to                       ${PLONEURL}/bika_setup/edit
    Click link  Analyses
    Select Checkbox  SamplingWorkflowEnabled
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# Update Laboratory Information
    Go to  ${PLONEURL}/bika_setup/laboratory/base_edit
    Input Text        Name            Laboratory Name
    Input Text        TaxNumber       0123456789
    Input Text        Phone           555-1234
    Input Text        Fax             555-1235
    Click link        Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Input Text        EmailAddress  laboratory@example.com
    Select From List  PhysicalAddress.country:record    South Africa
    Select From List  PhysicalAddress.state:record      Western Cape
    Select From List  PhysicalAddress.district:record   City of Cape Town
    Input Text        PhysicalAddress.city              Cape Town
    Input Text        PhysicalAddress.zip               2000
    Input Text        PhysicalAddress.address           Foo House\nFoo Street 20\nFoo Town
    Select From List  PostalAddress.selection           PhysicalAddress
    Input Text        PostalAddress.address             Post Box 25\nFoo Town
    Select From List  BillingAddress.selection          PostalAddress
    Input Text        LabURL                            www.example.com
    Click link        Bank details
    Input Text        AccountType    Savings
    Input Text        AccountName    Test Laboratory Inc
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111
    Click link       Accreditation
    Input Text       Confidence                 95
    Select Checkbox  LaboratoryAccredited
    Click Button  Save
    Wait Until Page Contains  Changes saved.


# ARTemplates
    Go to  ${PLONEURL}/bika_setup/bika_artemplates
    Click link  Add Template
    Wait Until Page Contains Element  title
    Input Text  title          New Template
    Input Text  description    Temporary test object
    Input Text  SamplePoint   Borehole 12
    Input Text  SampleType    Water
    Select Checkbox  ReportDryMatter
    Click link  css=#fieldsetlegend-sample-partitions
    wait until page contains element    Partitions-Container-0
    Select from dropdown  Partitions-Container-0        Glass Bottle 500ml
    Select from dropdown  Partitions-Preservation-0     Any
    Click Button  More
    wait until page contains element    Partitions-Container-1
    Select from dropdown      Partitions-Container-1        Any
    Select from dropdown      Partitions-Container-1        H2S04
    Click Link  Analyses
    Wait Until Page Contains Element  AnalysisProfile
    Select from dropdown   AnalysisProfile    Trace Metals
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# Attachment Types
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # this one fails
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains    is not unique

    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Calculation
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element      title
    Input Text  title          Calculating Nothing
    Input Text  description    Temporary test object
    Click Link  Calculation
    Wait Until Page Contains Element      InterimFields-keyword-0
    Input Text  InterimFields-keyword-0   This
    Input Text  InterimFields-title-0     This Field
    Input Text  InterimFields-value-0     1
    Input Text  InterimFields-unit-0      mg
    Click Button  More
    Input Text  InterimFields-keyword-1   That
    Input Text  InterimFields-title-1     That Field
    Input Text  InterimFields-value-1     2
    Input Text  InterimFields-unit-1      mg
    Click Button  More
    Input Text  InterimFields-keyword-2   Other
    Input Text  InterimFields-title-2     Other Field
    Input Text  InterimFields-value-2     0.5
    Input Text  InterimFields-unit-2      mg
    Input Text  Formula                   [This] + [That] - [Other]
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # test workflow
    # Can't disable Dry Matter here - use [2] which is our New Object.
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Select Checkbox  xpath=//input[@item_title='Calculating Nothing']
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link   All
    Select Checkbox  xpath=//input[@item_title='Calculating Nothing']
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Container Type
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Preservations
    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Click link  Add
    Wait Until Page Contains Element     title
    Input Text           title           Freeze Sample
    Input Text           description     Stick sample in regular freezer to 0 degrees.
    Select Radio Button  Category        lab
    Input Text           RetentionPeriod.days:record:ignore_empty     180
    Input Text           RetentionPeriod.hours:record:ignore_empty    0
    Input Text           RetentionPeriod.minutes:record:ignore_empty  0
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Method
    Go to  ${PLONEURL}/bika_setup/methods
    Click link    Add
    Wait Until Page Contains Element    title
    Input Text    title                 A New Method
    Input Text    description           Things you can do, some can't be done
    Input Text    Instructions          It's very simple.
    Click Button  Save
    Wait Until Page Contains            Changes saved.

    # test workflow
    Go to  ${PLONEURL}/bika_setup/methods
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Sample Matrices
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.


    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  default
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Sample Points
    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Input Text  SamplingFrequency.days:record:ignore_empty  30
    Input Text  SamplingFrequency.hours:record:ignore_empty  0
    Input Text  SamplingFrequency.minutes:record:ignore_empty  0
    Select Checkbox  Composite
    Click link  Location
    Input Text  Latitude.degrees:record:ignore_empty     45
    Input Text  Latitude.minutes:record:ignore_empty     30
    Input Text  Latitude.seconds:record:ignore_empty     30
    Input Text  Latitude.bearing:record:ignore_empty     N
    Input Text  Longitude.degrees:record:ignore_empty    45
    Input Text  Longitude.minutes:record:ignore_empty    30
    Input Text  Longitude.seconds:record:ignore_empty    30
    Input Text  Longitude.bearing:record:ignore_empty    E
    Input Text  Elevation                                10
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  all
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# Sampling Deviations
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    # test workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  default
    Select Checkbox  xpath=(//input[contains(@id, '_cb_')])[1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

# LabManager
    Go to  ${PLONEURL}/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Salutation
    Input Text  Salutation  Mr
    Input Text  Firstname   Avon
    Input Text  Surname     Barksdale
    Input Text  JobTitle    Player
    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress          avon@example.com
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# LabDepartment
    Go to  ${PLONEURL}/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select from list  Manager:list   Lab Manager 2
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# LabContact
    Go to  ${PLONEURL}/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  Mr
    Input Text  Firstname   Avon
    Input Text  Surname     Barksdale
    Input Text  JobTitle    Player
    Select from list  Department:list  Admin

    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress   client@example.com
    Input Text  BusinessPhone  555-0123
    Input Text  BusinessFax    555-0123
    Input Text  HomePhone      555-8888
    Input Text  MobilePhone    555-9999

    Click Link  Address
    Select From List  PhysicalAddress.country:record    South Africa
    Select From List  PhysicalAddress.state:record      Western Cape
    Select From List  PhysicalAddress.district:record   City of Cape Town
    Input Text        PhysicalAddress.city              Cape Town
    Input Text        PhysicalAddress.zip               2000
    Input Text        PhysicalAddress.address           Foo House\nFoo Street 20\nFoo Town
    Select From List  PostalAddress.selection           PhysicalAddress
    Input Text        PostalAddress.address             Post Box 25\nFoo Town

    Click Button  Save
    Wait Until Page Contains  Changes saved.

# Suppliers
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Page should contain  Suppliers
    Click link  Add
    Wait Until Page Contains Element  Name
    Input Text        Name            ACME Supplies
    Input Text        TaxNumber       0123456789
    Input Text        Phone           555-1234
    Input Text        Fax             555-1235
    Click link        Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Input Text        EmailAddress    supplier@example.com
    Select From List  PhysicalAddress.country:record    South Africa
    Select From List  PhysicalAddress.state:record      Western Cape
    Select From List  PhysicalAddress.district:record   City of Cape Town
    Input Text        PhysicalAddress.city              Cape Town
    Input Text        PhysicalAddress.zip               2000
    Input Text        PhysicalAddress.address           Foo House\nFoo Street 20\nFoo Town
    Select From List  PostalAddress.selection           PhysicalAddress
    Input Text        PostalAddress.address             Post Box 25\nFoo Town
    Select From List  BillingAddress.selection          PostalAddress
    Click link        Bank details
    Input Text        AccountType    Savings
    Input Text        AccountName    Supplier Inc
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Click link        ACME Supplies
    Wait Until Page Contains    Remarks
    Input Text        Remarks          Reference Sample Remarks
    Click button      Save remarks
    Wait until page contains    ===
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text        title           New Object
    Select From List  ReferenceDefinition:list
    Select Checkbox   Blank
    Select Checkbox   Hazardous
    Select From List  ReferenceManufacturer:list
    Input Text        CatalogueNumber  Catalogue Number
    Input Text        LotNumber  Lot Number
    Click Link  Dates
    Wait Until Page Contains Element  DateSampled
    SelectPrevMonthDate  DateSampled  1
    SelectPrevMonthDate  DateReceived  3
    SelectPrevMonthDate  DateOpened  4
    SelectNextMonthDate  ExpiryDate  5

    # Click Link  Reference Values
    # Wait Until Page Contains  Expected Values
    # Log  No new reference values are added  WARN

    Click Button  Save
    Wait Until Page Contains  Changes saved.


# Supplier Contact
    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-2/contacts
    Wait Until Page Contains Element  Remarks
    Input Text  Remarks  Contacts Remarks
    Click button  Save remarks
    Click link  Add
    Wait Until Page Contains Element  Salutation
    Input Text  Salutation  Mr
    Input Text  Firstname  Cameron
    Input Text  Surname  Dennis
    Input Text  JobTitle  Lawyer
    Input Text  Department  Admin
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    Click link  Edit
    Click link  Email Telephone Fax
    Input Text  EmailAddress  info@supplier.com
    Input Text  BusinessPhone  021 234 567
    Input Text  BusinessFax  021 234 568
    Input Text  HomePhone  021 123 456
    Input Text  MobilePhone  082 1234 567
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    Click link  Edit
    Click link  Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Select From List  PhysicalAddress.country:record   South Africa
    Select From List  PhysicalAddress.state:record     Western Cape
    Select From List  PhysicalAddress.district:record  City of Cape Town
    Input Text        PhysicalAddress.city             Cape Town
    Input Text        PhysicalAddress.zip              2000
    Input Text        PhysicalAddress.address          Nr 1,\nloop street
    Select From List  PostalAddress.selection          PhysicalAddress
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #now test Instruments
    #for that you need a supplier,manufacturer, instrument type and instrument - defined in that order
    #got supplier - so start with basic def of Manufacturer

# Manufacturer
    Go to  ${PLONEURL}/bika_setup/bika_manufacturers
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Manufacturer
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# Instrument

    Go to  ${PLONEURL}/bika_setup/bika_instrumenttypes
    Page should contain  Instrument Types
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    Go to   ${PLONEURL}/bika_setup/bika_instruments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title                 New Instrument
    Input Text  description           Temporary test object
    Select From List  InstrumentType  Auto titrator
    Select From List  Manufacturer    Boss
    Select From List  Supplier        Instruments Inc
    Input Text  Model                 Instrument Model 0123
    Input Text  SerialNo              Instrument Serial Number 123
    # Select From List  DataInterface:list
    # Input Text  DataInterfaceOptions-Key-0  Data Interface Options Key
    # Input Text  DataInterfaceOptions-Value-0  Data Interface Options Value

    Click link  Procedures
    Wait Until Page Contains Element  InlabCalibrationProcedure
    Input Text  InlabCalibrationProcedure  Inlab Calibration Procedure
    Input Text  PreventiveMaintenanceProcedure  Preventive Maintenance Procedure

    Click Button  Save
    Wait Until Page Contains  Changes saved.

    Log  Maintenance, Validations, CAlibrations, Certifications and Schedules not tested  WARN
    #Click link  Maintenance
    #Click link  Validations
    #Click link  Calibrations
    #Click link  Certifications
    #Click link  Schedule

# Containers
    Go to  ${PLONEURL}/bika_setup/bika_containers
    Page should contain  Containers
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select From List   ContainerType:list
    Input Text  Capacity  20 ml
    Select From List   Preservation:list
    Select Checkbox  PrePreserved
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# SampleTypes
    Go to  ${PLONEURL}/bika_setup/bika_sampletypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Input Text  RetentionPeriod.days:record:ignore_empty  30
    Input Text  RetentionPeriod.hours:record:ignore_empty  0
    Input Text  RetentionPeriod.minutes:record:ignore_empty  0
    Select Checkbox  Hazardous
    Select from list  SampleMatrix:list
    Input Text  Prefix  Prefix
    Input Text  MinimumVolume  20 ml
    Select from list  ContainerType:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# AnalysisCategories
    Go to  ${PLONEURL}/bika_setup/bika_analysiscategories
    Wait Until Page Contains  Analysis Categories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select From List  Department:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# AnalysisServices
    Go to                               ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains            Analysis Services
    Click link                          Add
    Wait Until Page Contains Element    title
    Input Text                          title                   New Analysis Service
    Input Text                          description             New service for Testing
    Input Text                          Unit                    measurement Unit
    Input Text                          Keyword                 AnalysisKeyword
    Select Radio Button                 PointOfCapture          lab
    Select From dropdown                Category                Metals
    Input Text                          Price                   50.23
    Input Text                          BulkPrice               30.00
    Input Text                          VAT                     15.00
    Select From dropdown                Department              Admin

    Click link                          Analysis
    Wait Until Page Contains Element    Precision
    Input Text                          Precision                                    3
    Select Checkbox                     ReportDryMatter
    select from list                    AttachmentOption                             Permitted
    Input Text                          MaxTimeAllowed.days:record:ignore_empty      3
    Input Text                          MaxTimeAllowed.hours:record:ignore_empty     3
    Input Text                          MaxTimeAllowed.minutes:record:ignore_empty   3

    Click link                          Method
    Wait Until Page Contains Element    Instrument

    # when instrument is selected method is disabled - instrument sets it.
# This is no longer true
#    select checkbox                     InstrumentEntryOfResults
#    select from list                    Instruments    AA 1   AA 2   Blott Titrator
#    select from list                    Instrument     AA 1
#    Run keyword and expect error        ValueError: Option 'Fiastar' not in list 'Instrument'.    select from list   Instrument   Fiastar
#    element should be disabled          _Method

    # Now remove instrument and set method fields manually
    unselect checkbox                   InstrumentEntryOfResults
    select from list                    Methods    12 dB SINAD   AES   ELISA
    Run keyword and expect error        ValueError: Option 'Elution' not in list '_Method'.    Select from list   _Method   Elution
    select from list                    _Method    AES

    # Set calculation fields manually
    unselect checkbox                   UseDefaultCalculation
    Select From list                    DeferredCalculation              Titration
    Wait until page contains element    InterimFields-title-2
    Input Text                          InterimFields-keyword-2          Other
    Input Text                          InterimFields-title-2            Other Field Title
    Input Text                          InterimFields-value-2            22
    Input Text                          InterimFields-unit-2             %
    Input Text                          DuplicateVariation               5
    Select Checkbox                     Accredited

    Click link                          Uncertainties
    Input Text                          Uncertainties-intercept_min-0    2
    Input Text                          Uncertainties-intercept_max-0    9
    Input Text                          Uncertainties-errorvalue-0       3.8
    Click Button                        Uncertainties_more
    Input Text                          Uncertainties-intercept_min-1    0
    Input Text                          Uncertainties-intercept_max-1    10
    Input Text                          Uncertainties-errorvalue-1       5.5

    Click link                          Result Options
    Input Text                          ResultOptions-ResultValue-0      10
    Input Text                          ResultOptions-ResultText-0       Result Text 0
    Click Button                        ResultOptions_more
    Input Text                          ResultOptions-ResultValue-1      2
    Input Text                          ResultOptions-ResultText-1       Result Text 1

    Click link                          Container and Preservation
    Select from dropdown                Container                        Pre Preserved
    Element Should Be Disabled          Preservation

    # this works but selemium doesn't manage it!
    # Select From list by label           PartitionSetup-sampletype-0      Pre Preserved
    # Element Should Be Disabled          PartitionSetup-preservation-0

    Select from list                    PartitionSetup-sampletype-0      Apple Pulp
    Textfield should contain            PartitionSetup-vol-0             100 g

    Click Button                        Save
    Wait Until Page Contains            Changes saved.

    # Duplicate AnalysisServices - first fail some validations
    Go to                      ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains   Analysis Services
    click element              xpath=//th[@cat='Metals']
    select checkbox            xpath=//input[@item_title='Calcium']
    select checkbox            xpath=//input[@item_title='Copper']
    click element              xpath=//input[@transition='duplicate']
    Wait until page contains   Copy analysis services
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_title:list']     Calcium2
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_keyword:list']   CAL2
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_title:list']     Copper2
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_keyword:list']   COP2
    click button               Copy
    Wait until page contains   Validation failed
    Page should contain        No new items were created
    Go to                      ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains   Analysis Services
    click element              xpath=//th[@cat='Metals']
    select checkbox            xpath=//input[@item_title='Calcium']
    select checkbox            xpath=//input[@item_title='Copper']
    click element              xpath=//input[@transition='duplicate']
    Wait until page contains   Copy analysis services
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_title:list']     Calcium2
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_keyword:list']   CAL2
    input text                 xpath=//tr[@source='Copper']//input[@name='dst_title:list']     Calcium2
    input text                 xpath=//tr[@source='Copper']//input[@name='dst_keyword:list']   CAL2
    click button               Copy
    Wait until page contains   Validation failed
    Page should contain        No new items were created
    # Duplicate AnalysisServices - Enter correct values
    Go to                      ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains   Analysis Services
    click element              xpath=//th[@cat='Metals']
    select checkbox            xpath=//input[@item_title='Calcium']
    select checkbox            xpath=//input[@item_title='Copper']
    click element              xpath=//input[@transition='duplicate']
    Wait until page contains   Copy analysis services
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_title:list']     Calcium2
    input text                 xpath=//tr[@source='Calcium']//input[@name='dst_keyword:list']   CAL2
    input text                 xpath=//tr[@source='Copper']//input[@name='dst_title:list']      Copper2
    input text                 xpath=//tr[@source='Copper']//input[@name='dst_keyword:list']    COP2
    click button               Copy
    Wait until page contains   were successfully

# AnalysisProfiles
    Go to    ${PLONEURL}/bika_setup/bika_analysisprofiles
    Wait Until Page Contains  Analysis Profile
    Click link  Add Profile
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Input Text  ProfileKey  Profile Key
    Click link  Analyses
    Page should contain  Profile Analyses
    Select Checkbox  xpath=//input[@item_title='Manganese']
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# AnalysisSpecifications
    Go to  ${PLONEURL}/bika_setup/bika_analysisspecs
    Wait Until Page Contains  Analysis Specifications
    Click link  Add
    Wait Until Page Contains Element  description
    Select From List  SampleType:list
    Input Text  title    Water Chemistry
    Input Text  description    Water chemistry default spec
    Click Element  xpath=//th[@cat='Water Chemistry']
    Input Text  xpath=//input[@selector='min_analysisservice-4']  3
    Input Text  xpath=//input[@selector='max_analysisservice-4']  4
    Input Text  xpath=//input[@selector='error_analysisservice-4']  5
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    Go to  ${PLONEURL}/bika_setup/bika_analysisspecs
    Wait Until Page Contains  Analysis Specifications
    Click link  Add
    Wait Until Page Contains Element  description
    Select From List  SampleType:list
    Input Text  title    Water Chemistry Alternate
    Input Text  description    Water chemistry Alternate
    Click Element  xpath=//th[@cat='Water Chemistry']
    Input Text  xpath=//input[@selector='min_analysisservice-4']  3
    Input Text  xpath=//input[@selector='max_analysisservice-4']  4
    Input Text  xpath=//input[@selector='error_analysisservice-4']  5
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# ReferenceDefinition
    Go to                               ${PLONEURL}/bika_setup/bika_referencedefinitions
    Wait Until Page Contains            Reference Definition
    Click link                          Add
    Wait Until Page Contains Element    title
    Input Text                          title          New Object
    Input Text                          description    Temporary test object
    Select Checkbox                     Blank
    Select Checkbox                     Hazardous
    Click link                          Reference Values
    Page should contain                 Specifications
    Wait Until Page Contains            Reference Values
    Click Element                       xpath=//th[@cat='Water Chemistry']
    Input Text                          xpath=//input[@selector='result_analysisservice-4']  1
    Input Text                          xpath=//input[@selector='error_analysisservice-4']   3
    Press Key                           xpath=//input[@selector='error_analysisservice-4']   \t
    Textfield value should be           xpath=//input[@selector='min_analysisservice-4']     0.97
    Textfield value should be           xpath=//input[@selector='max_analysisservice-4']     1.03
    Click Button                        Save
    Wait Until Page Contains            Changes saved.

# WorksheetTemplate
    Go to  ${PLONEURL}/bika_setup/bika_worksheettemplates
    Wait Until Page Contains  Worksheet Template
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select From List  Instrument:list
    Click link  Layout
    Wait Until Page Contains  Worksheet Layout
    Input Text  NoOfPositions  3
    Log  Can't select Reset using SESSION (breaks in zeo without sticky sessions)  WARN
    #Click Button  Reset
    sleep  1
    Click link  Analyses
    Wait Until Page Contains  Analysis Service
    Click Element  xpath=//th[@cat='Metals']
    Select Checkbox  xpath=//input[@item_title='Calcium']
    Select Checkbox  xpath=//input[@item_title='Copper']
    Select Checkbox  xpath=//input[@item_title='Iron']
    Select Checkbox  xpath=//input[@item_title='Magnesium']
    Select Checkbox  xpath=//input[@item_title='Manganese']
    Select Checkbox  xpath=//input[@item_title='Phosphorus']
    Select Checkbox  xpath=//input[@item_title='Sodium']
    Select Checkbox  xpath=//input[@item_title='Zinc']
    Click Button  Save
    Wait Until Page Contains  Changes saved.


# Add a Client
    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click link  Add
    Wait Until Page Contains Element  Name
    Input Text  Name          ACME Inc
    Input Text  ClientID      ACME
    Input Text  TaxNumber     98765A
    Input Text  Phone         011 3245679
    Input Text  Fax           011 3245678
    Input Text  EmailAddress  client@client.com
    Select Checkbox  BulkDiscount
    Select Checkbox  MemberDiscountApplies
    Click link        Address
    Select From List  PhysicalAddress.country:record    South Africa
    Select From List  PhysicalAddress.state:record      Western Cape
    Select From List  PhysicalAddress.district:record   City of Cape Town
    Input Text        PhysicalAddress.city              Cape Town
    Input Text        PhysicalAddress.zip               2000
    Input Text        PhysicalAddress.address           Foo House\nFoo Street 20\nFoo Town
    Select From List  PostalAddress.selection           PhysicalAddress
    Input Text        PostalAddress.address             Post Box 25\nFoo Town
    Select From List  BillingAddress.selection          PostalAddress
    Click link        Bank details
    Input Text        AccountType    Savings
    Input Text        AccountName    ACME INC
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111
    Click link  fieldsetlegend-preferences
    Select From List  EmailSubject:list
    Select From List  DefaultCategories:list
    Select From List  RestrictedCategories:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.

# Client Contact
    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click link  Happy Hills
    Click link  Contacts
    Click link  Add
    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  Mr
    Input Text  Firstname   Bob
    Input Text  Surname     Andrews
    Input Text  JobTitle    Desk Jockey
    Input Text  Department  Admin
    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress   client@example.com
    Input Text  BusinessPhone  555-0123
    Input Text  BusinessFax    555-0123
    Input Text  HomePhone      555-8888
    Input Text  MobilePhone    555-9999
    Click Link  Address
    Select From List  PhysicalAddress.country:record    South Africa
    Select From List  PhysicalAddress.state:record      Western Cape
    Select From List  PhysicalAddress.district:record   City of Cape Town
    Input Text        PhysicalAddress.city              Cape Town
    Input Text        PhysicalAddress.zip               2000
    Input Text        PhysicalAddress.address           Foo House\nFoo Street 20\nFoo Town
    Select From List  PostalAddress.selection           PhysicalAddress
    Input Text        PostalAddress.address             Post Box 25\nFoo Town
    Click Link  Publication preference
    Wait Until Page Contains Element  PublicationPreference:list
    Select from list  PublicationPreference:list  email
    Select Checkbox  AttachmentsPermitted
    Click Button  Save
    Wait Until Page Contains  Changes saved.

*** Keywords ***

