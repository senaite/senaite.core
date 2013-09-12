*** Settings ***

Library          Selenium2Library  timeout=10  implicit_wait=0.1
Library          String
Library  Remote  ${PLONE_URL}/RobotRemote
Resource         keywords.txt
Variables        plone/app/testing/interfaces.py
Suite Setup      Start browser
#Suite Teardown   Close All Browsers

*** Variables ***

${SELENIUM_SPEED}  0
${PLONEURL}        http://localhost:55001/plone

*** Test Cases ***

Create Attachment Types
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains Element  title
    Wait Until Page Contains  Changes saved.

Test Attachment Types Workflow
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Calculation
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element      title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Link  Calculation
    Wait Until Page Contains Element      InterimFields-keyword-0
    Input Text  InterimFields-keyword-0   This
    Input Text  InterimFields-title-0     This Field
    Input Text  InterimFields-value-0     1
    Input Text  InterimFields-unit-0      mg/l
    Input Text  InterimFields-keyword-1   That
    Input Text  InterimFields-title-1     That Field
    Input Text  InterimFields-value-1     1
    Input Text  InterimFields-unit-1      mg/l
    Input Text  Formula                   [This] + [That]
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Calculations Workflow
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Container Type
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Container Types Workflow
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Preservations
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

Test Preservations Workflow
    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Update Laboratory Information
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
    Input Text        LabURL                            ${LabURL}
    Click link        Bank details
    Input Text        AccountType    Savings
    Input Text        AccountName    Test Laboratory Inc
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111
    Click link       Accreditation
    Input Text       Confidence                 95
    Select Checkbox  LaboratoryAccredited
    Input Text       AccreditationBodyLong      Accreditation Body Name
    Input Text       AccreditationBody          ABBREVIATION
    Input Text       AccreditationBodyURL       http://www.body.com
    Input Text       Accreditation              Accreditation Type
    Input Text       AccreditationReference     Reference
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create Method
    Go to  ${PLONEURL}/bika_setup/methods
    Click link    Add
    Wait Until Page Contains Element    title
    Input Text    title                 A New Method
    Input Text    description           Things you can do, some can't be done
    Input Text    Instructions
    Click Button  Save
    Wait Until Page Contains            Changes saved.

Test Methods Workflow
    Go to  ${PLONEURL}/bika_setup/methods
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Sample Matrices
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.


Test Sample Matrices Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  default
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Sample Points
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
    Input Text  Elevation  ${Elevation}                  10
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Sample Points Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  all
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create Sampling Deviations
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Sampling Deviations Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  default
    Select Checkbox  xpath=//[contains(@id, '_cb_')][1]
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

Create LabManager
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

Create LabDepartment
    Go to  ${PLONEURL}/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select from list  Manager:list   Lab Manager 1
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create LabContact
    Log  Lab Contact  WARN
    Go to  ${PLONEURL}/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  Mr
    Input Text  Firstname   Avon
    Input Text  Surname     Barksdale
    Input Text  JobTitle    Player
    Select from list  Department:list  Administration

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
    Select From List  BillingAddress.selection          PostalAddress

    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create Suppliers
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Page should contain  Suppliers
    Click link  Add
    Wait Until Page Contains Element  TaxNumber
    Input Text        Name            Supplier Name
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
    Input Text        LabURL                            ${LabURL}
    Click link        Bank details
    Input Text        AccountType    Savings
    Input Text        AccountName    Supplier Inc
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111

    Click link  Reference Samples
    Wait Until Page Contains Element  Remarks
    Input Text  Remarks  Reference Sample Remarks
    Click button  Save remarks
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Select From List  ReferenceDefinition:list
    Select Checkbox  Blank
    Select Checkbox  Hazardous
    Select From List  ReferenceManufacturer:list
    Input Text  CatalogueNumber  Catalogue Number
    Input Text  LotNumber  Lot Number

    Click Link  Dates
    Wait Until Page Contains Element  DateSampled
    SelectPrevMonthDate  DateSampled  1
    SelectPrevMonthDate  DateReceived  3
    SelectPrevMonthDate  DateOpened  4
    SelectNextMonthDate  ExpiryDate  5

    Click Link  Reference Values

    Log  No new reference values are added  WARN

    Wait Until Page Contains  Expected Values
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #now test Contacts
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Click link  ${Name}

    Wait Until Page Contains Element  Remarks
    Click link  Contacts
    Wait Until Page Contains Element  Remarks

    Input Text  Remarks  Contacts Remarks
    Click button  Save remarks
    Click link  Add
    Wait Until Page Contains Element  Salutation
    Input Text  Salutation  ${Salutation}
    Input Text  Firstname  ${Firstname}
    Input Text  Surname  ${Surname}
    Input Text  JobTitle  ${Jobtitle}
    Input Text  Department  ${Department}

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
    Select From List  PhysicalAddress.country:record  ${Country}
    Select From List  PhysicalAddress.state:record  ${State}
    #district is on autoselect last entry
    Select From List  PhysicalAddress.district:record
    Input Text  PhysicalAddress.city  ${City}
    Input Text  PhysicalAddress.zip  ${ZIP}
    Input Text  PhysicalAddress.address  ${Physical Address}
    Select From List  PostalAddress.selection  PhysicalAddress
    Input Text  PostalAddress.address  ${Postal Address}

    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #now test Instruments
    #for that you need a supplier,manufacturer, instrument type and instrument - defined in that order
    #got supplier - so start with basic def of Manufacturer

    Go to  ${PLONEURL}/bika_setup/bika_manufacturers
    Page should contain  Manufacturers
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #now define an Instrument Type
    Log  Instrument Types  WARN

    Go to  ${PLONEURL}/bika_setup/bika_instrumenttypes
    Page should contain  Instrument Types
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.


    #Click link  Instruments
    Log  Instrument  WARN
