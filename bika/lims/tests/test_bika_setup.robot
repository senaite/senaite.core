*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  bika.lims.tests.base.Keywords

Variables  plone/app/testing/interfaces.py

Suite Setup     Start browser
#Suite Teardown  Close All Browsers

*** Variables ***

${SELENIUM_SPEED}  0

*** Test Cases ***

Setup
    Log in as site owner

    Create LabContact  salutation=Mr
    ...    firstname=Bob
    ...    surname=Dobbs
    ...    email=bob@example.com
    ...    jobtitle=Lab manager

    Create Department  title=Chemistry
    ...    description=Fourth floor
    ...    manager=Bob Dobbs

    Create LabContact  salutation=Mr
    ...    firstname=Analyst
    ...    surname=One
    ...    jobtitle=Assistant manager
    ...    department=Chemistry
    ...    email=analyst1@example.com
    ...    businessphone=021 555 1236
    ...    businessfax=021 555 1233
    ...    homephone=050 866 9887
    ...    mobilephone=083 555 8108

    Create AnalysisCategory  title=Regular Analyses
    ...    description=Regular Analyses, normal priority
    ...    department=Chemistry

    Create AnalysisService  title=Fibre - Crude
    ...    description=Simple crude fiber test
    ...    unit=mg
    ...    keyword=S1
    ...    category=Regular Analyses
    ...    department=Chemistry

    Create AnalysisService  title=Ash
    ...    description=Simple residual weight
    ...    unit=%
    ...    keyword=S2
    ...    category=Regular Analyses
    ...    department=Chemistry

    Create SampleType  title=Apple Pulp
    ...    description=Raw crushed apple
    ...    hazardous=
    ...    samplematrix=
    ...    prefix=AP
    ...    minvol=100 ml
    ...    containertype=

    Create SamplePoint  title=Apple Factory
    ...    description=Loading Bay
    ...    composite=1

    Set SampleType SamplePoints  Apple Pulp
    ...                          Apple Factory

    Create AnalysisProfile  Profile DE
    ...    Contains only a single service
    ...    PDE
    ...    Fibre - Crude

    Create AnalysisTemplate  title=Template DE
    ...    description=DE Profile with an extra partition
    ...    samplepoint=Apple Factory
    ...    sampletype=Apple Pulp
    ...    analysisprofile=Profile DE


*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}

Create LabContact
    [Arguments]  ${salutation}=
    ...          ${firstname}=
    ...          ${surname}=
    ...          ${jobtitle}=
    ...          ${department}=
    ...          ${email}=
    ...          ${businessphone}=
    ...          ${businessfax}=
    ...          ${homephone}=
    ...          ${mobilephone}=
    Go to  http://localhost:55001/plone/bika_setup/bika_labcontacts
    Click link  Add
    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  ${salutation}
    Input Text  Firstname  ${firstname}
    Input Text  Surname  ${surname}
    Input Text  JobTitle  ${jobtitle}
    Select from list  Department:list  ${department}
    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress  ${email}
    Input Text  BusinessPhone  ${businessphone}
    Input Text  BusinessFax  ${businessfax}
    Input Text  HomePhone  ${homephone}
    Input Text  MobilePhone  ${mobilephone}
    Click Button  Save
    Page should contain  ${firstname} ${surname}

Create Department
    [Arguments]  ${title}=
    ...          ${description}=
    ...          ${manager}=
    Go to  http://localhost:55001/plone/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${title}
    Input Text  description  ${description}
    Select from list  Manager:list  ${manager}
    Click Button  Save
    Page should contain  ${title}

Create AnalysisCategory
    [Arguments]  ${title}=
    ...          ${description}=
    ...          ${department}=
    Go to  http://localhost:55001/plone/bika_setup/bika_analysiscategories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${title}
    Input Text  description  ${description}
    Select from list  Department:list  ${department}
    Click Button  Save
    Page should contain  ${title}

Create SampleType
    [Arguments]    ${title}=
    ...            ${description}=
    ...            ${hazardous}=
    ...            ${samplematrix}=
    ...            ${prefix}=
    ...            ${minvol}=
    ...            ${containertype}=
    Go to  http://localhost:55001/plone/bika_setup/bika_sampletypes
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title        ${title}
    Input Text  description  ${description}
    Run Keyword Unless  '${hazardous}' == ''  Select Checkbox  Hazardous
    Run Keyword Unless  '${samplematrix}' == ''  Select from list  SampleMatrix:list  ${samplematrix}
    Input Text  Prefix  ${prefix}
    Input Text  MinimumVolume  ${minvol}
    Run Keyword Unless  '${containertype}' == ''  Select from list  ContainerType:list  ${containertype}
    Click Button  Save
    Page should contain  ${title}

