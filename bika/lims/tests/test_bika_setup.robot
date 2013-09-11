*** Settings ***

Library          Selenium2Library  timeout=10  implicit_wait=0.2
Library          String
Resource         keywords.txt
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${Manager Firstname}  Manager Firstname
${Manager Surname}    Manager Surname

#following are used to locate Analysis Service when defining an Analysis Profile
${AnalysisServices_global_Title}   Analysis Services Title
${AnalysisServices_locator}        Select ${AnalysisServices_global_Title}
${AnalysisCategory_global_Title}   Analysis Category Title
${ClientName_global}               Client Name

*** Test Cases ***

Setup

    Log in  test_labmanager    test_labmanager

    #Start independent Bika Setup options

    #BIKA Setup
    RunBikaSetup

    #Attachment Types
    Create Attachment Types  Title=Attachment Types Title
    ...    Description=Attachment Types Description

    Test Attachment Types Workflow

    #Batch Labels
    Create Batch Labels  Title=Batch Labels Title

    Test Batch Labels Workflow

    Test Batch Labels Cancel

    #Calculations
    Test Calculations Cancel  Title=Calculations Title
    ...    Description=Calculations Description
    ...    Change note=Calculations Change note

    Create Calculations Description  Title=Calculations Title
    ...    Description=Calculations Description
    ...    Change note=Calculations Change note

    Create Calculations Calculation  Keyword=Keyword
    ...    Field Title=Field Title
    ...    Default Value=Default Value
    ...    Unit=Unit
    ...    Calculation Formula=Calculation Formula
    ...    Change note=Calculations Change note

    Test Calculations Workflow

    #Container Types
    Test Container Types Cancel  Title=Container Types Title
    ...    Description=Container Types Description

    Create Container Types  Title=Container Types Title
    ...    Description=Container Types Description

    Test Container Types Workflow

    #Preservations
    Test Preservations Cancel  Title=Preservations Title
    ...    Description=Preservations Description


    Create Preservations  Title=Preservations Title
    ...    Description=Preservations Description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15

    Test Preservations Workflow


    #Lab Products
    Test Lab Products Cancel  Title=Lab Products Title
    ...    Description=Lab Products Description
    ...    Volume=Lab Products Volume
    ...    Unit=Lab Products Unit
    ...    VAT=16.00
    ...    Price=4321.39

    Create Lab Products  Title=Lab Products Title
    ...    Description=Lab Products Description
    ...    Volume=Lab Products Volume
    ...    Unit=Lab Products Unit
    ...    VAT=16.00
    ...    Price=4321.39

    Test Lab Products Workflow

    #Laboratory Information
    Test Laboratory Information Cancel  Name=Laboratory Name
    ...    VAT number=VAT number
    ...    Phone=Phone
    ...    Fax=Fax

    Create Laboratory Information  Name=Laboratory Name
    ...    VAT number=VAT number
    ...    Phone=Phone
    ...    Fax=Fax
    ...    Email=info@lab.com
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Foo House\nFoo Street 20\nFoo Town
    ...    Postal Address=Post Box 25\nFoo Town
    ...    LabURL=http://www.lab.com
    #not all variables passed - some are locally defined

    #Methods
    Test Methods Cancel  Title=Methods Title
    ...    Description=Methods Description
    ...    Instructions=Methods Instructions
    ...    Change note=Methods Change note

    Create Methods  Title=Methods Title
    ...    Description=Methods Description
    ...    Instructions=Methods Instructions
    ...    Change note=Methods Change note

    Test Methods Workflow


    #Sample Conditions
    Test Sample Conditions Cancel  Title=Sample Conditions Title
    ...    Description=Sample Conditions Description


    Create Sample Conditions  Title=Sample Conditions Title
    ...    Description=Sample Conditions Description


    Test Sample Conditions Workflow


    #Sample Matrices
    Test Sample Matrices Cancel  Title=Sample Matrices Title
    ...    Description=Sample Matrices Description


    Create Sample Matrices  Title=Sample Matrices Title
    ...    Description=Sample Matrices Description


    Test Sample Matrices Workflow

   #Sample Points
    Test Sample Points Cancel  Title=Sample Points Title
    ...    Description=Sample Points Description
    ...    Change note=Sample Points Change note

    Create Sample Points  Title=Sample Points Title
    ...    Description=Sample Points Description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15
    ...    Change note=Sample Points Change note

    Create Sample Points Location  Lat degrees=45
    ...    Lat minutes=30
    ...    Lat seconds=30
    ...    Lat bearing=N
    ...    Long degrees=45
    ...    Long minutes=30
    ...    Long seconds=30
    ...    Long bearing=E
    ...    Elevation=10
    ...    Change note=Sample Points Location Change note


    Test Sample Points Workflow


    #Sampling Deviations
    Test Sampling Deviations Cancel  Title=Sampling Deviations Title
    ...    Description=Sampling Deviations Description

    Create Sampling Deviations  Title=Sampling Deviations Title
    ...    Description=Sampling Deviations Description

    Test Sampling Deviations Workflow


#End independent Bika Setup options


