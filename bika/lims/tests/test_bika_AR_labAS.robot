*** Settings ***

Documentation  AR with Workflow disabled, Lab sample AS and 2 users

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  bika.lims.tests.base.Keywords
Resource  keywords.txt

Variables  plone/app/testing/interfaces.py

#file location -> /Applications/Plone/buildout-cache/eggs/plone.app.testing-4.2.2-py2.7.egg/plone/app/testing/interfaces.py

Suite Setup      Start browser
#Suite Teardown  Close All Browsers

*** Variables ***

# higher speed variablr slows process down ie 0.1, 0.3 etc in seconds
${SELENIUM_SPEED}  0

#use following to locate Analysis Service when defining an Analysis Profile
${AnalysisServices_global_Title}  Analysis Services Title
${AnalysisServices_locator}  Select ${AnalysisServices_global_Title}
${AnalysisCategory_global_Title}  Analysis Category Title
${ClientName_global}  Client Name
${Prefix_global}  PREFIX
${user-labmanager}  labmanager
${user-labmanager1}  labmanager1

#general purpose variable
${VALUE}
#general status variable
${STATUS}

${AR_name}
#hack in for year 2013 -> shoud be dynamic
${YEAR}  13



*** Test Cases ***

AnalysisRequest

    ShowTime

    #test availability ofkeywords in resource keywords.txt
    Test Keyword

    Log in as  ${user-labmanager}

    #BIKA Setup
    RunBikaSetup

    #Sample Types
    Create SampleTypes  Title=Sample Types Title
    ...    Description=Sample Types description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15

    Create LabDepartment  Title=Lab department
    ...    Description=Lab department description

    Create AnalysisCategories  Description=Analysis Category description

    Create AnalysisServices  Description=Analysis Services description

    Create AddClients  ID=987654321
    ...    Country=South Africa
    ...    State=Gauteng
           #District is on auto select last entry
    ...    City=City Name
    ...    ZIP=12345
    ...    Physical Address=Client House\nClient Street 20\nClient Town
    ...    Postal Address=Post Box 25\nClient Town


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

    Log out as  ${user-labmanager}

    Log in as  ${user-labmanager1}

    Verify AR

    ShowTime


*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}


ShowTime

    ${time}  GetTime
    Log  ${time}  WARN


RunBikaSetup
    Go to  http://localhost:55001/plone/bika_setup/edit
    #Click link  Analyses
    #Select Checkbox  SamplingWorkflowEnabled

    Click Link  Labels
    Select From List  AutoPrintLabels  None

    Log  BIKA Setup: label printing set to: None  WARN
    Click Button  Save
    Wait Until Page Contains  Changes saved.


Create SampleTypes
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Days}=
    ...          ${Hours}=
    ...          ${Minutes}=

    Go to  http://localhost:55001/plone/bika_setup/bika_sampletypes

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

    Input Text  Prefix  ${Prefix_global}
    Input Text  MinimumVolume  20 ml

    #Click Element  ContainerType:list
    Select from list  ContainerType:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.


Create LabDepartment
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #Select from list  Manager:list  ${Manager}
    Click Button  Save
    Page should contain  Changes saved.

Create AnalysisCategories
    [Arguments]  ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_analysiscategories
    Wait Until Page Contains  Analysis Categories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisCategory_global_Title}
    Input Text  description  ${Description}
    Select From List  Department:list

    Click Button  Save
    Page should contain  Changes saved.

Create AnalysisServices
    [Arguments]  ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_analysisservices
    Wait Until Page Contains  Analysis Services
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisServices_global_Title}
    Input Text  description  ${Description}
    Input Text  Unit  measurement Unit
    Input Text  Keyword  AnalysisKeyword

    Log  AS: Lab Sample selected  WARN

    Select Radio Button  PointOfCapture  lab
    #Select Radio Button  PointOfCapture  field

    Click Element  Category
    #if you know the category name, another option is to:
    #Input Text  Category  Analysis
    Select First From Dropdown  Category

    Input Text  Price  50.23
    Input Text  BulkPrice  30.00
    Input Text  VAT  15.00
    Click Element  Department
    #Input Text  Department  Lab
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
    Click Element  Method
    #following because in small test files this info is not available
    Select First From Dropdown  Method
    Click Element  Instrument
    Select First From Dropdown  Instrument
    Click Element  Calculation
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

    #sleep  2
    #Click Button  Save


    Log  AnalysisServices: Preservation fields NOT selected for DEBUG  WARN
    #Log  AnalysisServices: Preservation fields ARE selected  WARN

    #now move on to Container and Preservation without saving
    Click link  Container and Preservation
    Wait Until Page Contains Element  Preservation
    #Select Checkbox  Separate

    #Click Element  Preservation
    #Select First From Dropdown  Preservation

    #Click Element  Container
    #Select First From Dropdown  Container

    #Select From List  PartitionSetup-sampletype-0

    #Click Element  PartitionSetup-separate-0

    #Select From List  PartitionSetup-preservation-0

    #Select From List  PartitionSetup-container-0

    #Input Text  PartitionSetup-vol-0  Volume 123

    #sleep  2

    Click Button  Save
    Wait Until Page Contains  Changes saved.



#Clients
Create AddClients
    [Arguments]  ${ID}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=


    Go to  http://localhost:55001/plone/clients
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
    #Select From List  DefaultCategories:list
    #Select From List  RestrictedCategories:list

    Click Button  Save
    Page should contain  Changes saved.


#Client contact required before request may be submitted


#Contacts
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

    Go to  http://localhost:55001/plone/clients

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

    Log  What does archetypes-fieldname-CCContact field do??  WARN

#what is this supposed to do??
#add more clients
    #Click Element  archetypes-fieldname-CCContact

    Click Button  Save
    Page should contain  Changes saved.


