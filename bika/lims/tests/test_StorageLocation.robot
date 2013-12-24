*** Settings ***

Library          Selenium2Library  timeout=10  implicit_wait=0.2
Library          String
Library          Dialogs
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${PATH_TO_TEST} =
${PLONEURL}        http://localhost:55001/plone
${LOCATION_ADDRESS}         HAM.FZ1.S2

*** Test Cases ***

Test Storage Location
    Log in                      test_labmanager  test_labmanager

    Check Bika Setup imported correctly
    Create Setup Location
    Create Client Location
    Check AR Creation

*** Keywords ***

Start browser
    Open browser                ${PLONEURL}/login
    Set selenium speed          ${SELENIUM_SPEED}

Check Bika Setup imported correctly
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Page Should Contain         ${LOCATION_ADDRESS}

Create Setup Location
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             BIKA.FR1.S2
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Page should contain         BIKA.FR1.S2

Create Client Location
    Go to                       ${PLONEURL}/clients/client-1/storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             ${LOCATION_ADDRESS}
    Go to                       ${PLONEURL}/clients/client-1/storagelocations
    Page should contain         ${LOCATION_ADDRESS}

Create Location
    [Arguments]  ${address}
    Input Text                  title  ${address}
    Input Text                  SiteTitle  BIKA Labs
    Input Text                  SiteCode  BIKA
    Input Text                  SiteDescription  BIKA Labs site in Grabou
    Input Text                  LocationTitle  Freezer 1
    Input Text                  LocationCode  FR1
    Input Text                  LocationDescription  Freeze 1
    Input Text                  LocationType  Freezer
    Input Text                  ShelfTitle  Shelf 2
    Input Text                  ShelfCode  S2
    Input Text                  ShelfDescription  Second shelf from bottom
    Click Button                Save
    Wait until page contains    Changes saved.

Check AR Creation
    Go to                       ${PLONEURL}/clients/client-1
    ${ar_id}=                   Create AR
    Go to                       ${PLONEURL}/clients/client-1/${ar_id}
    Page should contain         ${LOCATION_ADDRESS}
    Go to                       ${PLONEURL}/clients/client-1/H2O-0001
    Wait until page contains    Sample Due
    Page should contain         Storage Location

Create AR
    Click Link                  link=Add
    Wait until page contains    Request new analyses
    @{time} =                   Get Time        year month day hour min sec
    Select from dropdown        ar_0_Contact       Rita
    SelectDate                  ar_0_SamplingDate   @{time}[2]
    Select From Dropdown        ar_0_SampleType    Water
    Select from dropdown        ar_0_StorageLocation       ${LOCATION_ADDRESS}
    Click Element               xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox             xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element               xpath=//th[@id='cat_lab_Metals']
    Select Checkbox             xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox             xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element               xpath=//th[@id='cat_lab_Microbiology']
    Select Checkbox             xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox             xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox             xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox             xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}

