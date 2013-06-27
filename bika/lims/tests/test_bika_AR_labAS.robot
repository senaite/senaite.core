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

${AnalysisServices_global_Title}  Analysis Services Title
${AnalysisServices_locator}  Select ${AnalysisServices_global_Title}
${AnalysisCategory_global_Title}  Analysis Category Title
${SampleTypesTitle}  Sample Types Title

${ClientName_global}  Client Name
${Prefix_global}  PREFIX
${AS_Keyword}  AnalysisKeyword

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
    ...    Preference=Email

    #signature upload not tested
    #end ClientContact

    Log out as  ${user-labmanager}

    Log in as  ${user-labmanager1}

    Verify AR

    DiffTime  ${saveTime}


*** Keywords ***

Start browser
    ShowAndSaveTime
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}


ShowTime

    ${time}  GetTime
    Log  ${time}  WARN


RunBikaSetup

    Log  Run Bika Setup  WARN
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

    Log  Create Sample Types  WARN
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

    Log  Create Analysis Specification  WARN
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

    Log  Create Lab Department  WARN
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

    Log  Create Analysis Categories  WARN
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

    Log  Create Analysis Services  WARN
    Go to  http://localhost:55001/plone/bika_setup/bika_analysisservices
    Wait Until Page Contains  Analysis Services

    Click link  Add

    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisServices_global_Title}
    Input Text  description  ${Description}
    Input Text  Unit  measurement Unit
    Input Text  Keyword  ${AS_Keyword}

    Log  AS: Lab Sample selected  WARN

    Select Radio Button  PointOfCapture  lab
    #Select Radio Button  PointOfCapture  field

    Select First From Dropdown  Category

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

    Select First From Dropdown  Method
    Select First From Dropdown  Instrument

    Log  Specifically not selecting Dry Matter Calculation  WARN
    SelectSpecificFromDropdown  Calculation  Residual

    #Select First From Dropdown  Calculation

    Log  Selecting interim fields  WARN
    Input Text  InterimFields-keyword-0  IF-Keyword
    Input Text  InterimFields-title-0  Field Title
    Input Text  InterimFields-value-0  Default Value
    Input Text  InterimFields-unit-0  Unit
    Select Checkbox  InterimFields-hidden-0

    Input Text  DuplicateVariation  5
    Select Checkbox  Accredited

    #Click Button  Save

    #now move on to Uncertainties without saving
    Click link  Uncertainties

    Log  Entering uncertainties  WARN

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

    Log  AnalysisServices: Selecting Preservation fields  WARN    

    #now move on to Container and Preservation without saving
    Click link  Container and Preservation
    Wait Until Page Contains Element  Preservation

    Select Checkbox  Separate
    Select First From Dropdown  Preservation
    Select First From Dropdown  Container
    Select From List  PartitionSetup-sampletype-0  Water
    Click Element  PartitionSetup-separate-0
    Select From List  PartitionSetup-preservation-0  Any
    Select From List  PartitionSetup-container-0  Any
    Input Text  PartitionSetup-vol-0  Volume 123

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

    Log  Add Clients  WARN
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

    Log  Create Client Contacts  WARN
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
    Log  Create Analysis Request  WARN
    Go to  http://localhost:55001/plone/clients
    Wait Until Page Contains  Clients
    Click Link  ${ClientName_global}
    Wait Until Page Contains  Analysis Request
    Click Link  Add
    Wait Until Page Contains  Request new analyses

    #Select First From Dropdown  ar_0_Batch

    Log  No Template or Profile selected  WARN
    #Select First From Dropdown  ar_0_Template
    #Select First From Dropdown  ar_0_Profile

    #Select First From Dropdown  ar_0_Profile
    #Select Specific From Dropdown  ar_0_Profile  Micro

    #Select First From Dropdown  ar_0_Sample

    SelectPrevMonthDate  ar_0_SamplingDate  1

    #Must select Sample Type otherwise the AR name changes and no end to end testing is possible
    Select Specific From Dropdown  ar_0_SampleType  ${Sample Types Title}

    #Select First From Dropdown  ar_0_SamplePoint
    #Select First From Dropdown  ar_0_ClientOrderNumber
    #Select First From Dropdown  ar_0_ClientReference
    #Select First From Dropdown  ar_0_ClientSampleID
    #Select First From Dropdown  ar_0_SamplingDeviation
    #Select First From Dropdown  ar_0_SampleCondition
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
    Select Checkbox  xpath=//input[@alt='Select ${AR_name_global}'] 

    #check AS state - To be preserved
    TestSampleState  xpath=//input[@selector='state_title_${AR_name_global}']  state_title_${AR_name_global}  To Be Preserved

    #check page state - Active
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-active']  Active

    Log  Preserve Sample  WARN
    Click Link  ${AR_name_global}
    Wait Until Page Contains Element  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P1']

    #There are 2 partitions since a seperate sample partition was requested
    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P1']
    #now select 2nd partition and enter values
    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P2']
    Select From List  xpath=//select[@selector='getContainer_PREFIX-0001-P2'] 
    Select From List  xpath=//select[@selector='getPreservation_PREFIX-0001-P2'] 

    Log  BUG: AR Preservation Converting unpreserved partition in sample due status and saving should move the partition status to to be preserved but leaves it incorrectly in sample due  WARN

    Log  Saving partitions before preserving  WARN
    Click Element  xpath=//input[@id='save_partitions_button_transition']
    #Nothing to check on page that changes have occurred - sleep
    sleep  1

    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P1']
    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P2']

    Click Element  xpath=//input[@id='preserve_transition']
    Wait Until Page Contains  PREFIX-0001-P1 is waiting to be received

    #check page state - Sample due
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-sample_due']  Sample Due
    TestSampleState  xpath=//input[@selector='state_title_PREFIX-0001-P1']  state_title_PREFIX-0001-P1  Sample Due
    TestSampleState  xpath=//input[@selector='state_title_PREFIX-0001-P2']  state_title_PREFIX-0001-P2  Sample Due
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  state_title_${AS_Keyword}  Sample Due

    Log  Receive Sample  WARN
    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P1']
    Select Checkbox  xpath=//input[@selector='PREFIX-0001_PREFIX-0001-P2']
    Click Element  receive_transition
    Wait Until Page Contains  Changes saved.

    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-sample_received']  Received
    #check 2 partitions states - Sample received
    TestSampleState  xpath=//input[@selector='state_title_PREFIX-0001-P1']  state_title_PREFIX-0001-P1  Sample received
    TestSampleState  xpath=//input[@selector='state_title_PREFIX-0001-P2']  state_title_PREFIX-0001-P2  Sample received
    #check AS state - Received
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  state_title_${AS_Keyword}  Received


    Log  Entering results  WARN
    #select a result
    Select From List  xpath=//tr[@cat='Analysis Category Title']/td/span/select[@selector='Result_${AS_Keyword}']
    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']

    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  ${AnalysisServices_global_Title}  Received

    Checkbox Should Be Selected  xpath=//input[@selector='${AR_name_global}_${AS_Keyword}']

    Click Element  submit_transition
    Page should contain  Changes saved.

    #page status remains Received
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-sample_received']  Received

    #AR status must have changed to: To be verified
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  ${AnalysisServices_global_Title}  To be verified
    
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

    Log  Not selecting Dry Matter - selecting Moisture  WARN     

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

    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-to_be_verified']  To be verified

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
    TestPageState  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']  To be verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-verify
    Click Link  workflow-transition-verify

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']
    TestPageState  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']  Verified

    #Check content status
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  ${AnalysisServices_global_Title}  Verified
    TestSampleState  xpath=//input[@selector='state_title_Clos']  Clostridia  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ecoli']  Ecoli  Verified   
    TestSampleState  xpath=//input[@selector='state_title_Entero']  Enterococcus  Verified
    TestSampleState  xpath=//input[@selector='state_title_Salmon']  Salmonella  Verified
    TestSampleState  xpath=//input[@selector='state_title_Moist']  Moisture  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ca']  Calcium  Verified
    TestSampleState  xpath=//input[@selector='state_title_Phos']  Phosphorus  Verified

    Log  Process Complete.  WARN