#Start dependent Bika Setup options


    #Lab Contact
    #requires 3 steps for testing the complete creation of a lab contact
    # 1) lab manager
    # 2) lab department which requires a lab manager
    # 3) lab contact which requires a department and manager

    #note the use of global variables Firstname and Surname

    #create a Lab Manager - this is a Lab Contact who is also a manager
    Create LabManager  Salutation=Dr
    ...    Firstname=${Manager Firstname}
    ...    Surname=${Manager Surname}
    ...    Email=manager@lab.com
    ...    Jobtitle=Lab manager


    #create a Lab Department
    #a department is required for creating a lab contact
    Create LabDepartment  Title=Lab department
    ...    Description=Lab department description
    ...    Manager=${Manager Firstname} ${Manager Surname}


    #now create a Lab Contact using the manager and department info
    Create LabContact  Salutation=Mr
    ...    Firstname=Contact Firstname
    ...    Middleinitial=Contact Middleinitial
    ...    Middlename=Contact Middlename
    ...    Surname=Contact Surname
    ...    Jobtitle=Analyst
    #this is the previously created department
    ...    Department=Lab department
    ...    Email=analyst@lab.com
    ...    Businessphone=012 345 678
    ...    Businessfax=012 345 679
    ...    Homephone=012 987 654
    ...    Mobilephone=098 765 432
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Foo House\nFoo Street 20\nFoo Town
    ...    Postal Address=Post Box 25\nFoo Town
    ...    Preference=file

    #signature upload not tested
    #end LabContact

    #Suppliers - dependent on Manufacturer, Instrument Type and Instrument
    Test Suppliers Cancel  Name=Supplier Name
    ...    VAT number=VAT number
    ...    Phone=Phone
    ...    Fax=Fax

    Create Suppliers  Name=Suppliers Name
    ...    VAT number=VAT number
    ...    Phone=Phone
    ...    Fax=Fax
    ...    Email=info@supplier.com
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Foo House\nFoo Street 20\nFoo Town
    ...    Postal Address=Post Box 25\nFoo Town
    ...    AccountType=Account Type
    ...    AccountName=Account Name
    ...    AccountNumber=Account Number
    ...    BankName=Bank Name
    ...    BankBranch=Bank Branch
    ...    Salutation=Mr
    ...    Firstname=Contact Firstname
    ...    Middleinitial=Contact Middleinitial
    ...    Middlename=Contact Middlename
    ...    Surname=Contact Surname
    ...    Jobtitle=Sales Representative
    ...    Department=Sales Department
    ...    ManufacturerTitle=Manufacturer Title
    ...    ManufacturerDescription=Manufacturer Description
    ...    InstrumentTypeTitle=Instrument Type Title
    ...    Instrument=Instrument Name
    ...    Change note=Instrument Change note
    #end Supplier

    #Containers - dependant on Container Types and Preservations
    Create Containers  Title=Containers Title
    ...    Description=Containers Description
    ...    Change note=Containers Change note
    #end Containers


    #Sample Types
    Create SampleTypes  Title=Sample Types Title
    ...    Description=Sample Types description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15
    #end Sample Types

    #Analysis Categories - requires lab department
    Create AnalysisCategories  Description=Analysis Category description
    #end Analysis Categories

    #Analysis Services - requires Analysis Categories, Methods, Instruments, Calculations, .....
    #Analysis Services <- note the use of global variable as title - also used by Analysis Profile
    Create AnalysisServices  Description=Analysis Services description
    #end Analysis Services

    #Analysis Profile <- note the use of global variable Analysis Service title
    Create AnalysisProfiles  Title=Analysis Profiles Title
    ...    Description=Analysis Profiles description
    #end Analysis Profile


    #Analysis Specifications <- note use of global variable ${AnalysisCategory_global_Title}
    Create AnalysisSpecifications  Description=Analysis Specifications description
    #end Analysis Specifications


    #Reference Definition
    Create ReferenceDefinition  Title= Reference DefinitionTitle
    ...    Description=ReferenceDefinition description
    #endReference Definition

    #Worksheet Template
    Create WorksheetTemplate  Title= Reference DefinitionTitle
    ...    Description=ReferenceDefinition description
    #end Worksheet Template


    Create ARTemplates  Title=Reference DefinitionTitle
    ...    Description=ReferenceDefinition description
    #end AR Templates

    Create AddClients  ID=987654321
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Client House\nClient Street 20\nClient Town
    ...    Postal Address=Post Box 25\nClient Town
    #end Clients

    #Client Contacts
    Create ClientContact  Salutation=Mrs
    ...    Firstname=Contact Firstname
    ...    Middleinitial=Contact Middleinitial
    ...    Middlename=Contact Middlename
    ...    Surname=Contact Surname
    ...    Jobtitle=Staff Geologist
    #this is the previously created department
    ...    Department=Client department
    ...    Email=staff@client.com
    ...    Businessphone=012 123 678
    ...    Businessfax=012 123 679
    ...    Homephone=012 789 654
    ...    Mobilephone=098 567 432
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Client House\nClient Street 20\nClient Town
    ...    Postal Address=Post Box 25\nClient Town
    ...    Preference=print

    #signature upload not tested
    #end ClientContact


#End dependent Bika Setup options

    DiffTime  ${saveTime}


*** Keywords ***


Start browser
    ShowAndSaveTime
    Log  Start Bika Setup Testing: independent categories  WARN
    Open browser  ${PLONEURL}/login_form
    Set selenium speed  ${SELENIUM_SPEED}


