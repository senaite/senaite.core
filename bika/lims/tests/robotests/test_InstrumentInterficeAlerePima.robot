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
${input_identifier1} =  alere_pima_beads
${ASId1} =  3
${ASTitle1} =  PIMA BEADS
${ClientSampleId1} =  LOW

${input_identifier2} =  alere_pima_cd4
${ASId2} =  2
${ASTitle2} =  PIMA CD4
${ClientSampleId2} =  10001
*** Test Cases ***

Import a slk Beads file
    [Documentation]  Firts we have to create the AS to match the
    ...              analysis in the file. Then we have to create the AR
    ...              and tranistion it. Finally qe can import the results.
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Create Analysis Service  ${ASId1}  ${ASTitle1}
    ${ar_id}=                Create an AR  ${ASTitle1}  ${ClientSampleId1}
    Execute transition receive on item ${ar_id} in ARList
    Import Instrument File     Alere Pima Beads  ${PATH_TO_TEST}/files/AssayID_3_PIMA BEADS_Lite.slk  ${input_identifier1}
    page should contain        ${ar_id}: ['Analysis 3'] imported sucessfully
    page should contain        No analyses 'sampled, sample_received, attachment_due, to_be_verified' states found for NORMAL

Import a slk CD4 file
    [Documentation]  Firts we have to create the AS to match the
    ...              analysis in the file. Then we have to create the AR
    ...              and tranistion it. Finally qe can import the results.
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    ${PATH_TO_TEST} =           run keyword   resource_filename
    Create Analysis Service  ${ASId2}  ${ASTitle2}
    ${ar_id}=                Create an AR  ${ASTitle2}  ${ClientSampleId2}
    Execute transition receive on item ${ar_id} in ARList
    Import Instrument File     Alere Pima CD4  ${PATH_TO_TEST}/files/AssayID_2_PIMA CD4.slk  ${input_identifier2}
    page should contain        ${ar_id}: ['Analysis 2'] imported sucessfully
    page should contain        No analyses 'sampled, sample_received, attachment_due, to_be_verified' states found for


*** Keywords ***

Create Analysis Service
   [Documentation]  Create an AS using the ID ASId
   [Arguments]  ${ASId}
   ...          ${ASTitle1}
    Go to                       ${PLONEURL}/bika_setup/bika_analysisservices
    Wait until page contains element    css=h1
    Click link                  link=Add
    Wait until page contains element  title
    Input text                  title  ${ASTitle1}
    Input text                  ShortTitle  ${ASId}
    Input text                  Keyword  ${ASId}
    Select from dropdown        Category  Microbiology
    Click button                Save
    Wait until page contains    Changes saved.

Create an AR
   [Arguments]  ${ASTitle}
   ...          ${ClientSampleId}
    @{time} =                   Get Time        year month day hour min sec
    go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    click link                  link=Add
    Select from dropdown        ar_0_Contact                Rita
    SelectDate                  ar_0_SamplingDate           @{time}[2]
    Select from dropdown        ar_0_SampleType             Bran
    Input text                  ar_0_ClientSampleID         ${ClientSampleId}
    Set Selenium Timeout        30
    click element               xpath=.//th[@id="cat_lab_Microbiology"]
    Select checkbox             xpath=//input[@title='${ASTitle}']
    Click Button                Save
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [Return]                    ${ar_id}

Import Instrument File
    [Documentation]  Select the instrument and file type.
    ...              Then import the file created by the instrument.
    [arguments]  ${instrument}  ${file}  ${input_identifier}

    Click Link                  Import
    Wait until page contains    Select a data interface
    Select from list            exim  ${instrument}
    Element Should Contain      ${input_identifier}_format  SLK
    Import AR Results Instrument File    ${file}  ${input_identifier}_file

Import AR Results Instrument File
    [Documentation]  Import the file from test files folder, and submit it.
    [arguments]                 ${file}
    ...                         ${input_identifier}
    Choose File                 ${input_identifier}  ${file}
    Click Button                Submit
    Wait until page contains    Log trace
