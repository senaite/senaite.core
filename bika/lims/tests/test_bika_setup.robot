*** Settings ***

Documentation  test_bika_setup_adf_final.robot

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  bika.lims.tests.base.Keywords

Variables  plone/app/testing/interfaces.py

Suite Setup     Start browser
#Suite Teardown  Close All Browsers

*** Variables ***

# higher speed variablr slows process down ie 0.1, 0.3 etc in seconds
${SELENIUM_SPEED}  0

${Manager Firstname}  Manager Firstname
${Manager Surname}  Manager Surname


*** Test Cases ***

Setup
    Log in as site owner

#Start independent Bika Setup options

    #Attachment Types
#Test Attachment Types Cancel <- write code

    Create Attachment Types  Title=Container Types Title
    ...    Description=Container Types Description

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

    #Preservations
    Test Preservations Cancel  Title=Preservations Title
    ...    Description=Preservations Description


    Create Preservations  Title=Preservations Title
    ...    Description=Preservations Description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15

    Test Preservations Workflow


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



#End dependent Bika Setup options



*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}

#Start independent Bika Setup options

#Attachment Types

#add Test Attachment Types Cancel


Create Attachment Types
    [Arguments]  ${Title}=
    ...          ${Description}=
    Go to  http://localhost:55001/plone/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains Element  title
    Page should contain  Changes saved

# add test to check that correct page is displayed - not edit page ??

Test Attachment Types Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_attachmenttypes
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved

#Batch Labels

Create Batch Labels
    [Arguments]  ${Title}=
    Go to  http://localhost:55001/plone/bika_setup/bika_batchlabels
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Click Button  Save
    #portalMessage info
    Page should contain  Changes saved

#specifically test the Deactivate and Activate options
Test Batch Labels Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_batchlabels
    Select Checkbox  list_select_all
    #sleep  1
    Click Button  deactivate_transition
    Page should contain  Changes saved
    #after deactivation no labels are shown
    #first show all labels before continuing
    Click link  all
    #sleep  1
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved

#specifically test the Cancel option
Test Batch Labels Cancel
    Go to  http://localhost:55001/plone/bika_setup/bika_batchlabels
    Click link  Add
    Wait Until Page Contains Element  title
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


#Calculations

Test Calculations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Go to  http://localhost:55001/plone/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #the name of the Change note field is: cmfeditions_version_comment
    Input Text  cmfeditions_version_comment  ${Change note}
    #sleep  2
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.

Create Calculations Description
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=
    Go to  http://localhost:55001/plone/bika_setup/bika_calculations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #the name of the Change note field is: cmfeditions_version_comment
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Wait Until Page Contains Element  title
    Page should contain  Changes saved
    #sleep  2

#continue on current page after saving

Create Calculations Calculation
    [Arguments]  ${Keyword}=
    ...          ${Field Title}=
    ...          ${Default Value}=
    ...          ${Unit}=
    ...          ${Calculation Formula}=
    ...          ${Change note}=
    Click link  Calculation
    Wait Until Page Contains Element  InterimFields-keyword-0
    Input Text  InterimFields-keyword-0  ${Keyword}
    Input Text  InterimFields-title-0  ${Field Title}
    Input Text  InterimFields-value-0  ${Default Value}
    Input Text  InterimFields-unit-0  ${Unit}
    Input Text  Formula  ${Calculation Formula}
    #the name of the Change note field is: cmfeditions_version_comment
    Input Text  cmfeditions_version_comment  ${Change note}
    Click Button  Save
    Page should contain  Changes saved

Test Calculations Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_calculations
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#Container Types
Test Container Types Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    Go to  http://localhost:55001/plone/bika_setup/bika_containertypes
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
    Go to  http://localhost:55001/plone/bika_setup/bika_containertypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Wait Until Page Contains Element  title
    Page should contain  Changes saved
    #sleep  2


Test Container Types Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_containertypes
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved

#Lab Products
Test Lab Products Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Volume}=
    ...          ${Unit}=
    ...          ${VAT}=
    ...          ${Price}=
    Go to  http://localhost:55001/plone/bika_setup/bika_labproducts
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
    Go to  http://localhost:55001/plone/bika_setup/bika_labproducts
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
    Wait Until Page Contains Element  title
    Page should contain  Changes saved
    #sleep  2