#BIKA Setup
RunBikaSetup
    Log  BIKA Setup  WARN
    Go to  ${PLONEURL}/bika_setup/edit
    Click link  Analyses
    Select Checkbox  SamplingWorkflowEnabled
    Click Button  Save
    Wait Until Page Contains  Changes saved.


#Attachment Types
Create Attachment Types
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Attachment Types  WARN
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains Element  title
    Wait Until Page Contains  Changes saved.

# add test to check that correct page is displayed - not edit page ??

Test Attachment Types Workflow
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


#Batch Labels
Create Batch Labels
    [Arguments]  ${Title}=
    Log  Batch Labels  WARN
    Go to  ${PLONEURL}/bika_setup/bika_batchlabels
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Click Button  Save
    #portalMessage info
    Wait Until Page Contains  Changes saved.


#specifically test the Deactivate and Activate options
Test Batch Labels Workflow
    Go to  ${PLONEURL}/bika_setup/bika_batchlabels
    Select Checkbox  list_select_all
    #sleep  1
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    #after deactivation no labels are shown
    #first show all labels before continuing
    Click link  all
    #sleep  1
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.

#specifically test the Cancel option
Test Batch Labels Cancel
    Go to  ${PLONEURL}/bika_setup/bika_batchlabels
    Click link  Add
    Wait Until Page Contains Element  title
    Click Button  Cancel
    Wait Until Page Contains  Add New Item operation was cancelled.


#Calculations
Test Calculations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Log  Calculations  WARN
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #the name of the Change note field is: cmfeditions_version_comment
    Input Text  cmfeditions_version_comment  ${Change note}
    #sleep  2
    Click Button  Cancel
    Wait Until Page Contains  Add New Item operation was cancelled.

Create Calculations Description
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Go to  ${PLONEURL}/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #the name of the Change note field is: cmfeditions_version_comment
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Wait Until Page Contains  Changes saved.

#continue on current page after saving

Create Calculations Calculation
    [Arguments]  ${Keyword}=
    ...          ${Field Title}=
    ...          ${Default Value}=
    ...          ${Unit}=
    ...          ${Calculation Formula}=
    ...          ${Change note}=
    Click Link  Calculation
    Wait Until Page Contains Element  InterimFields-keyword-0
    Input Text  InterimFields-keyword-0  ${Keyword}
    Input Text  InterimFields-title-0  ${Field Title}
    Input Text  InterimFields-value-0  ${Default Value}
    Input Text  InterimFields-unit-0  ${Unit}
    Input Text  Formula  ${Calculation Formula}
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Calculations Workflow
    Log  BUG: Calculations Workflow: - select all - deactivate - select all - activate  WARN
    Log  BUG: Calculations Workflow: - activate_transition Button does not appear  WARN
    Log  BUG: Calculations Workflow: - The added calculation also does not appear after deactivating  WARN
    Log  BUG: Calculations Workflow: not tested  WARN

    #Go to  ${PLONEURL}/bika_setup/bika_calculations
    #Select Checkbox  list_select_all
    #Click Button  deactivate_transition
    #Wait Until Page Contains  Changes saved.
    #Page Should Contain  Cannot deactivate calculation

    #now click the link All - also tested Click Link  All
    #Click Element  xpath=//a[@id='all']

    #Wait Until Page Contains Element  activate_transition
    #Select Checkbox  list_select_all
    #Click Button  activate_transition
    #Wait Until Page Contains  Changes saved.


#Container Types
Test Container Types Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Container Types  WARN
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #sleep  2
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.

Create Container Types
    [Arguments]  ${Title}=
    ...          ${Description}=
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains  Changes saved.


Test Container Types Workflow
    Go to  ${PLONEURL}/bika_setup/bika_containertypes
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.



#Preservations
Test Preservations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Preservations  WARN
    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select Radio Button  Category  field
    Select Radio Button  Category  lab
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Preservations
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Days}=
    ...          ${Hours}=
    ...          ${Minutes}=

    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select Radio Button  Category  field
    Select Radio Button  Category  lab
    Input Text  RetentionPeriod.days:record:ignore_empty  ${Days}
    Input Text  RetentionPeriod.hours:record:ignore_empty  ${Hours}
    Input Text  RetentionPeriod.minutes:record:ignore_empty  ${Minutes}

    Click Button  Save
    Wait Until Page Contains  Changes saved.


Test Preservations Workflow
    Go to  ${PLONEURL}/bika_setup/bika_preservations
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


#Lab Products
Test Lab Products Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Volume}=
    ...          ${Unit}=
    ...          ${VAT}=
    ...          ${Price}=
    Log  Lab Products  WARN
    Go to  ${PLONEURL}/bika_setup/bika_labproducts
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  Volume  ${Volume}
    Input Text  Unit  ${Unit}
    Input Text  VAT  ${VAT}
    Input Text  Price  ${Price}
    #sleep  2
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.

Create Lab Products
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Volume}=
    ...          ${Unit}=
    ...          ${VAT}=
    ...          ${Price}=
    Go to  ${PLONEURL}/bika_setup/bika_labproducts
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  Volume  ${Volume}
    Input Text  Unit  ${Unit}
    Input Text  VAT  ${VAT}
    Input Text  Price  ${Price}
    #sleep  2
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Lab Products Workflow
    Go to  ${PLONEURL}/bika_setup/bika_labproducts
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