#saving Instruments (from within) causes system to throw exception
#Approach instrument from another angle - go direct to URL

    Go to   ${PLONEURL}/bika_setup/bika_instruments
    Page should contain  Instruments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select From List  InstrumentType
    Select From List  Manufacturer
    Select From List  Supplier

    Input Text  Model  Instrument Model
    Input Text  SerialNo  Instrument Serial Number 123

    Select From List  DataInterface:list
    Input Text  DataInterfaceOptions-Key-0  Data Interface Options Key
    Input Text  DataInterfaceOptions-Value-0  Data Interface Options Value
    # Input Text  cmfeditions_version_comment  ${Change note}

    Click Button  Save
    sleep  0.5

    Click link  Procedures
    Wait Until Page Contains Element  InlabCalibrationProcedure
    Input Text  InlabCalibrationProcedure  Inlab Calibration Procedure
    Input Text  PreventiveMaintenanceProcedure  Preventive Maintenance Procedure

    Click Button  Save
    Wait Until Page Contains  Changes saved.

#At this stage numerous seletion options have appeared on a seperate bar Mainteneance etc
#test at later stage

    Log  Maintenance, Validations, CAlibrations, Certifications and Schedules not tested  WARN

    #Click link  Maintenance

    #Click link  Validations

    #Click link  Calibrations

    #Click link  Certifications

    #Click link  Schedule

    #end Suppliers

Create Containers
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

Create SampleTypes
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

