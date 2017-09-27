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

Test sampleprep_simple workflow - straight through
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    Write AT Field values   bika_setup   AutoPrintStickers=None
    ${PATH_TO_TEST} =  run keyword  resource_filename
    ${cat_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=AnalysisCategory  title=Metals
    ${service_uid} =  Create Object   bika_setup/bika_analysisservices  AnalysisService  s1  title=AL396152  Keyword=Al396152  Category=${cat_uid}
    ${st_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SampleType  title=Bran
    ${sp_uid} =  Get UID  catalog_name=bika_setup_catalog  portal_type=SamplePoint  title=Mill
    ${ar_uid} =  Create AR  /clients/client-1  analyses=${service_uid}  SampleType=${st_uid}  SamplePoint=${sp_uid}  PreparationWorkflow=sampleprep_simple

    # transition: Recieve.  SHould kick off the SamplePrep workflow.
    do action for  ${ar_uid}  receive
    go to   ${PLONEURL}/clients/client-1/BR-0001-R01/manage_results
    Page should contain    State: Sample Preparation (Pending)

    do action for  ${ar_uid}  complete
    go to   ${PLONEURL}/clients/client-1/BR-0001-R01/manage_results
    Page should contain    State: Received

*** Keywords ***
