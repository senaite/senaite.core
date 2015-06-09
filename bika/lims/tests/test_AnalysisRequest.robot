*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Library         bika.lims.testing.Keywords
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

${ar_factory_url}  portal_factory/AnalysisRequest/xxx/ar_add

*** Test Cases ***
Analysis request with sequence_start in Bika Setup
    Enable autologin as  LabManager
    Set sequence start                  85
    Create Simple AR
    Page Should Contain                 BAR-0085
    Create Simple AR
    Page Should Contain                 BAR-0086

Check Analysis Requests listing view
    Enable autologin as  LabManager
    Create Simple AR
    Open context menu           xpath=.//th[@id="foldercontents-getSample-column"]
    Click element               xpath=.//tr[@col_id="AdHoc"]
    Click link                  sample_due
    Open context menu           xpath=.//th[@id="foldercontents-getSample-column"]
    Click element               xpath=.//tr[@col_id="AdHoc"]
    Click link                  default
    Open context menu           xpath=.//th[@id="foldercontents-getSample-column"]
    Click element               xpath=.//tr[@col_id="AdHoc"]
    Click link                  sample_due
    Open context menu           xpath=.//th[@id="foldercontents-getSample-column"]
    Click element               xpath=.//tr[@col_id="AdHoc"]

Check CCContacts widget basic functionality
    Enable autologin as  LabManager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_CCContact                Rita
    Element Should Contain      ar_0_CCContact-listing        Rita

Check that the editable SamplePoint widget in AnalysisRequestView shows both Client and Lab items
    # Create a new Client/SamplePoint
    Enable autologin as  LabManager
    Set up Auto print stickers
    go to                        ${PLONEURL}/clients/client-1/portal_factory/SamplePoint/xxx/edit
    input text                   title                             Pringle Bay Beach
    click button                 Save
    wait until page contains     saved

    ${ar_id}=                    Create AR in client-1 with contact Rita
    go to                        ${PLONEURL}/clients/client-1/${ar_id}
    wait until page contains     Manage Analyses
    select from dropdown         css=#SamplePoint       Mil        1
    Textfield value should be    css=#SamplePoint       Mill
    select from dropdown         css=#SamplePoint       Pringle    1
    Textfield value should be    css=#SamplePoint       Pringle Bay Beach
    # can't be accessed in ar_add by any other client:
    go to                              ${PLONEURL}/clients/client-2/${ar_factory_url}
    wait until page contains element   css=#ar_0_SamplePoint
    Run Keyword And Expect Error   *   select from dropdown            css=#ar_0_SamplePoint     Pringle
    # or in the main AR header_table.
    ${ar_id}=                          Create AR in client-2 with contact Johanna
    go to                              ${PLONEURL}/clients/client-2/${ar_id}
    wait until page contains           Manage Analyses
    Run Keyword And Expect Error   *   select from dropdown            css=#SamplePoint     Pringle


Check the AR Add javascript
   # check that the Contact CC auto-fills correctly when a contact is selected
    Enable autologin as  LabManager
    Go to                     ${PLONEURL}/clients/client-1
    Wait until page contains  Happy
    Click Link                Add
    SelectDate                          ar_0_SamplingDate       1
    Select From Dropdown                ar_0_SampleType         Water
    Select from dropdown                ar_0_Contact            Rita
    Xpath Should Match X Times          //div[@class='reference_multi_item']   1
    Select from dropdown                ar_0_Contact            Neil
    Select from dropdown                ar_0_Priority           High
    Xpath Should Match X Times          //div[@class='reference_multi_item']   2

    # check that we can expand and collaps the analysis categories
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    wait until page contains            Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    element should not be visible             Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    page should contain                 Clostridia

# XXX Automatic expanded categories
# XXX Restricted categories
# XXX preservation workflow
# XXX field analyses
# XXX copy across in all fields

