*** Settings ***

Documentation  AR with Workflow disabled, Lab sample AS and 2 users

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  bika.lims.tests.base.Keywords
Resource  src/bika.lims/bika/lims/tests/keywords.txt
#Resource  keywords.txt


Variables  plone/app/testing/interfaces.py

#file location -> /Applications/Plone/buildout-cache/eggs/plone.app.testing-4.2.2-py2.7.egg/plone/app/testing/interfaces.py

Suite Setup      Start browser
#Suite Teardown  Close All Browsers

*** Variables ***

# higher speed variablr slows process down ie 0.1, 0.3 etc in seconds
${SELENIUM_SPEED}  0

${AnalysisServices_global_Title}  Analysis Services Title
${AnalysisServices_locator}  Select ${AnalysisServices_global_Title}
${AnalysisCategory_global_Title}  Analysis Category Title
${SampleTypesTitle}  Sample Types Title

${ClientName_global}  Client Name
${Prefix_global}  PREFIX

#AR name is created at runtime
${AR_name_global}

${user-labmanager}  labmanager
${user-labmanager1}  labmanager1

#general purpose variable
${VALUE}
#general status variable
${STATUS}

#empty string variable contained in AR name  <- just in case it returns
#use 'Set Global Variable' when setting
${YEAR}  



*** Test Cases ***

AnalysisRequest

    ShowTime

    #test availability ofkeywords in resource keywords.txt
    Test Keyword

    Log in as  ${user-labmanager}

    #BIKA Setup
    RunBikaSetup

    #Sample Types
    Create SampleTypes  Title=${SampleTypesTitle}
    ...    Description=Sample Types description
    ...    Days=5
    ...    Hours=10
    ...    Minutes=15

    #spec for metals
    Create AnalysisSpecification  SampleType=${SampleTypesTitle}

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