Create AnalysisCategories
    Log  Analysis Categories  WARN
    Go to  ${PLONEURL}/bika_setup/bika_analysiscategories
    Wait Until Page Contains  Analysis Categories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select From List  Department:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create AnalysisServices
    Go to                ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains  Analysis Services
    Click link           Add
    Wait Until Page Contains Element  title
    Input Text           title         New Analysis Service
    Input Text           description   New service for Testing
    Input Text           Unit          measurement Unit
    Input Text           Keyword       AnalysisKeyword
    Select Radio Button       PointOfCapture  lab
    Select From Dropdown      Category
    Input Text  Price  50.23
    Input Text  BulkPrice  30.00
    Input Text  VAT  15.00
    Select First From Dropdown  Department
    Click link  Analysis
    Wait Until Page Contains Element  Precision
    Input Text  Precision  3
    Select Checkbox  ReportDryMatter
    Select From List  AttachmentOption  n
    Input Text  MaxTimeAllowed.days:record:ignore_empty  3
    Input Text  MaxTimeAllowed.hours:record:ignore_empty  3
    Input Text  MaxTimeAllowed.minutes:record:ignore_empty  3
    Click link  Method
    Wait Until Page Contains Element  Instrument
    Select First From Dropdown  Method
    Select First From Dropdown  Instrument
    Select First From Dropdown  Calculation
    Input Text  InterimFields-keyword-0  Keyword
    Input Text  InterimFields-title-0  Field Title
    Input Text  InterimFields-value-0  Default Value
    Input Text  InterimFields-unit-0  Unit
    Select Checkbox  InterimFields-hidden-0
    Input Text  DuplicateVariation  5
    Select Checkbox  Accredited
    Click link  Uncertainties
    Input Text  Uncertainties-intercept_min-0  2
    Input Text  Uncertainties-intercept_max-0  9
    Input Text  Uncertainties-errorvalue-0  3.8
    Click Button  Uncertainties_more
    Input Text  Uncertainties-intercept_min-1  0
    Input Text  Uncertainties-intercept_max-1  10
    Input Text  Uncertainties-errorvalue-1  5.5
    Click link  Result Options
    Input Text  ResultOptions-ResultValue-0  10
    Input Text  ResultOptions-ResultText-0  Result Text 0
    Click Button  ResultOptions_more
    Input Text  ResultOptions-ResultValue-1  2
    Input Text  ResultOptions-ResultText-1  Result Text 1
    Click link  Container and Preservation
    Select Checkbox  Separate
    Select First From Dropdown  Preservation
    Select First From Dropdown  Container
    Select From List  PartitionSetup-sampletype-0
    Click Element  PartitionSetup-separate-0
    Select From List  PartitionSetup-preservation-0
    Select From List  PartitionSetup-container-0
    Input Text  PartitionSetup-vol-0  Volume 123
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create AnalysisProfiles
    Go to    ${PLONEURL}/bika_setup/bika_analysisprofiles
    Wait Until Page Contains  Analysis Profile
    Click link  Add Profile
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Input Text  ProfileKey  Profile Key
    Click link  Analyses
    Page should contain  Profile Analyses
    Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create AnalysisSpecifications
    Go to  ${PLONEURL}/bika_setup/bika_analysisspecs
    Wait Until Page Contains  Analysis Specifications
    Click link  Add
    Wait Until Page Contains Element  description
    Select From List  SampleType:list
    Input Text  description    Temporary test object
    Click link  Specifications
    Page should contain  Specifications
    Click Element  xpath=//th[@cat='Water Chemistry']
    Input Text  xpath=//input[@field='min']  3
    Input Text  xpath=//input[@field='max']  4
    Input Text  xpath=//input[@field='error']  5
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create ReferenceDefinition
    Go to  ${PLONEURL}/bika_setup/bika_referencedefinitions
    Wait Until Page Contains  Reference Definition
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Select Checkbox  Blank
    Select Checkbox  Hazardous
    Click link  Reference Values
    Page should contain  Specifications
    Wait Until Page Contains  Reference Values
    Click Element  xpath=//th[@cat='Water Chemistry']
    Input Text  xpath=//input[@field='result']  3
    Input Text  xpath=//input[@field='error']  5
    Click Element  xpath=//input[@field='min']
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create WorksheetTemplate
    Log  Worksheet Template  WARN
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
    Log  BUG: Worksheet Template:   WARN
    Click Button  Reset
    sleep  1
    Click link  Analyses
    Wait Until Page Contains  Analysis Service
    Click Element  xpath=//th[@cat='Water Chemistry']
    Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create ARTemplates
    Go to  ${PLONEURL}/bika_setup/bika_artemplates
    Wait Until Page Contains  AR Templates
    Click link  Add Template
    Wait Until Page Contains Element  title
    Input Text  title          New Object
    Input Text  description    Temporary test object
    Input Text  SamplePoint   Borehole 12
    Input Text  SampleType    Water
    Select Checkbox  ReportDryMatter
    Click link  Sample Partitions
    Wait Until Page Contains  Sample Partitions
    Select First From Dropdown  Partitions-Container-0
    Select First From Dropdown  Partitions-Preservation-0
    Click Button  More
    Select Specific From Dropdown  Partitions-Container-1  Glass
    Select Specific From Dropdown  Partitions-Preservation-1  HNO3
    Click Link  Analyses
    Wait Until Page Contains Element  AnalysisProfile
    Select from list   AnalysisProfile
    Log  BUG: AR Template: Analysis Profile Dropdown fails to close?  WARN
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Add a Client
    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click link  Add
    Wait Until Page Contains Element  Name
    Input Text  Name          ACME Things
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
    Input Text        AccountName    Test Laboratory Inc
    Input Text        AccountNumber  0123456789
    Input Text        BankName       Standard Bank
    Input Text        BankBranch     555-0111
    Click link  fieldsetlegend-preferences
    Select From List  EmailSubject:list
    Select From List  DefaultCategories:list
    Select From List  RestrictedCategories:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Create a Client Contact
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
    Select From List  BillingAddress.selection          PostalAddress
    Click Link  Publication preference
    Wait Until Page Contains Element  PublicationPreference
    Select from list  PublicationPreference:list  email
    Select Checkbox  AttachmentsPermitted
    Click Button  Save
    Wait Until Page Contains  Changes saved.

*** Keywords ***

Start browser
    Enable autologin as  test_labmanager
    Set selenium speed  ${SELENIUM_SPEED}
    Open browser        ${PLONEURL}/bika_setup/edit
    Click link  Analyses
    Select Checkbox  SamplingWorkflowEnabled
    Click Button  Save
    Wait Until Page Contains  Changes saved.


