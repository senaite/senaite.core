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
    ${client_uid} =  Create Object   clients  Client   client1  title=Clienty mcClient-Face
    ${cat_uid} =     Create Object   bika_setup/bika_analysiscategories  AnalysisCategory  c1  title=Viral
    ${st_uid} =      Create Object   bika_setup/bika_sampletypes  SampleType  ST1  title=Sample Type   Prefix=S
    ${Interims} =    Evaluate        [{'keyword':'CF', 'title':'Correction Factor', 'value':'', 'unit':'', 'hidden':False, 'wide':False}, {'keyword':'Matrix', 'title':'Matrix', 'value':'', 'unit':'', 'hidden':False, 'wide':False}, {'keyword':'Value', 'title':'Value', 'value':'', 'unit':'', 'hidden':False, 'wide':False}]
    ${calc_uid} =    Create Object   bika_setup/bika_calculations   Calculation   VL   title=Viral Load   InterimFields=${Interims}  Formula="TND" if "TND" in str([Value]) else [Value] if [Matrix] == "Plasma" else [Value] if str([Value]).startswith("<") else [Value] * [CF]

    # We're only going to test the HIV service from the XLSX, because that's all that our sample file contains
    ${service_uid} =  Create Object   bika_setup/bika_analysisservices  AnalysisService  s1  title=EasyQ HIV Service   Keyword=EasyQDirector  Category=${cat_uid}    UseDefaultCalculation=False    DeferredCalculation=${calc_uid}   DetectionLimitSelector=True  AllowManualDetectionLimit=True

    # And then create 16 new ARs.
    # We'll set the ClientSampleID to match the SampleID from the xlsx
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE1
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE2
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE3
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE4
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE5
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE6
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE7
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE8
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE9
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE10
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE11
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE12
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE13
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE14
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE15
    do action for  ${ar_uid}  receive
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}   ClientSampleID=HRE16
    do action for  ${ar_uid}  receive

    # import file
    Import Instrument File      Nuclisens EasyQ   ${PATH_TO_TEST}/files/nuclisens.xlsx
    # In the debug statement below, the browser pauses, and we can discover conditions to test for.
    # Only one AR and one result should have been imported!
    # These are uncalculated values from Value column, just verify they are
    # as expected
    page should contain   S-0001-R01 result for 'EasyQDirector:Value': '10'
    page should contain   S-0002-R01 result for 'EasyQDirector:Value': '99'
    page should contain   S-0003-R01 result for 'EasyQDirector:Value': '100'
    page should contain   S-0004-R01 result for 'EasyQDirector:Value': '182'
    page should contain   S-0005-R01 result for 'EasyQDirector:Value': '1000'
    page should contain   S-0006-R01 result for 'EasyQDirector:Value': '<10'
    page should contain   S-0007-R01 result for 'EasyQDirector:Value': '<100'
    page should contain   S-0008-R01 result for 'EasyQDirector:Value': 'TND'
    page should contain   S-0009-R01 result for 'EasyQDirector:Value': '10'
    page should contain   S-0010-R01 result for 'EasyQDirector:Value': '100'
    page should contain   S-0011-R01 result for 'EasyQDirector:Value': '182'
    page should contain   S-0012-R01 result for 'EasyQDirector:Value': '1000'
    page should contain   S-0013-R01 result for 'EasyQDirector:Value': '<10'
    page should contain   S-0014-R01 result for 'EasyQDirector:Value': '<100'
    page should contain   S-0015-R01 result for 'EasyQDirector:Value': 'TND'

    debug

    # Then verify calculated results in the ARs
    go to    ${PLONEURL}/clients/client-1/S-0001-R01/manage_results
    element should contain   css=[field="formatted_result"]    10
    go to    ${PLONEURL}/clients/client-1/S-0002-R01/manage_results
    element should contain   css=[field="formatted_result"]    99
    go to    ${PLONEURL}/clients/client-1/S-0003-R01/manage_results
    element should contain   css=[field="formatted_result"]    100
    go to    ${PLONEURL}/clients/client-1/S-0004-R01/manage_results
    element should contain   css=[field="formatted_result"]    182
    go to    ${PLONEURL}/clients/client-1/S-0005-R01/manage_results
    element should contain   css=[field="formatted_result"]    1000
    go to    ${PLONEURL}/clients/client-1/S-0006-R01/manage_results
    element should contain   css=[field="formatted_result"]    < 10
    go to    ${PLONEURL}/clients/client-1/S-0007-R01/manage_results
    element should contain   css=[field="formatted_result"]    < 100
    go to    ${PLONEURL}/clients/client-1/S-0008-R01/manage_results
    element should contain   css=[field="formatted_result"]    TND
    go to    ${PLONEURL}/clients/client-1/S-0009-R01/manage_results
    element should contain   css=[field="formatted_result"]    18
    go to    ${PLONEURL}/clients/client-1/S-0010-R01/manage_results
    element should contain   css=[field="formatted_result"]    182
    go to    ${PLONEURL}/clients/client-1/S-0011-R01/manage_results
    element should contain   css=[field="formatted_result"]    331
    go to    ${PLONEURL}/clients/client-1/S-0012-R01/manage_results
    element should contain   css=[field="formatted_result"]    1820
    go to    ${PLONEURL}/clients/client-1/S-0013-R01/manage_results
    element should contain   css=[field="formatted_result"]    < 10
    go to    ${PLONEURL}/clients/client-1/S-0014-R01/manage_results
    element should contain   css=[field="formatted_result"]    < 100
    go to    ${PLONEURL}/clients/client-1/S-0015-R01/manage_results
    element should contain   css=[field="formatted_result"]    TND

*** Keywords ***

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
