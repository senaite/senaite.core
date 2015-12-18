*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
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


Test import Horiba Jobin Yvon ICP csv
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    ${PATH_TO_TEST} =  run keyword  resource_filename
    ${cat_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=AnalysisCategory  title=Metals
    ${service_uid} =  Create Object   bika_setup/bika_analysisservices  AnalysisService  s1  title=AL396152  Keyword=Al396152  Category=${cat_uid}
    ${st_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SampleType  title=Bran
    ${sp_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SamplePoint  title=Mill
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}  SamplePoint=${sp_uid}
    do action for  ${ar_uid}  receive
    # import file
    Import Instrument File     Horiba Jobin-Yvon - ICP  ${PATH_TO_TEST}/files/ICPlimstest.csv
    page should contain        Service keyword Ni221647 not found
    page should contain        Import finished successfully: 1 ARs and 1 results updated
    go to    ${PLONEURL}/clients/client-1/BR-0001-R01/manage_results
    textfield value should be        css=[selector="Result_Al396152"]  0.1337

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