#Laboratory Information
Test Laboratory Information Cancel
    [Arguments]  ${Name}=
    ...          ${VAT number}=
    ...          ${Phone}=
    ...          ${Fax}=
    Log  Laboratory Information  WARN
    Go to  ${PLONEURL}/bika_setup/laboratory/base_edit
    Input Text  Name  ${Name}
    Input Text  TaxNumber  ${VAT number}
    Input Text  Phone  ${Phone}
    Input Text  Fax  ${Fax}
    #sleep  2
    Click Button  Cancel
#page returns to Edit Bika Setup which is an odd place to end up on!!!
    Page should contain  Edit cancelled

Create Laboratory Information
    [Arguments]  ${Name}=
    ...          ${VAT number}=
    ...          ${Phone}=
    ...          ${Fax}=
    ...          ${Email}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    ...          ${LabURL}=
    Go to  ${PLONEURL}/bika_setup/laboratory/base_edit
    Input Text  Name  ${Name}
    Input Text  TaxNumber  ${VAT number}
    Input Text  Phone  ${Phone}
    Input Text  Fax  ${Fax}

    Click link  Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Input Text  EmailAddress  ${Email}
    Select From List  PhysicalAddress.country:record  ${Country}
    Select From List  PhysicalAddress.state:record  ${State}
    #district is on autoselect last entry
    Select From List  PhysicalAddress.district:record
    Input Text  PhysicalAddress.city  ${City}
    Input Text  PhysicalAddress.zip  ${ZIP}
    Input Text  PhysicalAddress.address  ${Physical Address}
    Select From List  PostalAddress.selection  PhysicalAddress
    Input Text  PostalAddress.address  ${Postal Address}
    Select From List  BillingAddress.selection  PostalAddress
    Input Text  LabURL  ${LabURL}

    #following variables not via arguments

    Click link  Bank details
    Input Text  AccountType  Account Type
    Input Text  AccountName  Account Name
    Input Text  AccountNumber  Account Number
    Input Text  BankName  Bank Name
    Input Text  BankBranch  Bank Branch

    Click link  Accreditation
    Input Text  Confidence  100
    Select Checkbox  LaboratoryAccredited
    Input Text  AccreditationBodyLong  Accreditation Body Name
    Input Text  AccreditationBody  ABBREVIATION
    Input Text  AccreditationBodyURL  http://www.body.com
    Input Text  Accreditation  Accreditation Type
    Input Text  AccreditationReference  Reference

    Click Button  Save
    Wait Until Page Contains  Changes saved.


#Methods
Test Methods Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Instructions}=
    ...          ${Change note}=
    Log  Methods  WARN
    Go to  ${PLONEURL}/bika_setup/methods
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  Instructions  ${Instructions}
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.

Create Methods
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Instructions}=
    ...          ${Change note}=
    Go to  ${PLONEURL}/bika_setup/methods
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  Instructions  ${Instructions}
    #load document is not tested
    Input Text  cmfeditions_version_comment  ${Change note}
    #sleep  2
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Methods Workflow
    Go to  ${PLONEURL}/bika_setup/methods
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click Link  All
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.



#Sample Conditions
Test Sample Conditions Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Sample Conditions  WARN
    Go to  ${PLONEURL}/bika_setup/bika_sampleconditions
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sample Conditions
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  ${PLONEURL}/bika_setup/bika_sampleconditions
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains  Changes saved.


Test Sample Conditions Workflow
    Go to  ${PLONEURL}/bika_setup/bika_sampleconditions
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
#the link to "All" should also have an id called "all" like all others - not default
    #Click Link  All
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition

#Sample Matrices
Test Sample Matrices Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Sample Matrices  WARN
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sample Matrices
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #sleep  2
    Click Button  Save
    Wait Until Page Contains  Changes saved.
#Page contains "Changes saved" but is it the correct page?


Test Sample Matrices Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplematrices
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
#this link should also be called "all" like all others - not default
    #Click Link  All
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


#Sample Points
Test Sample Points Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Log  Sample Points  WARN
    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #Sampling Frequency data not entered for cancel test
    Select Checkbox  Composite
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sample Points
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Days}=
    ...          ${Hours}=
    ...          ${Minutes}=
    ...          ${Change note}=

    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  SamplingFrequency.days:record:ignore_empty  ${Days}
    Input Text  SamplingFrequency.hours:record:ignore_empty  ${Hours}
    Input Text  SamplingFrequency.minutes:record:ignore_empty  ${Minutes}
    Select Checkbox  Composite
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Wait Until Page Contains  Changes saved.


#continue on current page after saving

Create Sample Points Location

    Click link  Location
        [Arguments]  ${Lat degrees}=
    ...          ${Lat minutes}=
    ...          ${Lat seconds}=
    ...          ${Lat bearing}=
    ...          ${Long degrees}=
    ...          ${Long minutes}=
    ...          ${Long seconds}=
    ...          ${Long bearing}=
    ...          ${Elevation}=
    ...          ${Change note}=

    Input Text  Latitude.degrees:record:ignore_empty  ${Lat degrees}
    Input Text  Latitude.minutes:record:ignore_empty  ${Lat minutes}
    Input Text  Latitude.seconds:record:ignore_empty  ${Lat seconds}
    Input Text  Latitude.bearing:record:ignore_empty  ${Lat bearing}

    Input Text  Longitude.degrees:record:ignore_empty  ${Long degrees}
    Input Text  Longitude.minutes:record:ignore_empty  ${Long minutes}
    Input Text  Longitude.seconds:record:ignore_empty  ${Long seconds}
    Input Text  Longitude.bearing:record:ignore_empty  ${Long bearing}
    Input Text  Elevation  ${Elevation}
    Click Button  Save
    Wait Until Page Contains  Changes saved.



