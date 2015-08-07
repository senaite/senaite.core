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

AnalysisRequest views
    enable autologin as  LabManager
    Disable stickers

    Enable ShowPartitions
    given an ar add form in client-1 with columns layout and 1 ars
    select date  SamplingDate-0  1
    I select Rita from the Contact combogrid in column 0
    I select High from the Priority combogrid in column 0
    I select Bruma from the Template combogrid in column 0
    wait until element is visible  xpath=//span[@class='partnr' and .='1']
    xpath should match x times  .//span[@class='partnr' and .='1']  7

    Disable ShowPartitions
    given an ar add form in client-1 with columns layout and 1 ars
    select date  SamplingDate-0  1
    I select Rita from the Contact combogrid in column 0
    I select High from the Priority combogrid in column 0
    I select Bruma from the Template combogrid in column 0
    sleep  2
    Element should not be visible    xpath=//em[contains(@class, 'partnr')]
    click button  Save
    wait until page contains element  xpath=.//dd[contains(text(), 'created')]
    ${dd_text} =  Get text  xpath=.//dd[contains(text(), 'created')]
    ${ar_id} =  Set Variable  ${dd_text.split()[2]}
    ${ar_view_url} =      Set Variable  ${PLONEURL}/clients/client-1/${ar_id}/base_view
    ${ar_analyses_url} =  Set Variable  ${PLONEURL}/clients/client-1/${ar_id}/analyses
    ${ar_results_url} =   Set Variable  ${PLONEURL}/clients/client-1/${ar_id}/manage_results

    Receive AR   ${ar_id}

    Enable ShowPartitions
    Go to  ${ar_view_url}
    Page should contain              Sample Partitions
    Page should contain element      xpath=//*[@id='foldercontents-Partition-column']
    Page should contain element      partitions
    Go to  ${ar_analyses_url}
    Page should contain              Sample Partitions
    Page should contain element      xpath=//*[@id='foldercontents-Partition-column']
    Page should contain element      partitions

    Disable ShowPartitions
    Go to  ${ar_view_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']
    Page should not contain element  partitions
    Go to  ${ar_analyses_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']
    Page should not contain element  partitions

    ${sample_id} =            Set Variable   ${ar_id[:-4]}
    ${sample_view_url} =      Set Variable   ${PLONEURL}/clients/client-1/${sample_id}/base_view
    ${sample_analyses_url} =  Set Variable   ${PLONEURL}/clients/client-1/${sample_id}/analyses

    Enable ShowPartitions
    Go to  ${sample_view_url}
    Page should contain              Sample Partitions
    Page should contain element      xpath=//*[@id='foldercontents-Partition-column']

    Disable ShowPartitions
    Go to  ${sample_view_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']


*** Keywords ***

Enable ShowPartitions
    Go to                      ${PLONEURL}/bika_setup
    Click link                 Analyses
    Select Checkbox            ShowPartitions
    Click Button               Save
    Wait Until Page Contains   Changes saved.

Disable ShowPartitions
    Go to                      ${PLONEURL}/bika_setup
    Click link                 Analyses
    Unselect Checkbox          ShowPartitions
    Click Button               Save
    Wait Until Page Contains   Changes saved.

Receive AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@id="receive_transition"]
    Wait until page contains     saved
