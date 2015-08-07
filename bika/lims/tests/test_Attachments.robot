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

*** Test Cases ***
test Attachments
    Log in                                  test_labmanager         test_labmanager
    Wait until page contains                You are now logged in
    Go to                                   ${PLONEURL}/clients/client-1
    Wait until page contains element        css=body.portaltype-client
    Click Link                              Add
    Wait until page contains                Request new analyses
    Select from dropdown                    ar_0_Contact    Rita
    Select from dropdown                    ar_0_SampleType    Barley
    @{time} =    Get Time                   year month day hour min sec
    Select Date                             ar_0_SamplingDate    @{time}[2]
    Click Element                           cat_lab_Metals
    Select Checkbox                         //input[@title='Calcium']
    Click Button                            Save
    Wait until page contains                created
    Set Selenium Timeout                    2
    ${ar_id} =    Get text                  //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =    Set Variable              ${ar_id.split()[2]}

    go to                                   ${PLONEURL}/clients/client-1/${ar_id}
    click element                           css=.attachments
    ${PATH_TO_TEST} =  run keyword          resource_filename
    Choose File  AttachmentFile_file        ${PATH_TO_TEST}/files/SysmexXS-500i.csv
    Click Button                            Add
    Wait until page contains element        css=.collapsedBlockCollapsible
    click element                           css=.attachments
    Choose File  AttachmentFile_file        ${PATH_TO_TEST}/files/ArenaRPR.csv
    Select from list  Analysis              Calcium
    Click Button                            Add
    Wait until page contains element        css=.collapsedBlockCollapsible
    click element                           css=.attachments
    xpath should match x times              .//input[@class='delAttachmentButton']  2
    click element                           xpath=.//input[@class='delAttachmentButton'][1]
    Wait until page contains element        css=.collapsedBlockCollapsible
    click element                           css=.attachments
    xpath should match x times              .//input[@class='delAttachmentButton']  1






*** Keywords ***