Test Sample Points Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplepoints
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


#Sampling Deviations
Test Sampling Deviations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Sampling Deviations  WARN
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sampling Deviations
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains  Changes saved.

Test Sampling Deviations Workflow
    Go to  ${PLONEURL}/bika_setup/bika_samplingdeviations
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Wait Until Page Contains  Changes saved.
#require consistency - change id to all not default
    #Click link  all
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Wait Until Page Contains  Changes saved.


    #End independent Bika Setup options
    Log  End independent Bika Setup options  WARN

    #Start dependent Bika Setup options
    Log  Start dependent Bika Setup options  WARN


#LabContact
#3 steps to create a LabContact
#Labmanager, LabDepartment and LabContact

#Lab Manager
Create LabManager
    [Arguments]  ${Salutation}=
    ...          ${Firstname}=
    ...          ${Surname}=
    ...          ${Email}=
    ...          ${Jobtitle}=
    Log  Lab Manager  WARN
    Go to  ${PLONEURL}/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Salutation
    Input Text  Salutation  ${Salutation}
    Input Text  Firstname  ${Firstname}
    Input Text  Surname  ${Surname}
    Input Text  JobTitle  ${Jobtitle}

    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress  ${Email}

    Click Button  Save
    Wait Until Page Contains  Changes saved.

#Lab Department
Create LabDepartment
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Manager}=
    Log  Lab Department  WARN
    Go to  ${PLONEURL}/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select from list  Manager:list  ${Manager}
    Click Button  Save
    Wait Until Page Contains  Changes saved.

#Lab Contact
Create LabContact
    [Arguments]  ${Salutation}=
    ...          ${Firstname}=
    ...          ${Middleinitial}=
    ...          ${Middlename}=
    ...          ${Surname}=
    ...          ${Jobtitle}=
    ...          ${Department}=
    ...          ${Email}=
    ...          ${Businessphone}=
    ...          ${Businessfax}=
    ...          ${Homephone}=
    ...          ${Mobilephone}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    ...          ${Preference}=
    Log  Lab Contact  WARN
    Go to  ${PLONEURL}/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  ${Salutation}
    Input Text  Firstname  ${Firstname}
    Input Text  Middleinitial  ${Middleinitial}
    Input Text  Middlename  ${Middlename}
    Input Text  Surname  ${Surname}
    Input Text  JobTitle  ${Jobtitle}
    Select from list  Department:list  ${Department}
    #sleep  2

    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress  ${Email}
    Input Text  BusinessPhone  ${Businessphone}
    Input Text  BusinessFax  ${Businessfax}
    Input Text  HomePhone  ${Homephone}
    Input Text  MobilePhone  ${Mobilephone}
    #sleep  2

    Click Link  Address
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
    #sleep  2

    Click Link  Publication preference
    Wait Until Page Contains Element  PublicationPreference
    Select from list  PublicationPreference:list  ${Preference}
    #sleep  2

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end LabContact


#Suppliers
Test Suppliers Cancel
    [Arguments]  ${Name}=
    ...          ${VAT number}=
    ...          ${Phone}=
    ...          ${Fax}=
    Log  Suppliers  WARN
    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Click link  Add
    Input Text  Name  ${Name}
    Input Text  TaxNumber  ${VAT number}
    Input Text  Phone  ${Phone}
    Input Text  Fax  ${Fax}
    Click Button  Cancel
#page returns to Edit Bika Setup which is an odd place to end up on!!!
    Page should contain  Add New Item operation was cancelled.

