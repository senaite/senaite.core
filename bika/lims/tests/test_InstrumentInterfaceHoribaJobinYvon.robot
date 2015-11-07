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
${ASId} =  Ni
${ASTitle} =  Ni
${ClientSampleId} =  QC 350 PPM

*** Test Cases ***


LIMS-2042 import ICP csv using entire linename for Keyword
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    ${PATH_TO_TEST} =  run keyword  resource_filename
    ${cat_uid} =  getUID  catalog_name=bika_setup_catalog  portal_type=AnalysisCategory  title=Metals
    ${service_uid} =  createObject   bika_setup/bika_analysisservices  AnalysisService  s1  title=AL396152  Keyword=Al396152  Category=${cat_uid}
    debug
    ${st_uid} =  getUID  catalog_name=bika_setup_catalog  portal_type=SampleType  title=Bran
    ${sp_uid} =  getUID  catalog_name=bika_setup_catalog  portal_type=SamplePoint  title=Mill
    ${ar_uid} =  createAR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}  SamplePoint=${sp_uid}
    doActionFor  ${ar_uid}  receive
    # import file
    Import Instrument File     Horiba Jobin-Yvon - ICP  ${PATH_TO_TEST}/files/ICPlimstest.csv
    page should not contain    Service keyword Al396152 not found

ICP csv file
    [Documentation]  Firts we have to create the AS to match the
    ...              analysis in the file. Then we have to create the AR
    ...              and tranistion it. Finally qe can import the results.
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    ${PATH_TO_TEST} =           run keyword   resource_filename
    ${cat_uid} =  getUID  catalog_name=bika_setup_catalog  portal_type=AnalysisCategory  title=Metals
    ${service_uid} =  createObject   bika_setup/bika_analysisservices  AnalysisService  s1  title=Ni221647  Keyword=Ni221647  Category=${cat_uid}
    Import Instrument File     Horiba Jobin-Yvon - ICP  ${PATH_TO_TEST}/files/ICPlimstest.csv
    page should not contain    Service keyword Ni221647 not found

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

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

Import Instrument File
    [Documentation]  Select the instrument and file type.
    ...              Then import the file created by the instrument.
    [arguments]  ${instrument}  ${file}
    Go to                       ${PLONEURL}
    Click Link                  Import
    Wait until page contains    Select a data interface
    Select from list            exim  ${instrument}
    Element Should Contain      format  CSV
    Import AR Results Instrument File    ${file}  data_file

Import AR Results Instrument File
    [Documentation]  Import the file from test files folder, and submit it.
    [arguments]                 ${file}
    ...                         ${input_identifier}
    Choose File                 ${input_identifier}  ${file}
    Click Button                Submit
    Wait until page contains    Log trace