Test Lab Products Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_labproducts
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved
    #sleep  2


#Laboratory Information
Test Laboratory Information Cancel
    [Arguments]  ${Name}=
    ...          ${VAT number}=
    ...          ${Phone}=
    ...          ${Fax}=
    Go to  http://localhost:55001/plone/bika_setup/laboratory/base_edit
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
    Go to  http://localhost:55001/plone/bika_setup/laboratory/base_edit
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
    Page should contain  Changes saved.


#Methods
Test Methods Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Instructions}=
    ...          ${Change note}=
    Go to  http://localhost:55001/plone/bika_setup/methods
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
    Go to  http://localhost:55001/plone/bika_setup/methods
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Input Text  Instructions  ${Instructions}
    #load document is not tested
    Input Text  cmfeditions_version_comment  ${Change note}
    #sleep  2
    Click Button  Save
    Page should contain  Changes saved

Test Methods Workflow
    Go to  http://localhost:55001/plone/bika_setup/methods
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#Preservations
Test Preservations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_preservations
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

    Go to  http://localhost:55001/plone/bika_setup/bika_preservations
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
    Page should contain  Changes saved


Test Preservations Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_preservations
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#Sample Conditions
Test Sample Conditions Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_sampleconditions
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sample Conditions
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_sampleconditions
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Page should contain  Changes saved


Test Sample Conditions Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_sampleconditions
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Page should contain  Changes saved
#the link to "All" should also have an id called "all" like all others - not default
    #Click link  all
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved

#Sample Matrices
Test Sample Matrices Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sample Matrices
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_samplematrices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #sleep  2
    Click Button  Save
    Page should contain  Changes saved
#Page contains "Changes saved" but is it the correct page?


Test Sample Matrices Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_samplematrices
    Select Checkbox  list_select_all
    #sleep  2
    Click Button  deactivate_transition
    Page should contain  Changes saved
#this link should also be called "all" like all others - not default
    #Click link  all
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#Sample Points
Test Sample Points Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Change note}=

    Go to  http://localhost:55001/plone/bika_setup/bika_samplepoints
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

    Go to  http://localhost:55001/plone/bika_setup/bika_samplepoints
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
    Page should contain  Changes saved


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
    Page should contain  Changes saved



Test Sample Points Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_samplepoints
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Page should contain  Changes saved
    Click link  all
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#Sampling Deviations
Test Sampling Deviations Cancel
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Cancel
    Page should contain  Add New Item operation was cancelled.


Create Sampling Deviations
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_samplingdeviations
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Click Button  Save
    Page should contain  Changes saved

Test Sampling Deviations Workflow
    Go to  http://localhost:55001/plone/bika_setup/bika_samplingdeviations
    Select Checkbox  list_select_all
    Click Button  deactivate_transition
    Page should contain  Changes saved
#require consistency - change id to all not default
    #Click link  all
    Click link  default
    Select Checkbox  list_select_all
    Click Button  activate_transition
    Page should contain  Changes saved


#End independent Bika Setup options

#Start dependent Bika Setup options


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

    Go to  http://localhost:55001/plone/bika_setup/bika_labcontacts
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
    Page should contain  Changes saved.

#Lab Department
Create LabDepartment
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Manager}=

    Go to  http://localhost:55001/plone/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    Select from list  Manager:list  ${Manager}
    Click Button  Save
    Page should contain  Changes saved.

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

    Go to  http://localhost:55001/plone/bika_setup/bika_labcontacts
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
    Page should contain  Changes saved.

#end LabContact



#End dependent Bika Setup options

Select First Option in Dropdown
    Click Element  xpath=//div[contains(@class,'cg-DivItem')]

Log in
    [Arguments]  ${userid}  ${password}

    Go to  http://localhost:55001/plone/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

Log in as test user

    Log in  ${TEST_USER_NAME}  ${TEST_USER_PASSWORD}

Log in as site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Log in as test user with role
    [Arguments]  ${usrid}  ${role}

Log out
    Go to  http://localhost:55001/plone/logout
    Page should contain  logged out