Create Suppliers
    [Arguments]  ${Name}=
    ...          ${VAT number}=
    ...          ${Phone}=
    ...          ${Fax}=
    ...          ${Email}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    ...          ${AccountType}=
    ...          ${AccountName}=
    ...          ${AccountNumber}=
    ...          ${BankName}=
    ...          ${BankBranch}=
    ...          ${Salutation}=
    ...          ${Firstname}=
    ...          ${Middleinitial}=
    ...          ${Middlename}=
    ...          ${Surname}=
    ...          ${Jobtitle}=
    ...          ${Department}=
    ...          ${ManufacturerTitle}=
    ...          ${ManufacturerDescription}=
    ...          ${InstrumentTypeTitle}=
    ...          ${Instrument}=
    ...          ${Change note}=


    Go to  ${PLONEURL}/bika_setup/bika_suppliers
    Page should contain  Suppliers
    Click link  Add
    #Wait Until Page Contains Element  Name
    Wait Until Page Contains Element  TaxNumber
    Input Text  Name  ${Name}
    Input Text  TaxNumber  ${VAT number}
    Input Text  Phone  ${Phone}
    Input Text  Fax  ${Fax}

    Click link  Address
    Input Text  EmailAddress  ${Email}
    Select From List  PhysicalAddress.country:record  ${Country}
    Select From List  PhysicalAddress.state:record  ${State}
    #district is on autoselect last entry
    Select From List  PhysicalAddress.district:record
    Input Text  PhysicalAddress.city  ${City}
    Input Text  PhysicalAddress.zip  ${ZIP}
    Input Text  PhysicalAddress.address  ${Physical Address}
    Select From List  PostalAddress.selection  PhysicalAddress
    Input Text  PostalAddress.address  ${Postal Address}
    Select From List  BillingAddress.selection  PostalAddress

    Click link  Bank details
    Input Text  AccountType  ${AccountType}
    Input Text  AccountName  ${AccountName}
    Input Text  AccountNumber  ${AccountNumber}
    Input Text  BankName  ${BankName}
    Input Text  BankBranch  ${BankBranch}

    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #following variables not via arguments
    Log  Reference Samples  WARN
    Click link  Reference Samples
    Wait Until Page Contains Element  Remarks
    Input Text  Remarks  Reference Sample Remarks
    Click button  Save remarks
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  Reference Samples Title
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
    Input Text  Middleinitial  ${Middleinitial}
    Input Text  Middlename  ${Middlename}
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
    Input Text  title  ${ManufacturerTitle}
    Input Text  description  ${ManufacturerDescription}
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #now define an Instrument Type
    Log  Instrument Types  WARN

    Go to  ${PLONEURL}/bika_setup/bika_instrumenttypes
    Page should contain  Instrument Types
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${InstrumentTypeTitle}
    Input Text  description  Instrument Type Description
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
    Input Text  title  Instrument Title
    Input Text  description  Instrument Description
    Select From List  InstrumentType
    Select From List  Manufacturer
    Select From List  Supplier

    Input Text  Model  Instrument Model
    Input Text  SerialNo  Instrument Serial Number 123

    Select From List  DataInterface:list
    Input Text  DataInterfaceOptions-Key-0  Data Interface Options Key
    Input Text  DataInterfaceOptions-Value-0  Data Interface Options Value
    Input Text  cmfeditions_version_comment  ${Change note}

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


#Containers
Create Containers
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Log  Containers  WARN
    Go to  ${PLONEURL}/bika_setup/bika_containers
    Page should contain  Containers
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select From List   ContainerType:list
    Input Text  Capacity  20 ml
    Select From List   Preservation:list
    Select Checkbox  PrePreserved
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Containers

#Sample Types
Create SampleTypes
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Days}=
    ...          ${Hours}=
    ...          ${Minutes}=
    Log  Sample Types  WARN
    Go to  ${PLONEURL}/bika_setup/bika_sampletypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}

    Input Text  RetentionPeriod.days:record:ignore_empty  ${Days}
    Input Text  RetentionPeriod.hours:record:ignore_empty  ${Hours}
    Input Text  RetentionPeriod.minutes:record:ignore_empty  ${Minutes}

    Select Checkbox  Hazardous

    #Click Element  SampleMatrix:list
    Select from list  SampleMatrix:list

    Input Text  Prefix  Prefix
    Input Text  MinimumVolume  20 ml

    #Click Element  ContainerType:list
    Select from list  ContainerType:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Sample Types


#Analysis Categories
Create AnalysisCategories
    [Arguments]  ${Description}=
    Log  Analysis Categories  WARN
    Go to  ${PLONEURL}/bika_setup/bika_analysiscategories
    Wait Until Page Contains  Analysis Categories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisCategory_global_Title}
    Input Text  description  ${Description}
    Select From List  Department:list

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Analysis Categories


#Analysis Services
Create AnalysisServices
    [Arguments]  ${Description}=
    Go to                ${PLONEURL}/bika_setup/bika_analysisservices
    Wait Until Page Contains  Analysis Services
    Click link           Add
    Wait Until Page Contains Element  title
    Input Text           title         ${AnalysisServices_global_Title}
    Input Text           description   ${Description}
    Input Text           Unit          measurement Unit
    Input Text           Keyword       AnalysisKeyword
    Select Radio Button       PointOfCapture  lab

    Select From Dropdown      Category

    Input Text  Price  50.23
    Input Text  BulkPrice  30.00
    Input Text  VAT  15.00

    Select First From Dropdown  Department

    #sleep  2
    #Click Button  Save

    #now move on to Analysis without saving
    Click link  Analysis
    Wait Until Page Contains Element  Precision
    Input Text  Precision  3
    Select Checkbox  ReportDryMatter
    Select From List  AttachmentOption  n
    Input Text  MaxTimeAllowed.days:record:ignore_empty  3
    Input Text  MaxTimeAllowed.hours:record:ignore_empty  3
    Input Text  MaxTimeAllowed.minutes:record:ignore_empty  3
    #sleep  2
    #Click Button  Save

    #now move on to Analysis without saving
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

    #sleep  2
    #Click Button  Save

    #now move on to Uncertainties without saving
    Click link  Uncertainties

    Input Text  Uncertainties-intercept_min-0  2
    Input Text  Uncertainties-intercept_max-0  9
    Input Text  Uncertainties-errorvalue-0  3.8

    Click Button  Uncertainties_more
    Input Text  Uncertainties-intercept_min-1  0
    Input Text  Uncertainties-intercept_max-1  10
    Input Text  Uncertainties-errorvalue-1  5.5

    #sleep  2
    #Click Button  Save

    #now move on to Result Options without saving
    Click link  Result Options

    Input Text  ResultOptions-ResultValue-0  10
    Input Text  ResultOptions-ResultText-0  Result Text 0
    Click Button  ResultOptions_more
    Input Text  ResultOptions-ResultValue-1  2
    Input Text  ResultOptions-ResultText-1  Result Text 1

    #now move on to Container and Preservation without saving
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
    sleep  2
    #this page often seems to kick up a dialog - sleeping a little seems to help
    Wait Until Page Contains  Changes saved.
    sleep  2
    #end Analysis Services