#end LabContact

    #now continue with AR

    Go to  http://localhost:55001/plone/clients
    Wait Until Page Contains  Clients
    Click Link  ${ClientName_global}
    Wait Until Page Contains  Analysis Request
    Click Link  Add
    Wait Until Page Contains  Request new analyses

    Click Element  ar_0_Batch
    Select First From Dropdown  ar_0_Batch
    Click Element  ar_0_Template
    Select First From Dropdown  ar_0_Template
    Click Element  ar_0_Profile
    Select First From Dropdown  ar_0_Profile
    Click Element  ar_0_Sample
    Select First From Dropdown  ar_0_Sample
    Click Element  ar_0_SamplingDate
    Click link  1


    Click Element  ar_0_SampleType
    Input Text  ar_0_SampleType  Sample Types Title
    Select First From Dropdown  ar_0_SampleType



    Click Element  ar_0_SamplePoint
    Select First From Dropdown  ar_0_SamplePoint
    Click Element  ar_0_ClientOrderNumber
    Select First From Dropdown  ar_0_ClientOrderNumber
    Click Element  ar_0_ClientReference
    Select First From Dropdown  ar_0_ClientReference
    Click Element  ar_0_ClientSampleID
    Select First From Dropdown  ar_0_ClientSampleID
    Click Element  ar_0_SamplingDeviation
    Select First From Dropdown  ar_0_SamplingDeviation
    Click Element  ar_0_SampleCondition
    Select First From Dropdown  ar_0_SampleCondition
    Click Element  ar_0_DefaultContainerType
    Select First From Dropdown  ar_0_DefaultContainerType

    Select Checkbox  ar_0_AdHoc
    Select Checkbox  ar_0_Composite
    Select Checkbox  ar_0_ReportDryMatter
    Select Checkbox  ar_0_InvoiceExclude

    Log  AR: NO Copy Across Testing  WARN
    #Log  AR: Copy Across Testing  WARN

    #Click Element  Batch
    #Click Element  Template
    #Click Element  Profile
    #Click Element  Sample
    #Click Element  SamplingDate
    #Click Element  SampleType
    #Click Element  SamplePoint
    #Click Element  ClientOrderNumber
    #Click Element  ClientReference
    #Click Element  ClientSampleID
    #Click Element  SamplingDeviation
    #Click Element  SampleCondition
    #Click Element  DefaultContainerType
    #Click Element  AdHoc
    #Click Element  Composite
    #Click Element  ReportDryMatter
    #Click Element  InvoiceExclude

    #first select analysis category then service
    Click Element  cat_lab_${AnalysisCategory_global_Title}
    Select Checkbox  ar.0.Analyses:list:ignore_empty:record

    Click Button  Save
    Wait Until Page Contains  was successfully created.


    #build AR name
    ${AR_name}=  Set Variable  ${Prefix_global}${YEAR}-0001-R01
    Log  Using AR with Name: ${AR_name}  WARN
    #this selects the actual AR detail - that wil be a later test
    #Click Link  ${AR_name}

    #just select the AR checkbox
    #select all
    #Select Checkbox  analysisrequests_select_all
    #select specific
    Select Checkbox  xpath=//input[@alt='Select ${AR_name}']

    #test for Workflow State Change
    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${AR_name}']
    #Log  VALUE = ${VALUE}  WARN

    Should Be Equal  ${VALUE}  Sample Due  Workflow States incorrect: Expected: Sample Due -

    Click Element  receive_transition
    Wait Until Page Contains  Changes saved.

    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${AR_name}']
    Should Be Equal  ${VALUE}  Received  Workflow States incorrect: Expected: Received -

    Click Link  ${AR_name}
    Wait Until Page Contains  ${AR_name}

    Select From List  xpath=//select[@selector='Result_AnalysisKeyword']

    Click Element  submit_transition
    Page should contain  Changes saved.



Verify AR

    Log  Sleeping for 300  WARN
    sleep  300
    #Portlets have changed and AR not available when selecting AR

    Click Link  to_be_verified_${AR_name}

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']

    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']  To be verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-verify
    Click Link  workflow-transition-verify

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']
    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']  Verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-publish
    #Click Link  workflow-transition-publish
    Log  Publish NOT clicked - no way of testing result  WARN


Select First Option in Dropdown
    #sleep  0.5
    #Click Element  xpath=//div[contains(@class,'cg-DivItem')]
    Select First From Dropdown  UNKNOWN

Select First From Dropdown
    [Arguments]  ${elementName}
    sleep  0.5
    #select the first item in the dropdown and return status
    ${STATUS}  Run Keyword And Return Status  Click Element  xpath=//div[contains(@class,'cg-DivItem')]
    #if no content in dropdown output warning and continue
    Run Keyword If  '${STATUS}' == 'False'  Log  No items found in dropdown: ${elementName}  WARN


Log in
    [Arguments]  ${userid}  ${password}

    Go to  http://localhost:55001/plone/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

Log in as
    [Arguments]  ${user}
    Log in  test_${user}  test_${user}

Log in as test user
    Log in  ${TEST_USER_NAME}  ${TEST_USER_PASSWORD}

Log in as site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Log in as test user with role
    [Arguments]  ${usrid}  ${role}

Log out as
    [Arguments]  ${user}=

    Click Link  test_${user}
    sleep  0.5
    Click Link  Log out
    Log  User ${user} logging out!  WARN
    Wait Until Page Contains  Log in

Log out
    Go to  http://localhost:55001/plone/logout
    Page should contain  logged out



#stuff hereafter

    #xpath examples
    #Click Element  xpath=//th[@cat='${AnalysisCategory_global_Title}']
    #Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']

