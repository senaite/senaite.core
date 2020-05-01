# -*- coding: utf-8 -*-

PROFILE_ID = "profile-senaite.core:default"
PROJECTNAME = "senaite.core"

CONTENTS_TO_DELETE = (
    # List of items to delete
    "Members",
    "news",
    "events",
)

GROUPS = [
    {
        "id": "Analysts",
        "title": "Analysts",
        "roles": ["Analyst"],
    }, {
        "id": "Clients",
        "title": "Clients",
        "roles": ["Client"],
    }, {
        "id": "LabClerks",
        "title": "Lab Clerks",
        "roles": ["LabClerk"],
    }, {
        "id": "LabManagers",
        "title": "Lab Managers",
        "roles": ["LabManager"],
    }, {
        "id": "Preservers",
        "title": "Preservers",
        "roles": ["Preserver"],
    }, {
        "id": "Publishers",
        "title": "Publishers",
        "roles": ["Publisher"],
    }, {
        "id": "Verifiers",
        "title": "Verifiers",
        "roles": ["Verifier"],
    }, {
        "id": "Samplers",
        "title": "Samplers",
        "roles": ["Sampler"],
    }, {
        "id": "RegulatoryInspectors",
        "title": "Regulatory Inspectors",
        "roles": ["RegulatoryInspector"],
    }, {
        "id": "SamplingCoordinators",
        "title": "Sampling Coordinator",
        "roles": ["SamplingCoordinator"],
    }
]