#Analysis Profiles
Create AnalysisProfiles
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Analysis Profiles  WARN
    Go to    ${PLONEURL}/bika_setup/bika_analysisprofiles
    Wait Until Page Contains  Analysis Profile
    Click link  Add Profile
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  ProfileKey  Profile Key

    Click link  Analyses
    Page should contain  Profile Analyses
    Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Analysis Profiles


#Analysis Specifications
Create AnalysisSpecifications
    [Arguments]  ${Description}=
    Log  Analysis Specifications  WARN
    Go to  ${PLONEURL}/bika_setup/bika_analysisspecs
    Wait Until Page Contains  Analysis Specifications
    Click link  Add
    Wait Until Page Contains Element  description
    Select From List  SampleType:list
    Input Text  description  ${Description}

    Click link  Specifications
    Page should contain  Specifications

    Click Element  xpath=//th[@cat='${AnalysisCategory_global_Title}']

    Input Text  xpath=//input[@field='min']  3
    Input Text  xpath=//input[@field='max']  4
    Input Text  xpath=//input[@field='error']  5

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Analysis Specifications

#Reference Definition
Create ReferenceDefinition
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Reference Definition  WARN
    Go to  ${PLONEURL}/bika_setup/bika_referencedefinitions
    Wait Until Page Contains  Reference Definition
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select Checkbox  Blank
    Select Checkbox  Hazardous

    Click link  Reference Values
    Page should contain  Specifications
    Wait Until Page Contains  Reference Values

    Click Element  xpath=//th[@cat='${AnalysisCategory_global_Title}']

    Input Text  xpath=//input[@field='result']  3
    Input Text  xpath=//input[@field='error']  5
    Click Element  xpath=//input[@field='min']
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Reference Definition


#Worksheet Template
Create WorksheetTemplate
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  Worksheet Template  WARN
    Go to  ${PLONEURL}/bika_setup/bika_worksheettemplates
    Wait Until Page Contains  Worksheet Template
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select From List  Instrument:list

    Click link  Layout
    Wait Until Page Contains  Worksheet Layout
    Input Text  NoOfPositions  3

    Log  BUG: Worksheet Template: System Crash on Clicking Reset - Reset NOT CLICKED  WARN

    #Click Button  Reset

#system crash on reset
#!!!!!!!!!!!!!!!!!!



    sleep  1

    Click link  Analyses
    Wait Until Page Contains  Analysis Service
    Click Element  xpath=//th[@cat='${AnalysisCategory_global_Title}']
    Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Worksheet Template


#AR Templates
Create ARTemplates
    [Arguments]  ${Title}=
    ...          ${Description}=
    Log  AR Template  WARN
    Go to  ${PLONEURL}/bika_setup/bika_artemplates
    Wait Until Page Contains  AR Templates
    Click link  Add Template
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select First From Dropdown  SamplePoint
    Select First From Dropdown  SampleType
    Select Checkbox  ReportDryMatter

    Click link  Sample Partitions
    Wait Until Page Contains  Sample Partitions

    Select First From Dropdown  Partitions-Container-0
    Select First From Dropdown  Partitions-Preservation-0
    Click Button  More
    Select Specific From Dropdown  Partitions-Container-1  Glass
    Select Specific From Dropdown  Partitions-Preservation-1  HNO3


    Log  BUG: AR Template - Sample Partitions: First from dropdown selection fails due to invisible class cg-DivItem on Containers and Preservation (workaround: using class cg-colItem instead)  WARN

    #start workaround
    #click out of element
    #Click Element  xpath=//div[@id='portal-columns']
    #Click Element  Partitions-Container-0
    #sleep  0.5
    #${STATUS}  Run Keyword And Return Status  Click Element  xpath=//div[contains(@class,'cg-colItem')]
    #Run Keyword If  '${STATUS}' == 'False'  Log  Error in workaround  Partitions-Container-0   WARN

    #click out of element
    #Click Element  xpath=//div[@id='portal-columns']
    #Click Element  Partitions-Preservation-0
    #sleep  0.5
    #${STATUS}  Run Keyword And Return Status  Click Element  xpath=//div[contains(@class,'cg-colItem')]
    #Run Keyword If  '${STATUS}' == 'False'  Log  Error in workaround  Partitions-Preservation-0  WARN
    #end workaround



    Click Link  Analyses
    Wait Until Page Contains Element  AnalysisProfile
    Select First From Dropdown  AnalysisProfile

    Log  BUG: AR Template: Analysis Profile Dropdown fails to close?  WARN

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end AR Templates


#Clients
Create AddClients
    [Arguments]  ${ID}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    Log  Clients  WARN
    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click link  Add
    Wait Until Page Contains Element  Name

    Input Text  Name  ${ClientName_global}
    Input Text  ClientID  ${ID}
    Input Text  TaxNumber  98765A
    Input Text  Phone  011 3245679
    Input Text  Fax  011 3245678
    Input Text  EmailAddress  client@client.com

    Select Checkbox  BulkDiscount
    Select Checkbox  MemberDiscountApplies

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
    Select From List  BillingAddress.selection  PostalAddress
    Input Text  BillingAddress.address  ${Postal Address}

    Click link  Bank details
    Input Text  AccountType  Account Type
    Input Text  AccountName  Account Name
    Input Text  AccountNumber  Account Number
    Input Text  BankName  Bank Name
    Input Text  BankBranch  Bank Branch

    #Select Preferences link like this to avoid Admin Preferences confusion
    Click link  fieldsetlegend-preferences

    Select From List  EmailSubject:list
    Select From List  DefaultCategories:list
    Select From List  RestrictedCategories:list

    Click Button  Save
    Wait Until Page Contains  Changes saved.
    #end Clients


