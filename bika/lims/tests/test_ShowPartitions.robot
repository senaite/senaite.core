*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
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

AnalysisRequest views
    Log in        test_labmanager   test_labmanager

    Enable ShowPartitions
    Go to  ${PLONEURL}/clients/client-1
    Click Link                       Add
    Wait Until Page Contains         Request new analyses
    SelectDate                       ar_0_SamplingDate         1
    Select from dropdown             ar_0_Contact              Rita
    Select from dropdown             ar_0_Priority             High
    Select from dropdown             ar_0_Template             Bruma
    Element should be visible        xpath=//em[contains(@class, 'partnr_')]

    Disable ShowPartitions
    Go to  ${PLONEURL}/clients/client-1
    Click Link                       Add
    Wait Until Page Contains         Request new analyses
    SelectDate                       ar_0_SamplingDate         1
    Select from dropdown             ar_0_Contact              Rita
    Select from dropdown             ar_0_Priority             High
    Select from dropdown             ar_0_Template             Bruma
    Element should not be visible    xpath=//em[contains(@class, 'partnr_')]

    Click Button  Save
    Wait Until Page Contains         successfully created

    ${ar_id} =            Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =            Set Variable  ${ar_id.split()[2]}
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
    Click button                 xpath=//input[@value="Receive sample"]
    Wait until page contains     saved