Analysis Request with no sampling or preservation workflow
    Enable autologin as  LabManager
    Set autologin username  test_labmanager
    Go to                     ${PLONEURL}/clients/client-1
    Click Link                Add
    ${ar_id}=                 Complete ar_add form with template Bore
    Go to                     ${PLONEURL}/clients/client-1/analysisrequests
    Execute transition receive on items in form_id analysisrequests
    Disable autologin
    Enable autologin as  Analyst
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Submit results with out of range tests
    Disable autologin
    Enable autologin as  LabManager
    Set autologin username  test_labmanager1
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Add new Copper analysis to ${ar_id}
    ${ar_id} state should be sample_received
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
    Execute transition verify on items in form_id lab_analyses
#    Disable autologin
#    Enable autologin as  LabManager
# There is no "retract" transition on verified analyses - but there should/will be.
# Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
# Execute transition retract on items in form_id lab_analyses


Create two different ARs from the same sample.
    Enable autologin as  LabManager
    Set up Auto print stickers
    Create AR in client-1 with contact Rita
    Create Secondary AR
    In a client context, only allow selecting samples from that client.

AR with sampling workflow actived and preservation workflow desactived
    [Documentation]  It tests the AR workflow with the SamplingWorkflow
    ...  enabled, but without preserving the sample. This is the correct
    ...  workflow, but more things should be tested, like transitions from
    ...  button (both, SamplePartition and Analysis), etc
    Enable autologin as  LabManager
    Set autologin username  test_labmanager
    Enable Sampling Workflow
    ${ar_id}=           Create Simple AR
    Click Link          ${ar_id}
    Page Should Contain  to_be_sampled
    Save a Sampler and DateSampled on AR
    Execute transition sample inside ClientARView/ManageResults
    Execute transition receive inside ClientARView/ManageResults
    Disable autologin
    Enable autologin as  Analyst
    Go to               ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Submit results with out of range tests
    Disable autologin
    Enable autologin as  LabManager
    Set autologin username  test_labmanager1
    Execute transition verify inside ClientARView/ManageResults

AR with sampling workflow actived and preservation workflow actived
    [Documentation]  It tests the AR workflow with the SamplingWorkflow
    ...  enabled and with preserving the sample. This is the correct
    ...  workflow, but more things should be tested, like transitions from
    ...  button (both, SamplePartition and Analysis), etc
    Enable autologin as  LabManager
    Enable Sampling Workflow
    ${ar_id}=           Create Simple AR
    Click Link          ${ar_id}
    Page Should Contain  to_be_sampled
    Save a Sampler and DateSampled on AR
    Define container Glass Bottle 500ml and preservation HNO3 from Sample Partitions
    Execute transition sample inside ClientARView/ManageResults
    Select From List    //td[5]/span[2]/select  Lab Preserver 1
    @{time} =           Get Time        year month day hour min sec
    Select Date         //td[6]/input    @{time}[2]
    Select Checkbox     //td/input
    Click Button        id=preserve_transition
    Page Should Contain      is waiting to be received.
    Execute transition receive inside ClientARView/ManageResults
    Disable autologin
    Enable autologin as   Analyst
    Go to               ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Submit results with out of range tests
    Disable autologin
    Enable autologin as   LabManager
    Go to               ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Execute transition verify inside ClientARView/ManageResults

*** Keywords ***

Create AR in ${client_id} with contact ${contact}
    @{time} =                   Get Time        year month day hour min sec

    Go to                       ${PLONEURL}/clients/${client_id}
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses

    wait until page contains element    ar_0_Contact
    Select from dropdown        ar_0_Contact                ${contact}
    Select from dropdown        ar_0_Template               Bore
    Select Date                 ar_0_SamplingDate           @{time}[2]
    sleep                       1
    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    Go to                       ${PLONEURL}/clients/${client_id}/analysisrequests
    Wait until page contains    ${ar_id}
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@id="receive_transition"]
    Wait until page contains    saved
    [return]                    ${ar_id}