#Client contact required before request may be submitted

#Client Contacts
Create ClientContact
    [Arguments]  ${Salutation}=
    ...          ${Firstname}=
    ...          ${Middleinitial}=
    ...          ${Middlename}=
    ...          ${Surname}=
    ...          ${Jobtitle}=
    ...          ${Department}=
    ...          ${Email}=
    ...          ${Businessphone}=
    ...          ${Businessfax}=
    ...          ${Homephone}=
    ...          ${Mobilephone}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    ...          ${Preference}=
    Log  Client Contacts  WARN
    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click link  ${ClientName_global}
    Click link  Contacts
    Click link  Add

    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  ${Salutation}
    Input Text  Firstname  ${Firstname}
    Input Text  Middleinitial  ${Middleinitial}
    Input Text  Middlename  ${Middlename}
    Input Text  Surname  ${Surname}
    Input Text  JobTitle  ${Jobtitle}
    Input Text  Department  ${Department}

    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress  ${Email}
    Input Text  BusinessPhone  ${Businessphone}
    Input Text  BusinessFax  ${Businessfax}
    Input Text  HomePhone  ${Homephone}
    Input Text  MobilePhone  ${Mobilephone}

    Click Link  Address
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

    Click Link  Publication preference
    Wait Until Page Contains Element  PublicationPreference
    Select from list  PublicationPreference:list  ${Preference}
    Select Checkbox  AttachmentsPermitted

    Log  No tests done on: archetypes-fieldname-CCContact  WARN
    #Click Element  archetypes-fieldname-CCContact

    Click Button  Save
    Wait Until Page Contains  Changes saved.

    #end LabContact

    #now continue with AR
    Log  Analysis Request  WARN

    Go to  ${PLONEURL}/clients
    Wait Until Page Contains  Clients
    Click Link  ${ClientName_global}
    Wait Until Page Contains  Analysis Request
    Click Link  Add
    Wait Until Page Contains  Request new analyses

    Select First From Dropdown  ar_0_Batch
    Select First From Dropdown  ar_0_Template
    Select First From Dropdown  ar_0_Profile
    Select First From Dropdown  ar_0_Sample

    SelectPrevMonthDate  ar_0_SamplingDate  12

    Select First From Dropdown  ar_0_SampleType
    Select First From Dropdown  ar_0_SamplePoint
    Select First From Dropdown  ar_0_ClientOrderNumber
    Select First From Dropdown  ar_0_ClientReference
    Select First From Dropdown  ar_0_ClientSampleID
    Select First From Dropdown  ar_0_SamplingDeviation
    Select First From Dropdown  ar_0_SampleCondition
    Select First From Dropdown  ar_0_DefaultContainerType

    Select Checkbox  ar_0_AdHoc
    Select Checkbox  ar_0_Composite
    Select Checkbox  ar_0_ReportDryMatter
    Select Checkbox  ar_0_InvoiceExclude

    Log  AR: Copy Across Testing  WARN

    Click Element  Batch
    Click Element  Template
    Click Element  Profile
    Click Element  Sample
    Click Element  SamplingDate
    Click Element  SampleType
    Click Element  SamplePoint
    Click Element  ClientOrderNumber
    Click Element  ClientReference
    Click Element  ClientSampleID
    Click Element  SamplingDeviation
    Click Element  SampleCondition
    Click Element  DefaultContainerType
    Click Element  AdHoc
    Click Element  Composite
    Click Element  ReportDryMatter
    Click Element  InvoiceExclude

    Log  Saving AR:- Setting timeout to: 60  WARN
    Set Selenium Timeout  60

    Click Button  Save
    Wait Until Page Contains  successfully created.

    Log  Setting timeout to: ${SELENIUM_SPEED}  WARN
    Set Selenium Timeout  ${SELENIUM_SPEED}

    Log  Only stepping through links from here: no testing  WARN

    #is already on this ACTIVE link page
    Click link  Active
    sleep  1
    Click link  Due
    sleep  1
    Click link  Received
    sleep  1
    Click link  To be verified
    sleep  1
    Click link  Verified
    sleep  1
    Click link  Published
    sleep  1
    Click link  Cancelled
    sleep  1
    Click link  Invalid
    sleep  1
    Click link  assigned
    sleep  1
    Click link  unassigned
    sleep  1

    Click link  Edit
    sleep  1
    Click link  Contacts
    sleep  1
    Click link  Samples
    sleep  1
    Click link  SamplePoints
    sleep  1
    Click link  Batches
    sleep  1
    Click link  Analysis Requests
    sleep  1
    Click link  Analysis Profiles
    sleep  1
    Click link  AR Templates
    sleep  1
    Click link  Analysis Specifications
    sleep  1
    Click link  Attachments
    sleep  1

    Log  End Bika Setup Testing  WARN


#End dependent Bika Setup options
