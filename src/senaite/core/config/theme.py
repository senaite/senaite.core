# -*- coding: utf-8 -*-

import json
from string import Template

STATIC_URL = "++plone++senaite.core.static"
ICON_BASE_URL = "{}/assets/svg".format(STATIC_URL)

VARIABLES = {
    "icon_base_url": ICON_BASE_URL,
}

TEMPLATE = {
    "icons": {
        "AnalysisRequest": "$icon_base_url/sample.svg",
        "AnalysisService": "$icon_base_url/analysisservice.svg",
        "Method": "$icon_base_url/method.svg",
        "Sample": "$icon_base_url/sample.svg",
        "add": "$icon_base_url/plus-circle.svg",
        "delete": "$icon_base_url/trashcan.svg",
        "hazardous": "$icon_base_url/hazardous.svg",
        "invoice_exclude": "$icon_base_url/invoice_exclude.svg",
        "retest": "$icon_base_url/retest.svg",
        "warning": "$icon_base_url/warning.svg",
    }
}

CONFIG_JSON = Template(json.dumps(TEMPLATE)).safe_substitute(**VARIABLES)
CONFIG = json.loads(CONFIG_JSON)
