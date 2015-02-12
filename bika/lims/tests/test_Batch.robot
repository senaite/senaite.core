*** Settings ***

Library          BuiltIn
Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Library          DebugLibrary
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

Test AR created inside batches
    Log in  test_labmanager  test_labmanager

    Add Batch
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

Test Worksheets created inside Batch objects
    Log in                              test_labmanager         test_labmanager
    ## Add batch
    Go to                               ${PLONEURL}/batches
    Click Link                          Add
    Wait until page contains            Add Batch
    Input Text                          title                   Batch With Worksheet
    Set Selenium Timeout                10
    Click Button                        Save
    Wait until page contains            Changes saved.
    ## Add AR
    Wait until page contains            Add new
    input text                          ar_count  1
    click Link                          Add new
    Wait until page contains            Request new analyses
    Select from dropdown                css=#Client-0             Happy
    Select from dropdown                css=#Contact-0            Rita
    Select from dropdown                css=#SampleType-0         Apple
    Select from dropdown                css=#Profile-0            Hardness
    SelectDate                          css=#SamplingDate-0       1
    Click Button                        Save
    Wait until page contains            created
    select checkbox                     css=input[item_title='AP-0001-R01']
    click element                       css=#receive_transition
    Wait until page contains            Changes saved.
    ## Add Worksheet
    go to                               ${PLONEURL}/batches/B-001/worksheets
    select from list                    css=.analyst         test_analyst1
    click element                       css=.worksheet_add
    wait until page contains            Water Chemistry

Test batch inherited ARs
    Log in                              test_labmanager         test_labmanager
    ## Add batch
    Go to                               ${PLONEURL}/batches
    Click Link                          Add
    Wait until page contains            Add Batch
    Input Text                          title                   First Batch
    # ar context:
    Page should not contain element     Client
    Input Text                          description             contains ARs.
    Click Button                        Save
    go to                               ${PLONEURL}/batches/B-001/analysisrequests
    input text                          ar_count           1
    click link                          Add new
    wait until page contains            Request new analyses
    Select from dropdown                css=#Client-0             Happy
    ##Click element                       css=.ClientCopyButton
    Select from dropdown                css=#Contact-0            Rita
    ##Click element                       css=.ContactCopyButton
    SelectDate                          css=#SamplingDate-0       1
    ##Click element                       css=.SamplingDateCopyButton
    Select from dropdown                css=#SampleType-0         Water
    ##Click element                       css=.SampleTypeCopyButton
    Click element                       css=#cat_lab_Metals
    ##Select checkbox                     xpath=//input[@title='Calcium'][1]
    ##Click element                       xpath=//img[@name='Calcium']
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                10
    ## Add second batch
    Go to                               ${PLONEURL}/batches
    Click Link                          Add
    Input Text                          title           Second Batch
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

Test Batch-Attach
    Log in  test_labmanager  test_labmanager

    ${PATH_TO_TEST} =                   run keyword   resource_filename
    Add Batch
    Add AttachmentType
    go to                               ${PLONEURL}/batches/B-001/attachments
    click link                          Add
    Choose File                         AttachmentFile_file           ${PATH_TO_TEST}/test_Batch.robot
    select from dropdown                AttachmentType                MS
    Input Text                          AttachmentKeys                ASDFK
    click button                        Save
    Wait until page contains            Changes saved.

Test Batch-Contact-Auto-CC
    Log in                       test_labmanager  test_labmanager
    Go to                        http://localhost:55001/plone/clients/client-1/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Batch
    Input text                   description  Just a regular batch
    SelectDate                   BatchDate       1
    Select from dropdown         Contact    Rita
    Page should contain          Seemonster
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved

*** Keywords ***

Add Batch
    Go to                        http://localhost:55001/plone/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Batch
    Input text                   description  Just a regular batch
    SelectDate                   BatchDate       1
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved
    
Add ClientBatch
    Go to                        http://localhost:55001/plone/clients/client-1/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Batch
    Input text                   description  Just a regular batch
    SelectDate                   BatchDate       1
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved
    
Add AttachmentType
    Go to  ${PLONEURL}/bika_setup/bika_attachmenttypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title          MSDS
    Input Text  description    Temporary test object
    Click Button  Save
    Wait Until Page Contains  Changes saved.
    
Batch state should be
    [Arguments]   ${state_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Analysis Requests
    Page should contain element  css=span.state-${state_id}

Add AR
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Add new
    input text                   ar_count  1
    click Link                   Add new
    Wait until page contains     Request new analyses
    Select from dropdown         css=#Client-0             Happy
    Select from dropdown         css=#Contact-0            Rita
    Select from dropdown         css=#SampleType-0         Apple
    Select from dropdown         css=#Profile-0            Counts
    SelectDate                   css=#SamplingDate-0       1
    Click Button                 Save
    Wait until page contains     created

Receive AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Receive sample"]
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
    Click button                 xpath=//input[@value="Submit for verification"]
    Wait until page contains     saved

Retract AR
    [Arguments]   ${ar_id}
    Go to                               http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains            ${ar_id}
    Select checkbox                     xpath=//input[@item_title="${ar_id}"]
    Click button                        xpath=//input[@value="Retract"]
    Wait until page contains element    xpath=//input[@selector="state_title_AP-0001-R01" and @value="Received"]
    Go to                               http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains            Add new
    Click link                          ${ar_id}
    Wait until page contains            Results not requested
    Select Checkbox                     ar_manage_results_lab_select_all
    Click button                        xpath=//input[@value="Retract"]
    Wait Until Page Contains            Changes saved

Verify AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Verify"]
    Wait until page contains     saved