Create SamplePoint
    [Arguments]    ${title}=
    ...            ${description}=
    ...            ${composite}=
    Go to  http://localhost:55001/plone/bika_setup/bika_samplepoints
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title        ${title}
    Input Text  description  ${description}
    Run Keyword Unless  '${composite}' == ''  Select Checkbox  xpath=//*[@id='Composite']
    Click Button  Save
        Page should contain  ${title}

Set SampleType SamplePoints
    [Arguments]    ${sampletype}
    ...            @{samplepoints}
    Go to  http://localhost:55001/plone
    Input Text  searchGadget  ${sampletype}
    sleep  0.5
    Click Link  //a[@title='${sampletype}']
    Wait Until Page Contains  ${sampletype}
    Select From List  SamplePoints:list  @{samplepoints}
    Click Button  Save
    Page should contain  ${sampletype}

Create AnalysisProfile
    [Arguments]    ${title}
    ...            ${description}
    ...            ${profilekey}
    ...            @{services}
    Go to  http://localhost:55001/plone/bika_setup/bika_analysisprofiles
    Click link  Add Profile
    Wait Until Page Contains Element  title
    Input Text  title        ${title}
    Input Text  description  ${description}
    Input Text  ProfileKey   ${profilekey}
    Click Link  Analyses
    :FOR  ${service}  IN  @{services}
      \   Select Checkbox  xpath=//input[@item_title='${service}']
    Click Button  Save
    Page should contain  ${title}

Create AnalysisTemplate
    [Arguments]    ${title}=
    ...            ${description}=
    ...            ${samplepoint}=
    ...            ${sampletype}=
    ...            ${analysisprofile}=
    Go to  http://localhost:55001/plone/bika_setup/bika_artemplates
    Click link  Add Template
    Wait Until Page Contains Element  title
    Input Text  title        ${title}
    Input Text  description  ${description}
    Run Keyword Unless  '${samplepoint}' == ''  Input Text  SamplePoint  ${samplepoint}
    Run Keyword Unless  '${sampletype}' == ''  Input Text  SampleType  ${sampletype}
    Run Keyword Unless  '${analysisprofile}' == ''  Select From List  AnalysisProfile:list  ${analysisprofile}
    Click Button  Save
    Page should contain  ${title}

Set AnalysisTemplate Services
    [Arguments]    ${template}
    ...            @{services}
    Go to  http://localhost:55001/plone
    Input Text  searchGadget  ${template}
    sleep  0.5
    Click Link  //a[@title='${template}']
    Wait Until Page Contains  ${template}
    Click Link  Analyses
    :FOR  ${service}  IN  @{services}
      \   Select Checkbox  xpath=//input[@item_title='${service}']
    Click Button  Save
    Page should contain  ${sampletype}

Create AnalysisService
    [Arguments]    ${title}=
    ...            ${description}=
    ...            ${unit}=
    ...            ${keyword}=
    ...            ${category}=
    ...            ${department}=
    ...            ${price}=10
    ...            ${bulkprice}=10
    ...            ${precision}=3
    ...            ${drymatter}=0

    Go to  http://localhost:55001/plone/bika_setup/bika_analysisservices
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title        ${title}
    Input Text  description  ${description}
    Input Text  Unit         ${unit}
    Input Text  Keyword      ${keyword}
    Input Text  cmfeditions_version_comment  Create
    Input Text  Price        ${price}
    Input Text  BulkPrice    ${bulkprice}
    Input Text  Category     ${category}
    Sleep  0.6s
    Select First Option in Dropdown
    Input Text  Department   ${department}
    Sleep  0.6s
    Select First Option in Dropdown
    Click Link  Analysis
    Input Text  Precision    ${precision}
    Click Button  Save
    Page should contain  ${title}


Select First Option in Dropdown
    Click Element  xpath=//div[contains(@class,'cg-DivItem')]

Log in
    [Arguments]  ${userid}  ${password}

    Go to  http://localhost:55001/plone/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

Log in as test user

    Log in  ${TEST_USER_NAME}  ${TEST_USER_PASSWORD}

Log in as site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Log in as test user with role
    [Arguments]  ${usrid}  ${role}

Log out
    Go to  http://localhost:55001/plone/logout
    Page should contain  logged out
