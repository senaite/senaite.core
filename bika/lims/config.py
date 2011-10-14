from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList
from bika.lims import bikaMessageFactory as _

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "bika.lims"
SKINS_DIR = 'skins'

GLOBALS = globals()

DEPENDENCIES = [] #['plone.app.iterate']

# Old permissions:
ManageBika = 'BIKA: Manage Bika'
ManageClients = 'BIKA: Manage Clients'
ManageWorksheets = 'BIKA: Manage Worksheets'
ManageOrders = 'BIKA: Manage Orders'
DispatchOrder = 'BIKA: Dispatch Order'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageARImport = 'BIKA: Manage ARImport'
ManageSample = 'BIKA: Manage Sample'
ManageReferenceSuppliers = 'BIKA: Manage Reference Suppliers'
ManageReference = 'BIKA: Manage Reference'
PostInvoiceBatch = 'BIKA: Post Invoice batch'
ManagePricelists = 'BIKA: Manage Pricelists'
# New or changed permissions:
ReceiveSample = 'BIKA: Receive Sample'
ExpireSample = 'BIKA: Expire Sample'
DisposeSample = 'BIKA: Dispose Sample'
ImportAnalysis = 'BIKA: Import Analysis'
RejectWorksheet = 'BIKA: Reject Worksheet'
Retract = "BIKA: Retract"
Verify = 'BIKA: Verify'
VerifyOwnResults = 'BIKA: Verify own results'
Publish = 'BIKA: Publish'
EditSample = 'BIKA: Edit Sample'
EditAR = 'BIKA: Edit AR'
EditWorksheet = 'BIKA: Edit Worksheet'
ManageResults = 'BIKA: Manage Results'
ResultsNotRequested = 'BIKA: Results not requested'
ManageInvoices = 'BIKA: Manage Invoices'
AddAndRemoveAnalyses = 'BIKA: Add and remove Analyses'
ViewResults = 'BIKA: View Results'
EditResults = 'BIKA: Edit Results'
CancelAndReinstate = 'BIKA: Cancel and reinstate'

I18N_DOMAIN = 'bika.lims'

# These types will be auto-versioned.  They will need
# xx_edit.cpt.metadata to be modified in skins.
TYPES_TO_VERSION = ('AnalysisService',
                    'Calculation',
                    'SamplePoint',
                    'SampleType',
                    'AnalysisSpec',
                    'WorksheetTemplate',
                    )

BIKA_PERMISSIONS = (
    (ManageBika, ()),
    (ManageClients, ()),
    (ManageWorksheets, ()),
    (ManageOrders, ()),
    (ManageAnalysisRequests, ()),
    (ManageSample, ()),
    (ManageReferenceSuppliers, ()),
    (ManageReference, ()),
    (ManagePricelists, ()),
    (ManageARImport, ()),
    (DispatchOrder, ()),
    (PostInvoiceBatch, ()),
    (ReceiveSample, ()),
    (ExpireSample, ()),
    (DisposeSample, ()),
    (ImportAnalysis, ()),
    (RejectWorksheet, ()),
    (Retract, ()),
    (Verify, ()),
    (VerifyOwnResults, ()),
    (Publish, ()),
    (EditSample, ()),
    (EditAR, ()),
    (EditWorksheet, ()),
    (ManageResults, ()),
    (ResultsNotRequested, ()),
    (ManageInvoices, ()),
    (AddAndRemoveAnalyses, ()),
    (ViewResults, ()),
    (EditResults, ()),
    (CancelAndReinstate, ()),
)


PUBLICATION_PREFS = DisplayList((
    ('email', _('Email')),
    ('fax', _('Fax')),
    ('file', _('File')),
    ('pdf', _('PDF')),
    ('print', _('Print')),
    ('sms', _('SMS')),
))

POINTS_OF_CAPTURE = DisplayList((
    ('field', _('Field Analyses')),
    ('lab', _('Lab Analyses')),
))

SERVICE_POINT_OF_CAPTURE = DisplayList((
    ('field', _('Field')),
    ('lab', _('Lab')),
))

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', _('Analysis services')),
    ('LabProduct', _('Lab products')),
))

CLIENT_TYPES = DisplayList((
    ('corporate', 'Bulk Discount'),
    ('noncorporate', 'Standard Price'),
))

ANALYSIS_TYPES = DisplayList((
    ('a', _('Analysis')),
    ('b', _('Blank')),
    ('c', _('Control')),
    ('d', _('Duplicate')),
))
STD_TYPES = DisplayList((
    ('c', _('Control')),
    ('b', _('Blank')),
))
ATTACHMENT_OPTIONS = DisplayList((
    ('r', _('Required')),
    ('p', _('Permitted')),
    ('n', _('Not Permitted')),
))
ARIMPORT_OPTIONS = DisplayList((
    ('c', _('Classic')),
    ('p', _('Profiles')),
    ('s', _('Special')),
))
EMAIL_SUBJECT_OPTIONS = DisplayList((
    ('ar', _('Analysis Request ID')),
    ('co', _('Order ID')),
    ('cr', _('Client Reference')),
    ('cs', _('Client Sample ID')),
))
INSTRUMENT_EXPORTS = DisplayList((
    ('instrument1', _('Instrument 1')),
    ('instrument2', _('Instrument 2')),
    ('instrument3', _('Instrument 3')),
))

INSTRUMENT_IMPORTS = DisplayList((
    ('instrument1', _('Instrument 1')),
    ('instrument2', _('Instrument 2')),
    ('instrument3', _('Instrument 3')),
))

GENDERS = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ))

ADDRESS_TYPES = DisplayList((
    ('physical', _('Physical address')),
    ('mailing', _('Mailing address')),
    ('billing', _('Billing address')),
    ('shipping', _('Shipping address')),
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