Create AnalysisSpecification
    [Arguments]  ${SampleType}=


    Go to  http://localhost:55001/plone/bika_setup/bika_analysisspecs
    Click link  Add
    Wait Until Page Contains Element  SampleType:list
    Select From List  SampleType:list  ${SampleType}
    Input Text  description  Setting Samples specs for later range testing

    Click Link  Specifications
    Wait Until Page Contains Element  xpath=//th[@cat='Metals']

    Click Element  xpath=//th[@cat='Metals']
    #Calcium
    Input Text  xpath=//input[@selector='min_analysisservice-3']  9
    Input Text  xpath=//input[@selector='max_analysisservice-3']  11
    Input Text  xpath=//input[@selector='error_analysisservice-3']  10

    #Phosphorus
    Input Text  xpath=//input[@selector='min_analysisservice-11']  11
    Input Text  xpath=//input[@selector='max_analysisservice-11']  13
    Input Text  xpath=//input[@selector='error_analysisservice-11']  10

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

    Log  Not Selecting dry matter  WARN
    #Select Checkbox  ReportDryMatter

    Select From List  AttachmentOption  n
    Input Text  MaxTimeAllowed.days:record:ignore_empty  3
    Input Text  MaxTimeAllowed.hours:record:ignore_empty  3
    Input Text  MaxTimeAllowed.minutes:record:ignore_empty  3

    #Click Button  Save

    #now move on to Analysis without saving
    Click link  Method
    Wait Until Page Contains Element  Instrument
    Click Element  Method
    #following because in small test files this info is not available
    Select First From Dropdown  Method
    Click Element  Instrument
    Select First From Dropdown  Instrument

    Log  Specifically not selecting Dry Matter Calculation  WARN
    SelectSpecificFromDropdown  Calculation  Residual

    #Click Element  Calculation
    #Select First From Dropdown  Calculation

    Log  Selecting interim fields  WARN
    Input Text  InterimFields-keyword-0  Keyword
    Input Text  InterimFields-title-0  Field Title
    Input Text  InterimFields-value-0  Default Value
    Input Text  InterimFields-unit-0  Unit
    Select Checkbox  InterimFields-hidden-0

    Input Text  DuplicateVariation  5
    Select Checkbox  Accredited

    #Click Button  Save

    #now move on to Uncertainties without saving
    Click link  Uncertainties

    Log  Enetering uncertainties  WARN

    Input Text  Uncertainties-intercept_min-0  2
    Input Text  Uncertainties-intercept_max-0  9
    Input Text  Uncertainties-errorvalue-0  3.8

    Click Button  Uncertainties_more
    Input Text  Uncertainties-intercept_min-1  0
    Input Text  Uncertainties-intercept_max-1  10
    Input Text  Uncertainties-errorvalue-1  5.5

    #Click Button  Save

    #now move on to Result Options without saving
    Click link  Result Options

    Input Text  ResultOptions-ResultValue-0  10
    Input Text  ResultOptions-ResultText-0  Result Text 0
    Click Button  ResultOptions_more
    Input Text  ResultOptions-ResultValue-1  2
    Input Text  ResultOptions-ResultText-1  Result Text 1

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

    Log  No archetypes-fieldname-CCContact field selected  WARN
    #Click Element  no archetypes-fieldname-CCContact

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

    #Click Element  ar_0_Batch
    #Select First From Dropdown  ar_0_Batch

    Log  No Template or Profile selected  WARN
    #Click Element  ar_0_Template
    #Select First From Dropdown  ar_0_Template

    #Click Element  ar_0_Profile
    #Select First From Dropdown  ar_0_Profile

    #Click Element  ar_0_Profile
    #Input Text  ar_0_Profile  Micro
    #Select First From Dropdown  ar_0_Profile

    #Click Element  ar_0_Sample
    #Select First From Dropdown  ar_0_Sample

    SelectPrevMonthDate  ar_0_SamplingDate  1

    #Must select Sample Type otherwise the AR name changes and no end to end testing is possible
    #Click Element  ar_0_SampleType
    Input Text  ar_0_SampleType  ${Sample Types Title}
    Select First From Dropdown  ar_0_SampleType

    #Click Element  ar_0_SamplePoint
    #Select First From Dropdown  ar_0_SamplePoint
    #Click Element  ar_0_ClientOrderNumber
    #Select First From Dropdown  ar_0_ClientOrderNumber
    #Click Element  ar_0_ClientReference
    #Select First From Dropdown  ar_0_ClientReference
    #Click Element  ar_0_ClientSampleID
    #Select First From Dropdown  ar_0_ClientSampleID
    #Click Element  ar_0_SamplingDeviation
    #Select First From Dropdown  ar_0_SamplingDeviation
    #Click Element  ar_0_SampleCondition
    #Select First From Dropdown  ar_0_SampleCondition
    #Click Element  ar_0_DefaultContainerType
    #Select First From Dropdown  ar_0_DefaultContainerType

    #Select Checkbox  ar_0_AdHoc
    #Select Checkbox  ar_0_Composite
    #Select Checkbox  ar_0_ReportDryMatter
    #Select Checkbox  ar_0_InvoiceExclude

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
    Click Element  xpath=//th[@id='cat_lab_${AnalysisCategory_global_Title}']
    Select Checkbox  xpath=//input[@title='${AnalysisServices_global_Title}' and @name='ar.0.Analyses:list:ignore_empty:record']

    #Log  For some reason the Metals table is already open when a Profile is selected  WARN
    Click Element  xpath=//th[@id='cat_lab_Metals']
    Select Checkbox  xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox  xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']

    Click Element  xpath=//th[@id='cat_lab_Microbiology']
    Select Checkbox  xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox  xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox  xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox  xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']


    #Log  For some reason the Water table is not open when profile selected  WARN
    Click Element  xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox  xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']

    Click Button  Save
    Wait Until Page Contains  was successfully created.

    #build AR name
    Set Global Variable  ${AR_name_global}  ${Prefix_global}${YEAR}-0001-R01
    Log  Using AR with Name: ${AR_name_global}  WARN

    #this selects the actual AR detail - that wil be a later test
    #Click Link  ${AR_name_global}

    #just select the AR checkbox
    #select all
    #Select Checkbox  analysisrequests_select_all
    #select specific
    Select Checkbox  xpath=//input[@alt='Select ${AR_name_global}'] 

    #test for Workflow State Change
    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${AR_name_global}']
    #Log  VALUE = ${VALUE}  WARN

    Should Be Equal  ${VALUE}  Sample Due  Workflow States incorrect: Expected: Sample Due -
    #check page status


    Click Element  receive_transition
    Wait Until Page Contains  Changes saved.

    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${AR_name_global}']
    Should Be Equal  ${VALUE}  Received  Workflow States incorrect: Expected: Received -  
    #check page status

    Click Link  ${AR_name_global}
    Wait Until Page Contains  ${AR_name_global}

    #select a result
    #Select From List  xpath=//select[@selector='Result_AnalysisKeyword']
    Select From List  xpath=//tr[@cat='Analysis Category Title']/td/span/select[@selector='Result_AnalysisKeyword']
    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']

    TestSampleState  xpath=//input[@selector='state_title_AnalysisKeyword']  ${AnalysisServices_global_Title}  Received

    Checkbox Should Be Selected  xpath=//input[@selector='${AR_name_global}_AnalysisKeyword']

    Click Element  submit_transition
    Page should contain  Changes saved.

    #AR status must have changed to: To be verified
    TestSampleState  xpath=//input[@selector='state_title_AnalysisKeyword']  ${AnalysisServices_global_Title}  To be verified
    
    #Log  Bypassing state bug on AR - Received - should be To be verified  WARN
    #TestSampleState  xpath=//input[@selector='state_title_AnalysisKeyword']  ${AnalysisServices_global_Title}  Received

    #Page Status should be: ????
    #Now enter some results for the other AR's

    Select From List  xpath=//tr[@keyword='Clos']/td/span/select[@selector='Result_Clos']
    TestSampleState  xpath=//input[@selector='state_title_Clos']  Clostridia  Received

    Select From List  xpath=//tr[@keyword='Ecoli']/td/span/select[@selector='Result_Ecoli']
    TestSampleState  xpath=//input[@selector='state_title_Ecoli']  Ecoli  Received

    Click Element  submit_transition
    Page should contain  Changes saved.

    #test if changes to state have occurred
    TestSampleState  xpath=//input[@selector='state_title_Clos']  Clostridia  To be verified
    TestSampleState  xpath=//input[@selector='state_title_Ecoli']  Ecoli  To be verified

    #Now enter remaining results

    Select From List  xpath=//tr[@keyword='Entero']/td/span/select[@selector='Result_Entero']
    TestSampleState  xpath=//input[@selector='state_title_Entero']  Enterococcus  Received

    Select From List  xpath=//tr[@keyword='Salmon']/td/span/select[@selector='Result_Salmon']
    TestSampleState  xpath=//input[@selector='state_title_Salmon']  Salmonella  Received

    Log  No Result Fields for Dry Matter  WARN     

    #Moisture
    Input Text  xpath=//input[@selector='GM_Moist']  10
    Input Text  xpath=//input[@selector='NM_Moist']  10
    Input Text  xpath=//input[@selector='VM_Moist']  10
    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']
    Page Should Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png

    Input Text  xpath=//input[@selector='GM_Moist']  4
    Input Text  xpath=//input[@selector='NM_Moist']  5
    Input Text  xpath=//input[@selector='VM_Moist']  6
    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']
    Page Should Not Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png

    TestSampleState  xpath=//input[@selector='state_title_Moist']  Moisture  Received

    #Metals
    TestResultsRange  xpath=//input[@selector='Result_Ca']  2  10
    TestResultsRange  xpath=//input[@selector='Result_Phos']  20  11


    TestSampleState  xpath=//input[@selector='state_title_Ca']  Calcium  Received
    TestSampleState  xpath=//input[@selector='state_title_Phos']  Phosphorus  Received

    Click Element  submit_transition
    Page should contain  Changes saved.

    TestSampleState  xpath=//input[@selector='state_title_Entero']  Enterococcus  To be verified
    TestSampleState  xpath=//input[@selector='state_title_Salmon']  Salmonella  To be verified
    TestSampleState  xpath=//input[@selector='state_title_Moist']  Moisture  To be verified
    TestSampleState  xpath=//input[@selector='state_title_Ca']  Calcium  To be verified
    TestSampleState  xpath=//input[@selector='state_title_Phos']  Phosphorus  To be verified

    Log  Construction of AR: ${AR_name_global} complete  WARN


