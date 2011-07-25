from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "bika.lims"
SKINS_DIR = 'skins'

GLOBALS = globals()

ManageBika = 'BIKA: Manage Bika'
ManageClients = 'BIKA: Manage Clients'
ManageWorksheets = 'BIKA: Manage Worksheets'
ManageOrders = 'BIKA: Manage Orders'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageSample = 'BIKA: Manage Sample'
ManageReferenceSuppliers = 'BIKA: Manage Reference Suppliers'
ManageReference = 'BIKA: Manage Reference'
ManageInvoices = 'BIKA: Manage Invoices'
ManagePricelists = 'BIKA: Manage Pricelists'
ViewMethods = 'BIKA: View Methods'
EditAnalyses = 'BIKA: Edit analyses'
ViewResults = 'BIKA: View Results'
ManageARImport = 'BIKA: Manage ARImport'

# Workflow permissions
ReceiveSample = 'BIKA: Receive sample'
SubmitSample = 'BIKA: Submit sample'
VerifySample = 'BIKA: Verify sample'
PublishSample = 'BIKA: Publish sample'
RetractSample = 'BIKA: Retract sample'
ImportSample = 'BIKA: Import sample'

SubmitWorksheet = 'BIKA: Submit Worksheet'
VerifyWorksheet = 'BIKA: Verify Worksheet'
RetractWorksheet = 'BIKA: Retract Worksheet'

DispatchOrder = 'BIKA: Dispatch Order'

PostInvoiceBatch = 'BIKA: Post Invoice batch'

# Worksheet permissions
AssignAnalyses = 'BIKA: Assign analyses'
DeleteAnalyses = 'BIKA: Delete analyses'
SubmitResults = 'BIKA: Submit results'

I18N_DOMAIN = 'bika'

BIKA_PERMISSIONS = (
    (ManageBika, ()),
    (ManageClients, ()),
    (ManageWorksheets, ()),
    (ManageOrders, ()),
    (ManageAnalysisRequests, ()),
    (ManageSample, ()),
    (ManageReferenceSuppliers, ()),
    (ManageReference, ()),
    (EditAnalyses, ()),
    (ViewResults, ()),
    (ViewMethods, ()),
    (ReceiveSample, ()),
    (SubmitSample, ()),
    (VerifySample, ()),
    (PublishSample, ()),
    (RetractSample, ()),
    (ImportSample, ()),
    (ManageARImport, ()),
    (SubmitWorksheet, ()),
    (VerifyWorksheet, ()),
    (RetractWorksheet, ()),
    (DispatchOrder, ()),
    (DeleteAnalyses, ()),
    (SubmitResults, ()),
)

PUBLICATION_PREFS = DisplayList((
    ('email', 'Email'),
    ('fax', 'Fax'),
    ('file', 'File'),
    ('pdf', 'PDF'),
    ('print', 'Print'),
    ('sms', 'SMS'),
))

POINTS_OF_CAPTURE = DisplayList((
    ('field', 'Field Analyses'),
    ('lab', 'Lab Analyses'),
))

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', 'Analysis services'),
    ('LabProduct', 'Lab products'),
))

CLIENT_TYPES = DisplayList((
    ('corporate', 'Corporate'),
    ('noncorporate', 'Non Corporate'),
))

ANALYSIS_TYPES = DisplayList((
    ('a', 'Analysis'),
    ('b', 'Blank'),
    ('c', 'Control'),
    ('d', 'Duplicate'),
))
STD_TYPES = DisplayList((
    ('c', 'Control'),
    ('b', 'Blank'),
))
ATTACHMENT_OPTIONS = DisplayList((
    ('r', 'Required'),
    ('p', 'Permitted'),
    ('n', 'Not Permitted'),
))
ARIMPORT_OPTIONS = DisplayList((
    ('c', 'Classic'),
    ('p', 'Profiles'),
    ('s', 'Special'),
))
EMAIL_SUBJECT_OPTIONS = DisplayList((
    ('ar', 'Analysis Request ID'),
    ('co', 'Order ID'),
    ('cr', 'Client Reference'),
    ('cs', 'Client Sample ID'),
))
INSTRUMENT_EXPORTS = DisplayList((
    ('instrument1', 'Instrument 1'),
    ('instrument2', 'Instrument 2'),
    ('instrument3', 'Instrument 3'),
))

INSTRUMENT_IMPORTS = DisplayList((
    ('instrument1', 'Instrument 1'),
    ('instrument2', 'Instrument 2'),
    ('instrument3', 'Instrument 3'),
))

GENDERS = DisplayList((
    ('male', 'Male'),
    ('female', 'Female'),
    ))

ADDRESS_TYPES = DisplayList((
    ('physical', 'Physical address'),
    ('mailing', 'Mailing address'),
    ('billing', 'Billing address'),
    ('shipping', 'Shipping address'),
    ))

countries = [(x, x) for x in (
    "Unspecified",
    "Afghanistan",
    "Albania",
    "Algeria",
    "American Samoa",
    "Andorra",
    "Angola",
    "Anguilla",
    "Antarctica",
    "Antigua Barbuda",
    "Argentina",
    "Armenia",
    "Aruba",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bosnia Herzegovina",
    "Botswana",
    "Bouvet Island",
    "Brazil",
    "British Indian Ocean Territory",
    "Brunei Darussalam",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Cayman Islands",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Christmas Island",
    "Cocos (Keeling) Islands",
    "Colombia",
    "Comoros",
    "Congo",
    "Congo, Democratic Republic",
    "Cook Islands",
    "Costa Rica",
    "Cote D'Ivoire",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Ethiopia",
    "Falkland Islands (Malvinas)",
    "Faroe Islands",
    "Fiji",
    "Finland",
    "France",
    "French Guiana",
    "French Polynesia",
    "French Southern Territories",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Gibraltar",
    "Greece",
    "Greenland",
    "Grenada",
    "Guadeloupe",
    "Guam",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Heard Island Mcdonald Islands",
    "Holy See (Vatican City State)",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran, Islamic Republic",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea, Democratic People's Republic",
    "Korea, Republic",
    "Kuwait",
    "Kyrgyzstan",
    "Lao People's Democratic Republic",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libyan Arab Jamahiriya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Macao",
    "Macedonia, Former Yugoslav Republic",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Martinique",
    "Mauritania",
    "Mauritius",
    "Mayotte",
    "Mexico",
    "Micronesia, Federated States",
    "Moldova, Republic",
    "Monaco",
    "Mongolia",
    "Montserrat",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "Netherlands Antilles",
    "New Caledonia",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "Niue",
    "Norfolk Island",
    "Northern Mariana Islands",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestinian Territory, Occupied",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Pitcairn",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Reunion",
    "Romania",
    "Russian Federation",
    "Rwanda",
    "Saint Helena",
    "Saint Kitts Nevis",
    "Saint Lucia",
    "Saint Pierre Miquelon",
    "Saint Vincent Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia Montenegro",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Georgia South Sandwich Islands",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Svalbard Jan Mayen",
    "Swaziland",
    "Sweden",
    "Switzerland",
    "Syrian Arab Republic",
    "Taiwan, Province China",
    "Tajikistan",
    "Tanzania, United Republic",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tokelau",
    "Tonga",
    "Trinidad Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Turks Caicos Islands",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "United States Minor Outlying Islands",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Vietnam",
    "Virgin Islands, British",
    "Virgin Islands, U.S.",
    "Wallis Futuna",
    "Western Sahara",
    "Yemen",
    "Zambia",
    "Zimbabwe")]

COUNTRY_NAMES = DisplayList(countries)

