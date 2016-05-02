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

*** Test Cases ***


Test Nuclisens EasyQ XLSX importer
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    ${PATH_TO_TEST} =  run keyword  resource_filename
    # We need a category so that we can create AnalysisServices.
    ${cat_uid} =  Create Object    bika_setup/bika_analysiscategories  AnalysisCategory  c1  title=Viral
    # We're only going to test the HIV service from the XLSX, because that's all that our sample file contains
    ${service_uid} =  Create Object   bika_setup/bika_analysisservices  AnalysisService  s1  title=EasyQ HIV Service  Keyword=EasyQ HIV-1 v2.0  Category=${cat_uid}
    # Let's make a Plasma sample type
    ${st_uid} =  Create Object   bika_setup/bika_sampletypes  SampleType  ST1  title=Plasma   Prefix=PL
    # And then create a new AR with just the one AnalysisService.
    # We'll set the ClientSampleID to match the first valid result in the XLSX.
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE043
    # The AR and Sample must be received before any results can be added to it.
    do action for  ${ar_uid}  receive
    # import file
    Import Instrument File      Nuclisens EasyQ   ${PATH_TO_TEST}/files/nuclisens.xlsx
    # In the debug statement below, the browser pauses, and we can discover conditions to test for.
    # Only one AR and one result should have been imported!
    page should contain        Import finished successfully: 1 ARs and 1 results updated
    # And we must verify that the result is "710" (the 'cps/ml' part has been removed).
    go to    ${PLONEURL}/clients/client-1/PL-0001-R01/manage_results
    textfield value should be        css=[selector="Result_EasyQ HIV-1 v2.0"]  710 cps/ml

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}

Import Instrument File
    [Documentation]  Select the instrument and file type.
    ...              Then import the file created by the instrument.
    [arguments]  ${instrument}  ${file}
    Go to                       ${PLONEURL}
    Click Link                  Import
    Wait until page contains    Select a data interface
    Select from list            exim  ${instrument}
    # This instrument supports only XLSX!
    Element Should Contain      nuclisens_easyq_format  XLSX
    Choose File                 nuclisens_easyq_file    ${file}
    Click Button                Submit
    Wait until page contains    Log trace