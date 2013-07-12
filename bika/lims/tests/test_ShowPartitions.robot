*** Settings ***

Documentation    Test views with and without ShowPartitions setting enabled.
...              In most cases, the partition is still present in the page,
...              in a hidden field - so, test to see that all the javascript
...              still functions.

Library   Selenium2Library  timeout=10  implicit_wait=0.2
Library   String
Resource  keywords.txt

Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${SELENIUM_SPEED}       0

*** Test Cases ***

AnalysisRequest views
    Log in        test_labmanager  test_labmanager

    Enable ShowPartitions
    Go to  http://localhost:55001/plone/clients/client-1
    Click Link                      Add
    Wait Until Page Contains        Request new analyses
    Select from dropdown            ar_0_Template             Bruma
    Select from datepicker          ar_0_SamplingDate         1
    Element should be visible       xpath=//em[contains(@class, 'partnr_')]

    Disable ShowPartitions
    Go to  http://localhost:55001/plone/clients/client-1
    Click Link                      Add
    Wait Until Page Contains        Request new analyses
    Select from dropdown            ar_0_Template             Bruma
    Select from datepicker          ar_0_SamplingDate         1
    Element should not be visible   xpath=//em[contains(@class, 'partnr_')]

    Click Button  Save
    Wait Until Page Contains        successfully created

    # Get new Analysis Request ID and URL
    ${ar_id} =            Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =            Set Variable  ${ar_id.split()[2]}
    ${ar_view_url} =      Set Variable  http://localhost:55001/plone/clients/client-1/${ar_id}/base_view
    ${ar_analyses_url} =  Set Variable  http://localhost:55001/plone/clients/client-1/${ar_id}/analyses
    ${ar_results_url} =   Set Variable  http://localhost:55001/plone/clients/client-1/${ar_id}/manage_results

    Enable ShowPartitions
    Go to  ${ar_view_url}
    Page should contain             Sample Partitions
    Page should contain element     xpath=//*[@id='foldercontents-Partition-column']
    Page should contain element     partitions
    Go to  ${ar_analyses_url}
    Page should contain             Sample Partitions
    Page should contain element     xpath=//*[@id='foldercontents-Partition-column']
    Page should contain element     partitions

    Disable ShowPartitions
    Go to  ${ar_view_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']
    Page should not contain element  partitions
    Go to  ${ar_analyses_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']
    Page should not contain element  partitions

    # Get Sample ID and URL
    ${sample_id} =            Set Variable   ${ar_id[:-4]}
    ${sample_view_url} =      Set Variable   http://localhost:55001/plone/clients/client-1/${sample_id}/base_view
    ${sample_analyses_url} =  Set Variable   http://localhost:55001/plone/clients/client-1/${sample_id}/analyses

    Enable ShowPartitions
    Go to  ${sample_view_url}
    Page should contain             Sample Partitions
    Page should contain element     xpath=//*[@id='foldercontents-Partition-column']

    Disable ShowPartitions
    Go to  ${sample_view_url}
    Page should not contain          Sample Partitions
    Page should not contain element  xpath=//*[@id='foldercontents-Partition-column']


*** Keywords ***

Start browser
    Open browser        http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}

Enable ShowPartitions
    Go to              http://localhost:55001/plone/bika_setup
    Click link         Analyses
    Select Checkbox    ShowPartitions
    Click Button       Save
    Wait Until Page Contains  Changes saved.

Disable ShowPartitions
    Go to              http://localhost:55001/plone/bika_setup
    Click link         Analyses
    Unselect Checkbox  ShowPartitions
    Click Button       Save
    Wait Until Page Contains  Changes saved.
