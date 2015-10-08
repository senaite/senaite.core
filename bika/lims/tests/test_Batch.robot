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

*** Test Cases ***

Test Batch-AR
    Log in  test_labmanager  test_labmanager

    Set up Auto print stickers
    Add Batch  batch-1
    Batch state should be  open
    Add AR
    Receive AR  AP-0001-R01
    Batch state should be  open
    Submit AR  AP-0001-R01
    Batch state should be  open
    Retract AR  AP-0001-R01
    Submit AR  AP-0001-R01
    # Log out
    # Log in  test_labmanager1  test_labmanager1
    # Verify AR  AP-0001-R01

Test batch inherited ARs
    Log in                              test_labmanager         test_labmanager

    ## Add batch
    Go to                               ${PLONEURL}/batches
    Click Link                          Add
    Wait until page contains            Add Batch
    Input Text                          title                   First Batch
    select from dropdown                Client                  Happy
    Input Text                          description             contains ARs.
    Click Button                        Save

    go to                               ${PLONEURL}/batches/B-001/analysisrequests
    select from list                    ar_count           6
    click link                          Add new
    wait until page contains            Request new analyses
    Select from dropdown                ar_0_Contact            Rita
    Click element                       css=.ContactCopyButton
    SelectDate                          ar_0_SamplingDate       1
    Click element                       css=.SamplingDateCopyButton
    Select from dropdown                ar_0_SampleType         Water
    Click element                       css=.SampleTypeCopyButton
    Click element                       css=#cat_lab_Metals
    Select checkbox                     xpath=//input[@title='Calcium'][1]
    Click element                       xpath=//img[@name='Calcium']
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                10

    ## Add second batch
    Go to                               ${PLONEURL}/batches
    Click Link                          Add
    Input Text                          title           Second Batch
    select from dropdown                Client          Happy
    Input Text                          description     Inherit, delete, rinse, repeat
    Click Button                        Save

    go to                               ${PLONEURL}/batches/B-002/base_edit
    click element                       InheritedObjectsUI_more
    click element                       InheritedObjectsUI_more
    click element                       InheritedObjectsUI_more
    click element                       InheritedObjectsUI_more
    select from dropdown                InheritedObjectsUI-Title-0    0001
    select from dropdown                InheritedObjectsUI-Title-1    0002
    select from dropdown                InheritedObjectsUI-Title-2    0003
    select from dropdown                InheritedObjectsUI-Title-3    0004
    select from dropdown                InheritedObjectsUI-Title-4    0005
    Click button                        Save

    go to                               ${PLONEURL}/batches/B-002/base_edit
    Click element                       delete-row-0
    Click button                        Save
    go to                               ${PLONEURL}/batches/B-002/base_edit
    page should not contain element     delete-row-5
    Click element                       delete-row-0
    Click element                       delete-row-1
    Click element                       delete-row-2
    Click element                       delete-row-3
    select from dropdown                InheritedObjectsUI-Title-4    First Batch
    click button                        Save
    go to                               ${PLONEURL}/batches/B-002/batchbook

Test Batch with sequence_start in Bika Setup
    Log in                       test_labmanager         test_labmanager
    Add Batch                    batch-1
    Go to                        http://localhost:55001/plone/batches
    Page Should Contain          B-001
    Add Batch                    batch-2
    Go to                        http://localhost:55001/plone/batches
    Page Should Contain          B-002
    Set sequence start           45
    Add Batch                    batch-3
    Go to                        http://localhost:55001/plone/batches
    Page Should Contain          B-045
    Add Batch                    batch-4
    Go to                        http://localhost:55001/plone/batches
    Page Should Contain          B-046
    Set sequence start           22
    Add Batch                    batch-5
    Go to                        http://localhost:55001/plone/batches
    Page Should Contain          B-047


*** Keywords ***

Add Batch
    [Arguments]   ${batch_title}
    Go to                        http://localhost:55001/plone/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Batch
    Input text                   title  ${batch_title}
    Input text                   description  Just a regular batch
    Select from dropdown         Client     Happy
    SelectDate                   BatchDate       1
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved

Batch state should be
    [Arguments]   ${state_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Analysis Requests
    Page should contain element  css=span.state-${state_id}

Add AR
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Add new
    Select from list             ar_count  1
    click Link                   Add new
    Wait until page contains     Request new analyses
    Select from dropdown         ar_0_Contact            Rita
    Select from dropdown         ar_0_SampleType         Apple
    Select from dropdown         ar_0_Profile            Counts
    SelectDate                   ar_0_SamplingDate       1
    Click Button                 Save
    Wait until page contains     created

Receive AR
    [Arguments]   ${ar_id}
    Go to                            http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@id="receive_transition"]
    Wait until page contains     saved

Submit AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Add new
    Click link                   ${ar_id}
    Wait until page contains     Results not requested
    Input text                   xpath=//tr[@keyword='Ecolicnt']//input[@type='text']    10
    Input text                   xpath=//tr[@keyword='Enterocnt']//input[@type='text']   10
    Input text                   xpath=//tr[@keyword='TVBcnt']//input[@type='text']      10
    Press Key                    xpath=//tr[@keyword='TVBcnt']//input[@type='text']      \t
    focus                        css=#content-core
    Click button                 xpath=//input[@id="submit_transition"]
    Wait until page contains     saved

Retract AR
    [Arguments]   ${ar_id}
    Go to                               http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains            ${ar_id}
    Select checkbox                     xpath=//input[@item_title="${ar_id}"]
    Click button                        xpath=//input[@id="retract_transition"]
    Wait until page contains element    xpath=//input[@selector="state_title_AP-0001-R01" and @value="Received"]
    Go to                               http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains            Add new
    Click link                          ${ar_id}
    Wait until page contains            Results not requested
    Select Checkbox                     ar_manage_results_lab_select_all
    Click button                        xpath=//input[@id="retract_transition"]
    Wait Until Page Contains            Changes saved

Verify AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@id="verify_transition"]
    Wait until page contains     saved

Set up Auto print stickers
    Go to                               ${PLONEURL}/bika_setup/edit
    Click link                          Stickers
    Select From List By Value           AutoPrintStickers   None
    Click Button                        Save

Set sequence start
    [Arguments]   ${sequence_start}
    Go to                               http://localhost:55001/plone/bika_setup/edit
    Click link                          Id server
    Input text                          xpath=//input[@id='Prefixes-sequence_start-2']   ${sequence_start}
    Click Button                        Save
    Wait Until Page Contains            Changes saved
