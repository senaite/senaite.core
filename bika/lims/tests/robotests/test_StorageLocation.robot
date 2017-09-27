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

${SITE} =           HAM
${UNIT} =           FZ1
${SHELF} =          S2

*** Test Cases ***

Test Storage Location
    Enable autologin as  LabManager
    Check Bika Setup imported correctly
    Create Setup Location
    Check AR Creation

*** Keywords ***

Check Bika Setup imported correctly
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Page Should Contain         ${SITE}.${UNIT}.${SHELF}

Create Setup Location
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             BIKA  FR1  S3
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Page should contain         BIKA.FR1.S3

Create Location
    [Arguments]  ${centre}  ${unit}  ${shelf}
    Input Text                  title  ${centre}.${unit}.${shelf}
    Input Text                  SiteTitle  BIKA Labs
    Input Text                  SiteCode  BIKA
    Input Text                  SiteDescription  BIKA Labs site in Grabou
    Input Text                  LocationTitle  Freezer ${unit}
    Input Text                  LocationCode  ${unit}
    Input Text                  LocationDescription  Freezer
    Input Text                  LocationType  Freezer
    Input Text                  ShelfTitle  Shelf ${shelf}
    Input Text                  ShelfCode  ${shelf}
    Input Text                  ShelfDescription  Second shelf from bottom
    Click Button                Save
    Wait until page contains    Changes saved.

Check AR Creation
    ${ar_id}=                   Create AR
    Go to                       ${PLONEURL}/clients/client-1/${ar_id}
    Textfield Value Should Be   StorageLocation   ${SITE}.${UNIT}.${SHELF}    Storage location field is not set correctly
    Go to                       ${PLONEURL}/clients/client-1/H2O-0001
    Textfield Value Should Be   StorageLocation   ${SITE}.${UNIT}.${SHELF}    Storage location field is not set correctly

Create AR
    given an ar add form in client-1 with columns layout and 1 ars
    I select Rita from the Contact combogrid in column 0
    I select Water from the SampleType combogrid in column 0
    I select ${SITE}.${UNIT}.${SHELF} from the StorageLocation combogrid in column 0
    Select Date   SamplingDate-0  1
    I expand the lab Water Chemistry category
    I select the Moisture service in column 0
    I expand the lab Metals category
    I select the Calcium service in column 0
    I select the Phosphorus service in column 0
    I expand the lab Microbiology category
    I select the Clostridia service in column 0
    I select the Ecoli service in column 0
    I select the Enterococcus service in column 0
    I select the Salmonella service in column 0
    Click button  Save
    wait until page contains element  xpath=.//dd[contains(text(), 'created')]
    ${dd_text} =  Get text  xpath=.//dd[contains(text(), 'created')]
    ${ar_id} =  Set Variable  ${dd_text.split()[2]}
    [return]  ${ar_id}
