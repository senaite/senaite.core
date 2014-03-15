*** Settings ***

Library                 Selenium2Library  timeout=10  implicit_wait=0.2
Library                 Collections
Resource                keywords.txt
Variables               plone/app/testing/interfaces.py

Suite Setup             Start browser
Suite Teardown          Close All Browsers

*** Variables ***

${SELENIUM_SPEED}  0
${PLONEURL}        http://localhost:55001/plone
${ar_factory_url}  ar_add

*** Test Cases ***

Analysis Request with no samping or preservation workflow

    Go to        ${PLONEURL}/bika_setup/edit
    Click link  Analyses
    Unselect Checkbox  SamplingWorkflowEnabled
    Click Button  Save
    Wait Until Page Contains  Changes saved.

    Go to                     ${PLONEURL}/clients/client-1/${ar_factory_url}?col_count=1
    ${ar_id}=                 Complete ar_add form with template    Lab: Borehole 12 Hardness
    Go to                     ${PLONEURL}/clients/client-1/analysisrequests
    Execute transition receive on items in form_id analysisrequests
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Submit results with out of range tests
    Log out
    Log in                    test_labmanager1    test_labmanager1
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
    Execute transition verify on items in form_id lab_analyses
    Log out
    Log in                    test_labmanager    test_labmanager
    # There is no "retract" transition on verified analyses - but there should/will be.
    # Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
    # Execute transition retract on items in form_id lab_analyses




# XXX Automatic expanded categories
# XXX Restricted categories

# XXX samplingworkflow
# XXX preservation workflow

# XXX field analyses
# XXX copy across in all fields


*** Keywords ***

Start browser
    Open browser        ${PLONEURL}/login_form
    Log in              test_labmanager    test_labmanager
    Set selenium speed  ${SELENIUM_SPEED}

Complete ar_add form with template
    [Arguments]  ${template}=

    @{time} =               Get Time        year month day hour min sec

    SelectDate                  ar_0_SamplingDate     @{time}[2]
    Select from list            ar_0_ARTemplate       ${template}
    sleep    1

    #Click Element  Batch
    #Click Element  Sample
    #Select From List      ar_0_SamplePoint              Thing
    #Select From List      ar_0_ClientOrderNumber              Thing
    #Select From List      ar_0_ClientReference              Thing
    #Select From List      ar_0_ClientSampleID              Thing
    #Select From List      ar_0_SamplingDeviation              Thing
    #Select From List      ar_0_SampleCondition              Thing
    #Select From List      ar_0_DefaultContainerType              Thing
    #Select Checkbox  ar_0_AdHoc
    #Select Checkbox  ar_0_Composite
    #Select Checkbox  ar_0_ReportDryMatter
    #Select Checkbox  ar_0_InvoiceExclude

    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}

Complete ar_add form Without template
    @{time} =                  Get Time        year month day hour min sec
    SelectDate                 ar_0_SamplingDate   @{time}[2]
    Select From List           ar_0_SampleType    Water
    Click Element              xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox            xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Metals']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Microbiology']
    Select Checkbox            xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout       30
    Click Button               Save
    Wait until page contains   created
    Set Selenium Timeout       10
    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
    [return]                   ${ar_id}

Submit results with out of range tests
    [Documentation]   Complete all received analysis result entry fields
    ...               Do some out-of-range checking, too

    ${count} =          Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =          Convert to integer    ${count}
    :FOR    ${index}    IN RANGE    1   ${count+1}
    \    TestResultsRange    xpath=(//input[@type='text' and @field='Result'])[${index}]       5   10
    \    Press Key      xpath=(//input[@type='text' and @field='Result'])[${index}]   \\09
    sleep  1
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

Submit results
    [Documentation]   Complete all received analysis result entry fields

    ${count} =          Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =          Convert to integer    ${count}
    :FOR    ${index}    IN RANGE    1   ${count+1}
    \    Input text     xpath=(//input[@type='text' and @field='Result'])[${index}]   10
    \    Press Key      xpath=(//input[@type='text' and @field='Result'])[${index}]   \\09
    sleep  1
    Click Element               xpath=//input[@value='Submit for verification']
    Wait Until Page Contains    Changes saved.

TestResultsRange
    [Arguments]  ${locator}=
    ...          ${badResult}=
    ...          ${goodResult}=

    # Log  Testing Result Range for ${locator} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          ${locator}  ${badResult}
    Press Key           ${locator}  \\09
    Expect exclamation
    Input Text          ${locator}  ${goodResult}
    Press Key           ${locator}  \\09
    Expect no exclamation

Expect exclamation
    sleep  0.5
    Page should contain Image   ${PLONEURL}/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  0.5
    Page should not contain Image  ${PLONEURL}/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN






Temp
    #check AS state - To be preserved
    TestSampleState  xpath=//input[@selector='state_title_${AR_name_global}']  state_title_${AR_name_global}  To Be Preserved

    #check page state - Active
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-active']  Active

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




    #page status remains Received
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-sample_received']  Received

    #AR status must have changed to: To be verified
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  ${AnalysisServices_global_Title}  To be verified


Verify AR

    Log  Verifying AR: ${AR_name_global} by different user  WARN

    #Why does this not work??
    #Click Link  ${AR_name_global}
    Click Element  xpath=//a[@id='to_be_verified_${AR_name_global}']

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-to_be_verified']  To be verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-verify
    Click Link  workflow-transition-verify

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-verified']  Verified

    #Check content status
    TestSampleState  xpath=//input[@selector='state_title_${AS_Keyword}']  ${AnalysisServices_global_Title}  Verified
    TestSampleState  xpath=//input[@selector='state_title_Clos']  Clostridia  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ecoli']  Ecoli  Verified
    TestSampleState  xpath=//input[@selector='state_title_Entero']  Enterococcus  Verified
    TestSampleState  xpath=//input[@selector='state_title_Salmon']  Salmonella  Verified
    TestSampleState  xpath=//input[@selector='state_title_Moist']  Moisture  Verified
    TestSampleState  xpath=//input[@selector='state_title_Ca']  Calcium  Verified
    TestSampleState  xpath=//input[@selector='state_title_Phos']  Phosphorus  Verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-publish
    Click Link  workflow-transition-publish
    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']
    TestPageState  xpath=//dl[@id='plone-contentmenu-workflow']//span[@class='state-verified']  Published

    Log  Process Complete.  WARN