Verify AR

    Log  Verifying AR: ${AR_name_global} by different user  WARN

    #Why does this not work??
    #Click Link  ${AR_name_global}
    Click Element  xpath=//a[@id='to_be_verified_${AR_name_global}']

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']

    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']  To be verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-verify
    Click Link  workflow-transition-verify

    #Check page status
    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']
    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']  Verified

    #Check content status
    TestSampleState  xpath=//input[@selector='state_title_AnalysisKeyword']  ${AnalysisServices_global_Title}  Verified
    TestSampleState  xpath=//input[@selector='state_title_Clos']  Clostridia  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ecoli']  Ecoli  Verified   
    TestSampleState  xpath=//input[@selector='state_title_Entero']  Enterococcus  Verified
    TestSampleState  xpath=//input[@selector='state_title_Salmon']  Salmonella  Verified
    TestSampleState  xpath=//input[@selector='state_title_Moist']  Moisture  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ca']  Calcium  Verified
    TestSampleState  xpath=//input[@selector='state_title_Phos']  Phosphorus  Verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-publish
    #Click Link  workflow-transition-publish
    Log  Publish NOT clicked - no way of testing result  WARN

    Log  Process Complete.  WARN








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


SelectSpecificFromDropdown
    [Arguments]  ${Element}=
    ...          ${Option}=

    Click Element  ${Element}
    Input Text  ${Element}  ${Option}
    Select First From Dropdown  ${Element}


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