Create Simple AR
    Go to    ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link    Add
    Wait until page contains    Request new analyses
    Select from dropdown    ar_0_Contact    Rita
    Select from dropdown    ar_0_SampleType    Barley
    @{time} =    Get Time    year month day hour min sec
    Select Date    ar_0_SamplingDate    @{time}[2]
    Click Element  cat_lab_Metals
    Select Checkbox  //input[@title='Calcium']
    Click Button    Save
    Wait until page contains    created
    Set Selenium Timeout    2
    ${ar_id} =    Get text    //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =    Set Variable    ${ar_id.split()[2]}
    [Return]    ${ar_id}

Create Secondary AR
    Enable autologin as  LabManager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bruma
    select from dropdown        ar_0_Sample        H2O
    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        2
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}

In a client context, only allow selecting samples from that client.
    Enable autologin as  LabManager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-2
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact               Johanna
    Select from dropdown        ar_0_Template              Bore    1
    Run keyword and expect error  *    Select from dropdown        ar_0_Sample


Complete ar_add form with template ${template}
    Wait until page contains    Request new analyses
    @{time} =                   Get Time        year month day hour min sec
    SelectDate                  ar_0_SamplingDate   @{time}[2]
    Select from dropdown        ar_0_Contact       Rita
    Select from dropdown        ar_0_Priority           High
    Select from dropdown        ar_0_Template       ${template}
    Sleep                       5
    Click Button                Save
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}

Complete ar_add form Without template
    @{time} =                  Get Time        year month day hour min sec
    SelectDate                 ar_0_SamplingDate   @{time}[2]
    Select From Dropdown       ar_0_SampleType    Water
    Select from dropdown       ar_0_Contact       Rita
    Select from dropdown       ar_0_Priority           High
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
    Set Selenium Timeout       60
    Click Button               Save
    Wait until page contains   created
    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
    [return]                   ${ar_id}

Submit results with out of range tests
    [Documentation]   Complete all received analysis result entry fields
    ...               Do some out-of-range checking, too

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    TestResultsRange      xpath=(//input[@type='text' and @field='Result'])[${index}]       5   10
    Sleep                      5s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Submit results
    [Documentation]   Complete all received analysis result entry fields

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    Input text            xpath=(//input[@type='text' and @field='Result'])[${index}]   10
    Sleep                      5s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Add new ${service} analysis to ${ar_id}
    Go to                      ${PLONEURL}/clients/client-1/${ar_id}/analyses
    select checkbox            xpath=//input[@alt='Select ${service}']
    click element              save_analyses_button_transition
    wait until page contains   saved.

${ar_id} state should be ${state_id}
    Go to                        ${PLONEURL}/clients/client-1/${ar_id}
    log     span.state-${state_id}   warn
    Page should contain element  css=span.state-${state_id}

TestResultsRange
    [Arguments]  ${locator}=
    ...          ${badResult}=
    ...          ${goodResult}=

    # Log  Testing Result Range for ${locator} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          ${locator}  ${badResult}
    Press Key           ${locator}   \\9
    Expect exclamation
    Input Text          ${locator}  ${goodResult}
    Press Key           ${locator}   \\9
    Expect no exclamation

Expect exclamation
    sleep  .5
    Page should contain Image   ${PLONEURL}/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  .5
    Page should not contain Image  ${PLONEURL}/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

Save a Sampler and DateSampled on AR
    @{time} =           Get Time    year month day hour min sec
    Select Date         DateSampled    @{time}[2]
    Select From List    Sampler  Lab Sampler 1
    Click Button        Save
    Page Should Contain  Changes saved.

Define container ${container} and preservation ${preservation} from Sample Partitions
    Select From List    //span[2]/select    ${container}
    Select From List    //td[4]/span[2]/select    ${preservation}
    Click Button        save_partitions_button_transition

Set up Auto print stickers
    Go to                               ${PLONEURL}/bika_setup/edit
    Click link                          Stickers
    Select From List By Value           AutoPrintStickers   None
    Click Button                        Save

Set sequence start
    [Arguments]   ${sequence_start}
    Go to                               http://localhost:55001/plone/bika_setup/edit
    Click link                          Id server
    Input text                          xpath=//input[@id='SampleIDSequenceStart']   ${sequence_start}
    Click Button                        Save
    Wait Until Page Contains            Changes saved