Shleep
    [Arguments]  ${amount}=
    ...          ${comment}=

    Log  Sleeping ${amount}: ${comment}  WARN
    sleep  ${amount}



SelectDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element  ${Element}
    Click Link  ${Date}

SelectPrevMonthDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element        ${Element}
    sleep                0.5
    #Click Element        xpath=//a[@title='Prev']  
    Click Element        xpath=//div[@id='ui-datepicker-div']/div/a[@title='Prev']
    sleep                0.5
    #Click Link          ${Date}
    Click Link           xpath=//div[@id='ui-datepicker-div']/table/tbody/tr/td/a[contains (text(),'${Date}')]


SelectNextMonthDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element        ${Element}
    sleep                0.5
    Click Element        xpath=//a[@title='Next']
    sleep                0.5
    Click Link           ${Date}




TestResultsRange
    [Arguments]  ${element}=
    ...          ${badResult}=
    ...          ${goodResult}=

    Log  Testing Result Range for ${element} -:- values: ${badResult} and ${goodResult}  WARN
    Input Text  ${element}  ${badResult}
    #pres the tab key to move out the field
    Press Key  ${element}  \t
    #Warning img -> http://localhost:55001/plone/++resource++bika.lims.images/warning.png
    sleep  0.5
    Page Should Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png
    Input Text  ${element}  ${goodResult}
    Press Key  ${element}  \t
    sleep  0.5
    Page Should Not Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png



TestSampleState
    [Arguments]  ${element}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${element}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

