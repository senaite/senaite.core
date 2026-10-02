// packages/core/src/js/data.ts
var rawCountryData = [
  [
    "af",
    // Afghanistan
    "93",
    0,
    null,
    "0"
  ],
  [
    "ax",
    // Åland Islands (AKA Aland Islands)
    "358",
    1,
    ["18", "4", "50"],
    // (4 and 50 are mobile ranges shared with FI)
    // NOTE: https://en.wikipedia.org/wiki/Telephone%20numbers%20in%20%C3%85land says some 4XXX ranges (e.g. 4570) are specific to AX, but LPN doesn't respect this (https://libphonenumber.appspot.com/phonenumberparser?number=%2B3584570123456 says region=FI) so we won't either. Also it's too much of a maintenance burden to keep track of. Keep the 4 area code range here so that if the user selects AX and types this kind of number, we wont change the flag to FI. Whereas if they type a FI-only range then we will.
    "0"
  ],
  [
    "al",
    // Albania
    "355",
    0,
    null,
    "0"
  ],
  [
    "dz",
    // Algeria
    "213",
    0,
    null,
    "0"
  ],
  [
    "as",
    // American Samoa
    "1",
    5,
    ["684"],
    "1"
  ],
  [
    "ad",
    // Andorra
    "376"
  ],
  [
    "ao",
    // Angola
    "244"
  ],
  [
    "ai",
    // Anguilla
    "1",
    6,
    ["264"],
    "1"
  ],
  [
    "ag",
    // Antigua and Barbuda
    "1",
    7,
    ["268"],
    "1"
  ],
  [
    "ar",
    // Argentina
    "54",
    0,
    null,
    "0"
  ],
  [
    "am",
    // Armenia
    "374",
    0,
    null,
    "0"
  ],
  [
    "aw",
    // Aruba
    "297"
  ],
  [
    "ac",
    // Ascension Island
    "247"
  ],
  [
    "au",
    // Australia
    "61",
    0,
    ["4"],
    // (mobile range shared with CX and CC)
    "0"
  ],
  [
    "at",
    // Austria
    "43",
    0,
    null,
    "0"
  ],
  [
    "az",
    // Azerbaijan
    "994",
    0,
    null,
    "0"
  ],
  [
    "bs",
    // Bahamas
    "1",
    8,
    ["242"],
    "1"
  ],
  [
    "bh",
    // Bahrain
    "973"
  ],
  [
    "bd",
    // Bangladesh
    "880",
    0,
    null,
    "0"
  ],
  [
    "bb",
    // Barbados
    "1",
    9,
    ["246"],
    "1"
  ],
  [
    "by",
    // Belarus
    "375",
    0,
    null,
    "8"
  ],
  [
    "be",
    // Belgium
    "32",
    0,
    null,
    "0"
  ],
  [
    "bz",
    // Belize
    "501"
  ],
  [
    "bj",
    // Benin
    "229"
  ],
  [
    "bm",
    // Bermuda
    "1",
    10,
    ["441"],
    "1"
  ],
  [
    "bt",
    // Bhutan
    "975"
  ],
  [
    "bo",
    // Bolivia
    "591",
    0,
    null,
    "0"
  ],
  [
    "ba",
    // Bosnia and Herzegovina
    "387",
    0,
    null,
    "0"
  ],
  [
    "bw",
    // Botswana
    "267"
  ],
  [
    "br",
    // Brazil
    "55",
    0,
    null,
    "0"
  ],
  [
    "io",
    // British Indian Ocean Territory
    "246"
  ],
  [
    "vg",
    // British Virgin Islands
    "1",
    11,
    ["284"],
    "1"
  ],
  [
    "bn",
    // Brunei
    "673"
  ],
  [
    "bg",
    // Bulgaria
    "359",
    0,
    null,
    "0"
  ],
  [
    "bf",
    // Burkina Faso
    "226"
  ],
  [
    "bi",
    // Burundi
    "257"
  ],
  [
    "kh",
    // Cambodia
    "855",
    0,
    null,
    "0"
  ],
  [
    "cm",
    // Cameroon
    "237"
  ],
  [
    "ca",
    // Canada
    "1",
    1,
    [
      "204",
      "226",
      "236",
      "249",
      "250",
      "257",
      "263",
      "289",
      "306",
      "343",
      "354",
      "365",
      "367",
      "368",
      "382",
      "403",
      "416",
      "418",
      "428",
      "431",
      "437",
      "438",
      "450",
      "468",
      "474",
      "506",
      "514",
      "519",
      "548",
      "579",
      "581",
      "584",
      "587",
      "604",
      "613",
      "639",
      "647",
      "672",
      "683",
      "705",
      "709",
      "742",
      "753",
      "778",
      "780",
      "782",
      "807",
      "819",
      "825",
      "867",
      "873",
      "879",
      "902",
      "905",
      "942"
    ],
    "1"
  ],
  [
    "cv",
    // Cape Verde
    "238"
  ],
  [
    "bq",
    // Caribbean Netherlands
    "599",
    1,
    ["3", "4", "7"]
  ],
  [
    "ky",
    // Cayman Islands
    "1",
    12,
    ["345"],
    "1"
  ],
  [
    "cf",
    // Central African Republic
    "236"
  ],
  [
    "td",
    // Chad
    "235"
  ],
  [
    "cl",
    // Chile
    "56"
  ],
  [
    "cn",
    // China
    "86",
    0,
    null,
    "0"
  ],
  [
    "cx",
    // Christmas Island
    "61",
    2,
    ["4", "89164"],
    // (4 is a mobile range shared with AU and CC)
    "0"
  ],
  [
    "cc",
    // Cocos (Keeling) Islands
    "61",
    1,
    ["4", "89162"],
    // (4 is a mobile range shared with AU and CX)
    "0"
  ],
  [
    "co",
    // Colombia
    "57",
    0,
    null,
    "0"
  ],
  [
    "km",
    // Comoros
    "269"
  ],
  [
    "cg",
    // Congo (Brazzaville)
    "242"
  ],
  [
    "cd",
    // Congo (Kinshasa)
    "243",
    0,
    null,
    "0"
  ],
  [
    "ck",
    // Cook Islands
    "682"
  ],
  [
    "cr",
    // Costa Rica
    "506"
  ],
  [
    "ci",
    // Côte d'Ivoire
    "225"
  ],
  [
    "hr",
    // Croatia
    "385",
    0,
    null,
    "0"
  ],
  [
    "cu",
    // Cuba
    "53",
    0,
    null,
    "0"
  ],
  [
    "cw",
    // Curaçao
    "599",
    0
  ],
  [
    "cy",
    // Cyprus
    "357"
  ],
  [
    "cz",
    // Czech Republic
    "420"
  ],
  [
    "dk",
    // Denmark
    "45"
  ],
  [
    "dj",
    // Djibouti
    "253"
  ],
  [
    "dm",
    // Dominica
    "1",
    13,
    ["767"],
    "1"
  ],
  [
    "do",
    // Dominican Republic
    "1",
    2,
    ["809", "829", "849"],
    "1"
  ],
  [
    "ec",
    // Ecuador
    "593",
    0,
    null,
    "0"
  ],
  [
    "eg",
    // Egypt
    "20",
    0,
    null,
    "0"
  ],
  [
    "sv",
    // El Salvador
    "503"
  ],
  [
    "gq",
    // Equatorial Guinea
    "240"
  ],
  [
    "er",
    // Eritrea
    "291",
    0,
    null,
    "0"
  ],
  [
    "ee",
    // Estonia
    "372"
  ],
  [
    "sz",
    // Eswatini
    "268"
  ],
  [
    "et",
    // Ethiopia
    "251",
    0,
    null,
    "0"
  ],
  [
    "fk",
    // Falkland Islands (Malvinas)
    "500"
  ],
  [
    "fo",
    // Faroe Islands
    "298"
  ],
  [
    "fj",
    // Fiji
    "679"
  ],
  [
    "fi",
    // Finland
    "358",
    0,
    ["4", "50"],
    // (mobile ranges shared with AX)
    "0"
  ],
  [
    "fr",
    // France
    "33",
    0,
    null,
    "0"
  ],
  [
    "gf",
    // French Guiana
    "594",
    0,
    null,
    "0"
  ],
  [
    "pf",
    // French Polynesia
    "689"
  ],
  [
    "ga",
    // Gabon
    "241"
  ],
  [
    "gm",
    // Gambia
    "220"
  ],
  [
    "ge",
    // Georgia
    "995",
    0,
    null,
    "0"
  ],
  [
    "de",
    // Germany
    "49",
    0,
    null,
    "0"
  ],
  [
    "gh",
    // Ghana
    "233",
    0,
    null,
    "0"
  ],
  [
    "gi",
    // Gibraltar
    "350"
  ],
  [
    "gr",
    // Greece
    "30"
  ],
  [
    "gl",
    // Greenland
    "299"
  ],
  [
    "gd",
    // Grenada
    "1",
    14,
    ["473"],
    "1"
  ],
  [
    "gp",
    // Guadeloupe
    "590",
    0,
    null,
    "0"
  ],
  [
    "gu",
    // Guam
    "1",
    15,
    ["671"],
    "1"
  ],
  [
    "gt",
    // Guatemala
    "502"
  ],
  [
    "gg",
    // Guernsey
    "44",
    1,
    //* Only 79111 and 79117 belong to GG - the rest of 7911 is GB (e.g. 79110).
    ["1481", "7781", "7839", "79111", "79117"],
    "0"
  ],
  [
    "gn",
    // Guinea
    "224"
  ],
  [
    "gw",
    // Guinea-Bissau
    "245"
  ],
  [
    "gy",
    // Guyana
    "592"
  ],
  [
    "ht",
    // Haiti
    "509"
  ],
  [
    "hn",
    // Honduras
    "504"
  ],
  [
    "hk",
    // Hong Kong SAR China
    "852"
  ],
  [
    "hu",
    // Hungary
    "36",
    0,
    null,
    "06"
  ],
  [
    "is",
    // Iceland
    "354"
  ],
  [
    "in",
    // India
    "91",
    0,
    null,
    "0"
  ],
  [
    "id",
    // Indonesia
    "62",
    0,
    null,
    "0"
  ],
  [
    "ir",
    // Iran
    "98",
    0,
    null,
    "0"
  ],
  [
    "iq",
    // Iraq
    "964",
    0,
    null,
    "0"
  ],
  [
    "ie",
    // Ireland
    "353",
    0,
    null,
    "0"
  ],
  [
    "im",
    // Isle of Man
    "44",
    2,
    ["1624", "74576", "7524", "7624", "7924"],
    "0"
  ],
  [
    "il",
    // Israel
    "972",
    0,
    null,
    "0"
  ],
  [
    "it",
    // Italy
    "39",
    0,
    ["3"]
    // (mobile range shared with VA)
  ],
  [
    "jm",
    // Jamaica
    "1",
    4,
    ["658", "876"],
    "1"
  ],
  [
    "jp",
    // Japan
    "81",
    0,
    null,
    "0"
  ],
  [
    "je",
    // Jersey
    "44",
    3,
    //* Only 77003/77007/77008 belong to JE - the rest of 7700 is GB (e.g. 77001).
    ["1534", "7509", "77003", "77007", "77008", "7797", "7829", "7937"],
    "0"
  ],
  [
    "jo",
    // Jordan
    "962",
    0,
    null,
    "0"
  ],
  [
    "kz",
    // Kazakhstan
    "7",
    1,
    ["33", "7"],
    // (33 is shared with RU)
    "8"
  ],
  [
    "ke",
    // Kenya
    "254",
    0,
    null,
    "0"
  ],
  [
    "ki",
    // Kiribati
    "686",
    0,
    null,
    "0"
  ],
  [
    "xk",
    // Kosovo
    "383",
    0,
    null,
    "0"
  ],
  [
    "kw",
    // Kuwait
    "965"
  ],
  [
    "kg",
    // Kyrgyzstan
    "996",
    0,
    null,
    "0"
  ],
  [
    "la",
    // Laos
    "856",
    0,
    null,
    "0"
  ],
  [
    "lv",
    // Latvia
    "371"
  ],
  [
    "lb",
    // Lebanon
    "961",
    0,
    null,
    "0"
  ],
  [
    "ls",
    // Lesotho
    "266"
  ],
  [
    "lr",
    // Liberia
    "231",
    0,
    null,
    "0"
  ],
  [
    "ly",
    // Libya
    "218",
    0,
    null,
    "0"
  ],
  [
    "li",
    // Liechtenstein
    "423",
    0,
    null,
    "0"
  ],
  [
    "lt",
    // Lithuania
    "370",
    0,
    null,
    "0"
  ],
  [
    "lu",
    // Luxembourg
    "352"
  ],
  [
    "mo",
    // Macao SAR China
    "853"
  ],
  [
    "mg",
    // Madagascar
    "261",
    0,
    null,
    "0"
  ],
  [
    "mw",
    // Malawi
    "265",
    0,
    null,
    "0"
  ],
  [
    "my",
    // Malaysia
    "60",
    0,
    null,
    "0"
  ],
  [
    "mv",
    // Maldives
    "960"
  ],
  [
    "ml",
    // Mali
    "223"
  ],
  [
    "mt",
    // Malta
    "356"
  ],
  [
    "mh",
    // Marshall Islands
    "692",
    0,
    null,
    "1"
  ],
  [
    "mq",
    // Martinique
    "596",
    0,
    null,
    "0"
  ],
  [
    "mr",
    // Mauritania
    "222"
  ],
  [
    "mu",
    // Mauritius
    "230"
  ],
  [
    "yt",
    // Mayotte
    "262",
    1,
    ["2689", "269", "639", "7093"],
    "0"
  ],
  [
    "mx",
    // Mexico
    "52"
  ],
  [
    "fm",
    // Micronesia
    "691"
  ],
  [
    "md",
    // Moldova
    "373",
    0,
    null,
    "0"
  ],
  [
    "mc",
    // Monaco
    "377",
    0,
    null,
    "0"
  ],
  [
    "mn",
    // Mongolia
    "976",
    0,
    null,
    "0"
  ],
  [
    "me",
    // Montenegro
    "382",
    0,
    null,
    "0"
  ],
  [
    "ms",
    // Montserrat
    "1",
    16,
    ["664"],
    "1"
  ],
  [
    "ma",
    // Morocco
    "212",
    0,
    ["6", "7"],
    // (mobile ranges shared with EH)
    "0"
  ],
  [
    "mz",
    // Mozambique
    "258"
  ],
  [
    "mm",
    // Myanmar (Burma)
    "95",
    0,
    null,
    "0"
  ],
  [
    "na",
    // Namibia
    "264",
    0,
    null,
    "0"
  ],
  [
    "nr",
    // Nauru
    "674"
  ],
  [
    "np",
    // Nepal
    "977",
    0,
    null,
    "0"
  ],
  [
    "nl",
    // Netherlands
    "31",
    0,
    null,
    "0"
  ],
  [
    "nc",
    // New Caledonia
    "687"
  ],
  [
    "nz",
    // New Zealand
    "64",
    0,
    null,
    "0"
  ],
  [
    "ni",
    // Nicaragua
    "505"
  ],
  [
    "ne",
    // Niger
    "227"
  ],
  [
    "ng",
    // Nigeria
    "234",
    0,
    null,
    "0"
  ],
  [
    "nu",
    // Niue
    "683"
  ],
  [
    "nf",
    // Norfolk Island
    "672"
  ],
  [
    "kp",
    // North Korea
    "850",
    0,
    null,
    "0"
  ],
  [
    "mk",
    // North Macedonia
    "389",
    0,
    null,
    "0"
  ],
  [
    "mp",
    // Northern Mariana Islands
    "1",
    17,
    ["670"],
    "1"
  ],
  [
    "no",
    // Norway
    "47",
    0,
    ["4", "9"]
    // (mobile ranges shared with SJ)
  ],
  [
    "om",
    // Oman
    "968"
  ],
  [
    "pk",
    // Pakistan
    "92",
    0,
    null,
    "0"
  ],
  [
    "pw",
    // Palau
    "680"
  ],
  [
    "ps",
    // Palestinian Territories
    "970",
    0,
    null,
    "0"
  ],
  [
    "pa",
    // Panama
    "507"
  ],
  [
    "pg",
    // Papua New Guinea
    "675"
  ],
  [
    "py",
    // Paraguay
    "595",
    0,
    null,
    "0"
  ],
  [
    "pe",
    // Peru
    "51",
    0,
    null,
    "0"
  ],
  [
    "ph",
    // Philippines
    "63",
    0,
    null,
    "0"
  ],
  [
    "pl",
    // Poland
    "48"
  ],
  [
    "pt",
    // Portugal
    "351"
  ],
  [
    "pr",
    // Puerto Rico
    "1",
    3,
    ["787", "939"],
    "1"
  ],
  [
    "qa",
    // Qatar
    "974"
  ],
  [
    "re",
    // Réunion
    "262",
    0,
    null,
    "0"
  ],
  [
    "ro",
    // Romania
    "40",
    0,
    null,
    "0"
  ],
  [
    "ru",
    // Russia
    "7",
    0,
    ["33"],
    // (shared with KZ)
    "8"
  ],
  [
    "rw",
    // Rwanda
    "250",
    0,
    null,
    "0"
  ],
  [
    "ws",
    // Samoa
    "685"
  ],
  [
    "sm",
    // San Marino
    "378"
  ],
  [
    "st",
    // São Tomé & Príncipe
    "239"
  ],
  [
    "sa",
    // Saudi Arabia
    "966",
    0,
    null,
    "0"
  ],
  [
    "sn",
    // Senegal
    "221"
  ],
  [
    "rs",
    // Serbia
    "381",
    0,
    null,
    "0"
  ],
  [
    "sc",
    // Seychelles
    "248"
  ],
  [
    "sl",
    // Sierra Leone
    "232",
    0,
    null,
    "0"
  ],
  [
    "sg",
    // Singapore
    "65"
  ],
  [
    "sx",
    // Sint Maarten
    "1",
    21,
    ["721"],
    "1"
  ],
  [
    "sk",
    // Slovakia
    "421",
    0,
    null,
    "0"
  ],
  [
    "si",
    // Slovenia
    "386",
    0,
    null,
    "0"
  ],
  [
    "sb",
    // Solomon Islands
    "677"
  ],
  [
    "so",
    // Somalia
    "252",
    0,
    null,
    "0"
  ],
  [
    "za",
    // South Africa
    "27",
    0,
    null,
    "0"
  ],
  [
    "kr",
    // South Korea
    "82",
    0,
    null,
    "0"
  ],
  [
    "ss",
    // South Sudan
    "211",
    0,
    null,
    "0"
  ],
  [
    "es",
    // Spain
    "34"
  ],
  [
    "lk",
    // Sri Lanka
    "94",
    0,
    null,
    "0"
  ],
  [
    "bl",
    // St. Barthélemy
    "590",
    1,
    null,
    "0"
  ],
  [
    "sh",
    // St. Helena
    "290"
  ],
  [
    "kn",
    // St. Kitts & Nevis
    "1",
    18,
    ["869"],
    "1"
  ],
  [
    "lc",
    // St. Lucia
    "1",
    19,
    ["758"],
    "1"
  ],
  [
    "mf",
    // St. Martin
    "590",
    2,
    null,
    "0"
  ],
  [
    "pm",
    // St. Pierre & Miquelon
    "508",
    0,
    null,
    "0"
  ],
  [
    "vc",
    // St. Vincent & Grenadines
    "1",
    20,
    ["784"],
    "1"
  ],
  [
    "sd",
    // Sudan
    "249",
    0,
    null,
    "0"
  ],
  [
    "sr",
    // Suriname
    "597"
  ],
  [
    "sj",
    // Svalbard & Jan Mayen
    "47",
    1,
    ["4", "79", "9"]
    // (4 and 9 are mobile ranges shared with NO)
  ],
  [
    "se",
    // Sweden
    "46",
    0,
    null,
    "0"
  ],
  [
    "ch",
    // Switzerland
    "41",
    0,
    null,
    "0"
  ],
  [
    "sy",
    // Syria
    "963",
    0,
    null,
    "0"
  ],
  [
    "tw",
    // Taiwan
    "886",
    0,
    null,
    "0"
  ],
  [
    "tj",
    // Tajikistan
    "992"
  ],
  [
    "tz",
    // Tanzania
    "255",
    0,
    null,
    "0"
  ],
  [
    "th",
    // Thailand
    "66",
    0,
    null,
    "0"
  ],
  [
    "tl",
    // Timor-Leste
    "670"
  ],
  [
    "tg",
    // Togo
    "228"
  ],
  [
    "tk",
    // Tokelau
    "690"
  ],
  [
    "to",
    // Tonga
    "676"
  ],
  [
    "tt",
    // Trinidad & Tobago
    "1",
    22,
    ["868"],
    "1"
  ],
  [
    "tn",
    // Tunisia
    "216"
  ],
  [
    "tr",
    // Turkey
    "90",
    0,
    null,
    "0"
  ],
  [
    "tm",
    // Turkmenistan
    "993",
    0,
    null,
    "8"
  ],
  [
    "tc",
    // Turks & Caicos Islands
    "1",
    23,
    ["649"],
    "1"
  ],
  [
    "tv",
    // Tuvalu
    "688"
  ],
  [
    "vi",
    // U.S. Virgin Islands
    "1",
    24,
    ["340"],
    "1"
  ],
  [
    "ug",
    // Uganda
    "256",
    0,
    null,
    "0"
  ],
  [
    "ua",
    // Ukraine
    "380",
    0,
    null,
    "0"
  ],
  [
    "ae",
    // United Arab Emirates
    "971",
    0,
    null,
    "0"
  ],
  [
    "gb",
    // United Kingdom
    "44",
    0,
    null,
    "0"
  ],
  [
    "us",
    // United States
    "1",
    0,
    null,
    "1"
  ],
  [
    "uy",
    // Uruguay
    "598",
    0,
    null,
    "0"
  ],
  [
    "uz",
    // Uzbekistan
    "998"
  ],
  [
    "vu",
    // Vanuatu
    "678"
  ],
  [
    "va",
    // Vatican City
    "39",
    1,
    ["06698", "3"]
    // (3 is a mobile range shared with IT)
  ],
  [
    "ve",
    // Venezuela
    "58",
    0,
    null,
    "0"
  ],
  [
    "vn",
    // Vietnam
    "84",
    0,
    null,
    "0"
  ],
  [
    "wf",
    // Wallis & Futuna
    "681"
  ],
  [
    "eh",
    // Western Sahara
    "212",
    1,
    ["5288", "5289", "6", "7"],
    // (6 and 7 are mobile ranges shared with MA)
    "0"
  ],
  [
    "ye",
    // Yemen
    "967",
    0,
    null,
    "0"
  ],
  [
    "zm",
    // Zambia
    "260",
    0,
    null,
    "0"
  ],
  [
    "zw",
    // Zimbabwe
    "263",
    0,
    null,
    "0"
  ]
];
var allCountries = [];
for (const c of rawCountryData) {
  allCountries.push({
    name: "",
    // populated in the core library
    iso2: c[0],
    dialCode: c[1],
    priority: c[2] || 0,
    areaCodes: c[3] || null,
    nationalPrefix: c[4] || null
  });
}
var iso2Set = new Set(allCountries.map((c) => c.iso2));
var isIso2 = (val) => iso2Set.has(val);
var data_default = allCountries;

// packages/core/src/js/constants.ts
var EVENTS = {
  OPEN_COUNTRY_SELECTOR: "open:countryselector",
  CLOSE_COUNTRY_SELECTOR: "close:countryselector",
  COUNTRY_CHANGE: "countrychange",
  INPUT: "input",
  // used for synthetic input trigger
  STRICT_REJECT: "strict:reject"
};
var ITI_SLOTS = [
  "container",
  "input",
  "countryContainer",
  "selectedCountry",
  "selectedCountryPrimary",
  "selectedFlag",
  "arrow",
  "selectedDialCode",
  "countrySelector",
  "countrySelectorContainer",
  "searchWrapper",
  "searchIcon",
  "searchInput",
  "searchClear",
  "countryList",
  "countryListItem",
  "countryListItemFlag",
  "countryName",
  "dialCode",
  "countryCheck",
  "noResults"
];
var CLASSES = {
  HIDE: "iti__hide",
  V_HIDE: "iti__v-hide",
  ARROW_UP: "iti__arrow--up",
  GLOBE: "iti__globe",
  FLAG: "iti__flag",
  LOADING: "iti__loading",
  COUNTRY_ITEM: "iti__country",
  HIGHLIGHT: "iti__highlight",
  STRICT_REJECT_ANIMATION: "iti__strict-reject-animation"
};
var KEYS = {
  ARROW_UP: "ArrowUp",
  ARROW_DOWN: "ArrowDown",
  SPACE: " ",
  ENTER: "Enter",
  ESC: "Escape",
  TAB: "Tab"
};
var INPUT_TYPES = {
  PASTE: "insertFromPaste",
  DELETE_FORWARD: "deleteContentForward"
};
var REGEX = {
  ALPHA_UNICODE: /\p{L}/u,
  // any kind of letter from any language
  NON_PLUS_NUMERIC: /[^+0-9]/,
  // chars that are NOT + or digit
  NON_PLUS_NUMERIC_GLOBAL: /[^+0-9]/g,
  // chars that are NOT + or digit (global)
  HIDDEN_SEARCH_CHAR: /^[a-zA-ZÀ-ÿа-яА-Я ]$/
  // single acceptable hidden-search char
};
var TIMINGS = {
  SEARCH_DEBOUNCE_MS: 100,
  HIDDEN_SEARCH_RESET_MS: 1e3,
  NEXT_TICK: 0
};
var LAYOUT = {
  NARROW_VIEWPORT_WIDTH: 500,
  // keep in sync with .iti__country-list CSS media query
  FALLBACK_SELECTED_COUNTRY_WITH_DIAL_WIDTH: 78,
  // px width fallback when separateDialCode enabled
  FALLBACK_SELECTED_COUNTRY_NO_DIAL_WIDTH: 42,
  // px width fallback when no separate dial code
  INPUT_PADDING_EXTRA_LEFT: 6,
  // px gap between selected country container and input text
  DROPDOWN_MARGIN: 3,
  // px margin between dropdown and tel input
  FALLBACK_DROPDOWN_HEIGHT: 200
  // px height fallback for dropdown
};
var DIAL_CODE = {
  PLUS: "+",
  NANP: "1"
  // North American Numbering Plan
};
var E164_MAX_DIGITS = 15;
var UK = {
  ISO2: "gb",
  DIAL_CODE: "44",
  // +44 United Kingdom
  MOBILE_PREFIX: "7",
  // UK mobile numbers start with 7 after national trunk (0) or core section
  MOBILE_CORE_LENGTH: 10
  // core number length (excluding dial code / national prefix) for mobiles
};
var US = {
  ISO2: "us",
  DIAL_CODE: "1"
  // +1 United States
};
var PLACEHOLDER_POLICY = {
  AGGRESSIVE: "AGGRESSIVE",
  POLITE: "POLITE",
  OFF: "OFF"
};
var COUNTRY_SELECTOR_MODES = [
  "OFF",
  "DROPDOWN",
  "FULLSCREEN",
  "AUTO"
];
var NUMBER_FORMATS = [
  "E164",
  "INTERNATIONAL",
  "NATIONAL",
  "RFC3966"
];
var NUMBER_TYPES = [
  "FIXED_LINE",
  "MOBILE",
  "FIXED_LINE_OR_MOBILE",
  "TOLL_FREE",
  "PREMIUM_RATE",
  "SHARED_COST",
  "VOIP",
  "PERSONAL_NUMBER",
  "PAGER",
  "UAN",
  "VOICEMAIL",
  "UNKNOWN"
];
var VALIDATION_ERRORS = [
  "IS_POSSIBLE",
  "INVALID_COUNTRY_CODE",
  "TOO_SHORT",
  "TOO_LONG",
  "IS_POSSIBLE_LOCAL_ONLY",
  "INVALID_LENGTH"
];
var toEnumObject = (arr) => Object.fromEntries(arr.map((v) => [v, v]));
var NUMBER_FORMAT = toEnumObject(NUMBER_FORMATS);
var NUMBER_TYPE = toEnumObject(NUMBER_TYPES);
var VALIDATION_ERROR = toEnumObject(VALIDATION_ERRORS);
var COUNTRY_SELECTOR_MODE = toEnumObject(COUNTRY_SELECTOR_MODES);
var DATA_KEYS = {
  // e.g. <li data-iso2="us"> for country items in the country list
  ISO2: "iso2",
  DIAL_CODE: "dialCode",
  // e.g. <input data-intl-tel-input-id="0"> on the input element
  INSTANCE_ID: "intlTelInputId"
};
var ARIA = {
  EXPANDED: "aria-expanded",
  LABEL: "aria-label",
  SELECTED: "aria-selected",
  ACTIVE_DESCENDANT: "aria-activedescendant",
  HASPOPUP: "aria-haspopup",
  CONTROLS: "aria-controls",
  HIDDEN: "aria-hidden",
  AUTOCOMPLETE: "aria-autocomplete",
  MODAL: "aria-modal"
};

// packages/core/src/js/locale/en.ts
var interfaceTranslations = {
  selectedCountryAriaLabel: "Change country for phone number, currently selected ${countryName} (${dialCode})",
  noCountrySelected: "Select country for phone number",
  countryListAriaLabel: "List of countries",
  searchPlaceholder: "Search",
  clearSearchAriaLabel: "Clear search",
  searchEmptyState: "No results found",
  searchSummaryAria(count) {
    if (count === 0) {
      return "No results found";
    }
    if (count === 1) {
      return "1 result found";
    }
    return `${count} results found`;
  }
};
var en_default = interfaceTranslations;

// packages/core/src/js/core/options.ts
var mediaQuery = (q) => typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia(q).matches;
var isNarrowViewport = () => mediaQuery(`(max-width: ${LAYOUT.NARROW_VIEWPORT_WIDTH}px)`);
var resolveAutoCountrySelectorMode = () => {
  if (typeof navigator !== "undefined" && typeof window !== "undefined") {
    const isShortViewport = mediaQuery("(max-height: 600px)");
    const isCoarsePointer = mediaQuery("(pointer: coarse)");
    if (isNarrowViewport() || isCoarsePointer && isShortViewport) {
      return COUNTRY_SELECTOR_MODE.FULLSCREEN;
    }
  }
  return COUNTRY_SELECTOR_MODE.DROPDOWN;
};
var defaults = {
  //* How the country selector is displayed. "DROPDOWN" vs "FULLSCREEN", or "AUTO" to decide itself, or "OFF".
  countrySelectorMode: COUNTRY_SELECTOR_MODE.AUTO,
  //* The number type to enforce during validation.
  allowedNumberTypes: [NUMBER_TYPE.MOBILE, NUMBER_TYPE.FIXED_LINE],
  //* Whether or not to allow extensions after the main number.
  allowNumberExtensions: false,
  // Allow alphanumeric "phonewords" (e.g. +1 800 FLOWERS) as valid numbers
  allowPhonewords: false,
  //* Add custom classes to the elements we generate, keyed by slot name e.g. { selectedCountry: "rounded-l-lg" }.
  classNames: {},
  //* Add a custom class to the (injected) container element.
  containerClass: "",
  //* Locale for localising country names via Intl.DisplayNames.
  countryNameLocale: "en",
  //* Override individual country names by iso2 code.
  countryNameOverrides: {},
  //* The order of the countries in the country list. Defaults to alphabetical.
  countryOrder: null,
  //* Add a country search input at the top of the country selector.
  countrySearch: true,
  //* Modify the auto placeholder.
  customPlaceholder: null,
  //* Always show the dropdown
  dropdownAlwaysOpen: false,
  //* Optional DOM element to append the dropdown to (used to escape ancestors with overflow:hidden, or to mount in a custom container). Only consulted in dropdown rendering; ignored when the country selector renders as a fullscreen popup (see fullscreenParent).
  dropdownParent: null,
  //* Don't display these countries.
  excludeCountries: null,
  //* Fix the dropdown width to the input width (rather than being as wide as the longest country name).
  matchDropdownWidth: true,
  //* Format the number as the user types
  formatAsYouType: true,
  //* Optional DOM element to append the fullscreen popup to, instead of document.body (e.g. a modal <dialog>, where a body-mounted popup would be unreachable). Only consulted in fullscreen rendering (see dropdownParent for the dropdown). Null means document.body, which is resolved on open rather than here, as document may not exist yet (e.g. SSR).
  fullscreenParent: null,
  //* Inject hidden inputs with the names returned from this function, and on submit, populate them with the full number and selected country iso2.
  hiddenInputs: null,
  //* Translations for the core library UI strings e.g. search input placeholder, country names.
  uiTranslations: {},
  //* Initial country.
  initialCountry: "",
  //* Async lookup function used to determine the initial country (e.g. via IP). Ignored if initialCountry is set.
  initialCountryLookup: null,
  //* A function to load the utils script.
  loadUtils: null,
  //* Format used when displaying numbers (placeholder examples and stored values). One of "E164", "INTERNATIONAL", "NATIONAL".
  numberDisplayFormat: NUMBER_FORMAT.INTERNATIONAL,
  //* Display only these countries.
  onlyCountries: null,
  //* When to set the placeholder to an example number for the selected country: "POLITE" only when the input has no manually-set placeholder, "AGGRESSIVE" always, "OFF" never.
  placeholderNumberPolicy: PLACEHOLDER_POLICY.POLITE,
  //* Number type to use for placeholders.
  placeholderNumberType: NUMBER_TYPE.MOBILE,
  //* Add custom classes to the search input element.
  searchInputClass: "",
  //* Display the international dial code next to the selected flag.
  separateDialCode: true,
  //* When strictMode rejects a key (etc), play a short feedback animation
  strictRejectAnimation: true,
  //* Show flags - for both the selected country, and in the country list
  showFlags: true,
  //* Only allow certain chars e.g. a plus followed by numeric digits, and cap at max valid length.
  strictMode: true
};
var toString = (val) => JSON.stringify(val);
var isPlainObject = (val) => Boolean(val) && typeof val === "object" && !Array.isArray(val);
var isFunction = (val) => typeof val === "function";
var isElLike = (val) => {
  if (!val || typeof val !== "object") {
    return false;
  }
  const v = val;
  return v.nodeType === 1 && typeof v.tagName === "string" && typeof v.appendChild === "function";
};
var placeholderPolicySet = new Set(Object.values(PLACEHOLDER_POLICY));
var slotSet = new Set(ITI_SLOTS);
var warn = (message) => {
  console.warn(`[intl-tel-input] ${message}`);
};
var warnOption = (optionName, expectedType, actualValue) => {
  warn(
    `Option '${optionName}' must be ${expectedType}; got ${toString(actualValue)}. Ignoring.`
  );
};
var validateIso2Array = (key, value) => {
  const expectedType = "an array of iso2 country code strings";
  if (!Array.isArray(value)) {
    warnOption(key, expectedType, value);
    return false;
  }
  const valid = [];
  for (const v of value) {
    if (typeof v !== "string") {
      warnOption(key, expectedType, value);
      return false;
    }
    const lower = v.toLowerCase();
    if (!isIso2(lower)) {
      warn(`Invalid iso2 code in '${key}': '${v}'. Skipping.`);
    } else {
      valid.push(v);
    }
  }
  return valid;
};
var validateOptions = (customOptions) => {
  if (customOptions === void 0) {
    return {};
  }
  if (!isPlainObject(customOptions)) {
    const error = `The second argument must be an options object; got ${toString(customOptions)}. Using defaults.`;
    warn(error);
    return {};
  }
  const validatedOptions = {};
  for (const [key, value] of Object.entries(customOptions)) {
    if (!Object.hasOwn(defaults, key)) {
      warn(`Unknown option '${key}'. Ignoring.`);
      continue;
    }
    switch (key) {
      case "allowNumberExtensions":
      case "allowPhonewords":
      case "countrySearch":
      case "dropdownAlwaysOpen":
      case "matchDropdownWidth":
      case "formatAsYouType":
      case "showFlags":
      case "separateDialCode":
      case "strictMode":
      case "strictRejectAnimation":
        if (typeof value !== "boolean") {
          warnOption(key, "a boolean", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "countrySelectorMode":
        if (typeof value !== "string" || !COUNTRY_SELECTOR_MODES.includes(value)) {
          warnOption(
            "countrySelectorMode",
            `one of ${COUNTRY_SELECTOR_MODES.map((m) => `"${m}"`).join(", ")}`,
            value
          );
          break;
        }
        validatedOptions[key] = value;
        break;
      case "numberDisplayFormat":
        if (typeof value !== "string" || value === NUMBER_FORMAT.RFC3966 || !(value === NUMBER_FORMAT.E164 || value === NUMBER_FORMAT.INTERNATIONAL || value === NUMBER_FORMAT.NATIONAL)) {
          warnOption(
            "numberDisplayFormat",
            'one of "E164", "INTERNATIONAL", "NATIONAL"',
            value
          );
          break;
        }
        validatedOptions[key] = value;
        break;
      case "placeholderNumberPolicy":
        if (typeof value !== "string" || !placeholderPolicySet.has(value)) {
          const validPolicies = Array.from(placeholderPolicySet).join(", ");
          warnOption("placeholderNumberPolicy", `one of ${validPolicies}`, value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "containerClass":
      case "searchInputClass":
      case "countryNameLocale":
        if (typeof value !== "string") {
          warnOption(key, "a string", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "classNames": {
        if (!isPlainObject(value)) {
          warnOption("classNames", "an object", value);
          break;
        }
        const validSlots = {};
        for (const [slot, slotValue] of Object.entries(value)) {
          if (!slotSet.has(slot)) {
            warn(
              `Unknown slot '${slot}' in 'classNames'. Valid slots: ${ITI_SLOTS.join(", ")}. Skipping.`
            );
          } else if (typeof slotValue !== "string") {
            warnOption(`classNames.${slot}`, "a string", slotValue);
          } else {
            validSlots[slot] = slotValue.trim().replace(/\s+/g, " ");
          }
        }
        validatedOptions[key] = validSlots;
        break;
      }
      case "countryOrder": {
        if (value === null) {
          validatedOptions[key] = value;
        } else {
          const filtered = validateIso2Array(key, value);
          if (filtered !== false) {
            validatedOptions[key] = filtered;
          }
        }
        break;
      }
      case "customPlaceholder":
      case "hiddenInputs":
      case "initialCountryLookup":
      case "loadUtils":
        if (value !== null && !isFunction(value)) {
          warnOption(key, "a function or null", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "dropdownParent":
      case "fullscreenParent":
        if (value !== null && !isElLike(value)) {
          warnOption(key, "an HTMLElement or null", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "excludeCountries":
      case "onlyCountries": {
        if (value === null) {
          validatedOptions[key] = value;
        } else {
          const filtered = validateIso2Array(key, value);
          if (filtered !== false) {
            validatedOptions[key] = filtered;
          }
        }
        break;
      }
      case "uiTranslations":
        if (value && !isPlainObject(value)) {
          warnOption("uiTranslations", "an object", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "countryNameOverrides":
        if (value && !isPlainObject(value)) {
          warnOption("countryNameOverrides", "an object", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "initialCountry": {
        if (typeof value !== "string") {
          warnOption("initialCountry", "a string", value);
          break;
        }
        const lower = value.toLowerCase();
        if (lower && !isIso2(lower)) {
          warnOption("initialCountry", "a valid iso2 country code", value);
          break;
        }
        validatedOptions[key] = value;
        break;
      }
      case "placeholderNumberType":
        if (typeof value !== "string" || !NUMBER_TYPES.includes(value)) {
          const validTypes = NUMBER_TYPES.join(", ");
          warnOption("placeholderNumberType", `one of ${validTypes}`, value);
          break;
        }
        validatedOptions[key] = value;
        break;
      case "allowedNumberTypes":
        if (value !== null) {
          if (!Array.isArray(value)) {
            warnOption(
              "allowedNumberTypes",
              "an array of number types or null",
              value
            );
            break;
          }
          let allValid = true;
          for (const v of value) {
            if (typeof v !== "string" || !NUMBER_TYPES.includes(v)) {
              const validTypes = NUMBER_TYPES.join(", ");
              warnOption(
                "allowedNumberTypes",
                `an array of valid number types (${validTypes})`,
                v
              );
              allValid = false;
              break;
            }
          }
          if (allValid) {
            validatedOptions[key] = value;
          }
        } else {
          validatedOptions[key] = null;
        }
        break;
    }
  }
  return validatedOptions;
};
var normaliseOptions = (o) => {
  if (o.initialCountry) {
    o.initialCountry = o.initialCountry.toLowerCase();
  }
  if (o.onlyCountries?.length) {
    o.onlyCountries = o.onlyCountries.map((c) => c.toLowerCase());
  }
  if (o.excludeCountries?.length) {
    o.excludeCountries = o.excludeCountries.map((c) => c.toLowerCase());
  }
  if (o.countryOrder) {
    o.countryOrder = o.countryOrder.map((c) => c.toLowerCase());
  }
};
var applyOptionSideEffects = (o) => {
  if (o.countrySelectorMode === COUNTRY_SELECTOR_MODE.AUTO) {
    o.countrySelectorMode = resolveAutoCountrySelectorMode();
  }
  if (o.dropdownAlwaysOpen) {
    o.countrySelectorMode = COUNTRY_SELECTOR_MODE.DROPDOWN;
  }
  if (o.countrySelectorMode === COUNTRY_SELECTOR_MODE.FULLSCREEN) {
    o.matchDropdownWidth = false;
  } else {
    if (isNarrowViewport()) {
      o.matchDropdownWidth = true;
    }
  }
  if (o.onlyCountries?.length === 1) {
    o.initialCountry = o.onlyCountries[0];
  }
  if (o.separateDialCode && o.numberDisplayFormat === NUMBER_FORMAT.NATIONAL) {
    o.numberDisplayFormat = NUMBER_FORMAT.INTERNATIONAL;
  }
  if (o.countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF && !o.showFlags && !o.separateDialCode && o.numberDisplayFormat === NUMBER_FORMAT.NATIONAL) {
    o.numberDisplayFormat = NUMBER_FORMAT.INTERNATIONAL;
  }
  o.uiTranslations = { ...en_default, ...o.uiTranslations };
};

// packages/core/src/js/helpers/string.ts
var getNumeric = (s) => s.replace(/\D/g, "");
var normaliseString = (s = "") => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

// packages/core/src/js/helpers/dom.ts
var buildClassNames = (flags) => Object.keys(flags).filter((k) => Boolean(flags[k])).join(" ");
var createEl = (tagName, attrs, container) => {
  const el = document.createElement(tagName);
  if (attrs) {
    Object.entries(attrs).forEach(
      ([key, value]) => el.setAttribute(key, value)
    );
  }
  if (container) {
    container.appendChild(el);
  }
  return el;
};

// packages/core/src/js/core/icons.ts
var SVG_NS = "http://www.w3.org/2000/svg";
var buildSvg = ([tag, attrs, children]) => {
  const el = document.createElementNS(SVG_NS, tag);
  if (attrs) {
    for (const k in attrs) {
      el.setAttribute(k, String(attrs[k]));
    }
  }
  if (children) {
    for (const c of children) {
      el.appendChild(buildSvg(c));
    }
  }
  return el;
};
var buildSearchIcon = () => buildSvg(
  ["svg", { class: "iti__search-icon-svg", width: 14, height: 14, viewBox: "0 0 24 24", focusable: "false", [ARIA.HIDDEN]: "true" }, [
    ["circle", { cx: 11, cy: 11, r: 7 }],
    ["line", { x1: 21, y1: 21, x2: 16.65, y2: 16.65 }]
  ]]
);
var buildClearIcon = (id) => {
  const maskId = `iti-${id}-clear-mask`;
  return buildSvg(
    ["svg", { class: "iti__search-clear-svg", width: 12, height: 12, viewBox: "0 0 16 16", [ARIA.HIDDEN]: "true", focusable: "false" }, [
      ["mask", { id: maskId, maskUnits: "userSpaceOnUse" }, [
        ["rect", { width: 16, height: 16, fill: "white" }],
        ["path", { d: "M5.2 5.2 L10.8 10.8 M10.8 5.2 L5.2 10.8", stroke: "black", "stroke-linecap": "round", class: "iti__search-clear-x" }]
      ]],
      ["circle", { cx: 8, cy: 8, r: 8, class: "iti__search-clear-bg", mask: `url(#${maskId})` }]
    ]]
  );
};
var buildCheckIcon = () => buildSvg(
  ["svg", { class: "iti__country-check-svg", width: 14, height: 14, viewBox: "0 0 16 16", fill: "currentColor", focusable: "false", [ARIA.HIDDEN]: "true" }, [
    ["path", { d: "M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z" }]
  ]]
);
var buildGlobeIcon = () => buildSvg(
  ["svg", { width: 256, height: 256, viewBox: "0 0 512 512", class: "iti__globe-svg" }, [
    ["path", { d: "M508 213a240 240 0 0 0-449-87l-2 5-2 5c-8 14-13 30-17 46a65 65 0 0 1 56 4c16-10 35-19 56-27l9-3c-6 23-10 48-10 74h-16l4 6c3 4 5 8 6 13h6c0 22 3 44 8 65l2 10-25-10-4 5 12 18 9 3 6 2 8 3 9 26 1 2 16-7h1l-5-13-1-2c24 6 49 9 75 10v26l11 10 7 7v-30l1-13c22 0 44-3 65-8l10-2-21 48-1 1a317 317 0 0 1-14 23l-21 5h-2c6 16 7 33 1 50a240 240 0 0 0 211-265m-401-56-11 6c19-44 54-79 98-98-11 20-21 44-29 69-21 6-40 15-58 23m154 182v4c-29-1-57-6-81-13-7-25-12-52-13-81h94zm0-109h-94c1-29 6-56 13-81 24-7 52-12 81-13zm0-112c-22 1-44 4-65 8l-10 2 12-30 9-17 1-2a332 332 0 0 1 13-23c13-4 26-6 40-7zm187 69 6 4c4 12 6 25 6 38v1h-68c-1-26-4-51-10-74l48 20 1 1 14 8zm-14-44 10 20c-20-11-43-21-68-29-8-25-18-49-29-69 37 16 67 44 87 78M279 49h1c13 1 27 3 39 7l14 23 1 2a343 343 0 0 1 12 26l2 5 6 16c-23-6-48-9-74-10h-1zm0 87h1c29 1 56 6 81 13 7 24 12 51 12 80v1h-94zm2 207h-2v-94h95c-1 29-6 56-13 81-24 7-51 12-80 13m86 60-20 10c11-20 21-43 29-68 25-8 48-18 68-29-16 37-43 67-77 87m87-115-7 5-16 9-2 1a337 337 0 0 1-47 21c6-24 9-49 10-75h68c0 13-2 27-6 39" }],
    ["path", { d: "m261 428-2-2-22-21a40 40 0 0 0-32-11h-1a37 37 0 0 0-18 8l-1 1-4 2-2 2-5 4c-9-3-36-31-47-44s-32-45-34-55l3-2a151 151 0 0 0 11-9v-1a39 39 0 0 0 5-48l-3-3-11-19-3-4-5-7h-1l-3-3-4-3-5-2a35 35 0 0 0-16-3h-5c-4 1-14 5-24 11l-4 2-4 3-4 2c-9 8-17 17-18 27a380 380 0 0 0 212 259h3c12 0 25-10 36-21l10-12 6-11a39 39 0 0 0-8-40" }]
  ]]
);

// packages/core/src/js/core/countrySearch.ts
var normaliseName = (s) => normaliseString(s).replace(/[^\p{L}]+/gu, " ").trim();
var buildSearchTokens = (countries) => {
  const tokens = /* @__PURE__ */ new Map();
  for (const c of countries) {
    const normalisedName = normaliseName(c.name);
    const words = normalisedName.split(" ").filter(Boolean);
    const initials = words.map((w) => w[0] || "").join("");
    tokens.set(c.iso2, {
      normalisedName,
      words,
      initials,
      dialCodePlus: `+${c.dialCode}`
    });
  }
  return tokens;
};
var getMatchedCountries = (countries, searchTokens, query) => {
  const lowerQuery = normaliseString(query);
  const nameQuery = normaliseName(query);
  const skipNameBuckets = lowerQuery !== "" && nameQuery === "";
  const iso2Matches = [];
  const nameStartsWith = [];
  const nameContains = [];
  const dialCodeMatches = [];
  const dialCodeContains = [];
  const initialsMatches = [];
  const wordMatches = [];
  for (const c of countries) {
    const t = searchTokens.get(c.iso2);
    if (c.iso2 === lowerQuery) {
      iso2Matches.push(c);
    } else if (!skipNameBuckets && t.normalisedName.startsWith(nameQuery)) {
      nameStartsWith.push(c);
    } else if (!skipNameBuckets && t.normalisedName.includes(nameQuery)) {
      nameContains.push(c);
    } else if (lowerQuery === c.dialCode || lowerQuery === t.dialCodePlus) {
      dialCodeMatches.push(c);
    } else if (t.dialCodePlus.includes(lowerQuery)) {
      dialCodeContains.push(c);
    } else if (t.initials.includes(lowerQuery)) {
      initialsMatches.push(c);
    }
  }
  const queryWords = nameQuery.split(" ").filter(Boolean);
  if (queryWords.length > 1 && iso2Matches.length === 0 && nameStartsWith.length === 0 && nameContains.length === 0) {
    const claimed = /* @__PURE__ */ new Set([
      ...dialCodeMatches.map((c) => c.iso2),
      ...dialCodeContains.map((c) => c.iso2),
      ...initialsMatches.map((c) => c.iso2)
    ]);
    for (const c of countries) {
      if (claimed.has(c.iso2)) {
        continue;
      }
      const t = searchTokens.get(c.iso2);
      if (queryWords.some((qw) => t.words.some((sw) => sw.startsWith(qw)))) {
        wordMatches.push(c);
      }
    }
  }
  const sortByPriority = (a, b) => a.priority - b.priority;
  return [
    ...iso2Matches,
    ...nameStartsWith,
    ...nameContains,
    // priority sort is only relevant when showing multiple countries with the same dial code (that's what the priority field is used to distinguish between)
    ...dialCodeMatches.sort(sortByPriority),
    ...dialCodeContains.sort(sortByPriority),
    ...initialsMatches,
    ...wordMatches
  ];
};
var findFirstCountryStartingWith = (countries, searchTokens, query) => {
  const nameQuery = normaliseName(query);
  for (const c of countries) {
    const { normalisedName } = searchTokens.get(c.iso2);
    if (normalisedName.startsWith(nameQuery)) {
      return c;
    }
  }
  return null;
};

// packages/core/src/js/core/numerals.ts
var Numerals = class _Numerals {
  #userNumeralSet;
  //* Stateless conversion of any Arabic-Indic / Persian digits to ASCII 0-9.
  //* Use this when you need to normalise digits without affecting any instance's tracked numeral set (e.g. for the country-search query).
  static toAscii(str) {
    if (!str) {
      return "";
    }
    return str.replace(
      /[٠-٩]/g,
      (ch) => String.fromCharCode(48 + (ch.charCodeAt(0) - 1632))
    ).replace(
      /[۰-۹]/g,
      (ch) => String.fromCharCode(48 + (ch.charCodeAt(0) - 1776))
    );
  }
  constructor(initialValue) {
    if (initialValue) {
      this.#updateNumeralSet(initialValue);
    }
  }
  // If any Arabic-Indic digits, then label it as that set. Same for Persian. Otherwise assume ASCII.
  #updateNumeralSet(str) {
    if (/[٠-٩]/.test(str)) {
      this.#userNumeralSet = "arabic-indic";
    } else if (/[۰-۹]/.test(str)) {
      this.#userNumeralSet = "persian";
    } else {
      this.#userNumeralSet = "ascii";
    }
  }
  // Denormalise ASCII 0-9 to the user's numeral set. If not yet known, return as-is.
  // NOTE: normalise is always called before this, so it should be impossible for the numeral set to be unknown at this point.
  denormalise(str) {
    if (!this.#userNumeralSet || this.#userNumeralSet === "ascii") {
      return str;
    }
    const base = this.#userNumeralSet === "arabic-indic" ? 1632 : 1776;
    return str.replace(/[0-9]/g, (d) => String.fromCharCode(base + Number(d)));
  }
  // Normalize Eastern Arabic (U+0660-0669) and Persian/Extended Arabic-Indic (U+06F0-06F9) numerals to ASCII 0-9.
  // Tracks the user's numeral set as a side effect so denormalise can mirror it back.
  normalise(str) {
    if (!str) {
      return "";
    }
    this.#updateNumeralSet(str);
    if (this.#userNumeralSet === "ascii") {
      return str;
    }
    return _Numerals.toAscii(str);
  }
  isAscii() {
    return !this.#userNumeralSet || this.#userNumeralSet === "ascii";
  }
};

// packages/core/src/js/core/ui.ts
var supportsCssAnchor = typeof CSS !== "undefined" && typeof CSS.supports === "function" && CSS.supports("anchor-name: --x");
var UI = class {
  // private
  #options;
  #id;
  #isRTL;
  #originalPaddingLeft = "";
  #countries;
  #searchTokens;
  #searchDebounceTimer = null;
  #inlineDropdownHeight;
  #cssAnchorPositioningDone = false;
  #countryContainerEl;
  #selectedCountryEl;
  #selectedFlagEl;
  #selectedDialCodeEl;
  #arrowEl;
  #countrySelectorEl;
  #searchIconEl;
  #searchInputEl;
  #searchClearButtonEl;
  #countryListEl;
  #hiddenInputPhoneEl;
  #hiddenInputCountryEl;
  #noResultsMessageEl;
  #searchResultsLiveRegionEl;
  #detachedCountrySelectorEl;
  #selectedListItemEl = null;
  #highlightedListItemEl = null;
  #listItemByIso2 = /* @__PURE__ */ new Map();
  #countrySelectorAbortController = null;
  #resizeObserver;
  // public
  telInputEl;
  hadInitialPlaceholder;
  constructor(input, options, id) {
    input.dataset[DATA_KEYS.INSTANCE_ID] = id.toString();
    this.telInputEl = input;
    this.#options = options;
    this.#id = id;
    this.hadInitialPlaceholder = Boolean(input.getAttribute("placeholder"));
    this.#isRTL = !!this.telInputEl.closest("[dir=rtl]");
    this.#originalPaddingLeft = this.telInputEl.style.paddingLeft;
  }
  // Validate that the provided element is an HTMLInputElement.
  static validateInput(input) {
    const tagName = input?.tagName;
    const isInputEl = Boolean(input) && typeof input === "object" && tagName === "INPUT" && typeof input.setAttribute === "function";
    if (!isInputEl) {
      const type = Object.prototype.toString.call(input);
      throw new TypeError(
        `The first argument must be an HTMLInputElement, not ${type}`
      );
    }
  }
  //* Append any consumer-supplied classes (via the classNames option) for the given slot to our own classes for that element.
  #withSlotClass(slot, ourClasses) {
    const custom = this.#options.classNames[slot];
    return custom ? `${ourClasses} ${custom}` : ourClasses;
  }
  //* Generate all of the markup for the core library: the selected country overlay, and the country selector.
  buildMarkup(countries, searchTokens) {
    this.#countries = countries;
    this.#searchTokens = searchTokens;
    this.telInputEl.classList.add(
      ...this.#withSlotClass("input", "iti__tel-input").split(" ")
    );
    if (!this.telInputEl.hasAttribute("type")) {
      this.telInputEl.setAttribute("type", "tel");
    }
    if (!this.telInputEl.hasAttribute("autocomplete")) {
      this.telInputEl.setAttribute("autocomplete", "tel");
    }
    if (!this.telInputEl.hasAttribute("inputmode")) {
      this.telInputEl.setAttribute("inputmode", "tel");
    }
    const wrapper = this.#createWrapperAndInsert();
    this.#buildCountryContainer(wrapper);
    wrapper.appendChild(this.telInputEl);
    this.#updateInputPaddingAndReveal();
    this.#observeSelectedCountryResize();
    this.#buildHiddenInputs(wrapper);
    this.ensureDropdownWidthSet();
  }
  #createWrapperAndInsert() {
    const { countrySelectorMode, showFlags, containerClass } = this.#options;
    const parentClasses = buildClassNames({
      iti: true,
      "iti--input-container": true,
      "iti--has-country-selector": countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF,
      "iti--show-flags": showFlags,
      "iti--inline-country-selector": countrySelectorMode !== COUNTRY_SELECTOR_MODE.FULLSCREEN,
      [containerClass]: Boolean(containerClass)
    });
    const wrapper = createEl("div", {
      class: this.#withSlotClass("container", parentClasses)
    });
    if (this.#isRTL) {
      wrapper.setAttribute("dir", "ltr");
    }
    this.telInputEl.before(wrapper);
    return wrapper;
  }
  #buildCountryContainer(wrapper) {
    const { countrySelectorMode, separateDialCode, showFlags } = this.#options;
    const enableCountrySelector = countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF;
    if (!enableCountrySelector && !showFlags && !separateDialCode) {
      return;
    }
    this.#countryContainerEl = createEl(
      "div",
      // visibly hidden until we measure its width to set the input padding correctly
      {
        class: this.#withSlotClass(
          "countryContainer",
          `iti__country-container ${CLASSES.V_HIDE}`
        )
      },
      wrapper
    );
    if (enableCountrySelector) {
      this.#selectedCountryEl = createEl(
        "button",
        {
          type: "button",
          class: this.#withSlotClass("selectedCountry", "iti__selected-country"),
          [ARIA.EXPANDED]: "false",
          [ARIA.LABEL]: this.#options.uiTranslations.noCountrySelected,
          [ARIA.HASPOPUP]: "dialog",
          [ARIA.CONTROLS]: `iti-${this.#id}__country-selector`
        },
        this.#countryContainerEl
      );
      if (this.telInputEl.disabled) {
        this.#selectedCountryEl.setAttribute("disabled", "true");
      }
    } else {
      this.#selectedCountryEl = createEl(
        "div",
        { class: this.#withSlotClass("selectedCountry", "iti__selected-country") },
        this.#countryContainerEl
      );
    }
    const selectedCountryPrimary = createEl(
      "div",
      {
        class: this.#withSlotClass(
          "selectedCountryPrimary",
          "iti__selected-country-primary"
        )
      },
      this.#selectedCountryEl
    );
    this.#selectedFlagEl = createEl(
      "div",
      { class: this.#withSlotClass("selectedFlag", CLASSES.FLAG) },
      selectedCountryPrimary
    );
    if (enableCountrySelector) {
      this.#arrowEl = createEl(
        "div",
        {
          class: this.#withSlotClass("arrow", "iti__arrow"),
          [ARIA.HIDDEN]: "true"
        },
        selectedCountryPrimary
      );
    }
    if (separateDialCode) {
      this.#selectedDialCodeEl = createEl(
        "div",
        {
          class: this.#withSlotClass(
            "selectedDialCode",
            "iti__selected-dial-code"
          )
        },
        this.#selectedCountryEl
      );
    }
    if (enableCountrySelector) {
      this.#buildCountrySelector();
    }
  }
  ensureDropdownWidthSet() {
    const { matchDropdownWidth, countrySelectorMode } = this.#options;
    if (countrySelectorMode === COUNTRY_SELECTOR_MODE.OFF || !matchDropdownWidth || this.#countrySelectorEl.style.width) {
      return;
    }
    const inputWidth = this.telInputEl.offsetWidth;
    if (inputWidth > 0) {
      this.#countrySelectorEl.style.width = `${inputWidth}px`;
    }
  }
  #buildCountrySelector() {
    const {
      matchDropdownWidth,
      countrySelectorMode,
      countrySearch,
      uiTranslations,
      containerClass
    } = this.#options;
    const isFullscreen = countrySelectorMode === COUNTRY_SELECTOR_MODE.FULLSCREEN;
    const detachedParent = this.#getDetachedParent();
    const extraClasses = matchDropdownWidth ? "" : "iti--flexible-dropdown-width";
    this.#countrySelectorEl = createEl("div", {
      id: `iti-${this.#id}__country-selector`,
      class: this.#withSlotClass(
        "countrySelector",
        `iti__country-selector ${CLASSES.HIDE} ${extraClasses}`
      ),
      role: "dialog",
      [ARIA.MODAL]: "true"
    });
    if (this.#isRTL) {
      this.#countrySelectorEl.setAttribute("dir", "rtl");
    }
    if (countrySearch) {
      this.#buildSearchUI();
    }
    this.#countryListEl = createEl(
      "ul",
      {
        class: this.#withSlotClass("countryList", "iti__country-list"),
        id: `iti-${this.#id}__country-listbox`,
        role: "listbox",
        [ARIA.LABEL]: uiTranslations.countryListAriaLabel
      },
      this.#countrySelectorEl
    );
    if (!countrySearch) {
      this.#countryListEl.setAttribute("tabindex", "0");
    }
    this.#appendListItems();
    if (countrySearch) {
      this.#updateSearchResultsA11yText();
    }
    if (detachedParent) {
      const wrapperClasses = buildClassNames({
        iti: true,
        "iti--detached-country-selector": true,
        "iti--fullscreen-popup": isFullscreen,
        "iti--inline-country-selector": !isFullscreen,
        [containerClass]: Boolean(containerClass)
      });
      this.#detachedCountrySelectorEl = createEl("div", {
        class: this.#withSlotClass("countrySelectorContainer", wrapperClasses)
      });
      this.#detachedCountrySelectorEl.appendChild(this.#countrySelectorEl);
    } else {
      this.#countryContainerEl.appendChild(this.#countrySelectorEl);
    }
  }
  //* Resolve the DOM element to attach the country selector to. Fullscreen is always detached: it uses the consumer-supplied fullscreenParent, falling back to document.body; dropdown uses the consumer-supplied dropdownParent (if any); otherwise the country selector renders inline within the input wrapper (no detached element).
  //* NOTE: these are deliberately two separate options. For the dropdown, setting a parent switches it from inline to detached rendering (pos:fixed, positioned against the input), whereas the fullscreen popup is detached regardless, so its parent only relocates it. Sharing one option would force a detached dropdown on anyone who only needs to move the fullscreen popup e.g. into a modal <dialog> (issue #2199).
  #getDetachedParent() {
    const { countrySelectorMode, dropdownParent, fullscreenParent } = this.#options;
    if (countrySelectorMode === COUNTRY_SELECTOR_MODE.FULLSCREEN) {
      return fullscreenParent ?? document.body;
    }
    if (countrySelectorMode === COUNTRY_SELECTOR_MODE.DROPDOWN) {
      return dropdownParent;
    }
    return null;
  }
  #buildSearchUI() {
    const { uiTranslations, searchInputClass } = this.#options;
    const searchWrapper = createEl(
      "div",
      { class: this.#withSlotClass("searchWrapper", "iti__search-input-wrapper") },
      this.#countrySelectorEl
    );
    this.#searchIconEl = createEl(
      "span",
      {
        class: this.#withSlotClass("searchIcon", "iti__search-icon"),
        [ARIA.HIDDEN]: "true"
      },
      searchWrapper
    );
    this.#searchIconEl.appendChild(buildSearchIcon());
    this.#searchInputEl = createEl(
      "input",
      {
        id: `iti-${this.#id}__search-input`,
        // Chrome says inputs need either a name or an id
        type: "search",
        class: this.#withSlotClass(
          "searchInput",
          `iti__search-input ${searchInputClass}`
        ),
        placeholder: uiTranslations.searchPlaceholder,
        // role=combobox + aria-autocomplete=list + aria-activedescendant allows maintaining focus on the search input while allowing users to navigate search results with up/down keyboard keys
        role: "combobox",
        [ARIA.EXPANDED]: "true",
        [ARIA.LABEL]: uiTranslations.searchPlaceholder,
        [ARIA.CONTROLS]: `iti-${this.#id}__country-listbox`,
        [ARIA.AUTOCOMPLETE]: "list",
        autocomplete: "off"
      },
      searchWrapper
    );
    this.#searchClearButtonEl = createEl(
      "button",
      {
        type: "button",
        class: this.#withSlotClass(
          "searchClear",
          `iti__search-clear ${CLASSES.HIDE}`
        ),
        [ARIA.LABEL]: uiTranslations.clearSearchAriaLabel,
        tabindex: "-1"
      },
      searchWrapper
    );
    this.#searchClearButtonEl.appendChild(buildClearIcon(this.#id));
    this.#searchResultsLiveRegionEl = createEl(
      "span",
      { class: "iti__a11y-text" },
      this.#countrySelectorEl
    );
    this.#noResultsMessageEl = createEl(
      "div",
      {
        class: this.#withSlotClass("noResults", `iti__no-results ${CLASSES.HIDE}`),
        [ARIA.HIDDEN]: "true"
        // all a11y messaging happens in this.#searchResultsLiveRegionEl
      },
      this.#countrySelectorEl
    );
    this.#noResultsMessageEl.textContent = uiTranslations.searchEmptyState ?? null;
  }
  #updateInputPaddingAndReveal() {
    if (!this.#countryContainerEl) {
      return;
    }
    this.#updateInputPadding();
    this.#countryContainerEl.classList.remove(CLASSES.V_HIDE);
  }
  #buildHiddenInputs(wrapper) {
    const { hiddenInputs } = this.#options;
    if (!hiddenInputs) {
      return;
    }
    const telInputName = this.telInputEl.getAttribute("name") || "";
    const names = hiddenInputs(telInputName);
    if (names.phone) {
      const existingInput = this.telInputEl.form?.querySelector(
        `input[name="${names.phone}"]`
      );
      if (existingInput) {
        this.#hiddenInputPhoneEl = existingInput;
      } else {
        this.#hiddenInputPhoneEl = createEl("input", {
          type: "hidden",
          name: names.phone
        });
        wrapper.appendChild(this.#hiddenInputPhoneEl);
      }
    }
    if (names.country) {
      const existingInput = this.telInputEl.form?.querySelector(
        `input[name="${names.country}"]`
      );
      if (existingInput) {
        this.#hiddenInputCountryEl = existingInput;
      } else {
        this.#hiddenInputCountryEl = createEl("input", {
          type: "hidden",
          name: names.country
        });
        wrapper.appendChild(this.#hiddenInputCountryEl);
      }
    }
  }
  //* For each country: add a country list item <li> to the countryList <ul> container.
  #appendListItems() {
    const frag = document.createDocumentFragment();
    const liClass = this.#withSlotClass("countryListItem", CLASSES.COUNTRY_ITEM);
    for (let i = 0; i < this.#countries.length; i++) {
      const c = this.#countries[i];
      const listItem = createEl("li", {
        id: `iti-${this.#id}__item-${c.iso2}`,
        class: liClass,
        role: "option",
        [ARIA.SELECTED]: "false"
      });
      listItem.dataset[DATA_KEYS.DIAL_CODE] = c.dialCode;
      listItem.dataset[DATA_KEYS.ISO2] = c.iso2;
      this.#listItemByIso2.set(c.iso2, listItem);
      if (this.#options.showFlags) {
        createEl(
          "div",
          {
            class: this.#withSlotClass(
              "countryListItemFlag",
              `${CLASSES.FLAG} iti__${c.iso2}`
            )
          },
          listItem
        );
      }
      const nameEl = createEl(
        "span",
        { class: this.#withSlotClass("countryName", "iti__country-name") },
        listItem
      );
      nameEl.textContent = `${c.name} `;
      const dialEl = createEl(
        "span",
        { class: this.#withSlotClass("dialCode", "iti__dial-code") },
        nameEl
      );
      if (this.#isRTL) {
        dialEl.setAttribute("dir", "ltr");
      }
      dialEl.textContent = `(+${c.dialCode})`;
      frag.appendChild(listItem);
    }
    this.#countryListEl.appendChild(frag);
  }
  //* Update the input padding to make space for (1) the selected country/globe, (2) the arrow, and (3) the separate dial code, all of which are optional, hence handling this in the JS rather than CSS.
  #updateInputPadding() {
    if (this.#selectedCountryEl) {
      const fallbackWidth = this.#options.separateDialCode ? LAYOUT.FALLBACK_SELECTED_COUNTRY_WITH_DIAL_WIDTH : LAYOUT.FALLBACK_SELECTED_COUNTRY_NO_DIAL_WIDTH;
      const selectedCountryWidth = this.#selectedCountryEl.offsetWidth || this.#getHiddenSelectedCountryWidth() || fallbackWidth;
      const inputPadding = selectedCountryWidth + LAYOUT.INPUT_PADDING_EXTRA_LEFT;
      this.telInputEl.style.paddingLeft = `${inputPadding}px`;
    }
  }
  //* Keep the input padding in sync when the selected country's rendered width changes — e.g. responsive font-size shifts that change the dial code text width. Skip while hidden (offsetWidth === 0) so we don't waste work or clobber the padding using a fallback constant.
  #observeSelectedCountryResize() {
    if (!this.#selectedCountryEl || typeof ResizeObserver === "undefined") {
      return;
    }
    this.#resizeObserver = new ResizeObserver(() => {
      if (this.#selectedCountryEl?.offsetWidth) {
        this.#updateInputPadding();
      }
    });
    this.#resizeObserver.observe(this.#selectedCountryEl);
  }
  //* When input is in a hidden container during init, we cannot calculate the selected country width.
  //* Fix: clone the markup, make it invisible, add it to the end of the DOM, and then measure it's width.
  //* To get the right styling to apply, all we need is a shallow clone of the container,
  //* and then to inject a deep clone of the selectedCountryEl element.
  //* Measures in the LOCAL document.body: appending to the local body escapes any hidden ancestor container, and the input's own frame is where intl-tel-input's styles live (so the clone lays out correctly). We deliberately do NOT escape to window.top: that only measures correctly in the rare case where the top frame also loads the library's styles, and measures wrong when it doesn't (e.g. a same-origin iframe whose outer frame lacks the styles — cf. #2178). If the local frame itself isn't laid out yet (e.g. an iframe hidden during init), this returns 0 and the caller falls back to a sane constant; the ResizeObserver in #observeSelectedCountryResize then corrects the padding once the input becomes visible.
  #getHiddenSelectedCountryWidth() {
    if (!this.telInputEl.parentNode) {
      return 0;
    }
    const body = document.body;
    const containerClone = this.telInputEl.parentNode.cloneNode(
      false
    );
    containerClone.style.visibility = "hidden";
    body.appendChild(containerClone);
    const countryContainerClone = this.#countryContainerEl.cloneNode();
    containerClone.appendChild(countryContainerClone);
    const selectedCountryClone = this.#selectedCountryEl.cloneNode(
      true
    );
    countryContainerClone.appendChild(selectedCountryClone);
    const width = selectedCountryClone.offsetWidth;
    body.removeChild(containerClone);
    return width;
  }
  //* Measure the inline dropdown size once, lazily, on first open — see #getHiddenInlineDropdownSize for why measuring forces a reflow. Memoised via #inlineDropdownHeight so subsequent opens are free.
  //* Captured for two uses: (1) on open, decide whether to position the dropdown above or below the input; (2) when countrySearch is enabled, pin the dropdown height (and, when matchDropdownWidth is disabled, width) so it doesn't jump around as the country list is filtered.
  #ensureInlineDropdownSizeMeasured() {
    if (this.#inlineDropdownHeight !== void 0) {
      return;
    }
    const { countrySearch, matchDropdownWidth } = this.#options;
    const { height, width } = this.#getHiddenInlineDropdownSize();
    this.#inlineDropdownHeight = height;
    if (countrySearch) {
      this.#countrySelectorEl.style.height = `${height}px`;
      if (!matchDropdownWidth && width > 0) {
        this.#countrySelectorEl.style.width = `${width}px`;
      }
    }
  }
  // Measure the dropdown by moving it into a temporary hidden container on the body (it needs the right ancestor classes to lay out correctly). Restores it to its original position afterwards — a no-op during init (when it is still detached) but required when called lazily on first open (when it is already inserted).
  //* Deliberately measures in the LOCAL document.body (not window.top): this runs on first open, when the input's own frame is visibly rendered and styled. Escaping to the top frame breaks when the input is inside a same-origin iframe whose outer frame lacks intl-tel-input's styles (e.g. Storybook), as the dropdown would then be measured unstyled and come out far too tall (issue #2178).
  #getHiddenInlineDropdownSize() {
    const body = document.body;
    const selectorEl = this.#countrySelectorEl;
    const originalParent = selectorEl.parentNode;
    const originalNextSibling = selectorEl.nextSibling;
    selectorEl.classList.remove(CLASSES.HIDE);
    const tempContainer = createEl("div", {
      class: "iti iti--inline-country-selector"
    });
    tempContainer.appendChild(selectorEl);
    tempContainer.style.visibility = "hidden";
    body.appendChild(tempContainer);
    const height = selectorEl.offsetHeight;
    const width = selectorEl.offsetWidth;
    body.removeChild(tempContainer);
    selectorEl.classList.add(CLASSES.HIDE);
    if (originalParent) {
      originalParent.insertBefore(selectorEl, originalNextSibling);
    }
    return {
      height: height > 0 ? height : LAYOUT.FALLBACK_DROPDOWN_HEIGHT,
      width
    };
  }
  //* Update search results text (for a11y).
  #updateSearchResultsA11yText() {
    const { uiTranslations } = this.#options;
    const count = this.#countryListEl.childElementCount;
    this.#searchResultsLiveRegionEl.textContent = uiTranslations.searchSummaryAria(count);
  }
  //* Country search: Filter the countries according to the search query.
  #filterCountriesByQuery(query) {
    let matchedCountries;
    if (query === "") {
      matchedCountries = this.#countries;
    } else {
      const normalisedQuery = Numerals.toAscii(query);
      matchedCountries = getMatchedCountries(
        this.#countries,
        this.#searchTokens,
        normalisedQuery
      );
    }
    this.#showFilteredCountries(matchedCountries);
  }
  //* Pre-fill the search input with "+" and show all countries
  //* (used when user types "+" in the phone input to open the country selector).
  //* Explicitly focus the search input (openCountrySelector skips this when
  //* dropdownAlwaysOpen, but here we need focus to redirect subsequent keystrokes).
  prefillSearchWithPlus() {
    this.#searchInputEl.value = "+";
    this.#searchInputEl.focus();
    this.#filterCountriesByQuery("");
  }
  // Search input handlers
  #applySearchFilter() {
    const inputQuery = this.#searchInputEl.value.trim();
    this.#filterCountriesByQuery(inputQuery);
    if (this.#searchInputEl.value) {
      this.#searchClearButtonEl.classList.remove(CLASSES.HIDE);
    } else {
      this.#searchClearButtonEl.classList.add(CLASSES.HIDE);
    }
  }
  #handleSearchChange() {
    if (this.#searchDebounceTimer) {
      clearTimeout(this.#searchDebounceTimer);
    }
    this.#searchDebounceTimer = setTimeout(() => {
      this.#applySearchFilter();
      this.#searchDebounceTimer = null;
    }, TIMINGS.SEARCH_DEBOUNCE_MS);
  }
  #handleSearchClear() {
    this.#searchInputEl.value = "";
    this.#searchInputEl.focus();
    this.#applySearchFilter();
  }
  //* Check if a country list item element is visible within it's container (the country list), else scroll until it is.
  #scrollCountryListToItem(element) {
    const container = this.#countryListEl;
    const containerRect = container.getBoundingClientRect();
    const elementRect = element.getBoundingClientRect();
    const offsetTop = elementRect.top - containerRect.top + container.scrollTop;
    if (elementRect.top < containerRect.top) {
      container.scrollTop = offsetTop;
    } else if (elementRect.bottom > containerRect.bottom) {
      container.scrollTop = offsetTop - containerRect.height + elementRect.height;
    }
  }
  //* The element that holds focus while the country selector is open: the search input, or (when countrySearch is disabled) the country list itself.
  #getOpenFocusEl() {
    return this.#options.countrySearch ? this.#searchInputEl : this.#countryListEl;
  }
  //* Remove highlighting from the previous list item and highlight the new one.
  #highlightListItem(listItem, doScroll = true) {
    this.#highlightedListItemEl?.classList.remove(CLASSES.HIGHLIGHT);
    if (listItem) {
      listItem.classList.add(CLASSES.HIGHLIGHT);
      const activeDescendant = listItem.getAttribute("id") || "";
      this.#getOpenFocusEl().setAttribute(
        ARIA.ACTIVE_DESCENDANT,
        activeDescendant
      );
      if (doScroll) {
        this.#scrollCountryListToItem(listItem);
      }
      this.#highlightedListItemEl = listItem;
    } else {
      this.#highlightedListItemEl = null;
    }
  }
  //* Bind a form-submit listener that syncs the hidden inputs with the current phone number
  //* and country iso2. No-op if there are no hidden inputs or the input is not in a form.
  bindHiddenInputSubmitListener(signal, getPhone, getCountryIso2) {
    const form = this.telInputEl.form;
    if (!form || !this.#hiddenInputPhoneEl && !this.#hiddenInputCountryEl) {
      return;
    }
    form.addEventListener(
      "submit",
      () => {
        if (this.#hiddenInputPhoneEl) {
          this.#hiddenInputPhoneEl.value = getPhone();
        }
        if (this.#hiddenInputCountryEl) {
          this.#hiddenInputCountryEl.value = getCountryIso2();
        }
      },
      { signal }
    );
  }
  //* Wire up triggers that open/close the country selector: label click (focus input or swallow repeat click),
  //* selected-country click (open), and keydown on countryContainer (open on arrow/space/enter, close on tab).
  bindAllInitialCountrySelectorListeners(signal, onOpen, onClose) {
    const label = this.telInputEl.closest("label");
    if (label) {
      label.addEventListener(
        "click",
        (e) => {
          if (!this.isCountrySelectorOpen()) {
            this.telInputEl.focus();
          } else {
            e.preventDefault();
          }
        },
        { signal }
      );
    }
    this.#selectedCountryEl.addEventListener(
      "click",
      () => {
        if (!this.isCountrySelectorOpen() && !this.telInputEl.disabled && !this.telInputEl.readOnly) {
          onOpen();
        }
      },
      { signal }
    );
    this.#countryContainerEl.addEventListener(
      "keydown",
      (e) => {
        const openKeys = [
          KEYS.ARROW_UP,
          KEYS.ARROW_DOWN,
          KEYS.SPACE,
          KEYS.ENTER
        ];
        if (!this.isCountrySelectorOpen() && openKeys.includes(e.key)) {
          e.preventDefault();
          e.stopPropagation();
          onOpen();
        }
        if (e.key === KEYS.TAB) {
          onClose();
        }
      },
      { signal }
    );
  }
  //* Open the country selector: create a fresh AbortController, do the DOM work, and wire up all
  //* open-state listeners (which invoke the caller's onSelect / onClose callbacks).
  openCountrySelector(onSelect, onClose) {
    const { dropdownAlwaysOpen } = this.#options;
    this.#countrySelectorAbortController = new AbortController();
    if (this.#options.countrySelectorMode !== COUNTRY_SELECTOR_MODE.FULLSCREEN) {
      this.#ensureInlineDropdownSizeMeasured();
    }
    this.ensureDropdownWidthSet();
    if (this.#detachedCountrySelectorEl) {
      this.#injectAndPositionDetachedCountrySelector();
    } else {
      const positionBelow = this.#shouldPositionDropdownBelowInput();
      const distance = this.telInputEl.offsetHeight + LAYOUT.DROPDOWN_MARGIN;
      if (positionBelow) {
        this.#countrySelectorEl.style.top = `${distance}px`;
      } else {
        this.#countrySelectorEl.style.bottom = `${distance}px`;
      }
    }
    this.#countrySelectorEl.classList.remove(CLASSES.HIDE);
    this.#selectedCountryEl.setAttribute(ARIA.EXPANDED, "true");
    const itemToHighlight = this.#selectedListItemEl ?? this.#countryListEl.firstElementChild;
    if (itemToHighlight) {
      this.#highlightListItem(itemToHighlight);
    }
    if (!dropdownAlwaysOpen) {
      this.#getOpenFocusEl().focus();
    }
    if (this.#options.countrySelectorMode === COUNTRY_SELECTOR_MODE.FULLSCREEN && this.#detachedCountrySelectorEl && window.visualViewport) {
      this.#adjustFullscreenPopupToViewport();
      window.visualViewport.addEventListener(
        "resize",
        () => {
          this.#adjustFullscreenPopupToViewport();
          if (this.#highlightedListItemEl) {
            this.#scrollCountryListToItem(this.#highlightedListItemEl);
          }
        },
        { signal: this.#countrySelectorAbortController.signal }
      );
    }
    this.#arrowEl.classList.add(CLASSES.ARROW_UP);
    this.#bindCountrySelectorOpenListeners(onSelect, onClose);
  }
  //* Wire up all listeners needed while the country selector is open: list-item hover (highlight),
  //* list-item click & enter key (select), click-off & escape (close), search input (filter),
  //* (when countrySearch disabled) typed-char hidden search, and (when the country selector is in an
  //* external container) update (fixed) position on scroll/resize.
  #bindCountrySelectorOpenListeners(onSelect, onClose) {
    const signal = this.#countrySelectorAbortController.signal;
    this.#bindListItemHover(signal);
    this.#bindListItemClick(signal, onSelect);
    if (!this.#options.dropdownAlwaysOpen) {
      this.#bindOutsideClickToClose(signal, onClose);
    }
    this.#bindCountrySelectorKeydownListener(signal, onSelect, onClose);
    if (this.#options.countrySearch) {
      this.#bindSearchInputListener(signal);
    }
    if (this.#options.countrySelectorMode === COUNTRY_SELECTOR_MODE.DROPDOWN && this.#options.dropdownParent && !supportsCssAnchor) {
      document.addEventListener("scroll", onClose, { signal, capture: true, passive: true });
    }
  }
  //* When mouse over a list item, just highlight that one (so if they hit "enter" we know which to select).
  #bindListItemHover(signal) {
    this.#countryListEl.addEventListener(
      "mouseover",
      (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          this.#highlightListItem(listItem, false);
        }
      },
      { signal }
    );
  }
  //* Delegate clicks on the country list to the caller's onSelect callback, passing the clicked list item.
  #bindListItemClick(signal, onSelect) {
    this.#countryListEl.addEventListener(
      "click",
      (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          onSelect(listItem);
        }
      },
      { signal }
    );
  }
  //* Invoke onClickOff when the user clicks anywhere outside the country selector.
  #bindOutsideClickToClose(signal, onClickOff) {
    setTimeout(() => {
      document.documentElement.addEventListener(
        "click",
        (e) => {
          if (!this.#countrySelectorEl.contains(e.target)) {
            onClickOff();
          }
        },
        { signal }
      );
    }, 0);
  }
  //* Keyboard navigation while the country selector is open: arrow keys navigate, hidden-search keys filter,
  //* and enter/escape invoke the caller's callbacks (which handle country selection / close).
  //* Uses keydown rather than keypress so non-char keys (arrow, esc) fire and so holding a key repeats.
  #bindCountrySelectorKeydownListener(signal, onEnter, onEscape) {
    let query = "";
    let queryTimer = null;
    const handleKeydown = (e) => {
      const allowedKeys = [
        KEYS.ARROW_UP,
        KEYS.ARROW_DOWN,
        KEYS.ENTER,
        KEYS.ESC
      ];
      if (allowedKeys.includes(e.key)) {
        e.preventDefault();
        e.stopPropagation();
        if (e.key === KEYS.ARROW_UP || e.key === KEYS.ARROW_DOWN) {
          this.#handleUpDownKey(e.key);
        } else if (e.key === KEYS.ENTER && !e.isComposing) {
          onEnter(this.#highlightedListItemEl);
        } else if (e.key === KEYS.ESC) {
          onEscape();
          this.#selectedCountryEl.focus();
        }
      }
      if (!this.#options.countrySearch && REGEX.HIDDEN_SEARCH_CHAR.test(e.key)) {
        e.stopPropagation();
        if (queryTimer) {
          clearTimeout(queryTimer);
        }
        query += e.key.toLowerCase();
        this.#searchForCountry(query);
        queryTimer = setTimeout(() => {
          query = "";
        }, TIMINGS.HIDDEN_SEARCH_RESET_MS);
      }
    };
    this.#selectedCountryEl?.addEventListener("keydown", handleKeydown, { signal });
    this.#countrySelectorEl?.addEventListener("keydown", handleKeydown, { signal });
    if (this.#detachedCountrySelectorEl) {
      this.#countrySelectorEl?.addEventListener(
        "keydown",
        (e) => {
          if (e.key === KEYS.TAB) {
            e.preventDefault();
            onEscape();
            const focusEl = e.shiftKey ? this.#selectedCountryEl : this.telInputEl;
            focusEl.focus();
          }
        },
        { signal }
      );
    }
  }
  //* Wire up country search input listener: typing filters the list, the clear button resets it.
  #bindSearchInputListener(signal) {
    this.#searchInputEl.addEventListener(
      "input",
      () => this.#handleSearchChange(),
      { signal }
    );
    this.#searchClearButtonEl.addEventListener(
      "click",
      () => this.#handleSearchClear(),
      { signal }
    );
  }
  //* Hidden search (countrySearch disabled): jump to the first list item whose name starts with the query.
  #searchForCountry(query) {
    const match = findFirstCountryStartingWith(
      this.#countries,
      this.#searchTokens,
      query
    );
    if (match) {
      const listItem = this.#listItemByIso2.get(match.iso2);
      this.#highlightListItem(listItem);
    }
  }
  //* Highlight the next/prev item in the list (and ensure it is visible).
  #handleUpDownKey(key) {
    let next = key === KEYS.ARROW_UP ? this.#highlightedListItemEl?.previousElementSibling : this.#highlightedListItemEl?.nextElementSibling;
    if (!next && this.#countryListEl.childElementCount > 1) {
      next = key === KEYS.ARROW_UP ? this.#countryListEl.lastElementChild : this.#countryListEl.firstElementChild;
    }
    if (next) {
      this.#highlightListItem(next);
    }
  }
  // Update the selected list item in the country list
  #updateSelectedListItem(iso2) {
    if (this.#selectedListItemEl && this.#selectedListItemEl.dataset[DATA_KEYS.ISO2] !== iso2) {
      this.#selectedListItemEl.setAttribute(ARIA.SELECTED, "false");
      this.#selectedListItemEl.querySelector(".iti__country-check")?.remove();
      this.#selectedListItemEl = null;
    }
    if (iso2 && !this.#selectedListItemEl) {
      const newListItem = this.#countryListEl.querySelector(
        `[data-iso2="${iso2}"]`
      );
      if (newListItem) {
        newListItem.setAttribute(ARIA.SELECTED, "true");
        const checkIcon = createEl(
          "span",
          {
            class: this.#withSlotClass("countryCheck", "iti__country-check"),
            [ARIA.HIDDEN]: "true"
          },
          newListItem
        );
        checkIcon.appendChild(buildCheckIcon());
        this.#selectedListItemEl = newListItem;
        if (this.#options.dropdownAlwaysOpen) {
          this.#highlightListItem(newListItem);
        }
      }
    }
  }
  //* Country search: Filter the country list to the given array of countries.
  #showFilteredCountries(matchedCountries) {
    this.#countryListEl.replaceChildren();
    let noCountriesAddedYet = true;
    for (const c of matchedCountries) {
      const listItem = this.#listItemByIso2.get(c.iso2);
      if (listItem) {
        this.#countryListEl.appendChild(listItem);
        if (noCountriesAddedYet) {
          this.#highlightListItem(listItem, false);
          noCountriesAddedYet = false;
        }
      }
    }
    if (noCountriesAddedYet) {
      this.#highlightListItem(null);
      if (this.#noResultsMessageEl) {
        this.#noResultsMessageEl.classList.remove(CLASSES.HIDE);
      }
    } else if (this.#noResultsMessageEl) {
      this.#noResultsMessageEl.classList.add(CLASSES.HIDE);
    }
    this.#countryListEl.scrollTop = 0;
    this.#updateSearchResultsA11yText();
  }
  // UI: Close the country selector (DOM + abort scoped listeners).
  closeCountrySelector() {
    const { countrySearch } = this.#options;
    this.#countrySelectorAbortController.abort();
    this.#countrySelectorAbortController = null;
    this.#countrySelectorEl.classList.add(CLASSES.HIDE);
    this.#selectedCountryEl.setAttribute(ARIA.EXPANDED, "false");
    this.#getOpenFocusEl().removeAttribute(ARIA.ACTIVE_DESCENDANT);
    if (countrySearch) {
      this.#searchInputEl.value = "";
      this.#applySearchFilter();
      if (this.#highlightedListItemEl) {
        this.#highlightedListItemEl.classList.remove(CLASSES.HIGHLIGHT);
        this.#highlightedListItemEl = null;
      }
    }
    this.#arrowEl.classList.remove(CLASSES.ARROW_UP);
    if (this.#detachedCountrySelectorEl) {
      this.#detachedCountrySelectorEl.remove();
      this.#detachedCountrySelectorEl.style.top = "";
      this.#detachedCountrySelectorEl.style.bottom = "";
      this.#detachedCountrySelectorEl.style.height = "";
      this.#detachedCountrySelectorEl.style.paddingLeft = "";
      this.#detachedCountrySelectorEl.style.paddingRight = "";
    } else {
      this.#countrySelectorEl.style.top = "";
      this.#countrySelectorEl.style.bottom = "";
    }
  }
  #shouldPositionDropdownBelowInput() {
    if (this.#options.dropdownAlwaysOpen) {
      return true;
    }
    const inputPos = this.telInputEl.getBoundingClientRect();
    const spaceAbove = inputPos.top;
    const spaceBelow = window.innerHeight - inputPos.bottom;
    return spaceBelow >= this.#inlineDropdownHeight || spaceBelow >= spaceAbove;
  }
  // inject the country selector into its detached wrapper and apply positioning styles
  #injectAndPositionDetachedCountrySelector() {
    const isFullscreen = this.#options.countrySelectorMode === COUNTRY_SELECTOR_MODE.FULLSCREEN;
    const detachedParent = this.#getDetachedParent();
    if (isFullscreen) {
      if (window.innerWidth >= LAYOUT.NARROW_VIEWPORT_WIDTH) {
        const inputPos = this.telInputEl.getBoundingClientRect();
        this.#detachedCountrySelectorEl.style.paddingLeft = `${inputPos.left}px`;
        this.#detachedCountrySelectorEl.style.paddingRight = `${window.innerWidth - inputPos.right}px`;
      }
    } else {
      this.#setupCssAnchorPositioning();
    }
    if (!isFullscreen && !supportsCssAnchor) {
      const inputPos = this.telInputEl.getBoundingClientRect();
      this.#detachedCountrySelectorEl.style.left = `${inputPos.left}px`;
      if (this.#shouldPositionDropdownBelowInput()) {
        this.#detachedCountrySelectorEl.style.top = `${inputPos.bottom + LAYOUT.DROPDOWN_MARGIN}px`;
      } else {
        this.#detachedCountrySelectorEl.style.top = "unset";
        this.#detachedCountrySelectorEl.style.bottom = `${window.innerHeight - inputPos.top + LAYOUT.DROPDOWN_MARGIN}px`;
      }
    }
    detachedParent.appendChild(this.#detachedCountrySelectorEl);
  }
  //* Wire up CSS Anchor Positioning between the input and the detached country selector using a
  //* unique anchor name per instance. Called lazily on first open (memoised) — the matching styles in
  //* intlTelInput.css only take effect in browsers that support anchor(); elsewhere these
  //* properties are inert. We append our name to any existing anchor-name (read via
  //* getComputedStyle so we pick up CSS-defined values), so consumer-set anchors on the input
  //* are preserved. Caveat: this snapshots the consumer's value once — if they later change
  //* anchor-name via CSS (e.g. a class swap), our inline write will shadow the change.
  #setupCssAnchorPositioning() {
    if (this.#cssAnchorPositioningDone) {
      return;
    }
    this.#cssAnchorPositioningDone = true;
    const anchorName = `--iti-anchor-${this.#id}`;
    const existing = getComputedStyle(this.telInputEl).anchorName;
    this.telInputEl.style.anchorName = existing && existing !== "none" ? `${existing}, ${anchorName}` : anchorName;
    this.#detachedCountrySelectorEl.style.positionAnchor = anchorName;
  }
  // Adjust the fullscreen popup dimensions to match the visual viewport,
  // so it stays above the virtual keyboard on mobile devices.
  #adjustFullscreenPopupToViewport() {
    const vv = window.visualViewport;
    if (!vv || !this.#detachedCountrySelectorEl) {
      return;
    }
    this.#detachedCountrySelectorEl.style.height = `${vv.height}px`;
  }
  // UI: Whether the country selector is currently open (visible).
  isCountrySelectorOpen() {
    return !this.#countrySelectorEl.classList.contains(CLASSES.HIDE);
  }
  // Toggle the loading spinner on the selected flag (used during auto-country geoIP lookup).
  setLoading(isLoading) {
    this.#selectedFlagEl.classList.toggle(CLASSES.LOADING, isLoading);
  }
  //* Play the strict-reject animation (shake, or background-colour flash under prefers-reduced-motion) on the wrapper.
  //* Called when strictMode rejects the whole input (keystroke, or whole paste).
  //* Uses the wrapper (not the input) so any separateDialCode / country button move together with the input.
  playStrictRejectAnimation() {
    if (!this.#options.strictRejectAnimation) {
      return;
    }
    const wrapperEl = this.telInputEl.parentElement;
    if (!wrapperEl) {
      return;
    }
    wrapperEl.classList.remove(CLASSES.STRICT_REJECT_ANIMATION);
    void wrapperEl.offsetWidth;
    wrapperEl.classList.add(CLASSES.STRICT_REJECT_ANIMATION);
    wrapperEl.addEventListener(
      "animationend",
      () => wrapperEl.classList.remove(CLASSES.STRICT_REJECT_ANIMATION),
      { once: true }
    );
  }
  isLoading() {
    return this.#selectedFlagEl.classList.contains(CLASSES.LOADING);
  }
  // Set the disabled state of the input and country selector.
  setDisabled(disabled) {
    this.telInputEl.disabled = disabled;
    if (this.#selectedCountryEl) {
      if (disabled) {
        this.#selectedCountryEl.setAttribute("disabled", "true");
      } else {
        this.#selectedCountryEl.removeAttribute("disabled");
      }
    }
  }
  // Set the readonly state of the input and country selector.
  setReadonly(readonly) {
    this.telInputEl.readOnly = readonly;
    if (this.#selectedCountryEl) {
      if (readonly) {
        this.#selectedCountryEl.setAttribute("disabled", "true");
      } else {
        this.#selectedCountryEl.removeAttribute("disabled");
      }
    }
  }
  setSelectedCountry(selectedCountry) {
    const { countrySelectorMode, showFlags, separateDialCode, uiTranslations } = this.#options;
    const name = selectedCountry?.name;
    const dialCode = selectedCountry?.dialCode;
    const iso2 = selectedCountry?.iso2 ?? "";
    if (countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF) {
      this.#updateSelectedListItem(iso2);
    }
    if (this.#selectedCountryEl) {
      const flagClass = this.#withSlotClass(
        "selectedFlag",
        iso2 && showFlags ? `${CLASSES.FLAG} iti__${iso2}` : `${CLASSES.FLAG} ${CLASSES.GLOBE}`
      );
      let ariaLabel, title;
      let flagContent = null;
      if (iso2) {
        title = name;
        ariaLabel = uiTranslations.selectedCountryAriaLabel.replace("${countryName}", name).replace("${dialCode}", `+${dialCode}`);
        if (!showFlags) {
          flagContent = buildGlobeIcon();
        }
      } else {
        title = uiTranslations.noCountrySelected;
        ariaLabel = uiTranslations.noCountrySelected;
        flagContent = buildGlobeIcon();
      }
      this.#selectedFlagEl.className = flagClass;
      this.#selectedCountryEl.setAttribute("title", title);
      this.#selectedCountryEl.setAttribute(ARIA.LABEL, ariaLabel);
      if (flagContent) {
        this.#selectedFlagEl.replaceChildren(flagContent);
      } else {
        this.#selectedFlagEl.replaceChildren();
      }
    }
    if (separateDialCode) {
      const fullDialCode = dialCode ? `+${dialCode}` : "";
      this.#selectedDialCodeEl.textContent = fullDialCode;
      this.#updateInputPadding();
    }
  }
  destroy() {
    this.telInputEl.iti = void 0;
    delete this.telInputEl.dataset[DATA_KEYS.INSTANCE_ID];
    this.#resizeObserver?.disconnect();
    this.telInputEl.style.paddingLeft = this.#originalPaddingLeft;
    const wrapper = this.telInputEl.parentNode;
    if (wrapper) {
      wrapper.before(this.telInputEl);
      wrapper.remove();
    }
    this.#listItemByIso2.clear();
  }
};

// packages/core/src/js/data/country-data.ts
var processAllCountries = (options) => {
  const { onlyCountries, excludeCountries } = options;
  if (onlyCountries?.length) {
    return data_default.filter(
      (country) => onlyCountries.includes(country.iso2)
    );
  } else if (excludeCountries?.length) {
    return data_default.filter(
      (country) => !excludeCountries.includes(country.iso2)
    );
  }
  return [...data_default];
};
var generateCountryNames = (countries, options) => {
  const { countryNameLocale, countryNameOverrides, uiTranslations } = options;
  const bundledCountryNames = uiTranslations?.countryNames;
  let displayNames;
  try {
    const hasDisplayNames = typeof Intl !== "undefined" && typeof Intl.DisplayNames === "function";
    if (hasDisplayNames) {
      displayNames = new Intl.DisplayNames(countryNameLocale, {
        type: "region"
      });
    } else {
      displayNames = null;
    }
  } catch (e) {
    console.error(e);
    displayNames = null;
  }
  for (const c of countries) {
    c.name = countryNameOverrides[c.iso2] || bundledCountryNames?.[c.iso2] || displayNames?.of(c.iso2.toUpperCase()) || "";
  }
};
var processDialCodes = (countries) => {
  const dialCodes = /* @__PURE__ */ new Set();
  let dialCodeMaxLength = 0;
  const dialCodeToIso2Map = {};
  const addToDialCodeMap = (iso2, dialCode) => {
    if (!iso2 || !dialCode) {
      return;
    }
    if (dialCode.length > dialCodeMaxLength) {
      dialCodeMaxLength = dialCode.length;
    }
    if (!Object.hasOwn(dialCodeToIso2Map, dialCode)) {
      dialCodeToIso2Map[dialCode] = [];
    }
    const iso2List = dialCodeToIso2Map[dialCode];
    if (iso2List.includes(iso2)) {
      return;
    }
    iso2List.push(iso2);
  };
  const countriesSortedByPriority = [...countries].sort(
    (a, b) => a.priority - b.priority
  );
  for (const c of countriesSortedByPriority) {
    if (!dialCodes.has(c.dialCode)) {
      dialCodes.add(c.dialCode);
    }
    for (let k = 1; k < c.dialCode.length; k++) {
      const partialDialCode = c.dialCode.substring(0, k);
      addToDialCodeMap(c.iso2, partialDialCode);
    }
    addToDialCodeMap(c.iso2, c.dialCode);
    if (c.areaCodes) {
      const rootIso2Code = dialCodeToIso2Map[c.dialCode][0];
      for (const areaCode of c.areaCodes) {
        for (let k = 1; k < areaCode.length; k++) {
          const partialAreaCode = areaCode.substring(0, k);
          const partialDialCode = c.dialCode + partialAreaCode;
          addToDialCodeMap(rootIso2Code, partialDialCode);
          addToDialCodeMap(c.iso2, partialDialCode);
        }
        addToDialCodeMap(c.iso2, c.dialCode + areaCode);
      }
    }
  }
  return { dialCodes, dialCodeMaxLength, dialCodeToIso2Map };
};
var sortCountries = (countries, options) => {
  const { countryOrder } = options;
  countries.sort((a, b) => {
    if (countryOrder) {
      const aIndex = countryOrder.indexOf(a.iso2);
      const bIndex = countryOrder.indexOf(b.iso2);
      const aIndexExists = aIndex > -1;
      const bIndexExists = bIndex > -1;
      if (aIndexExists || bIndexExists) {
        if (aIndexExists && bIndexExists) {
          return aIndex - bIndex;
        }
        return aIndexExists ? -1 : 1;
      }
    }
    return a.name.localeCompare(b.name);
  });
};

// packages/core/src/js/data/intl-regionless.ts
var regionlessDialCodes = /* @__PURE__ */ new Set([
  "800",
  "808",
  "870",
  "881",
  "882",
  "883",
  "888",
  "979"
]);
var hasRegionlessDialCode = (number) => {
  const dialCode = getNumeric(number).slice(0, 3);
  return number.startsWith("+") && regionlessDialCodes.has(dialCode);
};

// packages/core/src/js/format/formatting.ts
var stripSeparateDialCode = (fullNumber, hasValidDialCode, separateDialCode, selectedCountry) => {
  if (!separateDialCode || !hasValidDialCode) {
    return fullNumber;
  }
  const dialCode = `+${selectedCountry.dialCode}`;
  const start = fullNumber[dialCode.length] === " " || fullNumber[dialCode.length] === "-" ? dialCode.length + 1 : dialCode.length;
  return fullNumber.substring(start);
};
var formatNumberAsYouType = (fullNumber, telInputValue, utils, selectedCountry, separateDialCode) => {
  const result = utils ? utils.formatNumberAsYouType(fullNumber, selectedCountry?.iso2) : fullNumber;
  const dialCode = selectedCountry?.dialCode;
  if (separateDialCode && telInputValue.charAt(0) !== "+" && result.includes(`+${dialCode}`)) {
    const afterDialCode = result.split(`+${dialCode}`)[1] || "";
    return afterDialCode.trim();
  }
  return result;
};

// packages/core/src/js/format/caret.ts
var computeNewCaretPosition = (relevantChars, formattedValue, prevCaretPos, isDeleteForwards) => {
  if (prevCaretPos === 0 && !isDeleteForwards) {
    return 0;
  }
  let relevantCharCount = 0;
  for (let i = 0; i < formattedValue.length; i++) {
    if (/[+0-9]/.test(formattedValue[i])) {
      relevantCharCount++;
    }
    if (relevantCharCount === relevantChars && !isDeleteForwards) {
      return i + 1;
    }
    if (isDeleteForwards && relevantCharCount === relevantChars + 1) {
      return i;
    }
  }
  return formattedValue.length;
};

// packages/core/src/js/data/nanp-regionless.ts
var regionlessNanpAreaCodes = /* @__PURE__ */ new Set([
  "800",
  "822",
  "833",
  "844",
  "855",
  "866",
  "877",
  "880",
  "881",
  "882",
  "883",
  "884",
  "885",
  "886",
  "887",
  "888",
  "889"
]);
var isRegionlessNanp = (number) => {
  const numeric = getNumeric(number);
  if (numeric.startsWith(DIAL_CODE.NANP) && numeric.length >= 4) {
    const areaCode = numeric.substring(1, 4);
    return regionlessNanpAreaCodes.has(areaCode);
  }
  return false;
};

// packages/core/src/js/intlTelInput.ts
var nextId = 0;
var ensureUtils = (methodName) => {
  if (!intlTelInput.utils) {
    throw new Error(
      `intlTelInput.utils is required for ${methodName}(). See: https://intl-tel-input.com/docs/utils`
    );
  }
};
var createDeferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
};
var Iti = class _Iti {
  //* PUBLIC FIELDS - READONLY
  //* Can't be private as it's called from intlTelInput convenience wrapper.
  id;
  // accessed externally via iti.promise.then(...)
  promise;
  //* PRIVATE FIELDS
  #ui;
  #options;
  #isAndroid;
  // country data
  #countries;
  #dialCodeMaxLength;
  #dialCodeToIso2Map;
  #dialCodes;
  #countryByIso2;
  #searchTokens;
  #selectedCountry = null;
  #maxCoreNumberLength = null;
  #fallbackCountryIso2;
  // is this instance still active (not destroyed)
  #isActive = true;
  #abortController;
  #numerals;
  //* Tracks whether the user has typed/pasted their own formatting chars, so AYT-formatting should back off.
  #userOverrideFormatting = false;
  #strictPasteSnapshot = null;
  #autoCountryDeferred;
  #utilsDeferred;
  constructor(input, customOptions = {}) {
    this.id = nextId++;
    UI.validateInput(input);
    const validatedOptions = validateOptions(customOptions);
    this.#options = { ...defaults, ...validatedOptions };
    normaliseOptions(this.#options);
    applyOptionSideEffects(this.#options);
    this.#ui = new UI(input, this.#options, this.id);
    this.#isAndroid = typeof navigator !== "undefined" && /Android/i.test(navigator.userAgent);
    this.#numerals = new Numerals(input.value);
    this.promise = this.#createInitPromise(this.#options);
    this.#countries = processAllCountries(this.#options);
    const { dialCodes, dialCodeMaxLength, dialCodeToIso2Map } = processDialCodes(this.#countries);
    this.#dialCodes = dialCodes;
    this.#dialCodeMaxLength = dialCodeMaxLength;
    this.#dialCodeToIso2Map = dialCodeToIso2Map;
    this.#countryByIso2 = new Map(this.#countries.map((c) => [c.iso2, c]));
    this.#init();
  }
  #getTelInputValue() {
    const inputValue = this.#ui.telInputEl.value.trim();
    return this.#numerals.normalise(inputValue);
  }
  #setTelInputValue(asciiValue) {
    this.#ui.telInputEl.value = this.#numerals.denormalise(asciiValue);
  }
  #createInitPromise(options) {
    const { initialCountry, initialCountryLookup, loadUtils } = options;
    const needsAutoCountryDeferred = !initialCountry && Boolean(initialCountryLookup);
    const needsUtilsDeferred = Boolean(loadUtils) && !intlTelInput.utils;
    if (needsAutoCountryDeferred) {
      this.#autoCountryDeferred = createDeferred();
    }
    if (needsUtilsDeferred) {
      this.#utilsDeferred = createDeferred();
    }
    return Promise.all([
      this.#autoCountryDeferred?.promise,
      this.#utilsDeferred?.promise
    ]).then(() => {
    });
  }
  #init() {
    this.#abortController = new AbortController();
    this.#processCountryData();
    this.#ui.buildMarkup(this.#countries, this.#searchTokens);
    this.#setInitialState();
    this.#initListeners();
    this.#startAsyncLoads();
    if (this.#options.dropdownAlwaysOpen) {
      this.openCountrySelector();
    }
  }
  //********************
  //*  PRIVATE METHODS
  //********************
  //* Prepare all of the country data, including onlyCountries, excludeCountries, countryOrder options.
  #processCountryData() {
    generateCountryNames(this.#countries, this.#options);
    sortCountries(this.#countries, this.#options);
    this.#searchTokens = buildSearchTokens(this.#countries);
  }
  //* Set the initial state of the input value and the selected country by:
  //* 1. Extracting a dial code from the given number
  //* 2. Using explicit initialCountry
  #setInitialState(overrideAutoCountry = false) {
    const attributeValueRaw = this.#ui.telInputEl.getAttribute("value");
    const attributeValue = this.#numerals.normalise(attributeValueRaw ?? "");
    const inputValue = this.#getTelInputValue();
    const useAttribute = attributeValue && attributeValue.startsWith("+") && (!inputValue || !inputValue.startsWith("+"));
    const value = useAttribute ? attributeValue : inputValue;
    const dialCode = this.#getDialCode(value);
    const isRegionlessNanpNumber = isRegionlessNanp(value);
    const { initialCountry, initialCountryLookup } = this.#options;
    const isAutoCountry = !initialCountry && Boolean(initialCountryLookup);
    const resolvedInitialCountry = isAutoCountry && intlTelInput.autoCountry ? intlTelInput.autoCountry : initialCountry;
    const doingAutoCountryLookup = isAutoCountry && !overrideAutoCountry && !intlTelInput.autoCountry;
    const isValidInitialCountry = isIso2(resolvedInitialCountry);
    if (dialCode) {
      if (isRegionlessNanpNumber) {
        if (isValidInitialCountry) {
          this.#updateSelectedCountry(resolvedInitialCountry);
        } else if (!doingAutoCountryLookup) {
          this.#updateSelectedCountry(US.ISO2);
        }
      } else {
        if (isValidInitialCountry) {
          this.#updateSelectedCountry(resolvedInitialCountry);
        }
        this.#updateCountryFromNumber(value);
      }
    } else if (isValidInitialCountry) {
      this.#updateSelectedCountry(resolvedInitialCountry);
    } else if (!doingAutoCountryLookup) {
      this.#updateSelectedCountry("");
    }
    if (value) {
      this.#updateValueFromNumber(value);
    }
  }
  //* Initialise the main event listeners: input keyup, and click selected country.
  #initListeners() {
    this.#bindAllTelInputListeners();
    if (this.#options.countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF) {
      this.#ui.bindAllInitialCountrySelectorListeners(
        this.#abortController.signal,
        () => this.openCountrySelector(),
        () => this.#closeCountrySelectorInternal()
      );
    }
    this.#ui.bindHiddenInputSubmitListener(
      this.#abortController.signal,
      () => this.getNumber(),
      () => this.#selectedCountry?.iso2 || ""
    );
  }
  //* Init requests: utils script / initial country lookup.
  #startAsyncLoads() {
    if (this.#utilsDeferred) {
      const { loadUtils } = this.#options;
      const doAttachUtils = () => {
        intlTelInput.attachUtils(loadUtils).catch(() => {
        });
      };
      if (intlTelInput.documentReady()) {
        doAttachUtils();
      } else {
        window.addEventListener("load", doAttachUtils, {
          signal: this.#abortController.signal
        });
      }
    }
    if (this.#autoCountryDeferred) {
      if (this.#selectedCountry) {
        this.#autoCountryDeferred.resolve();
      } else {
        this.#loadAutoCountry();
      }
    }
  }
  //* Perform the initial country lookup.
  async #loadAutoCountry() {
    if (intlTelInput.autoCountry) {
      this.#handleAutoCountryLoaded();
      return;
    }
    this.#ui.setLoading(true);
    if (intlTelInput.startedLoadingAutoCountry) {
      return;
    }
    intlTelInput.startedLoadingAutoCountry = true;
    if (typeof this.#options.initialCountryLookup === "function") {
      let timeoutId;
      try {
        const iso2 = await Promise.race([
          this.#options.initialCountryLookup(),
          new Promise((_, reject) => {
            timeoutId = setTimeout(
              () => reject(new Error("intl-tel-input: initialCountryLookup timed out after 10s")),
              1e4
            );
          })
        ]);
        const iso2Lower = typeof iso2 === "string" ? iso2.toLowerCase() : "";
        if (!isIso2(iso2Lower)) {
          intlTelInput.startedLoadingAutoCountry = false;
          _Iti.forEachInstance("handleAutoCountryFailure");
          return;
        }
        intlTelInput.autoCountry = iso2Lower;
        setTimeout(() => _Iti.forEachInstance("handleAutoCountryLoaded"));
      } catch {
        intlTelInput.startedLoadingAutoCountry = false;
        _Iti.forEachInstance("handleAutoCountryFailure");
      } finally {
        if (timeoutId !== void 0) {
          clearTimeout(timeoutId);
        }
      }
    }
  }
  #openCountrySelectorWithPlus() {
    this.openCountrySelector();
    this.#ui.prefillSearchWithPlus();
  }
  //* Delete the character just typed (the one immediately before the caret). Used by Android workarounds where we can't preventDefault on keydown.
  #removeJustTypedChar(inputValue) {
    const currentCaretPos = this.#ui.telInputEl.selectionStart || 0;
    const valueBeforeCaret = inputValue.substring(0, currentCaretPos - 1);
    const valueAfterCaret = inputValue.substring(currentCaretPos);
    this.#setTelInputValue(valueBeforeCaret + valueAfterCaret);
    return currentCaretPos - 1;
  }
  //* Initialize the tel input listeners.
  #bindAllTelInputListeners() {
    this.#bindInputListener();
    this.#bindKeydownListener();
    this.#bindStrictPasteListener();
  }
  //* Android workaround for handling plus when separateDialCode enabled (as impossible to handle with keydown/keyup, for which e.key always returns "Unidentified", see https://stackoverflow.com/q/59584061/217866)
  #handleAndroidPlusKey(inputValue) {
    this.#removeJustTypedChar(inputValue);
    this.#openCountrySelectorWithPlus();
  }
  //* Android strictMode workaround: the keydown-based filter can't block these because e.key is "Unidentified" on Android virtual keyboards, so strip them here on input.
  #handleAndroidStrictReject(inputValue, rejectedInput) {
    const newCaretPos = this.#removeJustTypedChar(inputValue);
    this.#ui.telInputEl.setSelectionRange(newCaretPos, newCaretPos);
    this.#ui.playStrictRejectAnimation();
    this.#dispatchEvent(EVENTS.STRICT_REJECT, {
      source: "key",
      rejectedInput,
      reason: "invalid"
    });
  }
  //* Format the input value using libphonenumber's AYT formatter, preserving caret position (called after an input event).
  #formatAsYouType(inputValue, isDeleteForwards) {
    const currentCaretPos = this.#ui.telInputEl.selectionStart || 0;
    const valueBeforeCaret = inputValue.substring(0, currentCaretPos);
    const relevantCharsBeforeCaret = valueBeforeCaret.replace(
      REGEX.NON_PLUS_NUMERIC_GLOBAL,
      ""
    ).length;
    const fullNumber = this.#getFullNumber();
    const formattedValue = formatNumberAsYouType(
      fullNumber,
      inputValue,
      intlTelInput.utils,
      this.#selectedCountry,
      this.#options.separateDialCode
    );
    const newCaretPos = computeNewCaretPosition(
      relevantCharsBeforeCaret,
      formattedValue,
      currentCaretPos,
      isDeleteForwards
    );
    this.#setTelInputValue(formattedValue);
    this.#ui.telInputEl.setSelectionRange(newCaretPos, newCaretPos);
  }
  //* If separateDialCode AND typed dial code (e.g. from paste or autofill, or from typing a dial code when countrySearch disabled), then remove the typed dial code.
  //* Only strip when a full dial code is actually present — otherwise a lone typed "+" (or partial prefix) would get erased.
  #stripTypedDialCode(inputValue) {
    if (inputValue.startsWith("+") && this.#selectedCountry && this.#getDialCode(inputValue)) {
      const cleanNumber = stripSeparateDialCode(
        inputValue,
        true,
        true,
        this.#selectedCountry
      );
      this.#setTelInputValue(cleanNumber);
    }
  }
  #bindInputListener() {
    this.#userOverrideFormatting = REGEX.ALPHA_UNICODE.test(
      this.#getTelInputValue()
    );
    this.#ui.telInputEl.addEventListener(
      "input",
      this.#handleInputEvent,
      {
        signal: this.#abortController.signal
      }
    );
  }
  //* On input event: (1) Update selected country, (2) Format-as-you-type.
  //* Note that this fires AFTER the input is updated.
  #handleInputEvent = (e) => {
    const {
      strictMode,
      formatAsYouType,
      separateDialCode,
      countrySelectorMode,
      countrySearch
    } = this.#options;
    const detail = e?.detail;
    if (detail?.["isCountryChange"]) {
      return;
    }
    let inputValue = this.#getTelInputValue();
    const isPaste = e?.inputType === INPUT_TYPES.PASTE;
    const isStrictPaste = strictMode && isPaste;
    if (this.#isAndroid && !isPaste && e?.data === "+" && separateDialCode && countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF && countrySearch) {
      this.#handleAndroidPlusKey(inputValue);
      return;
    }
    if (this.#isAndroid && !isPaste && strictMode && (e?.data === " " || e?.data === "-" || e?.data === ".")) {
      this.#handleAndroidStrictReject(inputValue, e.data);
      return;
    }
    if (isStrictPaste) {
      const didRejectPaste = this.#handleStrictPasteInputEvent();
      if (didRejectPaste) {
        return;
      }
      inputValue = this.#getTelInputValue();
    }
    if (this.#updateCountryFromNumber(inputValue)) {
      this.#dispatchCountryChangeEvent();
      this.#dispatchEvent(EVENTS.INPUT, { isCountryChange: true });
    }
    const isFormattingChar = !isStrictPaste && e?.data && REGEX.NON_PLUS_NUMERIC.test(e.data);
    const isNonStrictPaste = isPaste && inputValue && !strictMode;
    if (isFormattingChar || isNonStrictPaste) {
      this.#userOverrideFormatting = true;
    } else if (!REGEX.NON_PLUS_NUMERIC.test(inputValue)) {
      this.#userOverrideFormatting = false;
    }
    if (formatAsYouType && !this.#userOverrideFormatting && !detail?.["isSetNumber"] && this.#numerals.isAscii()) {
      this.#formatAsYouType(
        inputValue,
        e?.inputType === INPUT_TYPES.DELETE_FORWARD
      );
    }
    if (separateDialCode) {
      this.#stripTypedDialCode(inputValue);
    }
  };
  #bindKeydownListener() {
    const { strictMode, separateDialCode } = this.#options;
    if (!strictMode && !separateDialCode) {
      return;
    }
    this.#ui.telInputEl.addEventListener("keydown", this.#handleKeydownEvent, {
      signal: this.#abortController.signal
    });
  }
  //* On keydown event: (1) if strictMode then prevent invalid characters, (2) if separateDialCode then handle plus key
  //* Note that this fires BEFORE the input is updated.
  #handleKeydownEvent = (e) => {
    const { strictMode, separateDialCode, countrySelectorMode, countrySearch } = this.#options;
    if (!e.key || e.key.length !== 1 || e.altKey || e.ctrlKey || e.metaKey) {
      return;
    }
    if (separateDialCode && countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF && countrySearch && e.key === "+") {
      e.preventDefault();
      this.#openCountrySelectorWithPlus();
      return;
    }
    if (!strictMode) {
      return;
    }
    const inputValue = this.#getTelInputValue();
    const alreadyHasPlus = inputValue.startsWith("+");
    const isInitialPlus = !alreadyHasPlus && this.#ui.telInputEl.selectionStart === 0 && e.key === "+";
    const normalisedKey = this.#numerals.normalise(e.key);
    const isNumeric = /^[0-9]$/.test(normalisedKey);
    const isAllowedChar = separateDialCode ? isNumeric : isInitialPlus || isNumeric;
    const input = this.#ui.telInputEl;
    const selStart = input.selectionStart;
    const selEnd = input.selectionEnd;
    const before = inputValue.slice(0, selStart ?? void 0);
    const after = inputValue.slice(selEnd ?? void 0);
    const newValue = before + normalisedKey + after;
    const newFullNumber = this.#buildFullNumber(newValue);
    let hasExceededMaxLength = getNumeric(newFullNumber).length > E164_MAX_DIGITS;
    if (!hasExceededMaxLength && intlTelInput.utils && this.#maxCoreNumberLength) {
      const coreNumber = intlTelInput.utils.getCoreNumber(
        newFullNumber,
        this.#selectedCountry?.iso2
      );
      hasExceededMaxLength = coreNumber.length > this.#maxCoreNumberLength;
    }
    const newCountry = this.#resolveCountryChangeFromNumber(newFullNumber);
    const isChangingDialCode = newCountry !== null;
    if (!isAllowedChar || hasExceededMaxLength && !isChangingDialCode && !isInitialPlus) {
      this.#ui.playStrictRejectAnimation();
      this.#dispatchEvent(EVENTS.STRICT_REJECT, {
        source: "key",
        rejectedInput: e.key,
        reason: !isAllowedChar ? "invalid" : "max-length"
      });
      e.preventDefault();
    }
  };
  #bindStrictPasteListener() {
    if (!this.#options.strictMode) {
      return;
    }
    this.#ui.telInputEl.addEventListener("paste", this.#handleStrictPasteEvent, {
      signal: this.#abortController.signal
    });
  }
  // In strict mode, remember paste details before the browser inserts the pasted text.
  // The actual sanitisation runs on the following input event so native paste stays enabled.
  #handleStrictPasteEvent = (e) => {
    const input = this.#ui.telInputEl;
    const inputValue = this.#getTelInputValue();
    this.#strictPasteSnapshot = {
      pastedRaw: e.clipboardData?.getData("text") ?? "",
      value: inputValue,
      selectionStart: input.selectionStart ?? inputValue.length,
      selectionEnd: input.selectionEnd ?? inputValue.length
    };
  };
  // Handle paste input events when strictMode is enabled by sanitising the pasted content after
  // the browser inserts it, and rejecting it entirely if it would result in an invalid number.
  #handleStrictPasteInputEvent() {
    const input = this.#ui.telInputEl;
    const pasteSnapshot = this.#strictPasteSnapshot;
    this.#strictPasteSnapshot = null;
    if (!pasteSnapshot) {
      return false;
    }
    const pastedRaw = pasteSnapshot.pastedRaw;
    const originalValue = pasteSnapshot.value;
    const selStart = pasteSnapshot.selectionStart;
    const selEnd = pasteSnapshot.selectionEnd;
    const before = originalValue.slice(0, selStart);
    const after = originalValue.slice(selEnd);
    const iso2 = this.#selectedCountry?.iso2;
    const pasted = this.#numerals.normalise(pastedRaw);
    const initialCharSelected = selStart === 0 && selEnd > 0;
    const allowLeadingPlus = !originalValue.startsWith("+") || initialCharSelected;
    const allowedChars = pasted.replace(REGEX.NON_PLUS_NUMERIC_GLOBAL, "");
    const hasLeadingPlus = allowedChars.startsWith("+");
    const numerics = allowedChars.replace(/\+/g, "");
    const sanitised = hasLeadingPlus && allowLeadingPlus ? `+${numerics}` : numerics;
    let newValue = before + sanitised + after;
    let rejectReason = sanitised !== pasted ? "invalid" : null;
    if (newValue.length > 30) {
      this.#rejectStrictPasteAsTooLong(pasteSnapshot);
      return true;
    }
    const excessDigits = getNumeric(this.#buildFullNumber(newValue)).length - E164_MAX_DIGITS;
    if (excessDigits > 0) {
      if (selEnd !== originalValue.length) {
        this.#rejectStrictPasteAsTooLong(pasteSnapshot);
        return true;
      }
      newValue = newValue.slice(0, newValue.length - excessDigits);
      rejectReason = "max-length";
    }
    if (this.#maxCoreNumberLength && newValue.length > 5 && intlTelInput.utils) {
      let coreNumber = intlTelInput.utils.getCoreNumber(newValue, iso2);
      while (coreNumber.length === 0 && newValue.length > 0) {
        newValue = newValue.slice(0, -1);
        coreNumber = intlTelInput.utils.getCoreNumber(newValue, iso2);
      }
      if (!coreNumber) {
        this.#rejectStrictPasteAsTooLong(pasteSnapshot);
        return true;
      }
      if (coreNumber.length > this.#maxCoreNumberLength) {
        if (selEnd === originalValue.length) {
          const trimLength = coreNumber.length - this.#maxCoreNumberLength;
          newValue = newValue.slice(0, newValue.length - trimLength);
          rejectReason = "max-length";
        } else {
          this.#rejectStrictPasteAsTooLong(pasteSnapshot);
          return true;
        }
      }
    }
    this.#setTelInputValue(newValue);
    const caretPos = selStart + sanitised.length;
    input.setSelectionRange(caretPos, caretPos);
    if (rejectReason) {
      if (pasted.length > 0 && sanitised.length === 0) {
        this.#ui.playStrictRejectAnimation();
      }
      this.#dispatchEvent(EVENTS.STRICT_REJECT, {
        source: "paste",
        rejectedInput: pastedRaw,
        reason: rejectReason
      });
    }
    return false;
  }
  // Reject a paste entirely because it would exceed the max length, restoring the previous value.
  #rejectStrictPasteAsTooLong(pasteSnapshot) {
    this.#ui.playStrictRejectAnimation();
    this.#dispatchEvent(EVENTS.STRICT_REJECT, {
      source: "paste",
      rejectedInput: pasteSnapshot.pastedRaw,
      reason: "max-length"
    });
    this.#restoreValueBeforeStrictPaste(pasteSnapshot);
  }
  #restoreValueBeforeStrictPaste(pasteSnapshot) {
    this.#setTelInputValue(pasteSnapshot.value);
    this.#ui.telInputEl.setSelectionRange(
      pasteSnapshot.selectionStart,
      pasteSnapshot.selectionEnd
    );
  }
  //* Adhere to the input's maxlength attr.
  #truncateToMaxLength(number) {
    const max = Number(this.#ui.telInputEl.getAttribute("maxlength"));
    return max && number.length > max ? number.substring(0, max) : number;
  }
  //* Trigger a custom event on the input (typed via ItiEventMap).
  #dispatchEvent(name, detailProps = {}) {
    const e = new CustomEvent(name, {
      bubbles: true,
      cancelable: true,
      detail: detailProps
    });
    this.#ui.telInputEl.dispatchEvent(e);
  }
  //* Open the country selector. Bail if already open — otherwise the existing AbortController gets overwritten
  //* and its listeners leak. Reachable via openCountrySelectorWithPlus when dropdownAlwaysOpen is set.
  //* Public so consumers can programmatically open the country selector.
  openCountrySelector() {
    if (this.#ui.isCountrySelectorOpen()) {
      return;
    }
    this.#ui.openCountrySelector(
      (li) => this.#selectListItem(li),
      () => this.#closeCountrySelectorInternal()
    );
    this.#dispatchEvent(EVENTS.OPEN_COUNTRY_SELECTOR);
  }
  //* Update the input's value to the given number (format first if possible)
  //* NOTE: this is called from setInitialState, handleUtilsLoaded and setNumber.
  #updateValueFromNumber(fullNumber) {
    const { numberDisplayFormat, separateDialCode } = this.#options;
    let number = fullNumber;
    if (intlTelInput.utils && this.#selectedCountry) {
      const isRegionless = hasRegionlessDialCode(fullNumber);
      const preserveUserNational = !number.startsWith("+") && !separateDialCode;
      const useNational = numberDisplayFormat === NUMBER_FORMAT.NATIONAL && !isRegionless || preserveUserNational;
      let format;
      if (useNational) {
        format = NUMBER_FORMAT.NATIONAL;
      } else if (numberDisplayFormat === NUMBER_FORMAT.E164 && !isRegionless) {
        format = NUMBER_FORMAT.E164;
      } else {
        format = NUMBER_FORMAT.INTERNATIONAL;
      }
      number = intlTelInput.utils.formatNumber(
        number,
        this.#selectedCountry?.iso2,
        format
      );
    }
    number = this.#prepareNumberForInput(number);
    this.#setTelInputValue(number);
  }
  //* Check if need to select a new country based on the given number
  //* Note: called from setInitialState, keyup handler, setNumber.
  #updateCountryFromNumber(fullNumber) {
    const iso2 = this.#resolveCountryChangeFromNumber(fullNumber);
    if (iso2 !== null) {
      return this.#updateSelectedCountry(iso2);
    }
    return false;
  }
  // if there is a selected country, and the number doesn't start with a dial code, then add it
  #withDialCodePrefix(number) {
    const dialCode = this.#selectedCountry?.dialCode;
    const nationalPrefix = this.#selectedCountry?.nationalPrefix;
    const alreadyHasPlus = number.startsWith("+");
    if (alreadyHasPlus || !dialCode) {
      return number;
    }
    const hasPrefix = nationalPrefix && number.startsWith(nationalPrefix) && !this.#options.separateDialCode;
    const cleanNumber = hasPrefix ? number.substring(1) : number;
    return `+${dialCode}${cleanNumber}`;
  }
  //* Get the new country iso2 (or "" for empty/globe state) based on the input number, or return null if no change.
  #resolveCountryChangeFromNumber(fullNumber) {
    const plusIndex = fullNumber.indexOf("+");
    let number = plusIndex > 0 ? fullNumber.substring(plusIndex) : fullNumber;
    const selectedIso2 = this.#selectedCountry?.iso2;
    number = this.#withDialCodePrefix(number);
    const dialCodeMatch = this.#getDialCode(number, true);
    const numeric = getNumeric(number);
    if (dialCodeMatch) {
      const dialCodeMatchNumeric = getNumeric(dialCodeMatch);
      const iso2Codes = this.#dialCodeToIso2Map[dialCodeMatchNumeric];
      if (iso2Codes.length === 1) {
        if (iso2Codes[0] === selectedIso2) {
          return null;
        }
        return iso2Codes[0];
      }
      return this.#resolveCountryChangeFromMultiMatch(
        iso2Codes,
        dialCodeMatchNumeric,
        numeric
      );
    } else if (number.startsWith("+") && numeric.length) {
      const currentDial = this.#selectedCountry?.dialCode || "";
      if (currentDial && currentDial.startsWith(numeric)) {
        return null;
      }
      if (!selectedIso2) {
        return null;
      }
      return "";
    } else if ((!number || number === "+") && !selectedIso2 && this.#fallbackCountryIso2) {
      return this.#fallbackCountryIso2;
    }
    return null;
  }
  //* Resolve the country when multiple countries share the matched dial code.
  #resolveCountryChangeFromMultiMatch(iso2Codes, dialCodeMatchNumeric, numeric) {
    const selectedIso2 = this.#selectedCountry?.iso2;
    const selectedDialCode = this.#selectedCountry?.dialCode;
    if (!selectedIso2 && this.#fallbackCountryIso2 && iso2Codes.includes(this.#fallbackCountryIso2)) {
      return this.#fallbackCountryIso2;
    }
    const isRegionlessNanpNumber = selectedDialCode === DIAL_CODE.NANP && isRegionlessNanp(numeric);
    if (isRegionlessNanpNumber) {
      return null;
    }
    const areaCodes = this.#selectedCountry?.areaCodes;
    const priority = this.#selectedCountry?.priority;
    if (areaCodes) {
      const dialCodeAreaCodes = areaCodes.map(
        (areaCode) => `${selectedDialCode}${areaCode}`
      );
      for (const dialCodeAreaCode of dialCodeAreaCodes) {
        if (numeric.startsWith(dialCodeAreaCode)) {
          return null;
        }
      }
    }
    const isMainCountry = priority === 0;
    const hasAreaCodesButNoneMatched = areaCodes && !isMainCountry && numeric.length > dialCodeMatchNumeric.length;
    const isValidSelection = selectedIso2 && iso2Codes.includes(selectedIso2) && !hasAreaCodesButNoneMatched;
    const alreadySelected = selectedIso2 === iso2Codes[0];
    if (!isValidSelection && !alreadySelected) {
      return iso2Codes[0];
    }
    return null;
  }
  //* Update the selected country, dial code (if separateDialCode), placeholder, title, and selected list item.
  //* Note: called from setInitialState, updateCountryFromNumber, selectListItem, setSelectedCountry.
  #updateSelectedCountry(iso2) {
    const prevIso2 = this.#selectedCountry?.iso2 || "";
    this.#selectedCountry = iso2 ? this.#countryByIso2.get(iso2) : null;
    if (this.#selectedCountry) {
      this.#fallbackCountryIso2 = this.#selectedCountry.iso2;
    }
    this.#ui.setSelectedCountry(this.#selectedCountry);
    this.#updatePlaceholder();
    this.#updateMaxCoreNumberLength();
    return prevIso2 !== iso2;
  }
  //* Update the maximum valid number length for the currently selected country.
  #updateMaxCoreNumberLength() {
    const { strictMode, placeholderNumberType, allowedNumberTypes } = this.#options;
    if (!strictMode || !intlTelInput.utils) {
      return;
    }
    const iso2 = this.#selectedCountry?.iso2;
    if (!iso2) {
      this.#maxCoreNumberLength = null;
      return;
    }
    let exampleNumber = intlTelInput.utils.getExampleNumber(
      iso2,
      placeholderNumberType,
      NUMBER_FORMAT.E164
    );
    let validNumber = exampleNumber;
    while (intlTelInput.utils.isValidNumber(
      exampleNumber,
      iso2,
      allowedNumberTypes
    )) {
      validNumber = exampleNumber;
      exampleNumber += "0";
    }
    const coreNumber = intlTelInput.utils.getCoreNumber(validNumber, iso2);
    this.#maxCoreNumberLength = coreNumber.length;
    if (iso2 === "by") {
      this.#maxCoreNumberLength = coreNumber.length + 1;
    }
  }
  //* Update the input placeholder to an example number from the currently selected country.
  #updatePlaceholder() {
    const {
      placeholderNumberPolicy,
      placeholderNumberType,
      numberDisplayFormat,
      customPlaceholder
    } = this.#options;
    const shouldSetPlaceholder = placeholderNumberPolicy === PLACEHOLDER_POLICY.AGGRESSIVE || !this.#ui.hadInitialPlaceholder && placeholderNumberPolicy === PLACEHOLDER_POLICY.POLITE;
    if (!intlTelInput.utils || !shouldSetPlaceholder) {
      return;
    }
    let placeholder = this.#selectedCountry ? intlTelInput.utils.getExampleNumber(
      this.#selectedCountry.iso2,
      placeholderNumberType,
      numberDisplayFormat
    ) : "";
    placeholder = this.#prepareNumberForInput(placeholder);
    if (typeof customPlaceholder === "function") {
      placeholder = customPlaceholder(placeholder, this.#selectedCountry);
    }
    this.#ui.telInputEl.setAttribute("placeholder", placeholder);
  }
  //* Called when the user selects a list item from the country list (no-op if listItem is null).
  #selectListItem(listItem) {
    if (!listItem) {
      return;
    }
    const iso2 = listItem.dataset[DATA_KEYS.ISO2];
    const countryChanged = this.#updateSelectedCountry(iso2);
    this.#closeCountrySelectorInternal();
    const dialCode = listItem.dataset[DATA_KEYS.DIAL_CODE];
    this.#updateDialCode(dialCode);
    const inputValue = this.#getTelInputValue();
    this.#updateValueFromNumber(inputValue);
    this.#ui.telInputEl.focus();
    if (countryChanged) {
      this.#dispatchCountryChangeEvent();
      this.#dispatchEvent(EVENTS.INPUT, { isCountryChange: true });
    }
  }
  //* Public: close the country selector (consumer-callable; delegates to the internal helper
  //* without the destroy-specific path).
  closeCountrySelector() {
    this.#closeCountrySelectorInternal();
  }
  //* Close the country selector and unbind any listeners. The isDestroy flag forces close even
  //* when dropdownAlwaysOpen is set, so destroy() can fully tear down.
  #closeCountrySelectorInternal(isDestroy) {
    if (!this.#ui.isCountrySelectorOpen() || this.#options.dropdownAlwaysOpen && !isDestroy) {
      return;
    }
    this.#ui.closeCountrySelector();
    this.#dispatchEvent(EVENTS.CLOSE_COUNTRY_SELECTOR);
  }
  //* Replace any existing dial code with the new one
  //* Note: called from selectListItem and setSelectedCountry
  #updateDialCode(newDialCodeDigits) {
    const inputValue = this.#getTelInputValue();
    if (!inputValue.startsWith("+")) {
      return;
    }
    const newDialCode = `+${newDialCodeDigits}`;
    const prevDialCode = this.#getDialCode(inputValue);
    let newNumber;
    if (prevDialCode) {
      newNumber = inputValue.replace(prevDialCode, newDialCode);
    } else {
      newNumber = newDialCode;
    }
    this.#setTelInputValue(newNumber);
  }
  //* Try and extract a valid international dial code from a full telephone number.
  //* Note: returns the raw string inc plus character and any whitespace/dots etc.
  #getDialCode(number, includeAreaCode) {
    if (!number.startsWith("+")) {
      return "";
    }
    let dialCode = "";
    let numericChars = "";
    let foundBaseDialCode = false;
    for (let i = 0; i < number.length; i++) {
      const c = number.charAt(i);
      if (!/[0-9]/.test(c)) {
        continue;
      }
      numericChars += c;
      const hasMapEntry = Boolean(this.#dialCodeToIso2Map[numericChars]);
      if (!hasMapEntry) {
        break;
      }
      if (this.#dialCodes.has(numericChars)) {
        dialCode = number.substring(0, i + 1);
        foundBaseDialCode = true;
        if (!includeAreaCode) {
          break;
        }
      } else if (includeAreaCode && foundBaseDialCode) {
        dialCode = number.substring(0, i + 1);
      }
      if (numericChars.length === this.#dialCodeMaxLength) {
        break;
      }
    }
    return dialCode;
  }
  //* Build a full number from an already-normalised value, adding the dial code if separateDialCode is enabled.
  #buildFullNumber(value) {
    const dialCode = this.#selectedCountry?.dialCode;
    const numericValue = getNumeric(value);
    const usePrefix = this.#options.separateDialCode && !value.startsWith("+") && dialCode && numericValue;
    return (usePrefix ? `+${dialCode}` : "") + value;
  }
  //* Get the input value as a full number, adding the dial code if separateDialCode is enabled.
  #getFullNumber() {
    const value = this.#getTelInputValue();
    return this.#buildFullNumber(value);
  }
  //* Remove the dial code if separateDialCode is enabled also cap the length if the input has a maxlength attribute
  #prepareNumberForInput(fullNumber) {
    const hasValidDialCode = Boolean(this.#getDialCode(fullNumber));
    const number = stripSeparateDialCode(
      fullNumber,
      hasValidDialCode,
      this.#options.separateDialCode,
      this.#selectedCountry
    );
    return this.#truncateToMaxLength(number);
  }
  //* Dispatch the 'countrychange' event.
  #dispatchCountryChangeEvent() {
    this.#dispatchEvent(EVENTS.COUNTRY_CHANGE, this.#selectedCountry ?? null);
  }
  //**************************
  //*  INTERNAL METHODS
  //**************************
  //* Called when the initial country lookup returns.
  #handleAutoCountryLoaded() {
    if (!this.#autoCountryDeferred || !intlTelInput.autoCountry) {
      return;
    }
    if (!this.#isActive) {
      this.#autoCountryDeferred.resolve();
      return;
    }
    const isFocused = document.activeElement === this.#ui.telInputEl;
    const hasTypedValue = Boolean(this.#getTelInputValue());
    if (this.#ui.isLoading() && !(isFocused && hasTypedValue)) {
      this.setSelectedCountry(intlTelInput.autoCountry);
    } else {
      this.#fallbackCountryIso2 = intlTelInput.autoCountry;
    }
    this.#ui.setLoading(false);
    this.#autoCountryDeferred.resolve();
  }
  //* Called when the initial country lookup fails or times out.
  #handleAutoCountryFailure() {
    if (!this.#isActive) {
      this.#autoCountryDeferred?.reject();
      return;
    }
    if (this.#ui.isLoading()) {
      this.#setInitialState(true);
    }
    this.#ui.setLoading(false);
    this.#autoCountryDeferred?.reject();
  }
  //* Called when the utils request completes.
  #handleUtilsLoaded() {
    if (!this.#isActive) {
      this.#utilsDeferred?.resolve();
      return;
    }
    if (!intlTelInput.utils) {
      this.#utilsDeferred?.resolve();
      return;
    }
    const inputValue = this.#getTelInputValue();
    const isFocused = document.activeElement === this.#ui.telInputEl;
    if (inputValue && !isFocused) {
      this.#updateValueFromNumber(inputValue);
    }
    if (this.#selectedCountry) {
      this.#updatePlaceholder();
      this.#updateMaxCoreNumberLength();
    }
    this.#utilsDeferred?.resolve();
  }
  //* Called when the utils request fails or times out.
  #handleUtilsFailure(error) {
    if (!this.#isActive) {
      this.#utilsDeferred?.reject(error);
      return;
    }
    this.#utilsDeferred?.reject(error);
  }
  //********************
  //*  PUBLIC METHODS
  //********************
  //* Remove core library.
  destroy() {
    if (!this.#isActive) {
      return;
    }
    this.#isActive = false;
    if (this.#options.countrySelectorMode !== COUNTRY_SELECTOR_MODE.OFF) {
      this.#closeCountrySelectorInternal(true);
    }
    this.#abortController.abort();
    this.#ui.destroy();
    intlTelInput.instances.delete(String(this.id));
  }
  // check if the instance is still valid (not destroyed)
  isActive() {
    return this.#isActive;
  }
  //* Get the extension from the current number.
  getExtension() {
    if (!this.#isActive) {
      return "";
    }
    ensureUtils("getExtension");
    return intlTelInput.utils.getExtension(
      this.#getFullNumber(),
      this.#selectedCountry?.iso2
    );
  }
  //* Format the number to the given format (defaults to "E164").
  getNumber(format) {
    if (!this.#isActive) {
      return "";
    }
    ensureUtils("getNumber");
    const iso2 = this.#selectedCountry?.iso2;
    const fullNumber = this.#getFullNumber();
    const formattedNumber = intlTelInput.utils.formatNumber(
      fullNumber,
      iso2,
      format
    );
    return this.#numerals.denormalise(formattedNumber);
  }
  //* Get the type of the entered number e.g. "FIXED_LINE" / "MOBILE", or null if it can't be determined / instance is destroyed.
  getNumberType() {
    if (!this.#isActive) {
      return null;
    }
    ensureUtils("getNumberType");
    return intlTelInput.utils.getNumberType(
      this.#getFullNumber(),
      this.#selectedCountry?.iso2
    );
  }
  //* Get the country data for the currently selected country.
  getSelectedCountry() {
    return this.#selectedCountry ?? null;
  }
  //* Get the validation error e.g. "TOO_SHORT" / "TOO_LONG", or null if it can't be determined / instance is destroyed.
  getValidationError() {
    if (!this.#isActive) {
      return null;
    }
    ensureUtils("getValidationError");
    const iso2 = this.#selectedCountry?.iso2;
    return intlTelInput.utils.getValidationError(this.#getFullNumber(), iso2);
  }
  //* Validate the input value using number length only
  isValidNumber() {
    if (!this.#isActive) {
      return null;
    }
    ensureUtils("isValidNumber");
    const dialCode = this.#selectedCountry?.dialCode;
    const iso2 = this.#selectedCountry?.iso2;
    const number = this.#getFullNumber();
    const coreNumber = intlTelInput.utils.getCoreNumber(number, iso2);
    if (coreNumber) {
      if (dialCode === UK.DIAL_CODE) {
        if (coreNumber[0] === UK.MOBILE_PREFIX && coreNumber.length !== UK.MOBILE_CORE_LENGTH) {
          return false;
        }
      }
      const hasAlphaChar = REGEX.ALPHA_UNICODE.test(number);
      if (!hasAlphaChar && dialCode) {
        const nationalPortion = number.startsWith("+") ? number.slice(1 + dialCode.length) : number;
        const nationalDigitCount = getNumeric(nationalPortion).length;
        if (coreNumber.length > nationalDigitCount) {
          return false;
        }
      }
    }
    return this.#validateNumber("possible");
  }
  //* Validate the input value with precise validation
  isValidNumberPrecise() {
    if (!this.#isActive) {
      return null;
    }
    ensureUtils("isValidNumberPrecise");
    return this.#validateNumber("precise");
  }
  //* Shared internal validation logic to handle alpha character extension rules.
  #validateNumber(mode) {
    const { allowNumberExtensions, allowPhonewords, allowedNumberTypes } = this.#options;
    const iso2 = this.#selectedCountry?.iso2;
    const value = this.#getFullNumber();
    if (!this.#selectedCountry && !hasRegionlessDialCode(value)) {
      return false;
    }
    const check = mode === "precise" ? intlTelInput.utils.isValidNumberPrecise : intlTelInput.utils.isValidNumber;
    if (!check(value, iso2, allowedNumberTypes)) {
      return false;
    }
    if (REGEX.ALPHA_UNICODE.test(value)) {
      const hasExtension = Boolean(
        intlTelInput.utils.getExtension(value, iso2)
      );
      return hasExtension ? allowNumberExtensions : allowPhonewords;
    }
    return true;
  }
  //* Update the selected country, and update the input value accordingly.
  setSelectedCountry(iso2) {
    if (!this.#isActive) {
      return;
    }
    const iso2Lower = iso2?.toLowerCase();
    if (!isIso2(iso2Lower)) {
      throw new Error(`Invalid iso2 code: '${iso2Lower}'`);
    }
    const currentCountry = this.#selectedCountry?.iso2;
    const isCountryChange = iso2 && iso2Lower !== currentCountry || !iso2 && currentCountry;
    if (!isCountryChange) {
      return;
    }
    this.#updateSelectedCountry(iso2Lower);
    this.#updateDialCode(this.#selectedCountry?.dialCode || "");
    const inputValue = this.#getTelInputValue();
    this.#updateValueFromNumber(inputValue);
    this.#dispatchCountryChangeEvent();
    this.#dispatchEvent(EVENTS.INPUT, { isCountryChange: true });
  }
  //* Set the input value and update the country.
  setNumber(number) {
    if (!this.#isActive) {
      return;
    }
    const normalisedNumber = this.#numerals.normalise(number);
    const countryChanged = this.#updateCountryFromNumber(normalisedNumber);
    this.#updateValueFromNumber(normalisedNumber);
    if (countryChanged) {
      this.#dispatchCountryChangeEvent();
    }
    this.#dispatchEvent(EVENTS.INPUT, { isSetNumber: true });
  }
  //* Set the placeholder number type
  setPlaceholderNumberType(type) {
    if (!this.#isActive) {
      return;
    }
    this.#options.placeholderNumberType = type;
    this.#updatePlaceholder();
  }
  // Set the disabled state of the input and country selector.
  setDisabled(disabled) {
    if (!this.#isActive) {
      return;
    }
    this.#ui.setDisabled(disabled);
  }
  // Set the readonly state of the input and country selector.
  setReadonly(readonly) {
    if (!this.#isActive) {
      return;
    }
    this.#ui.setReadonly(readonly);
  }
  //********************
  //*  STATIC METHODS
  //********************
  // Internal instance notification used by utils/initial-country loaders.
  // Kept public so module-level helpers (e.g. attachUtils) can call it, while still allowing
  // access to private instance methods.
  static forEachInstance(method, ...args) {
    const values = [...intlTelInput.instances.values()];
    const arg = args[0];
    values.forEach((instance) => {
      if (!(instance instanceof _Iti)) {
        return;
      }
      switch (method) {
        case "handleUtilsLoaded":
          instance.#handleUtilsLoaded();
          break;
        case "handleUtilsFailure":
          instance.#handleUtilsFailure(arg);
          break;
        case "handleAutoCountryLoaded":
          instance.#handleAutoCountryLoaded();
          break;
        case "handleAutoCountryFailure":
          instance.#handleAutoCountryFailure();
          break;
      }
    });
  }
};
var attachUtils = async (source) => {
  if (intlTelInput.utils || intlTelInput.startedLoadingUtils) {
    return null;
  }
  if (typeof source !== "function") {
    throw new TypeError(
      `The argument passed to attachUtils must be a function that returns a promise for the utils module, not ${typeof source}`
    );
  }
  intlTelInput.startedLoadingUtils = true;
  try {
    const module = await source();
    const utils = module?.default;
    if (!utils || typeof utils !== "object") {
      throw new TypeError(
        "The loader function passed to attachUtils did not resolve to a module object with utils as its default export."
      );
    }
    intlTelInput.utils = utils;
    Iti.forEachInstance("handleUtilsLoaded");
    return true;
  } catch (error) {
    Iti.forEachInstance("handleUtilsFailure", error);
    throw error;
  }
};
var intlTelInput = Object.assign(
  (input, options) => {
    const iti = new Iti(input, options);
    intlTelInput.instances.set(String(iti.id), iti);
    input.iti = iti;
    return iti;
  },
  {
    defaults,
    //* Using a static var like this allows us to mock it in the tests.
    documentReady: () => document.readyState === "complete",
    //* Get the full list of all countries the library knows about.
    getAllCountries: () => data_default,
    //* A getter for the core library instance.
    getInstance: (input) => {
      const id = input.dataset[DATA_KEYS.INSTANCE_ID];
      return id ? intlTelInput.instances.get(id) ?? null : null;
    },
    //* A map from instance ID to instance object.
    instances: /* @__PURE__ */ new Map(),
    attachUtils,
    startedLoadingUtils: false,
    startedLoadingAutoCountry: false,
    version: "29.4.0",
    NUMBER_FORMAT,
    NUMBER_TYPE,
    VALIDATION_ERROR,
    PLACEHOLDER_POLICY,
    COUNTRY_SELECTOR_MODE
  }
);
var intlTelInput_default = intlTelInput;

// packages/core/dist/js/utils.js
var _scope = {};
(function() {
  var k = this || self;
  function m(a, b) {
    a = a.split(".");
    var c = k;
    a[0] in c || typeof c.execScript == "undefined" || c.execScript("var " + a[0]);
    for (var d; a.length && (d = a.shift()); ) a.length || b === void 0 ? c[d] && c[d] !== Object.prototype[d] ? c = c[d] : c = c[d] = {} : c[d] = b;
  }
  function n(a, b) {
    function c() {
    }
    c.prototype = b.prototype;
    a.na = b.prototype;
    a.prototype = new c();
    a.prototype.constructor = a;
    a.ta = function(d, e, f) {
      for (var g = Array(arguments.length - 2), h = 2; h < arguments.length; h++) g[h - 2] = arguments[h];
      return b.prototype[e].apply(d, g);
    };
  }
  ;
  function aa(a) {
    const b = [];
    let c = 0;
    for (const d in a) b[c++] = a[d];
    return b;
  }
  ;
  var ca = class {
    constructor(a) {
      if (ba !== ba) throw Error("SafeUrl is not meant to be built directly");
      this.g = a;
    }
    toString() {
      return this.g.toString();
    }
  }, ba = {};
  new ca("about:invalid#zClosurez");
  new ca("about:blank");
  const da = {};
  class fa {
    constructor() {
      if (da !== da) throw Error("SafeStyle is not meant to be built directly");
    }
    toString() {
      return "".toString();
    }
  }
  new fa();
  const ha = {};
  class ia {
    constructor() {
      if (ha !== ha) throw Error("SafeStyleSheet is not meant to be built directly");
    }
    toString() {
      return "".toString();
    }
  }
  new ia();
  const ja = {};
  class ka {
    constructor() {
      var a = k.trustedTypes && k.trustedTypes.emptyHTML || "";
      if (ja !== ja) throw Error("SafeHtml is not meant to be built directly");
      this.g = a;
    }
    toString() {
      return this.g.toString();
    }
  }
  new ka();
  function la(a, b) {
    this.g = a;
    this.l = !!b.ca;
    this.h = b.i;
    this.u = b.type;
    this.o = false;
    switch (this.h) {
      case ma:
      case na:
      case oa:
      case pa:
      case qa:
      case ra:
      case sa:
        this.o = true;
    }
    this.j = b.defaultValue;
  }
  var sa = 1, ra = 2, ma = 3, na = 4, oa = 6, pa = 16, qa = 18;
  function ta(a, b) {
    this.h = a;
    this.g = {};
    for (a = 0; a < b.length; a++) {
      var c = b[a];
      this.g[c.g] = c;
    }
  }
  function ua(a) {
    a = aa(a.g);
    a.sort(function(b, c) {
      return b.g - c.g;
    });
    return a;
  }
  ;
  function p() {
    this.h = {};
    this.j = this.m().g;
    this.g = this.l = null;
  }
  p.prototype.has = function(a) {
    return q(this, a.g);
  };
  p.prototype.get = function(a, b) {
    return r(this, a.g, b);
  };
  p.prototype.set = function(a, b) {
    t(this, a.g, b);
  };
  p.prototype.add = function(a, b) {
    va(this, a.g, b);
  };
  p.prototype.equals = function(a) {
    if (!a || this.constructor != a.constructor) return false;
    for (var b = ua(this.m()), c = 0; c < b.length; c++) {
      var d = b[c], e = d.g;
      if (q(this, e) != q(a, e)) return false;
      if (q(this, e)) {
        var f = d.h == 11 || d.h == 10, g = u(this, e);
        e = u(a, e);
        if (d.l) {
          if (g.length != e.length) return false;
          for (d = 0; d < g.length; d++) {
            var h = g[d], l = e[d];
            if (f ? !h.equals(l) : h != l) return false;
          }
        } else if (f ? !g.equals(e) : g != e) return false;
      }
    }
    return true;
  };
  function wa(a, b) {
    for (var c = ua(a.m()), d = 0; d < c.length; d++) {
      var e = c[d], f = e.g;
      if (q(b, f)) {
        a.g && delete a.g[e.g];
        var g = e.h == 11 || e.h == 10;
        if (e.l) {
          e = u(b, f) || [];
          for (var h = 0; h < e.length; h++) va(a, f, g ? e[h].clone() : e[h]);
        } else e = u(b, f), g ? (g = u(a, f)) ? wa(g, e) : t(a, f, e.clone()) : t(a, f, e);
      }
    }
  }
  p.prototype.clone = function() {
    var a = new this.constructor();
    a != this && (a.h = {}, a.g && (a.g = {}), wa(a, this));
    return a;
  };
  function q(a, b) {
    return a.h[b] != null;
  }
  function u(a, b) {
    var c = a.h[b];
    if (c == null) return null;
    if (a.l) {
      if (!(b in a.g)) {
        var d = a.l, e = a.j[b];
        if (c != null) if (e.l) {
          for (var f = [], g = 0; g < c.length; g++) f[g] = d.h(e, c[g]);
          c = f;
        } else c = d.h(e, c);
        return a.g[b] = c;
      }
      return a.g[b];
    }
    return c;
  }
  function r(a, b, c) {
    var d = u(a, b);
    return a.j[b].l ? d[c || 0] : d;
  }
  function v(a, b) {
    if (q(a, b)) a = r(a, b);
    else a: {
      a = a.j[b];
      if (a.j === void 0) if (b = a.u, b === Boolean) a.j = false;
      else if (b === Number) a.j = 0;
      else if (b === String) a.j = a.o ? "0" : "";
      else {
        a = new b();
        break a;
      }
      a = a.j;
    }
    return a;
  }
  function w(a, b) {
    return a.j[b].l ? q(a, b) ? a.h[b].length : 0 : q(a, b) ? 1 : 0;
  }
  function t(a, b, c) {
    a.h[b] = c;
    a.g && (a.g[b] = c);
  }
  function va(a, b, c) {
    a.h[b] || (a.h[b] = []);
    a.h[b].push(c);
    a.g && delete a.g[b];
  }
  function x(a, b) {
    var c = [], d;
    for (d in b) d != 0 && c.push(new la(d, b[d]));
    return new ta(a, c);
  }
  ;
  function y() {
  }
  y.prototype.g = function(a) {
    new a.h();
    throw Error("Unimplemented");
  };
  y.prototype.h = function(a, b) {
    if (a.h == 11 || a.h == 10) return b instanceof p ? b : this.g(a.u.prototype.m(), b);
    if (a.h == 14) return typeof b === "string" && xa.test(b) && (a = Number(b), a > 0) ? a : b;
    if (!a.o) return b;
    a = a.u;
    if (a === String) {
      if (typeof b === "number") return String(b);
    } else if (a === Number && typeof b === "string" && (b === "Infinity" || b === "-Infinity" || b === "NaN" || xa.test(b))) return Number(b);
    return b;
  };
  var xa = /^-?[0-9]+$/;
  function ya() {
  }
  n(ya, y);
  ya.prototype.g = function(a, b) {
    a = new a.h();
    a.l = this;
    a.h = b;
    a.g = {};
    return a;
  };
  function z() {
  }
  n(z, ya);
  z.prototype.h = function(a, b) {
    return a.h == 8 ? !!b : y.prototype.h.apply(this, arguments);
  };
  z.prototype.g = function(a, b) {
    return z.na.g.call(this, a, b);
  };
  function B(a, b) {
    a != null && this.g.apply(this, arguments);
  }
  B.prototype.h = "";
  B.prototype.set = function(a) {
    this.h = "" + a;
  };
  B.prototype.g = function(a, b, c) {
    this.h += String(a);
    if (b != null) for (let d = 1; d < arguments.length; d++) this.h += arguments[d];
    return this;
  };
  function C(a) {
    a.h = "";
  }
  B.prototype.toString = function() {
    return this.h;
  };
  function D() {
    p.call(this);
  }
  n(D, p);
  var za = null;
  function E() {
    p.call(this);
  }
  n(E, p);
  var Aa = null;
  function F(a) {
    return u(a, 9) || [];
  }
  function G() {
    p.call(this);
  }
  n(G, p);
  var Ba = null;
  D.prototype.m = function() {
    var a = za;
    a || (za = a = x(D, { 0: { name: "NumberFormat", ja: "i18n.phonenumbers.NumberFormat" }, 1: { name: "pattern", required: true, i: 9, type: String }, 2: { name: "format", required: true, i: 9, type: String }, 3: { name: "leading_digits_pattern", ca: true, i: 9, type: String }, 4: { name: "national_prefix_formatting_rule", i: 9, type: String }, 6: { name: "national_prefix_optional_when_formatting", i: 8, defaultValue: false, type: Boolean }, 5: { name: "domestic_carrier_code_formatting_rule", i: 9, type: String } }));
    return a;
  };
  D.m = D.prototype.m;
  E.prototype.m = function() {
    var a = Aa;
    a || (Aa = a = x(E, { 0: { name: "PhoneNumberDesc", ja: "i18n.phonenumbers.PhoneNumberDesc" }, 2: { name: "national_number_pattern", i: 9, type: String }, 9: { name: "possible_length", ca: true, i: 5, type: Number }, 10: { name: "possible_length_local_only", ca: true, i: 5, type: Number }, 6: { name: "example_number", i: 9, type: String } }));
    return a;
  };
  E.m = E.prototype.m;
  G.prototype.m = function() {
    var a = Ba;
    a || (Ba = a = x(G, {
      0: { name: "PhoneMetadata", ja: "i18n.phonenumbers.PhoneMetadata" },
      1: { name: "general_desc", i: 11, type: E },
      2: { name: "fixed_line", i: 11, type: E },
      3: { name: "mobile", i: 11, type: E },
      4: { name: "toll_free", i: 11, type: E },
      5: { name: "premium_rate", i: 11, type: E },
      6: { name: "shared_cost", i: 11, type: E },
      7: { name: "personal_number", i: 11, type: E },
      8: { name: "voip", i: 11, type: E },
      21: { name: "pager", i: 11, type: E },
      25: { name: "uan", i: 11, type: E },
      27: { name: "emergency", i: 11, type: E },
      28: { name: "voicemail", i: 11, type: E },
      29: { name: "short_code", i: 11, type: E },
      30: { name: "standard_rate", i: 11, type: E },
      31: { name: "carrier_specific", i: 11, type: E },
      33: { name: "sms_services", i: 11, type: E },
      24: { name: "no_international_dialling", i: 11, type: E },
      9: { name: "id", required: true, i: 9, type: String },
      10: { name: "country_code", i: 5, type: Number },
      11: { name: "international_prefix", i: 9, type: String },
      17: { name: "preferred_international_prefix", i: 9, type: String },
      12: { name: "national_prefix", i: 9, type: String },
      13: { name: "preferred_extn_prefix", i: 9, type: String },
      15: {
        name: "national_prefix_for_parsing",
        i: 9,
        type: String
      },
      16: { name: "national_prefix_transform_rule", i: 9, type: String },
      18: { name: "same_mobile_and_fixed_line_pattern", i: 8, defaultValue: false, type: Boolean },
      19: { name: "number_format", ca: true, i: 11, type: D },
      20: { name: "intl_number_format", ca: true, i: 11, type: D },
      22: { name: "main_country_for_code", i: 8, defaultValue: false, type: Boolean },
      23: { name: "leading_digits", i: 9, type: String }
    }));
    return a;
  };
  G.m = G.prototype.m;
  function H() {
    p.call(this);
  }
  n(H, p);
  var Ca = null, Da = { sa: 0, ra: 1, qa: 5, pa: 10, oa: 20 };
  H.prototype.m = function() {
    var a = Ca;
    a || (Ca = a = x(H, { 0: { name: "PhoneNumber", ja: "i18n.phonenumbers.PhoneNumber" }, 1: { name: "country_code", required: true, i: 5, type: Number }, 2: { name: "national_number", required: true, i: 4, type: Number }, 3: { name: "extension", i: 9, type: String }, 4: { name: "italian_leading_zero", i: 8, type: Boolean }, 8: { name: "number_of_leading_zeros", i: 5, defaultValue: 1, type: Number }, 5: { name: "raw_input", i: 9, type: String }, 6: { name: "country_code_source", i: 14, defaultValue: 0, type: Da }, 7: {
      name: "preferred_domestic_carrier_code",
      i: 9,
      type: String
    } }));
    return a;
  };
  H.ctor = H;
  H.ctor.m = H.prototype.m;
  var I = {
    1: "US AG AI AS BB BM BS CA DM DO GD GU JM KN KY LC MP MS PR SX TC TT VC VG VI".split(" "),
    7: ["RU", "KZ"],
    20: ["EG"],
    27: ["ZA"],
    30: ["GR"],
    31: ["NL"],
    32: ["BE"],
    33: ["FR"],
    34: ["ES"],
    36: ["HU"],
    39: ["IT", "VA"],
    40: ["RO"],
    41: ["CH"],
    43: ["AT"],
    44: ["GB", "GG", "IM", "JE"],
    45: ["DK"],
    46: ["SE"],
    47: ["NO", "SJ"],
    48: ["PL"],
    49: ["DE"],
    51: ["PE"],
    52: ["MX"],
    53: ["CU"],
    54: ["AR"],
    55: ["BR"],
    56: ["CL"],
    57: ["CO"],
    58: ["VE"],
    60: ["MY"],
    61: ["AU", "CC", "CX"],
    62: ["ID"],
    63: ["PH"],
    64: ["NZ"],
    65: ["SG"],
    66: ["TH"],
    81: ["JP"],
    82: ["KR"],
    84: ["VN"],
    86: ["CN"],
    90: ["TR"],
    91: ["IN"],
    92: ["PK"],
    93: ["AF"],
    94: ["LK"],
    95: ["MM"],
    98: ["IR"],
    211: ["SS"],
    212: ["MA", "EH"],
    213: ["DZ"],
    216: ["TN"],
    218: ["LY"],
    220: ["GM"],
    221: ["SN"],
    222: ["MR"],
    223: ["ML"],
    224: ["GN"],
    225: ["CI"],
    226: ["BF"],
    227: ["NE"],
    228: ["TG"],
    229: ["BJ"],
    230: ["MU"],
    231: ["LR"],
    232: ["SL"],
    233: ["GH"],
    234: ["NG"],
    235: ["TD"],
    236: ["CF"],
    237: ["CM"],
    238: ["CV"],
    239: ["ST"],
    240: ["GQ"],
    241: ["GA"],
    242: ["CG"],
    243: ["CD"],
    244: ["AO"],
    245: ["GW"],
    246: ["IO"],
    247: ["AC"],
    248: ["SC"],
    249: ["SD"],
    250: ["RW"],
    251: ["ET"],
    252: ["SO"],
    253: ["DJ"],
    254: ["KE"],
    255: ["TZ"],
    256: ["UG"],
    257: ["BI"],
    258: ["MZ"],
    260: ["ZM"],
    261: ["MG"],
    262: ["RE", "YT"],
    263: ["ZW"],
    264: ["NA"],
    265: ["MW"],
    266: ["LS"],
    267: ["BW"],
    268: ["SZ"],
    269: ["KM"],
    290: ["SH", "TA"],
    291: ["ER"],
    297: ["AW"],
    298: ["FO"],
    299: ["GL"],
    350: ["GI"],
    351: ["PT"],
    352: ["LU"],
    353: ["IE"],
    354: ["IS"],
    355: ["AL"],
    356: ["MT"],
    357: ["CY"],
    358: ["FI", "AX"],
    359: ["BG"],
    370: ["LT"],
    371: ["LV"],
    372: ["EE"],
    373: ["MD"],
    374: ["AM"],
    375: ["BY"],
    376: ["AD"],
    377: ["MC"],
    378: ["SM"],
    380: ["UA"],
    381: ["RS"],
    382: ["ME"],
    383: ["XK"],
    385: ["HR"],
    386: ["SI"],
    387: ["BA"],
    389: ["MK"],
    420: ["CZ"],
    421: ["SK"],
    423: ["LI"],
    500: ["FK"],
    501: ["BZ"],
    502: ["GT"],
    503: ["SV"],
    504: ["HN"],
    505: ["NI"],
    506: ["CR"],
    507: ["PA"],
    508: ["PM"],
    509: ["HT"],
    590: ["GP", "BL", "MF"],
    591: ["BO"],
    592: ["GY"],
    593: ["EC"],
    594: ["GF"],
    595: ["PY"],
    596: ["MQ"],
    597: ["SR"],
    598: ["UY"],
    599: ["CW", "BQ"],
    670: ["TL"],
    672: ["NF"],
    673: ["BN"],
    674: ["NR"],
    675: ["PG"],
    676: ["TO"],
    677: ["SB"],
    678: ["VU"],
    679: ["FJ"],
    680: ["PW"],
    681: ["WF"],
    682: ["CK"],
    683: ["NU"],
    685: ["WS"],
    686: ["KI"],
    687: ["NC"],
    688: ["TV"],
    689: ["PF"],
    690: ["TK"],
    691: ["FM"],
    692: ["MH"],
    800: ["001"],
    808: ["001"],
    850: ["KP"],
    852: ["HK"],
    853: ["MO"],
    855: ["KH"],
    856: ["LA"],
    870: ["001"],
    878: ["001"],
    880: ["BD"],
    881: ["001"],
    882: ["001"],
    883: ["001"],
    886: ["TW"],
    888: ["001"],
    960: ["MV"],
    961: ["LB"],
    962: ["JO"],
    963: ["SY"],
    964: ["IQ"],
    965: ["KW"],
    966: ["SA"],
    967: ["YE"],
    968: ["OM"],
    970: ["PS"],
    971: ["AE"],
    972: ["IL"],
    973: ["BH"],
    974: ["QA"],
    975: ["BT"],
    976: ["MN"],
    977: ["NP"],
    979: ["001"],
    992: ["TJ"],
    993: ["TM"],
    994: ["AZ"],
    995: ["GE"],
    996: ["KG"],
    998: ["UZ"]
  }, Ea = {
    AC: [, [
      ,
      ,
      "(?:[01589]\\d|[2-467])\\d{4}",
      ,
      ,
      ,
      ,
      ,
      ,
      [5, 6]
    ], [, , "6\\d{4}", , , , "62889", , , [5]], [, , "[2-47]\\d{4}", , , , "40123", , , [5]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "AC", 247, "00", , , , , , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "(?:0[1-9]|[1589]\\d)\\d{4}", , , , "542011", , , [6]], , , [, , , , , , , , , [-1]]],
    AD: [
      ,
      [, , "(?:1|6\\d)\\d{7}|[135-9]\\d{5}", , , , , , , [6, 8, 9]],
      [, , "[78]\\d{5}", , , , "712345", , , [6]],
      [, , "690\\d{6}|[356]\\d{5}", , , , "312345", , , [6, 9]],
      [, , "180[02]\\d{4}", , , , "18001234", , , [8]],
      [, , "[19]\\d{5}", , , , "912345", , , [6]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "AD",
      376,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})", "$1 $2", ["[135-9]"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["1"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["6"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "1800\\d{4}", , , , , , , [8]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    AE: [
      ,
      [, , "(?:[4-7]\\d|9[0-689])\\d{7}|800\\d{2,9}|[2-4679]\\d{7}", , , , , , , [5, 6, 7, 8, 9, 10, 11, 12]],
      [, , "[2-4679][2-8]\\d{6}", , , , "22345678", , , [8], [7]],
      [, , "5[02-68]\\d{7}", , , , "501234567", , , [9]],
      [, , "400\\d{6}|800\\d{2,9}", , , , "800123456"],
      [, , "900[02]\\d{5}", , , , "900234567", , , [9]],
      [, , "700[05]\\d{5}", , , , "700012345", , , [9]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "AE",
      971,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{2,9})", "$1 $2", ["60|8"]], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["[236]|[479][2-8]"], "0$1"], [, "(\\d{3})(\\d)(\\d{5})", "$1 $2 $3", ["[479]"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["5"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "600[25]\\d{5}", , , , "600212345", , , [9]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    AF: [, [, , "[2-7]\\d{8}", , , , , , , [9], [7]], [
      ,
      ,
      "(?:[25][0-8]|[34][0-4]|6[0-5])[2-9]\\d{6}",
      ,
      ,
      ,
      "234567890",
      ,
      ,
      ,
      [7]
    ], [, , "7\\d{8}", , , , "701234567", , , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "AF", 93, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[1-9]"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2-7]"], "0$1"]], [[, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2-7]"], "0$1"]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AG: [, [, , "(?:268|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [
      ,
      ,
      "268(?:4(?:6[0-38]|84)|56[0-2])\\d{4}",
      ,
      ,
      ,
      "2684601234",
      ,
      ,
      ,
      [7]
    ], [, , "268(?:464|7(?:1[3-9]|[28]\\d|3[0246]|64|7[0-689]))\\d{4}", , , , "2684641234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [
      ,
      ,
      "26848[01]\\d{4}",
      ,
      ,
      ,
      "2684801234",
      ,
      ,
      ,
      [7]
    ], "AG", 1, "011", "1", , , "([457]\\d{6})$|1", "268$1", , , , , [, , "26840[69]\\d{4}", , , , "2684061234", , , , [7]], , "268", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AI: [, [, , "(?:264|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [, , "264(?:292|4(?:6[12]|9[78]))\\d{4}", , , , "2644612345", , , , [7]], [, , "264(?:235|4(?:69|7[67])|5(?:3[6-9]|8[1-4])|7(?:29|72))\\d{4}", , , , "2642351234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "AI", 1, "011", "1", , , "([2457]\\d{6})$|1", "264$1", , , , , [, , "264724\\d{4}", , , , "2647241234", , , , [7]], , "264", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AL: [, [, , "(?:700\\d\\d|900)\\d{3}|8\\d{5,7}|(?:[2-5]|6\\d)\\d{7}", , , , , , , [6, 7, 8, 9], [5]], [, , "4505[0-2]\\d{3}|(?:[2358][16-9]\\d[2-9]|4410)\\d{4}|(?:[2358][2-5][2-9]|4(?:[2-57-9][2-9]|6\\d))\\d{5}", , , , "22345678", , , [8], [5, 6, 7]], [, , "6(?:[78][2-9]|9\\d)\\d{6}", , , , "672123456", , , [9]], [, , "800\\d{4}", , , , "8001234", , , [7]], [
      ,
      ,
      "900[1-9]\\d\\d",
      ,
      ,
      ,
      "900123",
      ,
      ,
      [6]
    ], [, , "808[1-9]\\d\\d", , , , "808123", , , [6]], [, , "700[2-9]\\d{4}", , , , "70021234", , , [8]], [, , , , , , , , , [-1]], "AL", 355, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3,4})", "$1 $2", ["80|9"], "0$1"], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["4[2-6]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2358][2-5]|4"], "0$1"], [, "(\\d{3})(\\d{5})", "$1 $2", ["[23578]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["6"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AM: [, [
      ,
      ,
      "(?:[1-489]\\d|55|60|77)\\d{6}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8],
      [5, 6]
    ], [, , "(?:(?:1[0-25]|47)\\d|2(?:2[2-46]|3[1-8]|4[2-69]|5[2-7]|6[1-9]|8[1-7])|3[12]2)\\d{5}", , , , "10123456", , , , [5, 6]], [, , "(?:33|4[1349]|55|77|88|9[13-9])\\d{6}", , , , "77123456"], [, , "800\\d{5}", , , , "80012345"], [, , "90[016]\\d{5}", , , , "90012345"], [, , "80[1-4]\\d{5}", , , , "80112345"], [, , , , , , , , , [-1]], [, , "60(?:2[78]|3[5-9]|4[02-9]|5[0-46-9]|[6-8]\\d|9[0-2])\\d{4}", , , , "60271234"], "AM", 374, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["[89]0"], "0 $1"], [
      ,
      "(\\d{3})(\\d{5})",
      "$1 $2",
      ["2|3[12]"],
      "(0$1)"
    ], [, "(\\d{2})(\\d{6})", "$1 $2", ["1|47"], "(0$1)"], [, "(\\d{2})(\\d{6})", "$1 $2", ["[3-9]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AO: [
      ,
      [, , "[29]\\d{8}", , , , , , , [9]],
      [, , "2\\d(?:[0134][25-9]|[25-9]\\d)\\d{5}", , , , "222123456"],
      [, , "9[1-79]\\d{7}", , , , "923123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "AO",
      244,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[29]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    AR: [
      ,
      [, , "(?:11|[89]\\d\\d)\\d{8}|[2368]\\d{9}", , , , , , , [10, 11], [6, 7, 8]],
      [
        ,
        ,
        "3(?:7(?:1[15]|81)|8(?:21|4[16]|69|9[12]))[46]\\d{5}|(?:2(?:2(?:2[59]|44|52)|3(?:26|44)|47[35]|9(?:[07]2|2[26]|34|46))|3327)[45]\\d{5}|(?:2(?:657|9(?:54|66))|3(?:48[27]|7(?:55|77)|8(?:65|78)))[2-8]\\d{5}|(?:2(?:284|3(?:02|23)|477|622|920)|3(?:4(?:46|89|92)|541))[2-7]\\d{5}|(?:(?:11[0-8]|670)\\d|2(?:2(?:0[45]|1[2-6]|3[3-6])|3(?:[06]4|7[45])|494|6(?:04|1[2-8]|[36][45]|4[3-6])|80[45]|9(?:[17][4-6]|[48][45]|9[3-6]))|3(?:364|4(?:1[2-8]|[25][4-6]|3[3-6]|84)|5(?:1[2-9]|[38][4-6])|6(?:2[45]|44)|7[069][45]|8(?:0[45]|1[2-7]|3[4-6]|5[3-6]|7[2-6]|8[3-68])))\\d{6}|(?:2(?:2(?:62|81)|320|9(?:42|83))|3(?:329|4(?:62|7[16])|5(?:43|64)|7(?:18|5[17])))[2-6]\\d{5}|2(?:2(?:21|4[23]|6[145]|7[1-4]|8[356]|9[267])|3(?:16|3[13-8]|43|5[346-8]|9[3-5])|6(?:2[46]|4[78]|5[1568])|9(?:03|2[1457-9]|3[1356]|4[08]|[56][23]|82))4\\d{5}|(?:2(?:257|3(?:24|46|92)|9(?:01|23|64))|3(?:4(?:42|64)|5(?:25|37|4[47]|71)|7(?:35|72)|825))[3-6]\\d{5}|(?:2(?:2(?:02|2[3467]|4[156]|5[45]|6[6-8]|91)|3(?:1[47]|25|[45][25]|96)|47[48]|625|932)|3(?:38[2578]|4(?:0[0-24-9]|3[78]|4[457]|58|6[035-9]|72|83|9[136-8])|5(?:2[124]|[368][23]|4[2689]|7[2-6])|7(?:16|2[15]|3[14]|4[13]|5[468]|7[3-5]|8[26])|8(?:2[67]|3[278]|4[3-5]|5[78]|6[1-378]|[78]7|94)))[4-6]\\d{5}",
        ,
        ,
        ,
        "1123456789",
        ,
        ,
        [10],
        [6, 7, 8]
      ],
      [
        ,
        ,
        "93(?:7(?:1[15]|81)|8(?:21|4[16]|69|9[12]))[46]\\d{5}|9(?:2(?:2(?:2[59]|44|52)|3(?:26|44)|47[35]|9(?:[07]2|2[26]|34|46))|3327)[45]\\d{5}|9(?:2(?:657|9(?:54|66))|3(?:48[27]|7(?:55|77)|8(?:65|78)))[2-8]\\d{5}|9(?:2(?:284|3(?:02|23)|477|622|920)|3(?:4(?:46|89|92)|541))[2-7]\\d{5}|(?:675\\d|9(?:11[0-8]\\d|2(?:2(?:0[45]|1[2-6]|3[3-6])|3(?:[06]4|7[45])|494|6(?:04|1[2-8]|[36][45]|4[3-6])|80[45]|9(?:[17][4-6]|[48][45]|9[3-6]))|3(?:364|4(?:1[2-8]|[25][4-6]|3[3-6]|84)|5(?:1[2-9]|[38][4-6])|6(?:2[45]|44)|7[069][45]|8(?:0[45]|1[2-7]|3[4-6]|5[3-6]|7[2-6]|8[3-68]))))\\d{6}|9(?:2(?:2(?:62|81)|320|9(?:42|83))|3(?:329|4(?:62|7[16])|5(?:43|64)|7(?:18|5[17])))[2-6]\\d{5}|92(?:2(?:21|4[23]|6[145]|7[1-4]|8[356]|9[267])|3(?:16|3[13-8]|43|5[346-8]|9[3-5])|6(?:2[46]|4[78]|5[1568])|9(?:03|2[1457-9]|3[1356]|4[08]|[56][23]|82))4\\d{5}|9(?:2(?:257|3(?:24|46|92)|9(?:01|23|64))|3(?:4(?:42|64)|5(?:25|37|4[47]|71)|7(?:35|72)|825))[3-6]\\d{5}|9(?:2(?:2(?:02|2[3467]|4[156]|5[45]|6[6-8]|91)|3(?:1[47]|25|[45][25]|96)|47[48]|625|932)|3(?:38[2578]|4(?:0[0-24-9]|3[78]|4[457]|58|6[035-9]|72|83|9[136-8])|5(?:2[124]|[368][23]|4[2689]|7[2-6])|7(?:16|2[15]|3[14]|4[13]|5[468]|7[3-5]|8[26])|8(?:2[67]|3[278]|4[3-5]|5[78]|6[1-378]|[78]7|94)))[4-6]\\d{5}",
        ,
        ,
        ,
        "91123456789",
        ,
        ,
        ,
        [6, 7, 8]
      ],
      [, , "800\\d{7,8}", , , , "8001234567"],
      [, , "60[04579]\\d{7}", , , , "6001234567", , , [10]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "AR",
      54,
      "00",
      "0",
      ,
      ,
      "0?(?:(11|2(?:2(?:02?|[13]|2[13-79]|4[1-6]|5[2457]|6[124-8]|7[1-4]|8[13-6]|9[1267])|3(?:02?|1[467]|2[03-6]|3[13-8]|[49][2-6]|5[2-8]|[67])|4(?:7[3-578]|9)|6(?:[0136]|2[24-6]|4[6-8]?|5[15-8])|80|9(?:0[1-3]|[19]|2\\d|3[1-6]|4[02568]?|5[2-4]|6[2-46]|72?|8[23]?))|3(?:3(?:2[79]|6|8[2578])|4(?:0[0-24-9]|[12]|3[5-8]?|4[24-7]|5[4-68]?|6[02-9]|7[126]|8[2379]?|9[1-36-8])|5(?:1|2[1245]|3[237]?|4[1-46-9]|6[2-4]|7[1-6]|8[2-5]?)|6[24]|7(?:[069]|1[1568]|2[15]|3[145]|4[13]|5[14-8]|7[2-57]|8[126])|8(?:[01]|2[15-7]|3[2578]?|4[13-6]|5[4-8]?|6[1-357-9]|7[36-8]?|8[5-8]?|9[124])))15)?",
      "9$1",
      ,
      ,
      [[, "(\\d{3})", "$1", ["0|1(?:0[0-35-7]|1[02-5]|2[015]|3[47]|4[478])|911"]], [, "(\\d{2})(\\d{4})", "$1-$2", ["[1-9]"]], [, "(\\d{3})(\\d{4})", "$1-$2", ["[2-9]"]], [, "(\\d{4})(\\d{4})", "$1-$2", ["[1-8]"]], [
        ,
        "(\\d{4})(\\d{2})(\\d{4})",
        "$1 $2-$3",
        [
          "2(?:2[024-9]|3[0-59]|47|6[245]|9[02-8])|3(?:3[28]|4[03-9]|5[2-46-8]|7[1-578]|8[2-9])",
          "2(?:[23]02|6(?:[25]|4[6-8])|9(?:[02356]|4[02568]|72|8[23]))|3(?:3[28]|4(?:[04679]|3[5-8]|5[4-68]|8[2379])|5(?:[2467]|3[237]|8[2-5])|7[1-578]|8(?:[2469]|3[2578]|5[4-8]|7[36-8]|8[5-8]))|2(?:2[24-9]|3[1-59]|47)",
          "2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3[78]|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8[23])|7[1-578]|8(?:[2469]|3[278]|5[56][46]|86[3-6]))|2(?:2[24-9]|3[1-59]|47)|38(?:[58][78]|7[378])|3(?:4[35][56]|58[45]|8(?:[38]5|54|76))[4-6]",
          "2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3(?:5(?:4[0-25689]|[56])|[78])|58|8[2379])|5(?:[2467]|3[237]|8(?:[23]|4(?:[45]|60)|5(?:4[0-39]|5|64)))|7[1-578]|8(?:[2469]|3[278]|54(?:4|5[13-7]|6[89])|86[3-6]))|2(?:2[24-9]|3[1-59]|47)|38(?:[58][78]|7[378])|3(?:454|85[56])[46]|3(?:4(?:36|5[56])|8(?:[38]5|76))[4-6]"
        ],
        "0$1",
        ,
        1
      ], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2-$3", ["1"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["[68]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2-$3", ["[23]"], "0$1", , 1], [
        ,
        "(\\d)(\\d{4})(\\d{2})(\\d{4})",
        "$2 15-$3-$4",
        [
          "9(?:2[2-469]|3[3-578])",
          "9(?:2(?:2[024-9]|3[0-59]|47|6[245]|9[02-8])|3(?:3[28]|4[03-9]|5[2-46-8]|7[1-578]|8[2-9]))",
          "9(?:2(?:[23]02|6(?:[25]|4[6-8])|9(?:[02356]|4[02568]|72|8[23]))|3(?:3[28]|4(?:[04679]|3[5-8]|5[4-68]|8[2379])|5(?:[2467]|3[237]|8[2-5])|7[1-578]|8(?:[2469]|3[2578]|5[4-8]|7[36-8]|8[5-8])))|92(?:2[24-9]|3[1-59]|47)",
          "9(?:2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3[78]|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8[23])|7[1-578]|8(?:[2469]|3[278]|5(?:[56][46]|[78])|7[378]|8(?:6[3-6]|[78]))))|92(?:2[24-9]|3[1-59]|47)|93(?:4[35][56]|58[45]|8(?:[38]5|54|76))[4-6]",
          "9(?:2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3(?:5(?:4[0-25689]|[56])|[78])|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8(?:[23]|4(?:[45]|60)|5(?:4[0-39]|5|64)))|7[1-578]|8(?:[2469]|3[278]|5(?:4(?:4|5[13-7]|6[89])|[56][46]|[78])|7[378]|8(?:6[3-6]|[78]))))|92(?:2[24-9]|3[1-59]|47)|93(?:4(?:36|5[56])|8(?:[38]5|76))[4-6]"
        ],
        "0$1"
      ], [, "(\\d)(\\d{2})(\\d{4})(\\d{4})", "$2 15-$3-$4", ["91"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{5})", "$1-$2-$3", ["8"], "0$1"], [, "(\\d)(\\d{3})(\\d{3})(\\d{4})", "$2 15-$3-$4", ["9"], "0$1"]],
      [
        [
          ,
          "(\\d{4})(\\d{2})(\\d{4})",
          "$1 $2-$3",
          [
            "2(?:2[024-9]|3[0-59]|47|6[245]|9[02-8])|3(?:3[28]|4[03-9]|5[2-46-8]|7[1-578]|8[2-9])",
            "2(?:[23]02|6(?:[25]|4[6-8])|9(?:[02356]|4[02568]|72|8[23]))|3(?:3[28]|4(?:[04679]|3[5-8]|5[4-68]|8[2379])|5(?:[2467]|3[237]|8[2-5])|7[1-578]|8(?:[2469]|3[2578]|5[4-8]|7[36-8]|8[5-8]))|2(?:2[24-9]|3[1-59]|47)",
            "2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3[78]|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8[23])|7[1-578]|8(?:[2469]|3[278]|5[56][46]|86[3-6]))|2(?:2[24-9]|3[1-59]|47)|38(?:[58][78]|7[378])|3(?:4[35][56]|58[45]|8(?:[38]5|54|76))[4-6]",
            "2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3(?:5(?:4[0-25689]|[56])|[78])|58|8[2379])|5(?:[2467]|3[237]|8(?:[23]|4(?:[45]|60)|5(?:4[0-39]|5|64)))|7[1-578]|8(?:[2469]|3[278]|54(?:4|5[13-7]|6[89])|86[3-6]))|2(?:2[24-9]|3[1-59]|47)|38(?:[58][78]|7[378])|3(?:454|85[56])[46]|3(?:4(?:36|5[56])|8(?:[38]5|76))[4-6]"
          ],
          "0$1",
          ,
          1
        ],
        [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2-$3", ["1"], "0$1", , 1],
        [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["[68]"], "0$1"],
        [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2-$3", ["[23]"], "0$1", , 1],
        [, "(\\d)(\\d{4})(\\d{2})(\\d{4})", "$1 $2 $3-$4", [
          "9(?:2[2-469]|3[3-578])",
          "9(?:2(?:2[024-9]|3[0-59]|47|6[245]|9[02-8])|3(?:3[28]|4[03-9]|5[2-46-8]|7[1-578]|8[2-9]))",
          "9(?:2(?:[23]02|6(?:[25]|4[6-8])|9(?:[02356]|4[02568]|72|8[23]))|3(?:3[28]|4(?:[04679]|3[5-8]|5[4-68]|8[2379])|5(?:[2467]|3[237]|8[2-5])|7[1-578]|8(?:[2469]|3[2578]|5[4-8]|7[36-8]|8[5-8])))|92(?:2[24-9]|3[1-59]|47)",
          "9(?:2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3[78]|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8[23])|7[1-578]|8(?:[2469]|3[278]|5(?:[56][46]|[78])|7[378]|8(?:6[3-6]|[78]))))|92(?:2[24-9]|3[1-59]|47)|93(?:4[35][56]|58[45]|8(?:[38]5|54|76))[4-6]",
          "9(?:2(?:[23]02|6(?:[25]|4(?:64|[78]))|9(?:[02356]|4(?:[0268]|5[2-6])|72|8[23]))|3(?:3[28]|4(?:[04679]|3(?:5(?:4[0-25689]|[56])|[78])|5(?:4[46]|8)|8[2379])|5(?:[2467]|3[237]|8(?:[23]|4(?:[45]|60)|5(?:4[0-39]|5|64)))|7[1-578]|8(?:[2469]|3[278]|5(?:4(?:4|5[13-7]|6[89])|[56][46]|[78])|7[378]|8(?:6[3-6]|[78]))))|92(?:2[24-9]|3[1-59]|47)|93(?:4(?:36|5[56])|8(?:[38]5|76))[4-6]"
        ]],
        [, "(\\d)(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3-$4", ["91"]],
        [, "(\\d{3})(\\d{3})(\\d{5})", "$1-$2-$3", ["8"], "0$1"],
        [, "(\\d)(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3-$4", ["9"]]
      ],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "810\\d{7}", , , , , , , [10]],
      [, , "810\\d{7}", , , , "8101234567", , , [10]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    AS: [, [, , "(?:[58]\\d\\d|684|900)\\d{7}", , , , , , , [10], [7]], [, , "684(?:274|6(?:22|33|44|55|77|88|9[19]))\\d{4}", , , , "6846221234", , , , [7]], [, , "684(?:2(?:48|5[2468]|7[246])|7(?:3[13]|70|82))\\d{4}", , , , "6847331234", , , , [7]], [
      ,
      ,
      "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "8002123456"
    ], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "AS", 1, "011", "1", , , "([267]\\d{6})$|1", "684$1", , , , , [, , , , , , , , , [-1]], , "684", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AT: [, [
      ,
      ,
      "1\\d{3,12}|2\\d{6,12}|43(?:(?:0\\d|5[02-9])\\d{3,9}|2\\d{4,5}|[3467]\\d{4}|8\\d{4,6}|9\\d{4,7})|5\\d{4,12}|8\\d{7,12}|9\\d{8,12}|(?:[367]\\d|4[0-24-9])\\d{4,11}",
      ,
      ,
      ,
      ,
      ,
      ,
      [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
      [3]
    ], [, , "1(?:11\\d|[2-9]\\d{3,11})|(?:316|463)\\d{3,10}|648[34]\\d{3,9}|(?:51|66|73)2\\d{3,10}|(?:2(?:1[467]|2[13-8]|5[2357]|6[1-46-8]|7[1-8]|8[124-7]|9[1458])|3(?:1[1-578]|3[23568]|4[5-7]|5[1378]|6[1-38]|8[3-68])|4(?:2[1-8]|35|7[1368]|8[2457])|5(?:2[1-8]|3[357]|4[147]|5[12578]|6[37])|6(?:13|2[1-47]|4[135-7]|5[468])|7(?:2[1-8]|35|4[13478]|5[68]|6[16-8]|7[1-6]|9[45]))\\d{4,10}", , , , "1234567890", , , , [3]], [
      ,
      ,
      "6(?:485|(?:5[0-3579]|6[013-9]|[7-9]\\d)\\d)\\d{3,9}",
      ,
      ,
      ,
      "664123456",
      ,
      ,
      [7, 8, 9, 10, 11, 12, 13]
    ], [, , "800\\d{6,10}", , , , "800123456", , , [9, 10, 11, 12, 13]], [, , "(?:8[69][2-68]|9(?:0[01]|3[019]))\\d{6,10}", , , , "900123456", , , [9, 10, 11, 12, 13]], [, , "8(?:10|2[018])\\d{6,10}|828\\d{5}", , , , "810123456", , , [8, 9, 10, 11, 12, 13]], [, , , , , , , , , [-1]], [, , "5(?:0[1-9]|17|[79]\\d)\\d{2,10}|7[28]0\\d{6,10}", , , , "780123456", , , [5, 6, 7, 8, 9, 10, 11, 12, 13]], "AT", 43, "00", "0", , , "0", , , , [[, "(\\d{4})", "$1", ["14"]], [, "(\\d)(\\d{3,12})", "$1 $2", ["1(?:11|[2-9])"], "0$1"], [, "(\\d{3})(\\d{2})", "$1 $2", ["517"], "0$1"], [
      ,
      "(\\d{2})(\\d{3,5})",
      "$1 $2",
      ["5[079]"],
      "0$1"
    ], [, "(\\d{6})", "$1", ["[18]"]], [, "(\\d{3})(\\d{3,10})", "$1 $2", ["(?:31|4)6|51|6(?:48|5[0-3579]|[6-9])|7(?:20|32|8)|[89]", "(?:31|4)6|51|6(?:485|5[0-3579]|[6-9])|7(?:20|32|8)|[89]"], "0$1"], [, "(\\d{4})(\\d{3,9})", "$1 $2", ["[2-467]|5[2-6]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["5"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4,7})", "$1 $2 $3", ["5"], "0$1"]], [[, "(\\d)(\\d{3,12})", "$1 $2", ["1(?:11|[2-9])"], "0$1"], [, "(\\d{3})(\\d{2})", "$1 $2", ["517"], "0$1"], [
      ,
      "(\\d{2})(\\d{3,5})",
      "$1 $2",
      ["5[079]"],
      "0$1"
    ], [, "(\\d{3})(\\d{3,10})", "$1 $2", ["(?:31|4)6|51|6(?:48|5[0-3579]|[6-9])|7(?:20|32|8)|[89]", "(?:31|4)6|51|6(?:485|5[0-3579]|[6-9])|7(?:20|32|8)|[89]"], "0$1"], [, "(\\d{4})(\\d{3,9})", "$1 $2", ["[2-467]|5[2-6]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["5"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4,7})", "$1 $2 $3", ["5"], "0$1"]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AU: [, [
      ,
      ,
      "1(?:[0-79]\\d{7}(?:\\d(?:\\d{2})?)?|8[0-24-9]\\d{7})|[2-478]\\d{8}|1\\d{4,7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [5, 6, 7, 8, 9, 10, 12]
    ], [, , "(?:(?:241|349)0\\d\\d|8(?:51(?:0(?:0[03-9]|[12479]\\d|3[2-9]|5[0-8]|6[1-9]|8[0-7])|1(?:[0235689]\\d|1[0-69]|4[0-589]|7[0-47-9])|2(?:0[0-79]|[18][13579]|2[14-9]|3[0-46-9]|[4-6]\\d|7[89]|9[0-4])|[34]\\d\\d)|91(?:(?:[0-58]\\d|6[0135-9])\\d|7(?:0[0-24-9]|[1-9]\\d)|9(?:[0-46-9]\\d|5[0-79]))))\\d{3}|(?:2(?:[0-26-9]\\d|3[0-8]|4[02-9]|5[0135-9])|3(?:[0-3589]\\d|4[0-578]|6[1-9]|7[0-35-9])|7(?:[013-57-9]\\d|2[0-8])|8(?:55|6[0-8]|[78]\\d|9[02-9]))\\d{6}", , , , "212345678", , , [9], [8]], [
      ,
      ,
      "4(?:79[01]|83[0-36-9]|95[0-3])\\d{5}|4(?:[0-36]\\d|4[047-9]|[58][0-24-9]|7[02-8]|9[0-47-9])\\d{6}",
      ,
      ,
      ,
      "412345678",
      ,
      ,
      [9]
    ], [, , "180(?:0\\d{3}|2)\\d{3}", , , , "1800123456", , , [7, 10]], [, , "190[0-26]\\d{6}", , , , "1900123456", , , [10]], [, , "13(?:00\\d{6}(?:\\d{2})?|45[0-4]\\d{3})|13\\d{4}", , , , "1300123456", , , [6, 8, 10, 12]], [, , , , , , , , , [-1]], [, , "14(?:5(?:1[0458]|[23][458])|71\\d)\\d{4}", , , , "147101234", , , [9]], "AU", 61, "001[14-689]|14(?:1[14]|34|4[17]|[56]6|7[47]|88)0011", "0", , , "(183[12])|0", , "0011", , [[
      ,
      "(\\d{2})(\\d{3,4})",
      "$1 $2",
      ["16"],
      "0$1"
    ], [, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["13"]], [, "(\\d{3})(\\d{3})", "$1 $2", ["19"]], [, "(\\d{3})(\\d{4})", "$1 $2", ["180", "1802"]], [, "(\\d{4})(\\d{3,4})", "$1 $2", ["19"]], [, "(\\d{2})(\\d{3})(\\d{2,4})", "$1 $2 $3", ["16"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["14|4"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["[2378]"], "(0$1)", "$CC ($1)"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1(?:30|[89])"]], [, "(\\d{4})(\\d{4})(\\d{4})", "$1 $2 $3", ["130"]]], [[
      ,
      "(\\d{2})(\\d{3,4})",
      "$1 $2",
      ["16"],
      "0$1"
    ], [, "(\\d{2})(\\d{3})(\\d{2,4})", "$1 $2 $3", ["16"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["14|4"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["[2378]"], "(0$1)", "$CC ($1)"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1(?:30|[89])"]]], [, , "163\\d{2,6}", , , , "1631234", , , [5, 6, 7, 8, 9]], 1, , [, , "1(?:3(?:00\\d{5}|45[0-4])|802)\\d{3}|1[38]00\\d{6}|13\\d{4}", , , , , , , [6, 7, 8, 10, 12]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AW: [, [, , "(?:[25-79]\\d\\d|800)\\d{4}", , , , , , , [7]], [
      ,
      ,
      "5(?:2\\d|8[1-9])\\d{4}",
      ,
      ,
      ,
      "5212345"
    ], [, , "(?:290|5[69]\\d|6(?:[03]0|22|4[0-2]|[69]\\d)|7(?:[34]\\d|7[07])|9(?:6[45]|9[4-8]))\\d{4}", , , , "5601234"], [, , "800\\d{4}", , , , "8001234"], [, , "900\\d{4}", , , , "9001234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:28\\d|501)\\d{4}", , , , "5011234"], "AW", 297, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[25-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    AX: [, [, , "2\\d{4,9}|35\\d{4,5}|(?:60\\d\\d|800)\\d{4,6}|7\\d{5,11}|(?:[14]\\d|3[0-46-9]|50)\\d{4,8}", , , , , , , [
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12
    ]], [, , "18[1-8]\\d{3,6}", , , , "181234567", , , [6, 7, 8, 9]], [, , "4946\\d{2,6}|(?:4[0-8]|50)\\d{4,8}", , , , "412345678", , , [6, 7, 8, 9, 10]], [, , "800\\d{4,6}", , , , "800123456", , , [7, 8, 9]], [, , "[67]00\\d{5,6}", , , , "600123456", , , [8, 9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "AX", 358, "00|99(?:[01469]|5(?:[14]1|3[23]|5[59]|77|88|9[09]))", "0", , , "0", , "00", , , , [, , , , , , , , , [-1]], , "18", [, , , , , , , , , [-1]], [
      ,
      ,
      "20\\d{4,8}|60[12]\\d{5,6}|7(?:099\\d{4,5}|5[03-9]\\d{3,7})|20[2-59]\\d\\d|(?:606|7(?:0[78]|1|3\\d))\\d{7}|(?:10|29|3[09]|70[1-5]\\d)\\d{4,8}",
      ,
      ,
      ,
      "10112345"
    ], , , [, , , , , , , , , [-1]]],
    AZ: [, [, , "365\\d{6}|(?:[124579]\\d|60|88)\\d{7}", , , , , , , [9], [7]], [, , "(?:2[12]428|3655[02])\\d{4}|(?:2(?:22[0-79]|63[0-28])|3654)\\d{5}|(?:(?:1[28]|46)\\d|2(?:[014-6]2|[23]3))\\d{6}", , , , "123123456", , , , [7]], [, , "36554\\d{4}|(?:[16]0|4[04]|5[015]|7[07]|99)\\d{7}", , , , "401234567"], [, , "88\\d{7}", , , , "881234567"], [, , "900200\\d{3}", , , , "900200123"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "AZ", 994, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3", ["[1-9]"]], [
      ,
      "(\\d{3})(\\d{2})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["90"],
      "0$1"
    ], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[28]|2|365|46", "1[28]|2|365[45]|46", "1[28]|2|365(?:4|5[02])|46"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[13-9]"], "0$1"]], [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["90"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[28]|2|365|46", "1[28]|2|365[45]|46", "1[28]|2|365(?:4|5[02])|46"], "(0$1)"], [
      ,
      "(\\d{2})(\\d{3})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["[13-9]"],
      "0$1"
    ]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BA: [
      ,
      [, , "6\\d{8}|(?:[35689]\\d|49|70)\\d{6}", , , , , , , [8, 9], [6]],
      [, , "(?:3(?:[05-79][2-9]|1[4579]|[23][24-9]|4[2-4689]|8[2457-9])|49[2-579]|5(?:0[2-49]|[13][2-9]|[268][2-4679]|4[4689]|5[2-79]|7[2-69]|9[2-4689]))\\d{5}", , , , "30212345", , , [8], [6]],
      [, , "6040\\d{5}|6(?:03|[1-356]|44|7\\d)\\d{6}", , , , "61123456"],
      [, , "8[08]\\d{6}", , , , "80123456", , , [8]],
      [, , "9[0246]\\d{6}", , , , "90123456", , , [8]],
      [, , "8[12]\\d{6}", , , , "82123456", , , [8]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "BA",
      387,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})", "$1-$2", ["[2-9]"]], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["6[1-3]|[7-9]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2-$3", ["[3-5]|6[56]"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["6"], "0$1"]],
      [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["6[1-3]|[7-9]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2-$3", ["[3-5]|6[56]"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["6"], "0$1"]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "703[235]0\\d{3}|70(?:2[0-5]|3[0146]|[56]0)\\d{4}", , , , "70341234", , , [8]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    BB: [, [, , "(?:246|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [, , "246521[0369]\\d{3}|246(?:2(?:2[78]|7[0-4])|4(?:1[024-6]|2\\d|3[2-9])|5(?:20|[34]\\d|54|7[1-3])|6(?:2\\d|38)|7[35]7|9(?:1[89]|63))\\d{4}", , , , "2464123456", , , , [7]], [, , "246(?:(?:2(?:[3568]\\d|4[0-57-9])|3(?:5[2-9]|6[0-6])|4(?:46|5\\d)|69[5-7]|8(?:[2-5]\\d|83))\\d|52(?:1[147]|20))\\d{3}", , , , "2462501234", , , , [7]], [
      ,
      ,
      "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "8002123456"
    ], [, , "(?:246976|900[2-9]\\d\\d)\\d{4}", , , , "9002123456", , , , [7]], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , "24631\\d{5}", , , , "2463101234", , , , [7]], "BB", 1, "011", "1", , , "([2-9]\\d{6})$|1", "246$1", , , , , [, , , , , , , , , [-1]], , "246", [, , , , , , , , , [-1]], [
      ,
      ,
      "246(?:292|367|4(?:1[7-9]|3[01]|4[47-9]|67)|7(?:1[2-9]|2\\d|3[016]|53))\\d{4}",
      ,
      ,
      ,
      "2464301234",
      ,
      ,
      ,
      [7]
    ], , , [, , , , , , , , , [-1]]],
    BD: [, [, , "[1-469]\\d{9}|8[0-79]\\d{7,8}|[2-79]\\d{8}|[2-9]\\d{7}|[3-9]\\d{6}|[57-9]\\d{5}", , , , , , , [6, 7, 8, 9, 10]], [
      ,
      ,
      "(?:4(?:31\\d\\d|423)|5222)\\d{3}(?:\\d{2})?|8332[6-9]\\d\\d|(?:3(?:03[56]|224)|4(?:22[25]|653))\\d{3,4}|(?:3(?:42[47]|529|823)|4(?:027|525|65(?:28|8))|562|6257|7(?:1(?:5[3-5]|6[12]|7[156]|89)|22[589]56|32|42675|52(?:[25689](?:56|8)|[347]8)|71(?:6[1267]|75|89)|92374)|82(?:2[59]|32)56|9(?:03[23]56|23(?:256|373)|31|5(?:1|2[4589]56)))\\d{3}|(?:3(?:02[348]|22[35]|324|422)|4(?:22[67]|32[236-9]|6(?:2[46]|5[57])|953)|5526|6(?:024|6655)|81)\\d{4,5}|(?:2(?:7(?:1[0-267]|2[0-289]|3[0-29]|4[01]|5[1-3]|6[013]|7[0178]|91)|8(?:0[125]|1[1-6]|2[0157-9]|3[1-69]|41|6[1-35]|7[1-5]|8[1-8]|9[0-6])|9(?:0[0-2]|1[0-4]|2[568]|3[3-6]|5[5-7]|6[0136-9]|7[0-7]|8[014-9]))|3(?:0(?:2[025-79]|3[2-4])|181|22[12]|32[2356]|824)|4(?:02[09]|22[348]|32[045]|523|6(?:27|54))|666(?:22|53)|7(?:22[57-9]|42[56]|82[35])8|8(?:0[124-9]|2(?:181|2[02-4679]8)|4[12]|[5-7]2)|9(?:[04]2|2(?:2|328)|81))\\d{4}|(?:2(?:[23]\\d|[45])\\d\\d|3(?:1(?:2[5-7]|[5-7])|425|822)|4(?:033|1\\d|[257]1|332|4(?:2[246]|5[25])|6(?:2[35]|56|62)|8(?:23|54)|92[2-5])|5(?:02[03489]|22[457]|32[35-79]|42[46]|6(?:[18]|53)|724|826)|6(?:023|2(?:2[2-5]|5[3-5]|8)|32[3478]|42[34]|52[47]|6(?:[18]|6(?:2[34]|5[24]))|[78]2[2-5]|92[2-6])|7(?:02|21\\d|[3-589]1|6[12]|72[24])|8(?:217|3[12]|[5-7]1)|9[24]1)\\d{5}|(?:(?:3[2-8]|5[2-57-9]|6[03-589])1|4[4689][18])\\d{5}|[59]1\\d{5}",
      ,
      ,
      ,
      "27111234"
    ], [, , "(?:1[13-9]\\d|644)\\d{7}|(?:3[78]|44|66)[02-9]\\d{7}", , , , "1812345678", , , [10]], [, , "80[03]\\d{7}", , , , "8001234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "96(?:0[1-69]|1[0-479]|2[278]|3[13-9]|4[0-47-9]|54|6[69]|7[78]|88)\\d{6}", , , , "9604123456", , , [10]], "BD", 880, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{4,6})", "$1-$2", ["31[5-8]|[459]1"], "0$1"], [
      ,
      "(\\d{3})(\\d{3,7})",
      "$1-$2",
      ["3(?:[67]|8[013-9])|4(?:6[168]|7|[89][18])|5(?:6[128]|9)|6(?:[15]|28|4[14])|7[2-589]|8(?:0[014-9]|[12])|9[358]|(?:3[2-5]|4[235]|5[2-578]|6[0389]|76|8[3-7]|9[24])1|(?:44|66)[01346-9]"],
      "0$1"
    ], [, "(\\d{4})(\\d{3,6})", "$1-$2", ["[13-9]|2[23]"], "0$1"], [, "(\\d)(\\d{7,8})", "$1-$2", ["2"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BE: [, [, , "4\\d{8}|[1-9]\\d{7}", , , , , , , [8, 9]], [, , "80[2-8]\\d{5}|(?:1[0-69]|[23][2-8]|4[23]|5\\d|6[013-57-9]|71|8[1-79]|9[2-4])\\d{6}", , , , "12345678", , , [8]], [, , "4[5-9]\\d{7}", , , , "450001234", , , [9]], [, , "800[1-9]\\d{4}", , , , "80012345", , , [8]], [, , "(?:70(?:2[0-57]|3[04-7]|44|6[04-69]|7[0579])|90\\d\\d)\\d{4}", , , , "90012345", , , [8]], [
      ,
      ,
      "7879\\d{4}",
      ,
      ,
      ,
      "78791234",
      ,
      ,
      [8]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BE", 32, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["(?:80|9)0"], "0$1"], [, "(\\d)(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[239]|4[23]"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[15-8]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["4"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "78(?:0[578]|1[014-8]|2[25]|3[15-8]|48|5[05]|60|7[06-8]|9\\d)\\d{4}", , , , "78102345", , , [8]], , , [, , , , , , , , , [-1]]],
    BF: [, [
      ,
      ,
      "[024-7]\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8]
    ], [, , "2(?:0(?:49|5[23]|6[5-7]|9[016-9])|4(?:4[569]|5[4-6]|6[5-7]|7[0179])|5(?:[34]\\d|50|6[5-8]))\\d{4}", , , , "20491234"], [, , "(?:0[1-7]|4[4-6]|5[0-8]|[67]\\d)\\d{6}", , , , "70123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BF", 226, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[024-7]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BG: [, [
      ,
      ,
      "00800\\d{7}|[2-7]\\d{6,7}|[89]\\d{6,8}|2\\d{5}",
      ,
      ,
      ,
      ,
      ,
      ,
      [6, 7, 8, 9, 12],
      [4, 5]
    ], [, , "2\\d{5,7}|(?:43[1-6]|70[1-9])\\d{4,5}|(?:[36]\\d|4[124-7]|[57][1-9]|8[1-6]|9[1-7])\\d{5,6}", , , , "2123456", , , [6, 7, 8], [4, 5]], [, , "(?:43[07-9]|99[69]\\d)\\d{5}|(?:8[7-9]|98)\\d{7}", , , , "43012345", , , [8, 9]], [, , "(?:00800\\d\\d|800)\\d{5}", , , , "80012345", , , [8, 12]], [, , "90\\d{6}", , , , "90123456", , , [8]], [, , "700\\d{5}", , , , "70012345", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BG", 359, "00", "0", , , "0", , , , [[, "(\\d{6})", "$1", ["1"]], [, "(\\d)(\\d)(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["2"], "0$1"], [
      ,
      "(\\d{3})(\\d{4})",
      "$1 $2",
      ["43[1-6]|70[1-9]"],
      "0$1"
    ], [, "(\\d)(\\d{3})(\\d{3,4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2,3})", "$1 $2 $3", ["[356]|4[124-7]|7[1-9]|8[1-6]|9[1-7]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["(?:70|8)0"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3", ["43[1-7]|7"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[48]|9[08]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["9"], "0$1"]], [[, "(\\d)(\\d)(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["2"], "0$1"], [
      ,
      "(\\d{3})(\\d{4})",
      "$1 $2",
      ["43[1-6]|70[1-9]"],
      "0$1"
    ], [, "(\\d)(\\d{3})(\\d{3,4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2,3})", "$1 $2 $3", ["[356]|4[124-7]|7[1-9]|8[1-6]|9[1-7]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["(?:70|8)0"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3", ["43[1-7]|7"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[48]|9[08]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["9"], "0$1"]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BH: [
      ,
      [
        ,
        ,
        "[136-9]\\d{7}",
        ,
        ,
        ,
        ,
        ,
        ,
        [8]
      ],
      [, , "(?:1(?:3[1356]|6[0156]|7\\d)\\d|6(?:1[16]\\d|500|6(?:0\\d|3[12]|44|55|7[7-9]|88)|9[69][69])|7(?:[07]\\d\\d|1(?:11|78)))\\d{4}", , , , "17001234"],
      [, , "(?:3(?:[0-79]\\d|8[0-57-9])\\d|6(?:3(?:00|33|6[16])|441|6(?:3[03-9]|[69]\\d|7[0-689])))\\d{4}", , , , "36001234"],
      [, , "8[02369]\\d{6}", , , , "80123456"],
      [, , "(?:87|9[0-8])\\d{6}", , , , "90123456"],
      [, , "84\\d{6}", , , , "84123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "BH",
      973,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{4})(\\d{4})", "$1 $2", ["[13679]|8[02-4679]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    BI: [, [, , "(?:[267]\\d|31)\\d{6}", , , , , , , [8]], [, , "(?:22|31)\\d{6}", , , , "22201234"], [, , "(?:29|6[1-9]|7[125-9])\\d{6}", , , , "79561234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BI", 257, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2367]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BJ: [, [, , "(?:01\\d|8)\\d{7}", , , , , , , [8, 10]], [, , "012\\d{7}", , , , "0120211234", , , [10]], [
      ,
      ,
      "01(?:2[5-9]|[4-69]\\d)\\d{6}",
      ,
      ,
      ,
      "0195123456",
      ,
      ,
      [10]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "857[58]\\d{4}", , , , "85751234", , , [8]], "BJ", 229, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["0"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "81\\d{6}", , , , "81123456", , , [8]], , , [, , , , , , , , , [-1]]],
    BL: [
      ,
      [, , "7090\\d{5}|(?:[56]9|[89]\\d)\\d{7}", , , , , , , [9]],
      [, , "(?:59(?:0(?:2[7-9]|3[3-7]|5[12]|87)|87\\d)|80[6-9]\\d\\d)\\d{4}", , , , "590271234"],
      [, , "(?:69(?:0\\d\\d|1(?:2[2-9]|3[0-5]))|7090[0-4])\\d{4}", , , , "690001234"],
      [, , "80[0-5]\\d{6}", , , , "800012345"],
      [, , "8[129]\\d{7}", , , , "810123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "9(?:(?:39[5-7]|76[018])\\d|475[0-6])\\d{4}", , , , "976012345"],
      "BL",
      590,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    BM: [, [, , "(?:441|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [, , "441(?:[46]\\d\\d|5(?:4\\d|60|89))\\d{4}", , , , "4414123456", , , , [7]], [
      ,
      ,
      "441(?:[2378]\\d|5[0-39]|9[02])\\d{5}",
      ,
      ,
      ,
      "4413701234",
      ,
      ,
      ,
      [7]
    ], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "BM", 1, "011", "1", , , "([2-9]\\d{6})$|1", "441$1", , , , , [, , , , , , , , , [-1]], , "441", [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    BN: [, [, , "[2-578]\\d{6}", , , , , , , [7]], [, , "22[0-7]\\d{4}|(?:2[013-9]|[34]\\d|5[0-25-9])\\d{5}", , , , "2345678"], [, , "(?:22[89]|[78]\\d\\d)\\d{4}", , , , "7123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "5[34]\\d{5}", , , , "5345678"], "BN", 673, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[2-578]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BO: [, [, , "(?:[2-7]\\d\\d|8001)\\d{5}", , , , , , , [8, 9], [7]], [
      ,
      ,
      "(?:2(?:2\\d\\d|5(?:11|[258]\\d|9[67])|6(?:12|2\\d|9[34])|8(?:2[34]|39|62))|3(?:3\\d\\d|4(?:6\\d|8[24])|8(?:25|42|5[257]|86|9[25])|9(?:[27]\\d|3[2-4]|4[248]|5[24]|6[2-6]))|4(?:4\\d\\d|6(?:11|[24689]\\d|72)))\\d{4}",
      ,
      ,
      ,
      "22123456",
      ,
      ,
      [8],
      [7]
    ], [, , "(?:57|[67]\\d)\\d{6}", , , , "71234567", , , [8]], [, , "8001[07]\\d{4}", , , , "800171234", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "50\\d{6}", , , , "50123456", , , [8], [7]], "BO", 591, "00(?:1\\d)?", "0", , , "0(1\\d)?", , , , [[, "(\\d)(\\d{7})", "$1 $2", ["[23]|4[46]|50"], , "0$CC $1"], [, "(\\d{8})", "$1", ["[5-7]"], , "0$CC $1"], [, "(\\d{3})(\\d{2})(\\d{4})", "$1 $2 $3", ["8"], , "0$CC $1"]], , [, , , , , , , , , [-1]], , , [, , "8001[07]\\d{4}", , , , , , , [9]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BQ: [, [
      ,
      ,
      "(?:[34]1|7\\d)\\d{5}",
      ,
      ,
      ,
      ,
      ,
      ,
      [7]
    ], [, , "(?:318[023]|41(?:6[023]|70)|7(?:1[578]|2[05]|50)\\d)\\d{3}", , , , "7151234"], [, , "(?:31(?:8[14-8]|9[14578])|416[14-9]|7(?:0[01]|7[07]|8\\d|9[056])\\d)\\d{3}", , , , "3181234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BQ", 599, "00", , , , , , , , , , [, , , , , , , , , [-1]], , "[347]", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BR: [, [, , "[1-467]\\d{9,10}|55[0-46-9]\\d{8}|[34]\\d{7}|55\\d{7,8}|(?:5[0-46-9]|[89]\\d)\\d{7,9}", , , , , , , [8, 9, 10, 11]], [
      ,
      ,
      "(?:[14689][1-9]|2[12478]|3[1-578]|5[13-5]|7[13-579])[2-5]\\d{7}",
      ,
      ,
      ,
      "1123456789",
      ,
      ,
      [10],
      [8]
    ], [, , "(?:[14689][1-9]|2[12478]|3[1-578]|5[13-5]|7[13-579])(?:7|9\\d)\\d{7}", , , , "11961234567", , , [10, 11], [8, 9]], [, , "800\\d{6,7}", , , , "800123456", , , [9, 10]], [, , "[59]00\\d{6,7}", , , , "500123456", , , [9, 10]], [, , "(?:30[03]\\d{3}|4(?:0(?:0\\d|20)|370|864))\\d{4}|300\\d{5}", , , , "40041234", , , [8, 10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BR", 55, "00(?:1[245]|2[1-35]|31|4[13]|[56]5|99)", "0", , , "(?:0|90)(?:(1[245]|2[1-35]|31|4[13]|[56]5|99)(\\d{10,11}))?", "$2", , , [
      [, "(\\d{3,6})", "$1", ["1(?:1[25-8]|2[357-9]|3[02-68]|4[12568]|5|6[0-8]|8[015]|9[0-47-9])|321|610"]],
      [, "(\\d{4})(\\d{4})", "$1-$2", ["300|4(?:0[02]|37|86)", "300|4(?:0(?:0|20)|370|864)"]],
      [, "(\\d{4})(\\d{4})", "$1-$2", ["[2-57]", "[2357]|4(?:[0-24-9]|3(?:[0-689]|7[1-9]))"]],
      [, "(\\d{3})(\\d{2,3})(\\d{4})", "$1 $2 $3", ["(?:[358]|90)0"], "0$1"],
      [, "(\\d{5})(\\d{4})", "$1-$2", ["9"]],
      [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2-$3", ["(?:[14689][1-9]|2[12478]|3[1-578]|5[13-5]|7[13-579])[2-57]"], "($1)", "0 $CC ($1)"],
      [, "(\\d{2})(\\d{5})(\\d{4})", "$1 $2-$3", ["[16][1-9]|[2-57-9]"], "($1)", "0 $CC ($1)"]
    ], [[
      ,
      "(\\d{4})(\\d{4})",
      "$1-$2",
      ["300|4(?:0[02]|37|86)", "300|4(?:0(?:0|20)|370|864)"]
    ], [, "(\\d{3})(\\d{2,3})(\\d{4})", "$1 $2 $3", ["(?:[358]|90)0"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2-$3", ["(?:[14689][1-9]|2[12478]|3[1-578]|5[13-5]|7[13-579])[2-57]"], "($1)", "0 $CC ($1)"], [, "(\\d{2})(\\d{5})(\\d{4})", "$1 $2-$3", ["[16][1-9]|[2-57-9]"], "($1)", "0 $CC ($1)"]], [, , , , , , , , , [-1]], , , [, , "(?:30[03]\\d{3}|4(?:0(?:0\\d|20)|864))\\d{4}|800\\d{6,7}|300\\d{5}", , , , , , , [8, 9, 10]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BS: [, [
      ,
      ,
      "(?:242|[58]\\d\\d|900)\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [10],
      [7]
    ], [, , "242(?:3(?:02|[236][1-9]|4[0-24-9]|5[0-68]|7[347]|8[0-4]|9[2-467])|461|502|6(?:0[1-5]|12|2[013]|[45]0|7[67]|8[78]|9[89])|7(?:02|88))\\d{4}", , , , "2423456789", , , , [7]], [, , "242(?:3(?:5[79]|7[56]|95)|4(?:[23][1-9]|4[1-35-9]|5[1-8]|6[2-8]|7\\d|81)|5(?:2[45]|3[35]|44|5[1-46-9]|65|77)|6[34]6|7(?:27|38)|8(?:0[1-9]|1[02-9]|2\\d|3[0-4]|[89]9))\\d{4}", , , , "2423591234", , , , [7]], [, , "242300\\d{4}|8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456", , , , [7]], [, , "900[2-9]\\d{6}", , , , "9002123456"], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "BS", 1, "011", "1", , , "([3-8]\\d{6})$|1", "242$1", , , , , [, , , , , , , , , [-1]], , "242", [, , , , , , , , , [-1]], [, , "242225\\d{4}", , , , "2422250123"], , , [, , , , , , , , , [-1]]],
    BT: [, [, , "[178]\\d{7}|[2-8]\\d{6}", , , , , , , [7, 8], [6]], [
      ,
      ,
      "(?:2[3-6]|[34][5-7]|5[236]|6[2-46]|7[246]|8[2-4])\\d{5}",
      ,
      ,
      ,
      "2345678",
      ,
      ,
      [7],
      [6]
    ], [, , "(?:1[67]|[78]7)\\d{6}", , , , "17123456", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BT", 975, "00", , , , , , , , [[, "(\\d{3})(\\d{3})", "$1 $2", ["[2-7]"]], [, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-6]|7[246]|8[2-4]"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[67]|[78]"]]], [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-6]|7[246]|8[2-4]"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[67]|[78]"]]], [, , , , , , , , , [-1]], , , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BW: [, [, , "(?:0800|(?:[37]|800)\\d)\\d{6}|(?:[2-6]\\d|90)\\d{5}", , , , , , , [7, 8, 10]], [, , "(?:2(?:4[0-48]|6[0-24]|9[0578])|3(?:1[0-35-9]|55|[69]\\d|7[013]|81)|4(?:6[03]|7[1267]|9[0-5])|5(?:3[03489]|4[0489]|7[1-47]|88|9[0-49])|6(?:2[1-35]|5[149]|8[013467]))\\d{4}", , , , "2401234", , , [7]], [, , "(?:321|7(?:[1-8]\\d|9[03]))\\d{5}", , , , "71123456", , , [8]], [, , "(?:0800|800\\d)\\d{6}", , , , "0800012345", , , [10]], [, , "90\\d{5}", , , , "9012345", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "79(?:1(?:[0-2]\\d|3[0-8])|2[0-7]\\d)\\d{3}",
      ,
      ,
      ,
      "79101234",
      ,
      ,
      [8]
    ], "BW", 267, "00", , , , , , , , [[, "(\\d{2})(\\d{5})", "$1 $2", ["90"]], [, "(\\d{3})(\\d{4})", "$1 $2", ["[24-6]|3[15-9]"]], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[37]"]], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["0"]], [, "(\\d{3})(\\d{4})(\\d{3})", "$1 $2 $3", ["8"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BY: [, [, , "(?:[12]\\d|33|44|902)\\d{7}|8(?:0[0-79]\\d{5,7}|[1-7]\\d{9})|8(?:1[0-489]|[5-79]\\d)\\d{7}|8[1-79]\\d{6,7}|8[0-79]\\d{5}|8\\d{5}", , , , , , , [
      6,
      7,
      8,
      9,
      10,
      11
    ], [5]], [, , "(?:1(?:5(?:1[1-5]|[24]\\d|6[2-4]|9[1-7])|6(?:[235]\\d|4[1-7])|7\\d\\d)|2(?:1(?:[246]\\d|3[0-35-9]|5[1-9])|2(?:[235]\\d|4[0-8])|3(?:[26]\\d|3[02-79]|4[024-7]|5[03-7])))\\d{5}", , , , "152450911", , , [9], [5, 6, 7]], [, , "(?:2(?:5[5-79]|9[1-9])|(?:33|44)\\d)\\d{6}", , , , "294911911", , , [9]], [, , "800\\d{3,7}|8(?:0[13]|20\\d)\\d{7}", , , , "8011234567"], [, , "(?:810|902)\\d{7}", , , , "9021234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "249\\d{6}", , , , "249123456", , , [9]], "BY", 375, "810", "8", , , "0|80?", , "8~10", , [[
      ,
      "(\\d{3})(\\d{3})",
      "$1 $2",
      ["800"],
      "8 $1"
    ], [, "(\\d{3})(\\d{2})(\\d{2,4})", "$1 $2 $3", ["800"], "8 $1"], [, "(\\d{4})(\\d{2})(\\d{3})", "$1 $2-$3", ["1(?:5[169]|6[3-5]|7[179])|2(?:1[35]|2[34]|3[3-5])", "1(?:5[169]|6(?:3[1-3]|4|5[125])|7(?:1[3-9]|7[0-24-6]|9[2-7]))|2(?:1[35]|2[34]|3[3-5])"], "8 0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["1(?:[56]|7[467])|2[1-3]"], "8 0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["[1-4]"], "8 0$1"], [
      ,
      "(\\d{3})(\\d{3,4})(\\d{4})",
      "$1 $2 $3",
      ["[89]"],
      "8 $1"
    ]], , [, , , , , , , , , [-1]], , , [, , "800\\d{3,7}|(?:8(?:0[13]|10|20\\d)|902)\\d{7}"], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    BZ: [, [, , "(?:0800\\d|[2-8])\\d{6}", , , , , , , [7, 11]], [, , "(?:2(?:[02]\\d|36|[68]0)|[3-58](?:[02]\\d|[68]0)|7(?:[02]\\d|32|[68]0))\\d{4}", , , , "2221234", , , [7]], [, , "6[0-35-7]\\d{5}", , , , "6221234", , , [7]], [, , "0800\\d{7}", , , , "08001234123", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "BZ", 501, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1-$2", ["[2-8]"]], [
      ,
      "(\\d)(\\d{3})(\\d{4})(\\d{3})",
      "$1-$2-$3-$4",
      ["0"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CA: [
      ,
      [, , "[2-9]\\d{9}|3\\d{6}", , , , , , , [7, 10]],
      [, , "(?:2(?:04|[23]6|[48]9|5[07]|63)|3(?:06|43|54|6[578]|82)|4(?:03|1[68]|[26]8|3[178]|50|74)|5(?:06|1[49]|48|79|8[147])|6(?:04|[18]3|39|47|72)|7(?:0[59]|42|53|78|8[02])|8(?:[06]7|19|25|7[39])|9(?:0[25]|42))[2-9]\\d{6}", , , , "5062345678", , , [10], [7]],
      [
        ,
        ,
        "(?:2(?:04|[23]6|[48]9|5[07]|63)|3(?:06|43|54|6[578]|82)|4(?:03|1[68]|[26]8|3[178]|50|74)|5(?:06|1[49]|48|79|8[147])|6(?:04|[18]3|39|47|72)|7(?:0[59]|42|53|78|8[02])|8(?:[06]7|19|25|7[39])|9(?:0[25]|42))[2-9]\\d{6}",
        ,
        ,
        ,
        "5062345678",
        ,
        ,
        [10],
        [7]
      ],
      [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456", , , [10]],
      [, , "900[2-9]\\d{6}", , , , "9002123456", , , [10]],
      [, , , , , , , , , [-1]],
      [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|(?:5(?:2[125-9]|3[23]|44|66|77|88)|6(?:22|33))[2-9]\\d{6}", , , , "5219023456", , , [10]],
      [, , "600[2-9]\\d{6}", , , , "6002012345", , , [10]],
      "CA",
      1,
      "011",
      "1",
      ,
      ,
      "1",
      ,
      ,
      1,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "310\\d{4}", , , , "3101234", , , [7]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    CC: [, [, , "1(?:[0-79]\\d{8}(?:\\d{2})?|8[0-24-9]\\d{7})|[148]\\d{8}|1\\d{5,7}", , , , , , , [6, 7, 8, 9, 10, 12]], [, , "8(?:51(?:0(?:02|31|60|89)|1(?:18|76)|223)|91(?:0(?:1[0-2]|29)|1(?:[28]2|50|79)|2(?:10|64)|3(?:[06]8|22)|4[29]8|62\\d|70[23]|959))\\d{3}", , , , "891621234", , , [9], [8]], [, , "4(?:79[01]|83[0-36-9]|95[0-3])\\d{5}|4(?:[0-36]\\d|4[047-9]|[58][0-24-9]|7[02-8]|9[0-47-9])\\d{6}", , , , "412345678", , , [9]], [
      ,
      ,
      "180(?:0\\d{3}|2)\\d{3}",
      ,
      ,
      ,
      "1800123456",
      ,
      ,
      [7, 10]
    ], [, , "190[0-26]\\d{6}", , , , "1900123456", , , [10]], [, , "13(?:00\\d{6}(?:\\d{2})?|45[0-4]\\d{3})|13\\d{4}", , , , "1300123456", , , [6, 8, 10, 12]], [, , , , , , , , , [-1]], [, , "14(?:5(?:1[0458]|[23][458])|71\\d)\\d{4}", , , , "147101234", , , [9]], "CC", 61, "001[14-689]|14(?:1[14]|34|4[17]|[56]6|7[47]|88)0011", "0", , , "([59]\\d{7})$|0", "8$1", "0011", , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CD: [, [, , "(?:(?:[189]|5\\d)\\d|2)\\d{7}|[1-68]\\d{6}", , , , , , , [7, 8, 9, 10]], [
      ,
      ,
      "(?:(?:12|573)\\d\\d|276)\\d{5}|[1-6]\\d{6}",
      ,
      ,
      ,
      "1234567"
    ], [, , "88\\d{5}|(?:8[0-69]|9[016-9])\\d{7}", , , , "991234567", , , [7, 9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CD", 243, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3", ["88"], "0$1"], [, "(\\d{2})(\\d{5})", "$1 $2", ["[1-6]"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[89]"], "0$1"], [
      ,
      "(\\d{2})(\\d{2})(\\d{3})(\\d{3})",
      "$1 $2 $3 $4",
      ["5"],
      "0$1"
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CF: [, [, , "8776\\d{4}|(?:[27]\\d|61)\\d{6}", , , , , , , [8]], [, , "(?:2[12]|61)\\d{6}", , , , "21612345"], [, , "7[02-7]\\d{6}", , , , "70012345"], [, , , , , , , , , [-1]], [, , "8776\\d{4}", , , , "87761234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CF", 236, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[26-8]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CG: [
      ,
      [, , "222\\d{6}|(?:0\\d|80)\\d{7}", , , , , , , [9]],
      [, , "222[1-589]\\d{5}", , , , "222123456"],
      [, , "026(?:1[0-5]|6[6-9])\\d{4}|0(?:[14-6]\\d\\d|2(?:40|5[5-8]|6[07-9]))\\d{5}", , , , "061234567"],
      [, , , , , , , , , [-1]],
      [, , "80[0-2]\\d{6}", , , , "800123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "CG",
      242,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["8"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[02]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    CH: [, [, , "8\\d{11}|[2-9]\\d{8}", , , , , , , [9, 12]], [
      ,
      ,
      "(?:2[12467]|3[1-4]|4[134]|5[256]|6[12]|[7-9]1)\\d{7}",
      ,
      ,
      ,
      "212345678",
      ,
      ,
      [9]
    ], [, , "(?:6[89]|7[235-9])\\d{7}", , , , "781234567", , , [9]], [, , "800\\d{6}", , , , "800123456", , , [9]], [, , "90[016]\\d{6}", , , , "900123456", , , [9]], [, , "84[0248]\\d{6}", , , , "840123456", , , [9]], [, , "878\\d{6}", , , , "878123456", , , [9]], [, , , , , , , , , [-1]], "CH", 41, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["8[047]|90"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2-79]|81"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["8"], "0$1"]], , [
      ,
      ,
      "74[0248]\\d{6}",
      ,
      ,
      ,
      "740123456",
      ,
      ,
      [9]
    ], , , [, , , , , , , , , [-1]], [, , "5[18]\\d{7}", , , , "581234567", , , [9]], , , [, , "860\\d{9}", , , , "860123456789", , , [12]]],
    CI: [, [, , "[02]\\d{9}", , , , , , , [10]], [, , "2(?:[15]\\d{3}|7(?:2(?:0[23]|1[2357]|2[245]|3[45]|4[3-5])|3(?:06|1[69]|[2-6]7)))\\d{5}", , , , "2123456789"], [, , "0[157]\\d{8}", , , , "0123456789"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CI", 225, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d)(\\d{5})", "$1 $2 $3 $4", ["2"]], [
      ,
      "(\\d{2})(\\d{2})(\\d{2})(\\d{4})",
      "$1 $2 $3 $4",
      ["0"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CK: [, [, , "[2-578]\\d{4}", , , , , , , [5]], [, , "(?:2\\d|3[13-7]|4[1-5])\\d{3}", , , , "21234"], [, , "[578]\\d{4}", , , , "71234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CK", 682, "00", , , , , , , , [[, "(\\d{2})(\\d{3})", "$1 $2", ["[2-578]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CL: [, [, , "12300\\d{6}|6\\d{9,10}|[2-9]\\d{8}", , , , , , , [9, 10, 11]], [
      ,
      ,
      "2(?:1982[0-6]|3314[05-9])\\d{3}|(?:2(?:1(?:160|962)|3(?:(?:[24]\\d|50)\\d|3(?:[0346-9]\\d|1[0-35-9]|2[1-9]|5[0-24-9])|600)|646[59])|(?:600|80[1-9])\\d\\d|9(?:(?:10[0-2]|7[1-9]\\d)\\d|3(?:[0-57-9]\\d\\d|6(?:0[02-9]|[1-9]\\d))|6(?:[0-8]\\d\\d|9(?:[02-79]\\d|1[05-9]))|9(?:[03-9]\\d\\d|1(?:[0235-9]\\d|4[0-24-9])|2(?:[0-79]\\d|8[0-46-9]))))\\d{4}|(?:22|3[2-5]|[47][1-35]|5[1-3578]|6[13-57]|8[1-9]|9[2458])\\d{7}",
      ,
      ,
      ,
      "600123456",
      ,
      ,
      [9]
    ], [, , "2(?:1982[0-6]|3314[05-9])\\d{3}|(?:2(?:1(?:160|962)|3(?:(?:[24]\\d|50)\\d|3(?:[0346-9]\\d|1[0-35-9]|2[1-9]|5[0-24-9])|600)|646[59])|80[1-8]\\d\\d|9(?:(?:10[0-2]|7[1-9]\\d)\\d|3(?:[0-57-9]\\d\\d|6(?:0[02-9]|[1-9]\\d))|6(?:[0-8]\\d\\d|9(?:[02-79]\\d|1[05-9]))|9(?:[03-9]\\d\\d|1(?:[0235-9]\\d|4[0-24-9])|2(?:[0-79]\\d|8[0-46-9]))))\\d{4}|(?:22|3[2-5]|[47][1-35]|5[1-3578]|6[13-57]|8[1-9]|9[2458])\\d{7}", , , , "221234567", , , [9]], [, , "(?:123|8)00\\d{6}", , , , "800123456", , , [9, 11]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , "600\\d{7,8}", , , , "6001234567", , , [10, 11]], [, , , , , , , , , [-1]], [, , "44\\d{7}", , , , "441234567", , , [9]], "CL", 56, "(?:0|1(?:1[0-69]|2[02-5]|5[13-58]|69|7[0167]|8[018]))0", , , , , , , , [[, "(\\d{4})", "$1", ["1(?:[03-589]|21)|[29]0|78"]], [, "(\\d{5})(\\d{4})", "$1 $2", ["219", "2196"], "($1)"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["60|809"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["44"]], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["2[1-36]"], "($1)"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["9(?:10|[2-9])"]], [
      ,
      "(\\d{2})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["3[2-5]|[47]|5[1-3578]|6[13-57]|8(?:0[1-8]|[1-9])"],
      "($1)"
    ], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["60|8"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["60"]]], [[, "(\\d{5})(\\d{4})", "$1 $2", ["219", "2196"], "($1)"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["60|809"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["44"]], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["2[1-36]"], "($1)"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["9(?:10|[2-9])"]], [
      ,
      "(\\d{2})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["3[2-5]|[47]|5[1-3578]|6[13-57]|8(?:0[1-8]|[1-9])"],
      "($1)"
    ], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["60|8"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["60"]]], [, , , , , , , , , [-1]], , , [, , "600\\d{7,8}", , , , , , , [10, 11]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CM: [
      ,
      [, , "[26]\\d{8}|88\\d{6,7}", , , , , , , [8, 9]],
      [, , "2(?:22|33)\\d{6}", , , , "222123456", , , [9]],
      [, , "(?:24[23]|6(?:[25-9]\\d|4[0-2]))\\d{6}", , , , "671234567", , , [9]],
      [, , "88\\d{6,7}", , , , "88012345"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "CM",
      237,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["88"]], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[26]|88"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    CN: [, [, , "(?:(?:1[03-689]|2\\d)\\d\\d|6)\\d{8}|1\\d{10}|[126]\\d{6}(?:\\d(?:\\d{2})?)?|86\\d{5,6}|(?:[3-579]\\d|8[0-57-9])\\d{5,9}", , , , , , , [7, 8, 9, 10, 11, 12], [5, 6]], [
      ,
      ,
      "(?:10(?:[02-79]\\d\\d|[18](?:0[1-9]|[1-9]\\d))|2(?:[02-57-9]\\d{3}|1(?:[18](?:0[1-9]|[1-9]\\d)|[2-79]\\d\\d))|(?:41[03]|8078|9(?:78|94))\\d\\d)\\d{5}|(?:10|2[0-57-9])(?:1(?:00|23)\\d\\d|95\\d{3,4})|(?:41[03]|9(?:78|94))(?:100\\d\\d|95\\d{3,4})|8078123|(?:43[35]|754|851)\\d{7,8}|(?:43[35]|754|851)(?:1(?:00\\d|23)\\d|95\\d{3,4})|(?:3(?:11|7[179])|4(?:[15]1|3[12])|5(?:1\\d|2[37]|3[12]|51|7[13-79]|9[15])|7(?:[39]1|5[57]|6[09])|8(?:71|98))(?:[02-8]\\d{7}|1(?:0(?:0\\d\\d(?:\\d{3})?|[1-9]\\d{5})|[13-9]\\d{6}|2(?:[0-24-9]\\d{5}|3\\d(?:\\d{4})?))|9(?:[0-46-9]\\d{6}|5\\d{3}(?:\\d(?:\\d{2})?)?))|(?:3(?:1[02-9]|35|49|5\\d|7[02-68]|9[1-68])|4(?:1[24-9]|2[179]|3[46-9]|5[2-9]|6[47-9]|7\\d|8[23])|5(?:3[03-9]|4[36]|5[02-9]|6[1-46]|7[028]|80|9[2-46-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[17]\\d|2[248]|3[04-9]|4[3-6]|5[0-3689]|6[2368]|9[02-9])|8(?:1[236-8]|2[5-7]|3\\d|5[2-9]|7[02-9]|8[36-8]|9[1-7])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))(?:[02-8]\\d{6}|1(?:0(?:0\\d\\d(?:\\d{2})?|[1-9]\\d{4})|[13-9]\\d{5}|2(?:[0-24-9]\\d{4}|3\\d(?:\\d{3})?))|9(?:[0-46-9]\\d{5}|5\\d{3,5}))",
      ,
      ,
      ,
      "1012345678",
      ,
      ,
      [7, 8, 9, 10, 11],
      [5, 6]
    ], [, , "1(?:610\\d|740[0-5])\\d{6}|1(?:[38]\\d|4[57]|[59][0-35-9]|6[25-7]|7[0-35-8])\\d{8}", , , , "13123456789", , , [11]], [, , "(?:(?:10|21)8|8)00\\d{7}", , , , "8001234567", , , [10, 12]], [, , "16[08]\\d{5}", , , , "16812345", , , [8]], [
      ,
      ,
      "10(?:10\\d{4}|96\\d{3,4})|400\\d{7}|950\\d{7,8}|(?:2[0-57-9]|3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))96\\d{3,4}",
      ,
      ,
      ,
      "4001234567",
      ,
      ,
      [7, 8, 9, 10, 11],
      [5, 6]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CN", 86, "00|1(?:[12]\\d|79)\\d\\d00", "0", , , "(1(?:[12]\\d|79)\\d\\d)|0", , "00", , [
      [, "(\\d{5,6})", "$1", ["1(?:00|2[13])|9[56]", "1(?:00|2(?:1|39))|9[56]", "1(?:00|2(?:1|395))|9[56]"]],
      [, "(\\d{5,6})", "$1", ["1(?:0|23)|781|[1-9]12", "1(?:0|23)|7812|[1-9]123", "1(?:0|23(?:[0-8]|9[0-46-9]))|78123|[1-9]123"]],
      [
        ,
        "(\\d{2})(\\d{5,6})",
        "$1 $2",
        [
          "(?:10|2[0-57-9])[19]|3(?:[157]|35|49|9[1-68])|4(?:1[124-9]|2[179]|6[47-9]|7|8[23])|5(?:[1357]|2[37]|4[36]|6[1-46]|80)|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:07|1[236-8]|2[5-7]|[37]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3|4[13]|5[1-5]|7[0-79]|9[0-35-9])|(?:4[35]|59|85)[1-9]",
          "(?:10|2[0-57-9])(?:1[02]|9[56])|8078|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))1",
          "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|80781|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))12",
          "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|807812|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))123",
          "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:078|1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))123"
        ],
        "0$1",
        "$CC $1"
      ],
      [, "(\\d{3})(\\d{4})", "$1 $2", [
        "[1-9]",
        "1[1-9]|26|[3-9]|(?:10|2[0-57-9])(?:[0-8]|9[0-47-9])",
        "1(?:0(?:[02-8]|1(?:[013-9]|2[0-24-9])|9[0-47-9])|[1-9])|2(?:[0-57-9](?:[02-8]|1(?:0[1-9]|[13-9]|2[0-24-9])|9[0-47-9])|6)|[3-9]",
        "1(?:0(?:[02-8]|1(?:[013-9]|2[0-24-9])|9[0-47-9])|[1-9])|2(?:[0-57-9](?:[02-8]|1(?:0[1-9]|[13-9]|2[0-24-9])|9[0-47-9])|6)|3(?:[0268]|3[0-46-9]|4[0-8]|9[079])|4(?:[049]|1[03]|2[02-68]|[35]0|6[0-356]|8[014-9])|5(?:0|2[0-24-689]|4[0-2457-9]|6[057-9]|8[1-9]|90)|6(?:[0-24578]|3[06-9]|6[14-79]|9[03-9])|7(?:0[02-9]|2[0135-79]|3[23]|4[0-27-9]|6[1457]|8)|8(?:[046]|1[01459]|2[0-489]|50|8[0-2459]|9[09])|9(?:0[0457]|1[08]|[268]|4[024-9]|5[06-9]|78|94)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))(?:[02-9]|1(?:[013-9]|2[0-24-9]))",
        "1(?:0(?:[02-8]|1(?:[013-9]|2[0-24-9])|9[0-47-9])|[1-9])|2(?:[0-57-9](?:[02-8]|1(?:0[1-9]|[13-9]|2[0-24-9])|9[0-47-9])|6)|3(?:[0268]|3[0-46-9]|4[0-8]|9[079])|4(?:[049]|1[03]|2[02-68]|[35]0|6[0-356]|8[014-9])|5(?:0|2[0-24-689]|4[0-2457-9]|6[057-9]|8[1-9]|90)|6(?:[0-24578]|3[06-9]|6[14-79]|9[03-9])|7(?:0[02-9]|2[0135-79]|3[23]|4[0-27-9]|6[1457]|8)|8(?:0(?:[0-689]|7[0-79])|1[01459]|2[0-489]|[46]|50|8[0-2459]|9[09])|9(?:0[0457]|1[08]|[268]|4[024-9]|5[06-9]|78|94)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:078|1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))(?:[02-9]|1(?:[013-9]|2[0-24-9]))"
      ]],
      [, "(\\d{4})(\\d{4})", "$1 $2", ["16[08]"]],
      [
        ,
        "(\\d{3})(\\d{5,6})",
        "$1 $2",
        [
          "3(?:[157]|35|49|9[1-68])|4(?:[17]|2[179]|6[47-9]|8[23])|5(?:[1357]|2[37]|4[36]|6[1-46]|80)|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]|4[13]|5[1-5])|(?:4[35]|59|85)[1-9]",
          "(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))[19]",
          "85[23](?:10|95)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:10|9[56])",
          "85[23](?:100|95)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:100|9[56])"
        ],
        "0$1",
        "$CC $1"
      ],
      [, "(\\d{4})(\\d{4})", "$1 $2", [
        "[1-9]",
        "1(?:0(?:[02-8]|1[1-9]|9[0-47-9])|[1-9])|2(?:[0-57-9](?:[0-8]|9[0-47-9])|6)|[3-9]",
        "1(?:0(?:[02-8]|1[1-9]|9[0-47-9])|[1-9])|26|3(?:[0268]|4[0-8]|9[079])|4(?:[049]|2[02-68]|[35]0|6[0-356]|8[014-9])|5(?:0|2[0-24-689]|4[0-2457-9]|6[057-9]|8[1-9]|90)|6(?:[0-24578]|3[06-9]|6[14-79]|9[03-9])|7(?:0[02-9]|2[0135-79]|3[23]|4[0-27-9]|6[1457]|8)|8(?:[046]|1[01459]|2[0-489]|5(?:0|[23][0-8])|8[0-2459]|9[09])|9(?:0[0457]|1[08]|[268]|4[024-9]|5[06-9])|(?:33|85[23]9)[0-46-9]|(?:2[0-57-9]|3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:[0-8]|9[0-47-9])",
        "1(?:0[02-8]|[1-9])|2(?:[0-57-9][0-8]|6)|3(?:[0268]|3[0-46-9]|4[0-8]|9[079])|4(?:[049]|2[02-68]|[35]0|6[0-356]|8[014-9])|5(?:0|2[0-24-689]|4[0-2457-9]|6[057-9]|90)|6(?:[0-24578]|3[06-9]|6[14-79]|9[03-9])|7(?:0[02-9]|2[0135-79]|3[23]|4[0-27-9]|6[1457]|8)|8(?:[046]|1[01459]|2[0-489]|5(?:0|[23](?:[02-8]|1[1-9]|9[0-46-9]))|8[0-2459]|9[09])|9(?:0[0457]|1[08]|[268]|4[024-9]|5[06-9])|(?:10|2[0-57-9])9[0-47-9]|(?:101|58|85[23]10)[1-9]|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:[02-8]|1(?:0[1-9]|[1-9])|9[0-47-9])"
      ]],
      [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["(?:4|80)0"]],
      [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["10|2(?:[02-57-9]|1[1-9])", "10|2(?:[02-57-9]|1[1-9])", "10[0-79]|2(?:[02-57-9]|1[1-79])|(?:10|21)8(?:0[1-9]|[1-9])"], "0$1", "$CC $1", 1],
      [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["3(?:[3-59]|7[02-68])|4(?:[26-8]|3[3-9]|5[2-9])|5(?:3[03-9]|[468]|7[028]|9[2-46-9])|6|7(?:[0-247]|3[04-9]|5[0-4689]|6[2368])|8(?:[1-358]|9[1-7])|9(?:[013479]|5[1-5])|(?:[34]1|55|79|87)[02-9]"], "0$1", "$CC $1", 1],
      [
        ,
        "(\\d{3})(\\d{7,8})",
        "$1 $2",
        ["9"]
      ],
      [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["80"], "0$1", "$CC $1", 1],
      [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["[3-578]"], "0$1", "$CC $1", 1],
      [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["1[3-9]"], , "$CC $1"],
      [, "(\\d{2})(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["[12]"], "0$1", , 1]
    ], [[
      ,
      "(\\d{2})(\\d{5,6})",
      "$1 $2",
      [
        "(?:10|2[0-57-9])[19]|3(?:[157]|35|49|9[1-68])|4(?:1[124-9]|2[179]|6[47-9]|7|8[23])|5(?:[1357]|2[37]|4[36]|6[1-46]|80)|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:07|1[236-8]|2[5-7]|[37]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3|4[13]|5[1-5]|7[0-79]|9[0-35-9])|(?:4[35]|59|85)[1-9]",
        "(?:10|2[0-57-9])(?:1[02]|9[56])|8078|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))1",
        "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|80781|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))12",
        "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|807812|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))123",
        "10(?:1(?:0|23)|9[56])|2[0-57-9](?:1(?:00|23)|9[56])|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:1[124-9]|2[179]|[35][1-9]|6[47-9]|7\\d|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:078|1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|3\\d|4[13]|5[1-5]|7[0-79]|9[0-35-9]))123"
      ],
      "0$1",
      "$CC $1"
    ], [
      ,
      "(\\d{3})(\\d{5,6})",
      "$1 $2",
      [
        "3(?:[157]|35|49|9[1-68])|4(?:[17]|2[179]|6[47-9]|8[23])|5(?:[1357]|2[37]|4[36]|6[1-46]|80)|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]|4[13]|5[1-5])|(?:4[35]|59|85)[1-9]",
        "(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[1-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))[19]",
        "85[23](?:10|95)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:10|9[56])",
        "85[23](?:100|95)|(?:3(?:[157]\\d|35|49|9[1-68])|4(?:[17]\\d|2[179]|[35][1-9]|6[47-9]|8[23])|5(?:[1357]\\d|2[37]|4[36]|6[1-46]|80|9[1-9])|6(?:3[1-5]|6[0238]|9[12])|7(?:01|[1579]\\d|2[248]|3[014-9]|4[3-6]|6[023689])|8(?:1[236-8]|2[5-7]|[37]\\d|5[14-9]|8[36-8]|9[1-8])|9(?:0[1-3689]|1[1-79]|[379]\\d|4[13]|5[1-5]))(?:100|9[56])"
      ],
      "0$1",
      "$CC $1"
    ], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["(?:4|80)0"]], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["10|2(?:[02-57-9]|1[1-9])", "10|2(?:[02-57-9]|1[1-9])", "10[0-79]|2(?:[02-57-9]|1[1-79])|(?:10|21)8(?:0[1-9]|[1-9])"], "0$1", "$CC $1", 1], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["3(?:[3-59]|7[02-68])|4(?:[26-8]|3[3-9]|5[2-9])|5(?:3[03-9]|[468]|7[028]|9[2-46-9])|6|7(?:[0-247]|3[04-9]|5[0-4689]|6[2368])|8(?:[1-358]|9[1-7])|9(?:[013479]|5[1-5])|(?:[34]1|55|79|87)[02-9]"], "0$1", "$CC $1", 1], [
      ,
      "(\\d{3})(\\d{7,8})",
      "$1 $2",
      ["9"]
    ], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["80"], "0$1", "$CC $1", 1], [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["[3-578]"], "0$1", "$CC $1", 1], [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["1[3-9]"], , "$CC $1"], [, "(\\d{2})(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["[12]"], "0$1", , 1]], [, , , , , , , , , [-1]], , , [, , "(?:(?:10|21)8|[48])00\\d{7}|950\\d{7,8}", , , , , , , [10, 11, 12]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CO: [, [, , "(?:46|60\\d\\d)\\d{6}|(?:1\\d|[39])\\d{9}", , , , , , , [8, 10, 11], [4, 7]], [
      ,
      ,
      "601055(?:[0-4]\\d|50)\\d\\d|6010(?:[0-4]\\d|5[0-4])\\d{4}|(?:46|60(?:[18][1-9]|[24-7][2-9]))\\d{6}",
      ,
      ,
      ,
      "6012345678",
      ,
      ,
      [8, 10],
      [4, 7]
    ], [, , "333301[0-5]\\d{3}|3333(?:00|2[5-9]|[3-9]\\d)\\d{4}|(?:3(?:(?:0[0-5]|1\\d|5[01]|70)\\d|2(?:[0-3]\\d|4[1-9])|3(?:00|3[0-24-9]))|9(?:101|408))\\d{6}", , , , "3211234567", , , [10]], [, , "1800\\d{7}", , , , "18001234567", , , [11]], [, , "(?:19(?:0[01]|4[78])|901)\\d{7}", , , , "19001234567", , , [10, 11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CO", 57, "00(?:4(?:[14]4|56)|[579])", "0", , , "0([3579]|4(?:[14]4|56))?", , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["46"]], [
      ,
      "(\\d{3})(\\d{7})",
      "$1 $2",
      ["6|90"],
      "($1)",
      "0$CC $1"
    ], [, "(\\d{3})(\\d{7})", "$1 $2", ["3[0-357]|9[14]"], , "0$CC $1"], [, "(\\d)(\\d{3})(\\d{7})", "$1-$2-$3", ["1"], "0$1"]], [[, "(\\d{4})(\\d{4})", "$1 $2", ["46"]], [, "(\\d{3})(\\d{7})", "$1 $2", ["6|90"], "($1)", "0$CC $1"], [, "(\\d{3})(\\d{7})", "$1 $2", ["3[0-357]|9[14]"], , "0$CC $1"], [, "(\\d)(\\d{3})(\\d{7})", "$1 $2 $3", ["1"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CR: [, [, , "(?:8\\d|90)\\d{8}|(?:[24-8]\\d{3}|3005)\\d{4}", , , , , , , [8, 10]], [
      ,
      ,
      "210[7-9]\\d{4}|2(?:[024-7]\\d|1[1-9])\\d{5}",
      ,
      ,
      ,
      "22123456",
      ,
      ,
      [8]
    ], [, , "(?:3005\\d|6500[01])\\d{3}|(?:5[07]|6[0-4]|7[0-3]|8[3-9])\\d{6}", , , , "83123456", , , [8]], [, , "800\\d{7}", , , , "8001234567", , , [10]], [, , "90[059]\\d{7}", , , , "9001234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:210[0-6]|4\\d{3}|5100)\\d{4}", , , , "40001234", , , [8]], "CR", 506, "00", , , , "(19(?:0[0-2468]|1[09]|20|66|77|99))", , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[2-7]|8[3-9]"], , "$CC $1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["[89]"], , "$CC $1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    CU: [, [, , "(?:[2-7]|8\\d\\d)\\d{7}|[2-47]\\d{6}|[34]\\d{5}", , , , , , , [6, 7, 8, 10], [4, 5]], [, , "(?:3[23]|4[89])\\d{4,6}|(?:31|4[36]|8(?:0[25]|78)\\d)\\d{6}|(?:2[1-4]|4[1257]|7\\d)\\d{5,6}", , , , "71234567", , , , [4, 5]], [, , "(?:5\\d|6[2-4])\\d{6}", , , , "51234567", , , [8]], [, , "800\\d{7}", , , , "8001234567", , , [10]], [, , , , , , , , , [-1]], [, , "807\\d{7}", , , , "8071234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CU", 53, "119", "0", , , "0", , , , [[, "(\\d{2})(\\d{4,6})", "$1 $2", ["2[1-4]|[34]"], "(0$1)"], [
      ,
      "(\\d)(\\d{6,7})",
      "$1 $2",
      ["7"],
      "(0$1)"
    ], [, "(\\d)(\\d{7})", "$1 $2", ["[56]"], "0$1"], [, "(\\d{3})(\\d{7})", "$1 $2", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CV: [, [, , "(?:[2-59]\\d\\d|800)\\d{4}", , , , , , , [7]], [, , "2(?:2[1-7]|3[0-8]|4[12]|5[1256]|6\\d|7[1-3]|8[1-5])\\d{4}", , , , "2211234"], [, , "(?:36|5[1-389]|9\\d)\\d{5}", , , , "9911234"], [, , "800\\d{4}", , , , "8001234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:3[3-5]|4[356])\\d{5}", , , , "3401234"], "CV", 238, "0", , , , , , , , [[
      ,
      "(\\d{3})(\\d{2})(\\d{2})",
      "$1 $2 $3",
      ["[2-589]"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CW: [, [, , "(?:[34]1|60|(?:7|9\\d)\\d)\\d{5}", , , , , , , [7, 8]], [, , "9(?:4(?:3[0-5]|4[14]|6\\d)|50\\d|7(?:2[014]|3[02-9]|4[4-9]|6[357]|77|8[7-9])|8(?:3[39]|[46]\\d|7[01]|8[57-9]))\\d{4}", , , , "94351234"], [, , "953[01]\\d{4}|9(?:5[12467]|6[5-9])\\d{5}", , , , "95181234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "60[0-2]\\d{4}", , , , "6001234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "CW", 599, "00", , , , , , , , [[
      ,
      "(\\d{3})(\\d{4})",
      "$1 $2",
      ["[3467]"]
    ], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["9[4-8]"]]], , [, , "955\\d{5}", , , , "95581234", , , [8]], 1, "[69]", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CX: [, [, , "1(?:[0-79]\\d{8}(?:\\d{2})?|8[0-24-9]\\d{7})|[148]\\d{8}|1\\d{5,7}", , , , , , , [6, 7, 8, 9, 10, 12]], [, , "8(?:51(?:0(?:01|30|59|88)|1(?:17|46|75)|2(?:22|35))|91(?:00[6-9]|1(?:[28]1|49|78)|2(?:09|63)|3(?:12|26|75)|4(?:56|97)|64\\d|7(?:0[01]|1[0-2])|958))\\d{3}", , , , "891641234", , , [9], [8]], [
      ,
      ,
      "4(?:79[01]|83[0-36-9]|95[0-3])\\d{5}|4(?:[0-36]\\d|4[047-9]|[58][0-24-9]|7[02-8]|9[0-47-9])\\d{6}",
      ,
      ,
      ,
      "412345678",
      ,
      ,
      [9]
    ], [, , "180(?:0\\d{3}|2)\\d{3}", , , , "1800123456", , , [7, 10]], [, , "190[0-26]\\d{6}", , , , "1900123456", , , [10]], [, , "13(?:00\\d{6}(?:\\d{2})?|45[0-4]\\d{3})|13\\d{4}", , , , "1300123456", , , [6, 8, 10, 12]], [, , , , , , , , , [-1]], [, , "14(?:5(?:1[0458]|[23][458])|71\\d)\\d{4}", , , , "147101234", , , [9]], "CX", 61, "001[14-689]|14(?:1[14]|34|4[17]|[56]6|7[47]|88)0011", "0", , , "([59]\\d{7})$|0", "8$1", "0011", , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    CY: [, [
      ,
      ,
      "(?:[279]\\d|[58]0)\\d{6}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8]
    ], [, , "2[2-6]\\d{6}", , , , "22345678"], [, , "9(?:10|[4-79]\\d)\\d{5}", , , , "96123456"], [, , "800\\d{5}", , , , "80001234"], [, , "90[09]\\d{5}", , , , "90012345"], [, , "80[1-9]\\d{5}", , , , "80112345"], [, , "700\\d{5}", , , , "70012345"], [, , , , , , , , , [-1]], "CY", 357, "00", , , , , , , , [[, "(\\d{2})(\\d{6})", "$1 $2", ["[257-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "(?:50|77)\\d{6}", , , , "77123456"], , , [, , , , , , , , , [-1]]],
    CZ: [, [, , "(?:[2-578]\\d|60)\\d{7}|9\\d{8,11}", , , , , , , [9, 10, 11, 12]], [
      ,
      ,
      "(?:2\\d|3[1257-9]|4[16-9]|5[13-9])\\d{7}",
      ,
      ,
      ,
      "212345678",
      ,
      ,
      [9]
    ], [, , "7060\\d{5}|(?:60[1-8]|7(?:0[2-5]|19|[2379]\\d))\\d{6}", , , , "601123456", , , [9]], [, , "800\\d{6}", , , , "800123456", , , [9]], [, , "9(?:0[05689]|76)\\d{6}", , , , "900123456", , , [9]], [, , "8[134]\\d{7}", , , , "811234567", , , [9]], [, , "70[01]\\d{6}", , , , "700123456", , , [9]], [, , "9[17]0\\d{6}", , , , "910123456", , , [9]], "CZ", 420, "00", , , , , , , , [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-8]|9[015-7]"]], [, "(\\d{2})(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3 $4", ["96"]], [, "(\\d{2})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["9"]], [
      ,
      "(\\d{3})(\\d{3})(\\d{3})(\\d{3})",
      "$1 $2 $3 $4",
      ["9"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "9(?:5\\d|7[2-4])\\d{6}", , , , "972123456", , , [9]], , , [, , "9(?:3\\d{9}|6\\d{7,10})", , , , "93123456789"]],
    DE: [, [, , "[2579]\\d{5,14}|49(?:[34]0|69|8\\d)\\d\\d?|49(?:37|49|60|7[089]|9\\d)\\d{1,3}|49(?:2[024-9]|3[2-689]|7[1-7])\\d{1,8}|(?:1|[368]\\d|4[0-8])\\d{3,13}|49(?:[015]\\d|2[13]|31|[46][1-8])\\d{1,9}", , , , , , , [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [2, 3]], [
      ,
      ,
      "32\\d{9,11}|49[1-6]\\d{10}|322\\d{6}|49[0-7]\\d{3,9}|(?:[34]0|[68]9)\\d{3,13}|(?:2(?:0[1-689]|[1-3569]\\d|4[0-8]|7[1-7]|8[0-7])|3(?:[3569]\\d|4[0-79]|7[1-7]|8[1-8])|4(?:1[02-9]|[2-48]\\d|5[0-6]|6[0-8]|7[0-79])|5(?:0[2-8]|[124-6]\\d|[38][0-8]|[79][0-7])|6(?:0[02-9]|[1-358]\\d|[47][0-8]|6[1-9])|7(?:0[2-8]|1[1-9]|[27][0-7]|3\\d|[4-6][0-8]|8[0-5]|9[013-7])|8(?:0[2-9]|1[0-79]|2\\d|3[0-46-9]|4[0-6]|5[013-9]|6[1-8]|7[0-8]|8[0-24-6])|9(?:0[6-9]|[1-4]\\d|[589][0-7]|6[0-8]|7[0-467]))\\d{3,12}",
      ,
      ,
      ,
      "30123456",
      ,
      ,
      [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
      [2, 3, 4]
    ], [, , "1(?:6[023]|7\\d)\\d{7,8}|15(?:[0-25-9]\\d\\d|3(?:10|33))\\d{6}", , , , "15123456789", , , [10, 11]], [, , "800\\d{7,12}", , , , "8001234567890", , , [10, 11, 12, 13, 14, 15]], [, , "(?:137[7-9]|900(?:[135]|9\\d))\\d{6}", , , , "9001234567", , , [10, 11]], [, , "180\\d{5,11}|13(?:7[1-6]\\d\\d|8)\\d{4}", , , , "18012345", , , [7, 8, 9, 10, 11, 12, 13, 14]], [, , "700\\d{8}", , , , "70012345678", , , [11]], [, , , , , , , , , [-1]], "DE", 49, "00", "0", , , "0", , , , [
      [, "(\\d{2})(\\d{3,13})", "$1 $2", ["3[02]|40|[68]9"], "0$1"],
      [, "(\\d{6})", "$1", ["227", "2277"]],
      [, "(\\d{3})(\\d{3,12})", "$1 $2", ["2(?:0[1-389]|1[124]|2[18]|3[14])|3(?:[35-9][15]|4[015])|906|(?:2[4-9]|4[2-9]|[579][1-9]|[68][1-8])1", "2(?:0[1-389]|12[0-8])|3(?:[35-9][15]|4[015])|906|2(?:[13][14]|2[18])|(?:2[4-9]|4[2-9]|[579][1-9]|[68][1-8])1"], "0$1"],
      [
        ,
        "(\\d{4})(\\d{2,11})",
        "$1 $2",
        ["[24-6]|3(?:[3569][02-46-9]|4[2-4679]|7[2-467]|8[2-46-8])|70[2-8]|8(?:0[2-9]|[1-8])|90[7-9]|[79][1-9]", "[24-6]|3(?:3(?:0[1-467]|2[127-9]|3[124578]|7[1257-9]|8[1256]|9[145])|4(?:2[135]|4[13578]|9[1346])|5(?:0[14]|2[1-3589]|6[1-4]|7[13468]|8[13568])|6(?:2[1-489]|3[124-6]|6[13]|7[12579]|8[1-356]|9[135])|7(?:2[1-7]|4[145]|6[1-5]|7[1-4])|8(?:21|3[1468]|6|7[1467]|8[136])|9(?:0[12479]|2[1358]|4[134679]|6[1-9]|7[136]|8[147]|9[1468]))|70[2-8]|8(?:0[2-9]|[1-8])|90[7-9]|[79][1-9]|3[68]4[1347]|3(?:47|60)[1356]|3(?:3[46]|46|5[49])[1246]|3[4579]3[1357]"],
        "0$1"
      ],
      [, "(\\d{3})(\\d{4})", "$1 $2", ["138"], "0$1"],
      [, "(\\d{5})(\\d{2,10})", "$1 $2", ["3"], "0$1"],
      [, "(\\d{3})(\\d{5,11})", "$1 $2", ["181"], "0$1"],
      [, "(\\d{3})(\\d)(\\d{4,10})", "$1 $2 $3", ["1(?:3|80)|9"], "0$1"],
      [, "(\\d{3})(\\d{7,8})", "$1 $2", ["1[67]"], "0$1"],
      [, "(\\d{3})(\\d{7,12})", "$1 $2", ["8"], "0$1"],
      [, "(\\d{5})(\\d{6})", "$1 $2", ["185", "1850", "18500"], "0$1"],
      [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["7"], "0$1"],
      [, "(\\d{4})(\\d{7})", "$1 $2", ["18[68]"], "0$1"],
      [, "(\\d{4})(\\d{7})", "$1 $2", ["15[1279]"], "0$1"],
      [, "(\\d{5})(\\d{6})", "$1 $2", ["15[03568]", "15(?:[0568]|3[13])"], "0$1"],
      [, "(\\d{3})(\\d{8})", "$1 $2", ["18"], "0$1"],
      [, "(\\d{3})(\\d{2})(\\d{7,8})", "$1 $2 $3", ["1(?:6[023]|7)"], "0$1"],
      [, "(\\d{4})(\\d{2})(\\d{7})", "$1 $2 $3", ["15[279]"], "0$1"],
      [, "(\\d{3})(\\d{2})(\\d{8})", "$1 $2 $3", ["15"], "0$1"]
    ], [
      [, "(\\d{2})(\\d{3,13})", "$1 $2", ["3[02]|40|[68]9"], "0$1"],
      [
        ,
        "(\\d{3})(\\d{3,12})",
        "$1 $2",
        ["2(?:0[1-389]|1[124]|2[18]|3[14])|3(?:[35-9][15]|4[015])|906|(?:2[4-9]|4[2-9]|[579][1-9]|[68][1-8])1", "2(?:0[1-389]|12[0-8])|3(?:[35-9][15]|4[015])|906|2(?:[13][14]|2[18])|(?:2[4-9]|4[2-9]|[579][1-9]|[68][1-8])1"],
        "0$1"
      ],
      [
        ,
        "(\\d{4})(\\d{2,11})",
        "$1 $2",
        ["[24-6]|3(?:[3569][02-46-9]|4[2-4679]|7[2-467]|8[2-46-8])|70[2-8]|8(?:0[2-9]|[1-8])|90[7-9]|[79][1-9]", "[24-6]|3(?:3(?:0[1-467]|2[127-9]|3[124578]|7[1257-9]|8[1256]|9[145])|4(?:2[135]|4[13578]|9[1346])|5(?:0[14]|2[1-3589]|6[1-4]|7[13468]|8[13568])|6(?:2[1-489]|3[124-6]|6[13]|7[12579]|8[1-356]|9[135])|7(?:2[1-7]|4[145]|6[1-5]|7[1-4])|8(?:21|3[1468]|6|7[1467]|8[136])|9(?:0[12479]|2[1358]|4[134679]|6[1-9]|7[136]|8[147]|9[1468]))|70[2-8]|8(?:0[2-9]|[1-8])|90[7-9]|[79][1-9]|3[68]4[1347]|3(?:47|60)[1356]|3(?:3[46]|46|5[49])[1246]|3[4579]3[1357]"],
        "0$1"
      ],
      [, "(\\d{3})(\\d{4})", "$1 $2", ["138"], "0$1"],
      [, "(\\d{5})(\\d{2,10})", "$1 $2", ["3"], "0$1"],
      [, "(\\d{3})(\\d{5,11})", "$1 $2", ["181"], "0$1"],
      [, "(\\d{3})(\\d)(\\d{4,10})", "$1 $2 $3", ["1(?:3|80)|9"], "0$1"],
      [, "(\\d{3})(\\d{7,8})", "$1 $2", ["1[67]"], "0$1"],
      [, "(\\d{3})(\\d{7,12})", "$1 $2", ["8"], "0$1"],
      [, "(\\d{5})(\\d{6})", "$1 $2", ["185", "1850", "18500"], "0$1"],
      [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["7"], "0$1"],
      [, "(\\d{4})(\\d{7})", "$1 $2", ["18[68]"], "0$1"],
      [, "(\\d{4})(\\d{7})", "$1 $2", ["15[1279]"], "0$1"],
      [, "(\\d{5})(\\d{6})", "$1 $2", ["15[03568]", "15(?:[0568]|3[13])"], "0$1"],
      [, "(\\d{3})(\\d{8})", "$1 $2", ["18"], "0$1"],
      [, "(\\d{3})(\\d{2})(\\d{7,8})", "$1 $2 $3", ["1(?:6[023]|7)"], "0$1"],
      [, "(\\d{4})(\\d{2})(\\d{7})", "$1 $2 $3", ["15[279]"], "0$1"],
      [, "(\\d{3})(\\d{2})(\\d{8})", "$1 $2 $3", ["15"], "0$1"]
    ], [, , "16(?:4\\d{1,10}|[89]\\d{1,11})", , , , "16412345", , , [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]], , , [, , , , , , , , , [-1]], [, , "18(?:1\\d{5,11}|[2-9]\\d{8})", , , , "18500123456", , , [8, 9, 10, 11, 12, 13, 14]], , , [
      ,
      ,
      "1(?:6(?:013|255|399)|7(?:(?:[015]1|[69]3)3|[2-4]55|[78]99))\\d{7,8}|15(?:(?:[03-68]00|113)\\d|2\\d55|7\\d99|9\\d33)\\d{7}",
      ,
      ,
      ,
      "177991234567",
      ,
      ,
      [12, 13]
    ]],
    DJ: [, [, , "(?:2\\d|77)\\d{6}", , , , , , , [8]], [, , "2(?:1[2-5]|7[45])\\d{5}", , , , "21360003"], [, , "77\\d{6}", , , , "77831001"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "DJ", 253, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[27]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    DK: [, [, , "[2-9]\\d{7}", , , , , , , [8]], [
      ,
      ,
      "(?:2(?:[0-59][1-9]|[6-8]\\d)|3(?:[0-3][1-9]|4[13]|5[1-58]|6[1347-9]|7\\d|8[1-8]|9[1-79])|4(?:[0-25][1-9]|[34][2-9]|6[13-579]|7[13579]|8[1-47]|9[127])|5(?:[0-36][1-9]|4[146-9]|5[3-57-9]|7[568]|8[1-358]|9[1-69])|6(?:[0135][1-9]|2[1-68]|4[2-8]|6[1689]|[78]\\d|9[15689])|7(?:[0-69][1-9]|7[3-9]|8[147])|8(?:[16-9][1-9]|2[1-58])|9(?:[1-47-9][1-9]|6\\d))\\d{5}",
      ,
      ,
      ,
      "32123456"
    ], [, , "(?:2[6-8]|37|6[78]|96)\\d{6}|(?:2[0-59]|3[0-689]|[457]\\d|6[0-69]|8[126-9]|9[1-47-9])[1-9]\\d{5}", , , , "34412345"], [, , "80\\d{6}", , , , "80123456"], [, , "90\\d{6}", , , , "90123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "DK", 45, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    DM: [
      ,
      [, , "(?:[58]\\d\\d|767|900)\\d{7}", , , , , , , [10], [7]],
      [
        ,
        ,
        "767(?:2(?:55|66)|4(?:2[01]|4[0-25-9])|50[0-4])\\d{4}",
        ,
        ,
        ,
        "7674201234",
        ,
        ,
        ,
        [7]
      ],
      [, , "767(?:2(?:[2-4689]5|7[5-7])|31[5-7]|61[1-8]|70[1-6])\\d{4}", , , , "7672251234", , , , [7]],
      [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"],
      [, , "900[2-9]\\d{6}", , , , "9002123456"],
      [, , , , , , , , , [-1]],
      [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"],
      [, , , , , , , , , [-1]],
      "DM",
      1,
      "011",
      "1",
      ,
      ,
      "([2-7]\\d{6})$|1",
      "767$1",
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      "767",
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    DO: [
      ,
      [, , "(?:[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]],
      [
        ,
        ,
        "8(?:[04]9[2-9]\\d\\d|29(?:2(?:[0-59]\\d|6[04-9]|7[0-27]|8[0237-9])|3(?:[0-35-9]\\d|4[7-9])|[45]\\d\\d|6(?:[0-27-9]\\d|[3-5][1-9]|6[0135-8])|7(?:0[013-9]|[1-37]\\d|4[1-35689]|5[1-4689]|6[1-57-9]|8[1-79]|9[1-8])|8(?:0[146-9]|1[0-48]|[248]\\d|3[1-79]|5[01589]|6[013-68]|7[124-8]|9[0-8])|9(?:[0-24]\\d|3[02-46-9]|5[0-79]|60|7[0169]|8[57-9]|9[02-9])))\\d{4}",
        ,
        ,
        ,
        "8092345678",
        ,
        ,
        ,
        [7]
      ],
      [, , "8[024]9[2-9]\\d{6}", , , , "8092345678", , , , [7]],
      [, , "800(?:14|[2-9]\\d)\\d{5}|8[024]9[01]\\d{6}|8(?:33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"],
      [, , "900[2-9]\\d{6}", , , , "9002123456"],
      [, , , , , , , , , [-1]],
      [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"],
      [, , , , , , , , , [-1]],
      "DO",
      1,
      "011",
      "1",
      ,
      ,
      "1",
      ,
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      "8001|8[024]9",
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    DZ: [
      ,
      [, , "(?:[1-4]|[5-79]\\d|80)\\d{7}", , , , , , , [8, 9]],
      [, , "9619\\d{5}|(?:[1-3]\\d|4[013-689])\\d{6}", , , , "12345678"],
      [, , "5(?:4[0-29]|6[0-4])\\d{6}|(?:55|6\\d|7[7-9])\\d{7}", , , , "551234567", , , [9]],
      [, , "800\\d{6}", , , , "800123456", , , [9]],
      [, , "80[3-689]1\\d{5}", , , , "808123456", , , [9]],
      [, , "80[12]1\\d{5}", , , , "801123456", , , [9]],
      [, , , , , , , , , [-1]],
      [, , "98[23]\\d{6}", , , , "983123456", , , [9]],
      "DZ",
      213,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[1-4]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["9"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-8]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    EC: [, [, , "1\\d{9,10}|(?:[2-7]|9\\d)\\d{7}", , , , , , , [8, 9, 10, 11], [7]], [, , "[2-7][2-7]\\d{6}", , , , "22123456", , , [8], [7]], [, , "964[0-2]\\d{5}|9(?:39|[57][89]|6[0-36-9]|[89]\\d)\\d{6}", , , , "991234567", , , [9]], [
      ,
      ,
      "1800\\d{7}|1[78]00\\d{6}",
      ,
      ,
      ,
      "18001234567",
      ,
      ,
      [10, 11]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "[2-7]890\\d{4}", , , , "28901234", , , [8]], "EC", 593, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{4})", "$1-$2", ["[2-7]"]], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2-$3", ["[2-7]"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["9"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["1"]]], [[, "(\\d)(\\d{3})(\\d{4})", "$1-$2-$3", ["[2-7]"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["9"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["1"]]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    EE: [, [, , "8\\d{9}|[4578]\\d{7}|(?:[3-8]\\d|90)\\d{5}", , , , , , , [7, 8, 10]], [, , "(?:3[23589]|4[3-8]|6\\d|7[1-9]|88)\\d{5}", , , , "3212345", , , [7]], [
      ,
      ,
      "(?:5\\d{5}|8(?:1(?:0(?:0(?:00|[178]\\d)|[3-9]\\d\\d)|(?:1(?:0[2-6]|1\\d)|[2-79]\\d\\d)\\d)|2(?:0(?:0(?:00|4\\d)|(?:19|[2-7]\\d)\\d)|(?:(?:[124-69]\\d|3[5-9])\\d|7(?:[0-79]\\d|8[013-9])|8(?:[2-6]\\d|7[01]))\\d)|[349]\\d{4}))\\d\\d|5(?:(?:[02]\\d|5[0-478])\\d|1(?:[0-8]\\d|95)|6(?:4[0-4]|5[1-589]))\\d{3}",
      ,
      ,
      ,
      "51234567",
      ,
      ,
      [7, 8]
    ], [, , "800(?:(?:0\\d\\d|1)\\d|[2-9])\\d{3}", , , , "80012345"], [, , "(?:40\\d\\d|900)\\d{4}", , , , "9001234", , , [7, 8]], [, , , , , , , , , [-1]], [, , "70[0-2]\\d{5}", , , , "70012345", , , [8]], [, , , , , , , , , [-1]], "EE", 372, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[369]|4[3-8]|5(?:[0-2]|5[0-478]|6[45])|7[1-9]|88", "[369]|4[3-8]|5(?:[02]|1(?:[0-8]|95)|5[0-478]|6(?:4[0-4]|5[1-589]))|7[1-9]|88"]], [, "(\\d{4})(\\d{3,4})", "$1 $2", ["[45]|8(?:00|[1-49])", "[45]|8(?:00[1-9]|[1-49])"]], [
      ,
      "(\\d{2})(\\d{2})(\\d{4})",
      "$1 $2 $3",
      ["7"]
    ], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["8"]]], , [, , , , , , , , , [-1]], , , [, , "800[2-9]\\d{3}", , , , , , , [7]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    EG: [
      ,
      [, , "[189]\\d{8,9}|[24-6]\\d{8}|[135]\\d{7}", , , , , , , [8, 9, 10], [6, 7]],
      [, , "13[23]\\d{6}|(?:15|57)\\d{6,7}|(?:2\\d|3|4[05-8]|5[05]|6[24-689]|8[2468]|9[235-7])\\d{7}", , , , "234567890", , , [8, 9], [6, 7]],
      [, , "1[0-25]\\d{8}", , , , "1001234567", , , [10]],
      [, , "800\\d{7}", , , , "8001234567", , , [10]],
      [, , "900\\d{7}", , , , "9001234567", , , [10]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "EG",
      20,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d)(\\d{7,8})", "$1 $2", ["[23]"], "0$1"], [, "(\\d{2})(\\d{6,7})", "$1 $2", ["1[35]|[4-6]|8[2468]|9[235-7]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[89]"], "0$1"], [, "(\\d{2})(\\d{8})", "$1 $2", ["1"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    EH: [
      ,
      [, , "[5-8]\\d{8}", , , , , , , [9]],
      [, , "528[89]\\d{5}", , , , "528812345"],
      [, , "(?:6(?:[0-79]\\d|8[0-247-9])|7(?:[016-8]\\d|2[0-8]|3[01]|5[0-5]))\\d{6}", , , , "650123456"],
      [, , "80[0-7]\\d{6}", , , , "801234567"],
      [, , "89\\d{7}", , , , "891234567"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "(?:592(?:4[0-2]|93)|80[89]\\d\\d)\\d{4}", , , , "592401234"],
      "EH",
      212,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    ER: [, [, , "[178]\\d{6}", , , , , , , [7], [6]], [, , "(?:1(?:1[12568]|[24]0|55|6[146])|8\\d\\d)\\d{4}", , , , "8370362", , , , [6]], [, , "(?:17[1-3]|7\\d\\d)\\d{4}", , , , "7123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "ER", 291, "00", "0", , , "0", , , , [[
      ,
      "(\\d)(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["[178]"],
      "0$1"
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    ES: [, [, , "(?:400|[5-9]\\d\\d)\\d{6}", , , , , , , [9]], [, , "96906(?:0[0-8]|1[1-9]|[2-9]\\d)\\d\\d|9(?:69(?:0[0-57-9]|[1-9]\\d)|73(?:[0-8]\\d|9[1-9]))\\d{4}|(?:400|8(?:[1356]\\d|[28][0-8]|[47][1-9])|9(?:[135]\\d|[268][0-8]|4[1-9]|7[124-9]))\\d{6}", , , , "810123456"], [, , "96906(?:09|10)\\d\\d|(?:590(?:10[0-2]|600)|97390\\d)\\d{3}|(?:6\\d|7[1-48])\\d{7}", , , , "612345678"], [, , "[89]00\\d{6}", , , , "800123456"], [
      ,
      ,
      "80[367]\\d{6}",
      ,
      ,
      ,
      "803123456"
    ], [, , "90[12]\\d{6}", , , , "901123456"], [, , "70\\d{7}", , , , "701234567"], [, , , , , , , , , [-1]], "ES", 34, "00", , , , , , , , [[, "(\\d{4})", "$1", ["905", "905[124578]"]], [, "(\\d{6})", "$1", ["[79]9"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[89]00"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[4-9]"]]], [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[89]00"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[4-9]"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "51\\d{7}", , , , "511234567"], , , [, , , , , , , , , [-1]]],
    ET: [, [, , "(?:11|[2-57-9]\\d)\\d{7}", , , , , , , [9], [7]], [
      ,
      ,
      "(?:11(?:[124]\\d\\d|3(?:[0-79]\\d|8[0-7])|5(?:[02-9]\\d|1[0-57-9])|6(?:[02-79]\\d|1[0-57-9]|8[0-8]))|2(?:2(?:11[1-9]|22[0-7]|33\\d|44[1467]|66[1-68])|5(?:11[124-6]|33[2-8]|44[1467]|55[14]|66[1-3679]|77[124-79]|880))|3(?:3(?:11[0-46-8]|(?:22|55)[0-6]|33[0134689]|44[04]|66[01467])|4(?:44[0-8]|55[0-69]|66[0-3]|77[1-5]))|4(?:6(?:119|22[0-24-7]|33[1-5]|44[13-69]|55[14-689]|660|88[1-4])|7(?:(?:11|22)[1-9]|33[13-7]|44[13-6]|55[1-689]))|5(?:7(?:227|55[05]|(?:66|77)[14-8])|8(?:11[149]|22[013-79]|33[0-68]|44[013-8]|550|66[1-5]|77\\d)))\\d{4}",
      ,
      ,
      ,
      "111112345",
      ,
      ,
      ,
      [7]
    ], [, , "700[1-9]\\d{5}|(?:7(?:0[1-9]|1[0-8]|2[1-35-79]|3\\d|77|86|99)|(?:8[01]|9\\d)\\d)\\d{6}", , , , "911234567"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "ET", 251, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[1-57-9]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    FI: [
      ,
      [, , "[1-35689]\\d{4}|7\\d{10,11}|(?:[124-7]\\d|3[0-46-9])\\d{8}|[1-9]\\d{5,8}", , , , , , , [5, 6, 7, 8, 9, 10, 11, 12]],
      [
        ,
        ,
        "1[3-7][1-8]\\d{3,6}|(?:19[1-8]|[23568][1-8]\\d|9(?:00|[1-8]\\d))\\d{2,6}",
        ,
        ,
        ,
        "131234567",
        ,
        ,
        [5, 6, 7, 8, 9]
      ],
      [, , "4946\\d{2,6}|(?:4[0-8]|50)\\d{4,8}", , , , "412345678", , , [6, 7, 8, 9, 10]],
      [, , "800\\d{4,6}", , , , "800123456", , , [7, 8, 9]],
      [, , "[67]00\\d{5,6}", , , , "600123456", , , [8, 9]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "FI",
      358,
      "00|99(?:[01469]|5(?:[14]1|3[23]|5[59]|77|88|9[09]))",
      "0",
      ,
      ,
      "0",
      ,
      "00",
      ,
      [[, "(\\d{5})", "$1", ["75[12]"], "0$1"], [, "(\\d{5})", "$1", ["20[2-59]"], "0$1"], [, "(\\d{6})", "$1", ["11"]], [, "(\\d{3})(\\d{3,7})", "$1 $2", ["(?:[1-3]0|[68])0|70[07-9]"], "0$1"], [
        ,
        "(\\d{2})(\\d{4,8})",
        "$1 $2",
        ["[14]|2[09]|50|7[135]"],
        "0$1"
      ], [, "(\\d{2})(\\d{6,10})", "$1 $2", ["7"], "0$1"], [, "(\\d)(\\d{4,9})", "$1 $2", ["(?:19|[2568])[1-8]|3(?:0[1-9]|[1-9])|9"], "0$1"]],
      [[, "(\\d{5})", "$1", ["20[2-59]"], "0$1"], [, "(\\d{3})(\\d{3,7})", "$1 $2", ["(?:[1-3]0|[68])0|70[07-9]"], "0$1"], [, "(\\d{2})(\\d{4,8})", "$1 $2", ["[14]|2[09]|50|7[135]"], "0$1"], [, "(\\d{2})(\\d{6,10})", "$1 $2", ["7"], "0$1"], [, "(\\d)(\\d{4,9})", "$1 $2", ["(?:19|[2568])[1-8]|3(?:0[1-9]|[1-9])|9"], "0$1"]],
      [, , , , , , , , , [-1]],
      1,
      "1[03-79]|[2-9]",
      [, , "20(?:2[023]|9[89])\\d{1,6}|(?:60[12]\\d|7099)\\d{4,5}|(?:606|7(?:0[78]|1|3\\d))\\d{7}|(?:[1-3]00|7(?:0[1-5]\\d\\d|5[03-9]))\\d{3,7}"],
      [, , "20\\d{4,8}|60[12]\\d{5,6}|7(?:099\\d{4,5}|5[03-9]\\d{3,7})|20[2-59]\\d\\d|(?:606|7(?:0[78]|1|3\\d))\\d{7}|(?:10|29|3[09]|70[1-5]\\d)\\d{4,8}", , , , "10112345"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    FJ: [
      ,
      [, , "45\\d{5}|(?:0800\\d|[235-9])\\d{6}", , , , , , , [7, 11]],
      [, , "603\\d{4}|(?:3[0-6]|6[25-7]|8[58])\\d{5}", , , , "3212345", , , [7]],
      [, , "(?:[279]\\d|45|5[01568]|8[034679])\\d{5}", , , , "7012345", , , [7]],
      [, , "0800\\d{7}", , , , "08001234567", , , [11]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "FJ",
      679,
      "0(?:0|52)",
      ,
      ,
      ,
      ,
      ,
      "00",
      ,
      [[, "(\\d{3})(\\d{4})", "$1 $2", ["[235-9]|45"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["0"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    FK: [, [, , "[2-7]\\d{4}", , , , , , , [5]], [, , "[2-47]\\d{4}", , , , "31234"], [, , "[56]\\d{4}", , , , "51234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "FK", 500, "00", , , , , , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    FM: [, [, , "(?:[39]\\d\\d|820)\\d{4}", , , , , , , [7]], [
      ,
      ,
      "31(?:00[67]|208|309)\\d\\d|(?:3(?:[2357]0[1-9]|602|804|905)|(?:820|9[2-6]\\d)\\d)\\d{3}",
      ,
      ,
      ,
      "3201234"
    ], [, , "31(?:00[67]|208|309)\\d\\d|(?:3(?:[2357]0[1-9]|602|804|905)|(?:820|9[2-7]\\d)\\d)\\d{3}", , , , "3501234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "FM", 691, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[389]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    FO: [, [, , "[2-9]\\d{5}", , , , , , , [6]], [, , "(?:20|[34]\\d|8[19])\\d{4}", , , , "201234"], [, , "(?:[27][1-9]|5\\d|9[16])\\d{4}", , , , "211234"], [, , "80[257-9]\\d{3}", , , , "802123"], [
      ,
      ,
      "90(?:[13-5][15-7]|2[125-7]|9\\d)\\d\\d",
      ,
      ,
      ,
      "901123"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "6[0-36]\\d{4}", , , , "601234"], "FO", 298, "00", , , , "(10(?:01|[12]0|88))", , , , [[, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["[2-9]"], , "$CC $1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    FR: [, [, , "[1-9]\\d{8}", , , , , , , [9]], [, , "(?:26[013-9]|59[1-35-9])\\d{6}|(?:[13]\\d|2[0-57-9]|4[1-9]|5[0-8])\\d{7}", , , , "123456789"], [, , "(?:6(?:[0-24-8]\\d|3[0-8]|9[589])|7[3-9]\\d)\\d{6}", , , , "612345678"], [, , "80[0-5]\\d{6}", , , , "801234567"], [
      ,
      ,
      "836(?:0[0-36-9]|[1-9]\\d)\\d{4}|8(?:1[2-9]|2[2-47-9]|3[0-57-9]|[569]\\d|8[0-35-9])\\d{6}",
      ,
      ,
      ,
      "891123456"
    ], [, , "8(?:1[01]|2[0156]|4[024]|84)\\d{6}", , , , "884012345"], [, , , , , , , , , [-1]], [, , "9\\d{8}", , , , "912345678"], "FR", 33, "00", "0", , , "0", , , , [[, "(\\d{4})", "$1", ["10"]], [, "(\\d{3})(\\d{3})", "$1 $2", ["1"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"], "0 $1"], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[1-79]"], "0$1"]], [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"], "0 $1"], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[1-79]"], "0$1"]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]], [, , "80[6-9]\\d{6}", , , , "806123456"], , , [, , , , , , , , , [-1]]],
    GA: [, [, , "(?:[067]\\d|11)\\d{6}|[2-7]\\d{6}", , , , , , , [7, 8]], [, , "[01]1\\d{6}", , , , "01441234", , , [8]], [, , "(?:(?:0[2-7]|7[467])\\d|6(?:0[0-4]|10|[256]\\d))\\d{5}|[2-7]\\d{6}", , , , "06031234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "GA", 241, "00", , , , "0(11\\d{6}|60\\d{6}|61\\d{6}|6[256]\\d{6}|7[467]\\d{6})", "$1", , , [[, "(\\d)(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2-7]"], "0$1"], [
      ,
      "(\\d{2})(\\d{2})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["0"]
    ], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["11|[67]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GB: [, [, , "[1-357-9]\\d{9}|[18]\\d{8}|8\\d{6}", , , , , , , [7, 9, 10], [4, 5, 6, 8]], [
      ,
      ,
      "(?:1(?:1(?:3(?:[0-58]\\d\\d|73[0-5])|4(?:(?:[0-5]\\d|70)\\d|69[7-9])|(?:(?:5[0-26-9]|[78][0-49])\\d|6(?:[0-4]\\d|5[01]))\\d)|(?:2(?:(?:0[024-9]|2[3-9]|3[3-79]|4[1-689]|[58][02-9]|6[0-47-9]|7[013-9]|9\\d)\\d|1(?:[0-7]\\d|8[0-3]))|(?:3(?:0\\d|1[0-8]|[25][02-9]|3[02-579]|[468][0-46-9]|7[1-35-79]|9[2-578])|4(?:0[03-9]|[137]\\d|[28][02-57-9]|4[02-69]|5[0-8]|[69][0-79])|5(?:0[1-35-9]|[16]\\d|2[024-9]|3[015689]|4[02-9]|5[03-9]|7[0-35-9]|8[0-468]|9[0-57-9])|6(?:0[034689]|1\\d|2[0-35689]|[38][013-9]|4[1-467]|5[0-69]|6[13-9]|7[0-8]|9[0-24578])|7(?:0[0246-9]|2\\d|3[0236-8]|4[03-9]|5[0-46-9]|6[013-9]|7[0-35-9]|8[024-9]|9[02-9])|8(?:0[35-9]|2[1-57-9]|3[02-578]|4[0-578]|5[124-9]|6[2-69]|7\\d|8[02-9]|9[02569])|9(?:0[02-589]|[18]\\d|2[02-689]|3[1-57-9]|4[2-9]|5[0-579]|6[2-47-9]|7[0-24578]|9[2-57]))\\d)\\d)|2(?:0[013478]|3[0189]|4[017]|8[0-46-9]|9[0-2])\\d{3})\\d{4}|1(?:2(?:0(?:46[1-4]|87[2-9])|545[1-79]|76(?:2\\d|3[1-8]|6[1-6])|9(?:7(?:2[0-4]|3[2-5])|8(?:2[2-8]|7[0-47-9]|8[3-5])))|3(?:6(?:38[2-5]|47[23])|8(?:47[04-9]|64[0157-9]))|4(?:044[1-7]|20(?:2[23]|8\\d)|6(?:0(?:30|5[2-57]|6[1-8]|7[2-8])|140)|8(?:052|87[1-3]))|5(?:2(?:4(?:3[2-79]|6\\d)|76\\d)|6(?:26[06-9]|686))|6(?:06(?:4\\d|7[4-79])|295[5-7]|35[34]\\d|47(?:24|61)|59(?:5[08]|6[67]|74)|9(?:55[0-4]|77[23]))|7(?:26(?:6[13-9]|7[0-7])|(?:442|688)\\d|50(?:2[0-3]|[3-68]2|76))|8(?:27[56]\\d|37(?:5[2-5]|8[239])|843[2-58])|9(?:0(?:0(?:6[1-8]|85)|52\\d)|3583|4(?:66[1-8]|9(?:2[01]|81))|63(?:23|3[1-4])|9561))\\d{3}",
      ,
      ,
      ,
      "1212345678",
      ,
      ,
      [9, 10],
      [4, 5, 6, 7, 8]
    ], [, , "7(?:457[0-57-9]|700[01]|911[028])\\d{5}|7(?:[1-3]\\d\\d|4(?:[0-46-9]\\d|5[0-689])|5(?:0[0-8]|[13-9]\\d|2[0-35-9])|7(?:0[1-9]|[1-7]\\d|8[02-9]|9[0-689])|8(?:[014-9]\\d|[23][0-8])|9(?:[024-9]\\d|1[02-9]|3[0-689]))\\d{6}", , , , "7400123456", , , [10]], [, , "80[08]\\d{7}|800\\d{6}|8001111", , , , "8001234567"], [, , "(?:8(?:4[2-5]|7[0-3])|9(?:[01]\\d|8[2-49]))\\d{7}|845464\\d", , , , "9012345678", , , [7, 10]], [, , , , , , , , , [-1]], [, , "70\\d{8}", , , , "7012345678", , , [10]], [
      ,
      ,
      "56\\d{8}",
      ,
      ,
      ,
      "5612345678",
      ,
      ,
      [10]
    ], "GB", 44, "00", "0", " x", , "0|180020", , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["800", "8001", "80011", "800111", "8001111"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3", ["845", "8454", "84546", "845464"], "0$1"], [, "(\\d{3})(\\d{6})", "$1 $2", ["800"], "0$1"], [, "(\\d{5})(\\d{4,5})", "$1 $2", ["1(?:38|5[23]|69|76|94)", "1(?:(?:38|69)7|5(?:24|39)|768|946)", "1(?:3873|5(?:242|39[4-6])|(?:697|768)[347]|9467)"], "0$1"], [, "(\\d{4})(\\d{5,6})", "$1 $2", ["1(?:[2-69][02-9]|[78])"], "0$1"], [
      ,
      "(\\d{2})(\\d{4})(\\d{4})",
      "$1 $2 $3",
      ["[25]|7(?:0|6[02-9])", "[25]|7(?:0|6(?:[03-9]|2[356]))"],
      "0$1"
    ], [, "(\\d{4})(\\d{6})", "$1 $2", ["7"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[1389]"], "0$1"]], , [, , "76(?:464|652)\\d{5}|76(?:0[0-28]|2[356]|34|4[01347]|5[49]|6[0-369]|77|8[14]|9[139])\\d{6}", , , , "7640123456", , , [10]], 1, , [, , , , , , , , , [-1]], [, , "(?:3[0347]|55)\\d{8}", , , , "5512345678", , , [10]], , , [, , , , , , , , , [-1]]],
    GD: [, [, , "(?:473|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [
      ,
      ,
      "473(?:2(?:3[0-2]|69)|3(?:2[89]|86)|4(?:[06]8|3[5-9]|4[0-4]|5[59]|73|90)|63[68]|7(?:58|84)|800|938)\\d{4}",
      ,
      ,
      ,
      "4732691234",
      ,
      ,
      ,
      [7]
    ], [, , "473(?:4(?:0[2-79]|1[04-9]|2[0-5]|49|5[6-8])|5(?:2[01]|3[3-8])|901)\\d{4}", , , , "4734031234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], "GD", 1, "011", "1", , , "([2-9]\\d{6})$|1", "473$1", , , , , [, , , , , , , , , [-1]], , "473", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GE: [, [, , "(?:[3-57]\\d\\d|800)\\d{6}", , , , , , , [9], [6, 7]], [, , "(?:3(?:[256]\\d|4[124-9]|7[0-4])|4(?:1\\d|2[2-7]|3[1-79]|4[2-8]|7[239]|9[1-7]))\\d{6}", , , , "322123456", , , , [6, 7]], [
      ,
      ,
      "5(?:(?:(?:0555|1(?:[17]77|555))[5-9]|757(?:7[7-9]|8[01]))\\d|22252[0-4])\\d\\d|5(?:0(?:0(?:1[09]|70)|505)|1(?:0[01]0|1(?:07|33|51))|2(?:0[02]0|2[25]2)|3(?:0[03]0|3[35]3)|4(?:0[04]0|411)|5222|9000)[0-4]\\d{3}|(?:5(?:0(?:0(?:0\\d|1[12]|2[02]|3[0-6]|4[04]|5[05]|77|88|9[09])|(?:[14]\\d|77)\\d|22[02])|1(?:1(?:[03][01]|[124]\\d|5[02-6]|7[0-6])|4\\d\\d)|2(?:228|555)|3555|4(?:4(?:[02-9]\\d|14)|555)|5(?:[0157-9]\\d\\d|200|333|4(?:44|55))|6[89]\\d\\d|7(?:(?:[0147-9]\\d|22)\\d|5(?:00|[57]5))|8(?:0(?:[018]\\d|2[0-4])|5(?:55|8[89])|8(?:55|88))|9(?:090|[1-35-9]\\d\\d))|790\\d\\d)\\d{4}",
      ,
      ,
      ,
      "555123456"
    ], [, , "800\\d{6}", , , , "800123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "70[67]\\d{6}", , , , "706123456"], "GE", 995, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["70"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["32"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[57]"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[348]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , "70[67]\\d{6}"], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GF: [, [
      ,
      ,
      "(?:694\\d|7093)\\d{5}|(?:59|[89]\\d)\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [9]
    ], [, , "(?:59(?:4(?:[02-49]\\d|1[0-5]|5[6-9]|6[0-3]|80)|88\\d)|80[6-9]\\d\\d)\\d{4}", , , , "594101234"], [, , "(?:694(?:[0-249]\\d|3[0-8])|7093[0-3])\\d{4}", , , , "694201234"], [, , "80[0-5]\\d{6}", , , , "800012345"], [, , "8[129]\\d{7}", , , , "890123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:(?:396|76\\d)\\d|476[0-6])\\d{4}", , , , "976012345"], "GF", 594, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-7]|80[6-9]|9[47]"], "0$1"], [
      ,
      "(\\d{3})(\\d{2})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["[89]"],
      "0$1"
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GG: [
      ,
      [, , "(?:1481|[357-9]\\d{3})\\d{6}|8\\d{6}(?:\\d{2})?", , , , , , , [7, 9, 10], [6]],
      [, , "1481[25-9]\\d{5}", , , , "1481256789", , , [10], [6]],
      [, , "7(?:(?:781|839)\\d|911[17])\\d{5}", , , , "7781123456", , , [10]],
      [, , "80[08]\\d{7}|800\\d{6}|8001111", , , , "8001234567"],
      [, , "(?:8(?:4[2-5]|7[0-3])|9(?:[01]\\d|8[0-3]))\\d{7}|845464\\d", , , , "9012345678", , , [7, 10]],
      [, , , , , , , , , [-1]],
      [, , "70\\d{8}", , , , "7012345678", , , [10]],
      [, , "56\\d{8}", , , , "5612345678", , , [10]],
      "GG",
      44,
      "00",
      "0",
      ,
      ,
      "([25-9]\\d{5})$|0|180020",
      "1481$1",
      ,
      ,
      ,
      ,
      [, , "76(?:464|652)\\d{5}|76(?:0[0-28]|2[356]|34|4[01347]|5[49]|6[0-369]|77|8[14]|9[139])\\d{6}", , , , "7640123456", , , [10]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "(?:3[0347]|55)\\d{8}", , , , "5512345678", , , [10]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    GH: [, [, , "[235]\\d{8}|800\\d{5,6}", , , , , , , [8, 9], [7]], [
      ,
      ,
      "3082[0-5]\\d{4}|3(?:0(?:[237]\\d|8[01])|[167](?:2[0-6]|7\\d|80)|2(?:2[0-5]|7\\d|80)|3(?:2[0-3]|7\\d|80)|4(?:2[013-9]|3[01]|7\\d|80)|5(?:2[0-7]|7\\d|80)|8(?:2[0-2]|7\\d|80)|9(?:[28]0|7\\d))\\d{5}",
      ,
      ,
      ,
      "302345678",
      ,
      ,
      [9],
      [7]
    ], [, , "(?:2(?:[0346-9]\\d|5[67])|5(?:[03-7]\\d|9[1-9]))\\d{6}", , , , "231234567", , , [9]], [, , "800\\d{5,6}", , , , "80012345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "GH", 233, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[237]|8[0-2]"]], [, "(\\d{3})(\\d{5})", "$1 $2", ["8"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2358]"], "0$1"]], [[, "(\\d{3})(\\d{5})", "$1 $2", ["8"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2358]"], "0$1"]], [, , , , , , , , , [-1]], , , [
      ,
      ,
      "800\\d{5,6}"
    ], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GI: [, [, , "(?:[25]\\d|60)\\d{6}", , , , , , , [8]], [, , "2190[0-2]\\d{3}|2(?:0(?:[02]\\d|3[01])|16[24-9]|2[2-5]\\d)\\d{4}", , , , "20012345"], [, , "5251[0-4]\\d{3}|(?:5(?:[146-8]\\d\\d|250)|60(?:1[01]|6\\d))\\d{4}", , , , "57123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "GI", 350, "00", , , , , , , , [[, "(\\d{3})(\\d{5})", "$1 $2", ["2"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GL: [, [
      ,
      ,
      "(?:19|[2-689]\\d|70)\\d{4}",
      ,
      ,
      ,
      ,
      ,
      ,
      [6]
    ], [, , "(?:19|3[1-7]|[68][1-9]|70|9\\d)\\d{4}", , , , "321000"], [, , "[245]\\d{5}", , , , "221234"], [, , "80\\d{4}", , , , "801234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "3[89]\\d{4}", , , , "381234"], "GL", 299, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["19|[2-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GM: [, [, , "[48]\\d{8}|[2-9]\\d{6}", , , , , , , [7, 9]], [
      ,
      ,
      "(?:4(?:[23]\\d\\d|4(?:1[024679]|(?:4(?:[237-9]\\d|4[14-9])|8[0-389]\\d)\\d|5(?:5(?:3\\d|4[0-7])|[67]\\d\\d)))|5(?:5(?:3\\d|4[0-7])|6[67]\\d|7(?:1[04]|2[035]|3[58]|48))|8[0-389]\\d\\d)\\d{3}|44[6-9]\\d{4}",
      ,
      ,
      ,
      "5661234"
    ], [, , "(?:(?:[23679]\\d|4[015]|8(?:(?:3[35]|6[68]|99)\\d|7(?:[27]\\d|4[015])))\\d|5(?:[0-489]\\d|56))\\d{4}|8[4-7]\\d{5}", , , , "3012345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "GM", 220, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[235-9]|4(?:[0-35]|4[16-9])"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[48]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GN: [, [, , "722\\d{6}|(?:3|6\\d)\\d{7}", , , , , , , [8, 9]], [
      ,
      ,
      "3(?:0(?:24|3[12]|4[1-35-7]|5[13]|6[189]|[78]1|9[1478])|1\\d\\d)\\d{4}",
      ,
      ,
      ,
      "30241234",
      ,
      ,
      [8]
    ], [, , "6[0-356]\\d{7}", , , , "601123456", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "722\\d{6}", , , , "722123456", , , [9]], "GN", 224, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["3"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[67]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GP: [, [, , "7090\\d{5}|(?:[56]9|[89]\\d)\\d{7}", , , , , , , [9]], [
      ,
      ,
      "(?:59(?:0(?:0[1-68]|[14][0-24-9]|2[0-68]|3[1-9]|5[3-579]|[68][0-689]|7[08]|9\\d)|87\\d)|80[6-9]\\d\\d)\\d{4}",
      ,
      ,
      ,
      "590201234"
    ], [, , "(?:69(?:0\\d\\d|1(?:2[2-9]|3[0-5]))|7090[0-4])\\d{4}", , , , "690001234"], [, , "80[0-5]\\d{6}", , , , "800012345"], [, , "8[129]\\d{7}", , , , "810123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:(?:39[5-7]|76[018])\\d|475[0-6])\\d{4}", , , , "976012345"], "GP", 590, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-79]|80[6-9]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"], "0$1"]], , [, , , , , , , , , [-1]], 1, , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GQ: [
      ,
      [, , "222\\d{6}|(?:3\\d|55|[89]0)\\d{7}", , , , , , , [9]],
      [, , "33[0-24-9]\\d[46]\\d{4}|3(?:33|5\\d)\\d[7-9]\\d{4}", , , , "333091234"],
      [, , "(?:222|55\\d)\\d{6}", , , , "222123456"],
      [, , "80\\d[1-9]\\d{5}", , , , "800123456"],
      [, , "90\\d[1-9]\\d{5}", , , , "900123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "GQ",
      240,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[235]"]], [, "(\\d{3})(\\d{6})", "$1 $2", ["[89]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    GR: [
      ,
      [
        ,
        ,
        "5005000\\d{3}|8\\d{9,11}|(?:[269]\\d|70)\\d{8}",
        ,
        ,
        ,
        ,
        ,
        ,
        [10, 11, 12]
      ],
      [, , "2(?:1\\d\\d|2(?:2[1-46-9]|[36][1-8]|4[1-7]|5[1-4]|7[1-5]|[89][1-9])|3(?:1\\d|2[1-57]|[35][1-3]|4[13]|7[1-7]|8[124-6]|9[1-79])|4(?:1\\d|2[1-8]|3[1-4]|4[13-5]|6[1-578]|9[1-5])|5(?:1\\d|[29][1-4]|3[1-5]|4[124]|5[1-6])|6(?:1\\d|[269][1-6]|3[1245]|4[1-7]|5[13-9]|7[14]|8[1-5])|7(?:1\\d|2[1-5]|3[1-6]|4[1-7]|5[1-57]|6[135]|9[125-7])|8(?:1\\d|2[1-5]|[34][1-4]|9[1-57]))\\d{6}", , , , "2123456789", , , [10]],
      [, , "68[57-9]\\d{7}|(?:69|94)\\d{8}", , , , "6912345678", , , [10]],
      [, , "800\\d{7,9}", , , , "8001234567"],
      [, , "90[19]\\d{7}", , , , "9091234567", , , [10]],
      [, , "8(?:0[16]|12|[27]5|50)\\d{7}", , , , "8011234567", , , [10]],
      [, , "70\\d{8}", , , , "7012345678", , , [10]],
      [, , , , , , , , , [-1]],
      "GR",
      30,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["21|7"]], [, "(\\d{4})(\\d{6})", "$1 $2", ["2(?:2|3[2-57-9]|4[2-469]|5[2-59]|6[2-9]|7[2-69]|8[2-49])|5"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2689]"]], [, "(\\d{3})(\\d{3,4})(\\d{5})", "$1 $2 $3", ["8"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "5005000\\d{3}", , , , "5005000123", , , [10]],
      ,
      ,
      [
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        [-1]
      ]
    ],
    GT: [, [, , "80\\d{6}|(?:1\\d{3}|[2-7])\\d{7}", , , , , , , [8, 11]], [, , "[267][2-9]\\d{6}", , , , "22456789", , , [8]], [, , "(?:[3-5]\\d\\d|80[0-4])\\d{5}", , , , "51234567", , , [8]], [, , "18[01]\\d{8}", , , , "18001112222", , , [11]], [, , "19\\d{9}", , , , "19001112222", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "GT", 502, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[2-8]"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GU: [, [
      ,
      ,
      "(?:[58]\\d\\d|671|900)\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [10],
      [7]
    ], [, , "671(?:2\\d\\d|3(?:00|3[39]|4[349]|55|6[26])|4(?:00|56|7[1-9]|8[02-9])|5(?:55|6[2-5]|88)|6(?:3[2-578]|4[24-9]|5[34]|78|8[235-9])|7(?:[0479]7|2[0167]|3[45]|8[7-9])|8(?:[2-57-9]8|6[478])|9(?:2[29]|6[79]|7[1279]|8[7-9]|9[16-9]))\\d{4}", , , , "6713001234", , , , [7]], [
      ,
      ,
      "671(?:2\\d\\d|3(?:00|3[39]|4[349]|55|6[26])|4(?:00|56|7[1-9]|8[02-9])|5(?:55|6[2-5]|88)|6(?:3[2-578]|4[24-9]|5[34]|78|8[235-9])|7(?:[0479]7|2[0167]|3[45]|8[7-9])|8(?:[2-57-9]8|6[478])|9(?:2[29]|6[79]|7[1279]|8[7-9]|9[16-9]))\\d{4}",
      ,
      ,
      ,
      "6713001234",
      ,
      ,
      ,
      [7]
    ], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "GU", 1, "011", "1", , , "([2-9]\\d{6})$|1", "671$1", , 1, , , [, , , , , , , , , [-1]], , "671", [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    GW: [, [, , "[49]\\d{8}|4\\d{6}", , , , , , , [7, 9]], [, , "443\\d{6}", , , , "443201234", , , [9]], [, , "9(?:5\\d|6[569]|77)\\d{6}", , , , "955012345", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "40\\d{5}", , , , "4012345", , , [7]], "GW", 245, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["40"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[49]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    GY: [, [, , "(?:[2-8]\\d{3}|9008)\\d{3}", , , , , , , [7]], [
      ,
      ,
      "(?:2(?:1[6-9]|2[0-35-9]|3[1-4]|5[3-9]|6\\d|7[0-79])|3(?:2[25-9]|3\\d)|4(?:4[0-24]|5[56])|50[0-6]|77[1-57])\\d{4}",
      ,
      ,
      ,
      "2201234"
    ], [, , "(?:51[01]|6\\d\\d|7(?:[0-5]\\d|6[0-79]|70|8[067]))\\d{4}", , , , "6091234"], [, , "(?:289|8(?:00|6[28]|88|99))\\d{4}", , , , "2891234"], [, , "9008\\d{3}", , , , "9008123"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "515\\d{4}", , , , "5151234"], "GY", 592, "001", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[2-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    HK: [, [, , "8[0-46-9]\\d{6,7}|9\\d{4,7}|(?:[2-7]|9\\d{3})\\d{7}", , , , , , , [5, 6, 7, 8, 9, 11]], [
      ,
      ,
      "(?:2(?:[13-9]\\d|2[013-9])\\d|3(?:(?:[1569][0-24-9]|4[0-246-9]|7[0-24-69])\\d|8(?:4[0-8]|[579]\\d|6[0-5]))|58(?:0[1-9]|1[2-9]))\\d{4}",
      ,
      ,
      ,
      "21234567",
      ,
      ,
      [8]
    ], [, , "(?:4(?:0(?:6[0-3]|9[3-6])|24[3-6]|44[0-35-9]|6(?:4[0-57-9]|6[0-6])|7(?:4[0-48]|6[0-5]))|5(?:25[3-7]|35[4-8]|73[0-6]|95[0-8])|6(?:26[013-8]|(?:66|78)[0-5])|7(?:0(?:7[1-8]|8[0-8])|10[1-4])|84(?:4[0-2]|8[0-35-9])|9(?:29[013-9]|39[014-9]|59[0-467]|899))\\d{4}|(?:4(?:4[0-35-9]|6[0-357-9]|7[0-35])|5(?:[1-59][0-46-9]|6[0-4689]|7[0-246-9])|6(?:0[1-9]|[13-59]\\d|[268][0-57-9]|7[0-79])|70[1-59]|84[0-39]|9(?:0[1-9]|1[02-9]|[2358][0-8]|[467]\\d))\\d{5}", , , , "51234567", , , [8]], [
      ,
      ,
      "800\\d{6}",
      ,
      ,
      ,
      "800123456",
      ,
      ,
      [9]
    ], [, , "900(?:[0-24-9]\\d{7}|3\\d{1,4})", , , , "90012345678", , , [5, 6, 7, 8, 11]], [, , , , , , , , , [-1]], [, , "8(?:1[0-4679]\\d|2(?:[0-36]\\d|7[0-4])|3(?:[034]\\d|2[09]|70))\\d{4}", , , , "81123456", , , [8]], [, , , , , , , , , [-1]], "HK", 852, "00(?:30|5[09]|[126-9]?)", , , , , , "00", , [[, "(\\d{3})(\\d{2,5})", "$1 $2", ["900", "9003"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[2-7]|8[1-4]|9(?:0[1-9]|[1-8])"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["8"]], [, "(\\d{3})(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["9"]]], , [
      ,
      ,
      "7(?:1(?:0[08]|1[0-3679]|3[013]|69|9[0136])|2(?:[02389]\\d|1[18]|7[27-9])|3(?:[0-38]\\d|7[0-369]|9[2357-9])|47\\d|5(?:[178]\\d|5[0-5])|6(?:0[0-7]|2[236-9]|[35]\\d)|7(?:[27]\\d|8[7-9])|8(?:[23689]\\d|7[1-9])|9(?:[025]\\d|6[0-246-8]|7[0-36-9]|8[238]))\\d{4}",
      ,
      ,
      ,
      "71123456",
      ,
      ,
      [8]
    ], , , [, , , , , , , , , [-1]], [, , "30(?:0[1-9]|[15-7]\\d|2[047]|89)\\d{4}", , , , "30161234", , , [8]], , , [, , , , , , , , , [-1]]],
    HN: [, [, , "8\\d{10}|[237-9]\\d{7}", , , , , , , [8, 11]], [
      ,
      ,
      "2(?:2(?:0[0-59]|1[1-9]|[23]\\d|4[02-8]|5[57]|6[2458]|7[0135689]|8[01346-9]|9[0-2])|4(?:0[578]|2[3-59]|3[13-9]|4[0-68]|5[1-3589]|80)|5(?:0[2357-9]|1[1-6]|4[03-58]|5\\d|6[014-69]|7[04]|80)|6(?:[056]\\d|17|2[067]|3[047]|4[0-378]|[78][0-8]|9[01])|7(?:0[5-79]|2[01]|6[46-9]|7[02-9]|8[034]|91)|8(?:79|8[0-357-9]|9[1-57-9]))\\d{4}",
      ,
      ,
      ,
      "22123456",
      ,
      ,
      [8]
    ], [, , "[37-9]\\d{7}", , , , "91234567", , , [8]], [, , "8002\\d{7}", , , , "80021234567", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "HN", 504, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1-$2", ["[237-9]"]], [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["8"]]], [[, "(\\d{4})(\\d{4})", "$1-$2", ["[237-9]"]]], [, , , , , , , , , [-1]], , , [, , "8002\\d{7}", , , , , , , [11]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    HR: [, [, , "[2-69]\\d{8}|80\\d{5,7}|[1-79]\\d{7}|6\\d{6}", , , , , , , [7, 8, 9], [6]], [
      ,
      ,
      "1\\d{7}|(?:2[0-3]|3[1-5]|4[02-47-9]|5[1-3])\\d{6,7}",
      ,
      ,
      ,
      "12345678",
      ,
      ,
      [8, 9],
      [6, 7]
    ], [, , "9(?:(?:0[1-9]|[12589]\\d)\\d\\d|7(?:[0679]\\d\\d|5(?:[01]\\d|44|55|77|9[5-79])))\\d{4}|98\\d{6}", , , , "921234567", , , [8, 9]], [, , "80\\d{5,7}", , , , "800123456"], [, , "6[01459]\\d{6}|6[01]\\d{5}", , , , "6001234", , , [7, 8]], [, , , , , , , , , [-1]], [, , "7[45]\\d{6}", , , , "74123456", , , [8]], [, , , , , , , , , [-1]], "HR", 385, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3", ["6[01]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2,3})", "$1 $2 $3", ["8"], "0$1"], [, "(\\d)(\\d{4})(\\d{3})", "$1 $2 $3", ["1"], "0$1"], [
      ,
      "(\\d{2})(\\d{3})(\\d{3,4})",
      "$1 $2 $3",
      ["6|7[245]"],
      "0$1"
    ], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["9"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[2-57]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "62\\d{6,7}|72\\d{6}", , , , "62123456", , , [8, 9]], , , [, , , , , , , , , [-1]]],
    HT: [, [, , "[2-589]\\d{7}", , , , , , , [8]], [, , "2(?:2\\d|5[1-5]|81|9[149])\\d{5}", , , , "22453300"], [, , "(?:[34]\\d|5[568])\\d{6}", , , , "34101234"], [, , "8\\d{7}", , , , "80012345"], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:[67][0-4]|8[0-3589]|9\\d)\\d{5}", , , , "98901234"], "HT", 509, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{4})", "$1 $2 $3", ["[2-589]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    HU: [, [, , "[235-7]\\d{8}|[1-9]\\d{7}", , , , , , , [8, 9], [6, 7]], [, , "(?:1\\d|[27][2-9]|3[2-7]|4[24-9]|5[2-79]|6[23689]|8[2-57-9]|9[2-69])\\d{6}", , , , "12345678", , , [8], [6, 7]], [, , "(?:[257]0|3[01])\\d{7}", , , , "201234567", , , [9]], [, , "(?:[48]0\\d|680[29])\\d{5}", , , , "80123456"], [
      ,
      ,
      "9[01]\\d{6}",
      ,
      ,
      ,
      "90123456",
      ,
      ,
      [8]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "21\\d{7}", , , , "211234567", , , [9]], "HU", 36, "00", "06", , , "06", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["1"], "(06 $1)"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[27][2-9]|3[2-7]|4[24-9]|5[2-79]|6|8[2-57-9]|9[2-69]"], "(06 $1)"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[2-9]"], "06 $1"]], , [, , , , , , , , , [-1]], , , [, , "(?:[48]0\\d|680[29])\\d{5}"], [, , "38\\d{7}", , , , "381234567", , , [9]], , , [, , , , , , , , , [-1]]],
    ID: [, [
      ,
      ,
      "00[1-9]\\d{9,14}|(?:[1-36]|8\\d{5})\\d{6}|00\\d{9}|[1-9]\\d{8,10}|[2-9]\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
      [5, 6]
    ], [
      ,
      ,
      "2[124]\\d{7,8}|619\\d{8}|2(?:1(?:14|500)|2\\d{3})\\d{3}|61\\d{5,8}|(?:2(?:[35][1-4]|6[0-8]|7[1-6]|8\\d|9[1-8])|3(?:1|[25][1-8]|3[1-68]|4[1-3]|6[1-3568]|7[0-469]|8\\d)|4(?:0[1-589]|1[01347-9]|2[0-36-8]|3[0-24-68]|43|5[1-378]|6[1-5]|7[134]|8[1245])|5(?:1[1-35-9]|2[25-8]|3[124-9]|4[1-3589]|5[1-46]|6[1-8])|6(?:[25]\\d|3[1-69]|4[1-6])|7(?:02|[125][1-9]|[36]\\d|4[1-8]|7[0-36-9])|9(?:0[12]|1[013-8]|2[0-479]|5[125-8]|6[23679]|7[159]|8[01346]))\\d{5,8}",
      ,
      ,
      ,
      "218350123",
      ,
      ,
      [7, 8, 9, 10, 11],
      [5, 6]
    ], [, , "8[1-35-9]\\d{7,10}", , , , "812345678", , , [9, 10, 11, 12]], [, , "00(?:1803\\d{5,11}|7803\\d{7})|(?:177\\d|800)\\d{5,7}", , , , "8001234567", , , [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]], [, , "809\\d{7}", , , , "8091234567", , , [10]], [, , "804\\d{7}", , , , "8041234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "ID", 62, "00[89]", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["15"]], [, "(\\d{2})(\\d{5,9})", "$1 $2", ["2[124]|[36]1"], "(0$1)"], [, "(\\d{3})(\\d{5,7})", "$1 $2", ["800"], "0$1"], [
      ,
      "(\\d{3})(\\d{5,8})",
      "$1 $2",
      ["[2-79]"],
      "(0$1)"
    ], [, "(\\d{3})(\\d{3,4})(\\d{3})", "$1-$2-$3", ["8[1-35-9]"], "0$1"], [, "(\\d{3})(\\d{6,8})", "$1 $2", ["1"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["804"], "0$1"], [, "(\\d{3})(\\d)(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["80"], "0$1"], [, "(\\d{3})(\\d{4})(\\d{4,5})", "$1-$2-$3", ["8"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})(\\d{2,8})", "$1 $2 $3 $4", ["001"]], [, "(\\d{2})(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["0"]]], [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["15"]], [
      ,
      "(\\d{2})(\\d{5,9})",
      "$1 $2",
      ["2[124]|[36]1"],
      "(0$1)"
    ], [, "(\\d{3})(\\d{5,7})", "$1 $2", ["800"], "0$1"], [, "(\\d{3})(\\d{5,8})", "$1 $2", ["[2-79]"], "(0$1)"], [, "(\\d{3})(\\d{3,4})(\\d{3})", "$1-$2-$3", ["8[1-35-9]"], "0$1"], [, "(\\d{3})(\\d{6,8})", "$1 $2", ["1"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["804"], "0$1"], [, "(\\d{3})(\\d)(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["80"], "0$1"], [, "(\\d{3})(\\d{4})(\\d{4,5})", "$1-$2-$3", ["8"], "0$1"]], [, , , , , , , , , [-1]], , , [, , "001803\\d{5,11}|(?:007803\\d|8071)\\d{6}", , , , , , , [10, 11, 12, 13, 14, 15, 16, 17]], [
      ,
      ,
      "(?:1500|8071\\d{3})\\d{3}",
      ,
      ,
      ,
      "8071123456",
      ,
      ,
      [7, 10]
    ], , , [, , , , , , , , , [-1]]],
    IE: [, [, , "(?:1\\d|[2569])\\d{6,8}|4\\d{6,9}|7\\d{8}|8\\d{8,9}", , , , , , , [7, 8, 9, 10], [5, 6]], [, , "(?:1\\d|21)\\d{6,7}|(?:2[24-9]|4(?:0[24]|5\\d|7)|5(?:0[45]|1\\d|8)|6(?:1\\d|[237-9])|9(?:1\\d|[35-9]))\\d{5}|(?:23|4(?:[1-469]|8\\d)|5[23679]|6[4-6]|7[14]|9[04])\\d{7}", , , , "2212345", , , , [5, 6]], [, , "8(?:22|[35-9]\\d)\\d{6}", , , , "850123456", , , [9]], [, , "1800\\d{6}", , , , "1800123456", , , [10]], [
      ,
      ,
      "15(?:1[2-8]|[2-8]0|9[089])\\d{6}",
      ,
      ,
      ,
      "1520123456",
      ,
      ,
      [10]
    ], [, , "18[59]0\\d{6}", , , , "1850123456", , , [10]], [, , "700\\d{6}", , , , "700123456", , , [9]], [, , "76\\d{7}", , , , "761234567", , , [9]], "IE", 353, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{5})", "$1 $2", ["2[24-9]|47|58|6[237-9]|9[35-9]"], "(0$1)"], [, "(\\d{3})(\\d{5})", "$1 $2", ["[45]0"], "(0$1)"], [, "(\\d)(\\d{3,4})(\\d{4})", "$1 $2 $3", ["1"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[2569]|4[1-69]|7[14]"], "(0$1)"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["70"], "0$1"], [
      ,
      "(\\d{3})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["81"],
      "(0$1)"
    ], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[78]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1"]], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["4"], "(0$1)"], [, "(\\d{2})(\\d)(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , "18[59]0\\d{6}", , , , , , , [10]], [, , "818\\d{6}", , , , "818123456", , , [9]], , , [, , "88210[1-9]\\d{4}|8(?:[35-79]5\\d\\d|8(?:[013-9]\\d\\d|2(?:[01][1-9]|[2-9]\\d)))\\d{5}", , , , "8551234567", , , [10]]],
    IL: [
      ,
      [, , "1\\d{6}(?:\\d{3,5})?|[57]\\d{8}|[1-489]\\d{7}", , , , , , , [
        7,
        8,
        9,
        10,
        11,
        12
      ]],
      [, , "153\\d{8,9}|29[1-9]\\d{5}|(?:2[0-8]|[3489]\\d)\\d{6}", , , , "21234567", , , [8, 11, 12], [7]],
      [, , "55(?:4(?:0[0-3]|10|6[015-9])|57[0-289]|8[06][0-2])\\d{4}|5(?:(?:[0-2][02-9]|[36]\\d|[49][2-9]|8[3-7])\\d|5(?:01|2\\d|3[0-3]|4[3-5]|5[0-25689]|6[6-8]|7[0-267]|8[7-9]|9[1-9]))\\d{5}", , , , "502345678", , , [9]],
      [, , "1(?:255|80[019]\\d{3})\\d{3}", , , , "1800123456", , , [7, 10]],
      [, , "1212\\d{4}|1(?:200|9(?:0[0-2]|19|9\\d))\\d{6}", , , , "1919123456", , , [8, 10]],
      [, , "1700\\d{6}", , , , "1700123456", , , [10]],
      [, , , , , , , , , [-1]],
      [, , "7(?:280[01]|38(?:[05]\\d|8[01358])|8(?:33|55|77|81)\\d)\\d{4}|7(?:18|2[23]|3[237]|47|6[258]|7\\d|82|9[2-9])\\d{6}", , , , "771234567", , , [9]],
      "IL",
      972,
      "0(?:0|1(?:05|[2-9]))",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{4})(\\d{3})", "$1-$2", ["125"]], [, "(\\d{4})(\\d{2})(\\d{2})", "$1-$2-$3", ["121"]], [, "(\\d)(\\d{3})(\\d{4})", "$1-$2-$3", ["[2-489]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1-$2-$3", ["[57]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1-$2-$3", ["12"]], [, "(\\d{4})(\\d{6})", "$1-$2", ["159"]], [
        ,
        "(\\d)(\\d{3})(\\d{3})(\\d{3})",
        "$1-$2-$3-$4",
        ["1[7-9]"]
      ], [, "(\\d{3})(\\d{1,2})(\\d{3})(\\d{4})", "$1-$2 $3-$4", ["15"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "1700\\d{6}", , , , , , , [10]],
      [, , "1599\\d{6}", , , , "1599123456", , , [10]],
      ,
      ,
      [, , "151\\d{8,9}", , , , "15112340000", , , [11, 12]]
    ],
    IM: [, [, , "1624\\d{6}|(?:[3578]\\d|90)\\d{8}", , , , , , , [10], [6]], [, , "1624(?:230|[5-8]\\d\\d)\\d{3}", , , , "1624756789", , , , [6]], [, , "76245[06]\\d{4}|7(?:4576|[59]24\\d|624[0-4689])\\d{5}", , , , "7924123456"], [, , "808162\\d{4}", , , , "8081624567"], [
      ,
      ,
      "8(?:440[49]06|72299\\d)\\d{3}|(?:8(?:45|70)|90[0167])624\\d{4}",
      ,
      ,
      ,
      "9016247890"
    ], [, , , , , , , , , [-1]], [, , "70\\d{8}", , , , "7012345678"], [, , "56\\d{8}", , , , "5612345678"], "IM", 44, "00", "0", , , "([25-8]\\d{5})$|0|180020", "1624$1", , , , , [, , , , , , , , , [-1]], , "74576|(?:16|7[56])24", [, , , , , , , , , [-1]], [, , "3440[49]06\\d{3}|(?:3(?:08162|3\\d{4}|45624|7(?:0624|2299))|55\\d{4})\\d{4}", , , , "5512345678"], , , [, , , , , , , , , [-1]]],
    IN: [, [, , "(?:000800|[2-9]\\d\\d)\\d{7}|1\\d{7,12}", , , , , , , [8, 9, 10, 11, 12, 13], [6, 7]], [
      ,
      ,
      "(?:2717(?:[2-7]\\d|95)|6828[235-7]\\d)\\d{4}|(?:170[24]|280[13468]|4(?:20[24]|72[2-8])|552[1-7])\\d{6}|(?:271[0-689]|682[0-79]|782[0-6])[2-7]\\d{5}|(?:2(?:[02][2-79]|90)|3(?:23|80)|683|79[1-6])\\d{7}|(?:11|33|4[04]|80)[2-7]\\d{7}|(?:342|674|788)(?:[0189][2-7]|[2-7]\\d)\\d{5}|(?:1(?:2[0-249]|3[0-25]|4[145]|[59][14]|6[014]|7[1257]|8[01346])|2(?:1[257]|3[013]|4[01]|5[0137]|6[0158]|78|8[1568]|9[14])|3(?:26|4[13]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|3[15]|5[12]|6[0-26-9]|7[014-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|[578]1|9[15])|6(?:12|[2-47]1|5[17]|6[13]|80)|7(?:12|2[14]|3[134]|4[47]|5[15]|[67]1)|8(?:16|2[014]|3[126]|6[136]|7[078]|8[34]|91))[2-7]\\d{6}|(?:1(?:2[35-8]|3[346-9]|4[236-9]|[59][0235-9]|6[235-9]|7[34689]|8[257-9])|2(?:1[134689]|3[24-8]|4[2-8]|5[25689]|6[2-4679]|7[3-79]|8[2-479]|9[235-9])|3(?:01|1[79]|2[1245]|4[5-8]|5[125689]|6[235-7]|7[157-9]|8[2-46-8])|4(?:1[14578]|2[5689]|3[2-467]|5[4-7]|6[35]|73|8[2689]|9[2389])|5(?:[16][146-9]|2[14-8]|3[1346]|4[14-69]|5[46]|7[2-4]|8[2-8]|9[246])|6(?:1[1358]|2[2457]|3[2-4]|4[235-7]|5[2-689]|6[24578]|7[235689]|8[14-6])|7(?:1[013-9]|2[0235-9]|3[2679]|4[1-35689]|5[2-46-9]|[67][02-9]|8[013-7]|90)|8(?:1[1357-9]|2[235-8]|3[03-57-9]|4[0-24-9]|5\\d|6[2457-9]|7[1-6]|8[1256]|9[2-4]))\\d[2-7]\\d{5}",
      ,
      ,
      ,
      "7410410123",
      ,
      ,
      [10],
      [6, 7, 8]
    ], [
      ,
      ,
      "(?:6(?:1279|828[01489])|7(?:887[02-9]|9313)|8(?:079[04-9]|(?:84|91)7[02-8]))\\d{5}|(?:160[01]|6(?:(?:12|[2-4]1|5[17]|6[13]|80)[0189]|7(?:1[0189]|86))|7(?:1(?:2[0189]|9[0-5])|3(?:2[5-8]|[34][017-9]|9[016-9])|5(?:[15][017-9]|2[04-9]|9[7-9])|6(?:0[0-47]|1[0-257-9]|2[0-4]|3[19]|5[4589])|70[0289]|88[089])|8(?:0(?:6[67]|7[02-8])|70[017-9]|84[01489]|91[0-289]))\\d{6}|(?:731|8(?:16|2[014]|3[126]|6[136]|7[78]|83))(?:[0189]\\d|7[02-8])\\d{5}|(?:6(?:(?:1[1358]|2[2457]|3[2-4]|4[235-7]|5[2-689]|6[24578])\\d|7(?:[23569]\\d|4[0189]|8[0-57-9])|8(?:[14-6]\\d|2[0-79]))|7(?:1(?:[013-8]\\d|9[6-9])|3(?:2[0-49]|9[2-5])|5(?:2[1-3]|9[0-6])|6(?:0[5689]|2[5-9]|3[02-8]|4\\d|5[0-367])|70[13-7]|881))[0189]\\d{5}|(?:6(?:[09]\\d|1[04679]|2[03689]|3[05-9]|4[0489]|50|6[069]|7[07]|8[7-9])|7(?:[024]\\d|3[05-8]|5[0346-8]|6[6-9]|7[1-9]|8[0-79]|9[07-9])|8(?:0[01589]|1[0-57-9]|2[235-9]|3[03-57-9]|[45]\\d|6[02457-9]|7[1-69]|8[0-25-9]|9[02-9])|9\\d\\d)\\d{7}",
      ,
      ,
      ,
      "8123456789",
      ,
      ,
      [10]
    ], [, , "000800\\d{7}|180(?:0\\d{4,9}|3\\d{9})", , , , "1800123456"], [, , "186[12]\\d{9}", , , , "1861123456789", , , [13]], [, , "1860\\d{7}", , , , "18603451234", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "IN", 91, "00", "0", , , "0", , , , [[, "(\\d{7})", "$1", ["575"]], [, "(\\d{8})", "$1", ["5(?:0|2[23]|3[03]|[67]1|88)", "5(?:0|2(?:21|3)|3(?:0|3[23])|616|717|888)", "5(?:0|2(?:21|3)|3(?:0|3[23])|616|717|8888)"], , , 1], [, "(\\d{4})(\\d{4,5})", "$1 $2", ["180", "1800"], , , 1], [
      ,
      "(\\d{3})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["140"],
      ,
      ,
      1
    ], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["11|2[02]|33|4[04]|79[1-6]|80[2-46]", "11|2[02]|33|4[04]|79[1-6]|80(?:[2-4]|6[0-589])", "11|2[02]|33|4[04]|79(?:[124-6]|3(?:[02-9]|1[0-24-9]))|80(?:[2-4]|6[0-589])"], "0$1", , 1], [
      ,
      "(\\d{3})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      [
        "1(?:2[0-249]|3[0-25]|4[145]|[68]|7[1257])|2(?:1[257]|3[013]|4[01]|5[0137]|6[0158]|78|8[1568])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|5[12]|[78]1)|6(?:12|[2-4]1|5[17]|6[13]|80)|7(?:12|3[134]|61|88)|8(?:16|2[014]|3[126]|6[136]|7[078]|8[34]|91)|(?:43|59|75)[15]|(?:1[59]|29|67)[14]",
        "1(?:2[0-24]|3[0-25]|4[145]|[59][14]|6[1-9]|7[1257]|8[1-57-9])|2(?:1[257]|3[013]|4[01]|5[0137]|6[058]|78|8[1568]|9[14])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|3[15]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|[578]1|9[15])|674|7(?:(?:3[34]|5[15])[2-6]|61[346]|88[0-8])|8(?:70[2-6]|84[235-7]|91[3-7])|(?:1(?:29|60|8[06])|261|552|6(?:12|[2-47]1|5[17]|6[13]|80)|7(?:12|31)|8(?:16|2[014]|3[126]|6[136]|7[78]|83))[2-7]",
        "1(?:2[0-24]|3[0-25]|4[145]|[59][14]|6[1-9]|7[1257]|8[1-57-9])|2(?:1[257]|3[013]|4[01]|5[0137]|6[058]|78|8[1568]|9[14])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|3[15]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|[578]1|9[15])|6(?:12(?:[2-6]|7[0-8])|74[2-7])|7(?:3171|5[15][2-6]|61[346]|88(?:[2-7]|82))|8(?:70[2-6]|84(?:[2356]|7[19])|91(?:[3-6]|7[19]))|73[134][2-6]|8(?:16|2[014]|3[126]|6[136]|7[78]|83)(?:[2-6]|7[19])|(?:1(?:29|60|8[06])|261|552|6(?:[2-4]1|5[17]|6[13]|7(?:1|4[0189])|80)|7(?:12|88[01]))[2-7]"
      ],
      "0$1",
      ,
      1
    ], [
      ,
      "(\\d{4})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["1(?:[2-479]|5[0235-9])|[2-5]|6(?:1[1358]|2[2457-9]|3[2-5]|4[235-7]|5[2-689]|6[24578]|7[235689]|8[1-6])|7(?:1[013-9]|3[129]|5[29]|6[02-5]|70)|807", "1(?:[2-479]|5[0235-9])|[2-5]|6(?:1[1358]|2(?:[2457]|84|95)|3(?:[2-4]|55)|4[235-7]|5[2-689]|6[24578]|7(?:[23569]|8[0-57-9])|8[1-6])|7(?:1(?:[013-8]|9[6-9])|3(?:17|2[0-49]|9[2-57])|5(?:2[1-3]|9[0-6])|6(?:0[5689]|2[5-9]|3[02-8]|4|5[0-367])|70[13-7])|807[19]", "1(?:[2-479]|5(?:[0236-9]|5[013-9]))|[2-5]|6(?:2(?:84|95)|355|8(?:28[235-7]|3))|73179|807(?:1|9[1-3])|(?:1552|6(?:(?:1[1358]|2[2457]|3[2-4]|4[235-7]|5[2-689]|6[24578])\\d|7(?:[23569]\\d|8[0-57-9])|8(?:[14-6]\\d|2[0-79]))|7(?:1(?:[013-8]\\d|9[6-9])|3(?:2[0-49]|9[2-57])|5(?:2[1-3]|9[0-6])|6(?:0[5689]|2[5-9]|3[02-8]|4\\d|5[0-367])|70[13-7]))[2-7]"],
      "0$1",
      ,
      1
    ], [, "(\\d{5})(\\d{5})", "$1 $2", ["16|[6-9]"], "0$1", , 1], [, "(\\d{4})(\\d{2,4})(\\d{4})", "$1 $2 $3", ["18[06]", "18[06]0"], , , 1], [, "(\\d{3})(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["0"]], [, "(\\d{4})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["18"], , , 1]], [
      [, "(\\d{8})", "$1", ["5(?:0|2[23]|3[03]|[67]1|88)", "5(?:0|2(?:21|3)|3(?:0|3[23])|616|717|888)", "5(?:0|2(?:21|3)|3(?:0|3[23])|616|717|8888)"], , , 1],
      [, "(\\d{4})(\\d{4,5})", "$1 $2", ["180", "1800"], , , 1],
      [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["140"], , , 1],
      [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["11|2[02]|33|4[04]|79[1-6]|80[2-46]", "11|2[02]|33|4[04]|79[1-6]|80(?:[2-4]|6[0-589])", "11|2[02]|33|4[04]|79(?:[124-6]|3(?:[02-9]|1[0-24-9]))|80(?:[2-4]|6[0-589])"], "0$1", , 1],
      [
        ,
        "(\\d{3})(\\d{3})(\\d{4})",
        "$1 $2 $3",
        [
          "1(?:2[0-249]|3[0-25]|4[145]|[68]|7[1257])|2(?:1[257]|3[013]|4[01]|5[0137]|6[0158]|78|8[1568])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|5[12]|[78]1)|6(?:12|[2-4]1|5[17]|6[13]|80)|7(?:12|3[134]|61|88)|8(?:16|2[014]|3[126]|6[136]|7[078]|8[34]|91)|(?:43|59|75)[15]|(?:1[59]|29|67)[14]",
          "1(?:2[0-24]|3[0-25]|4[145]|[59][14]|6[1-9]|7[1257]|8[1-57-9])|2(?:1[257]|3[013]|4[01]|5[0137]|6[058]|78|8[1568]|9[14])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|3[15]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|[578]1|9[15])|674|7(?:(?:3[34]|5[15])[2-6]|61[346]|88[0-8])|8(?:70[2-6]|84[235-7]|91[3-7])|(?:1(?:29|60|8[06])|261|552|6(?:12|[2-47]1|5[17]|6[13]|80)|7(?:12|31)|8(?:16|2[014]|3[126]|6[136]|7[78]|83))[2-7]",
          "1(?:2[0-24]|3[0-25]|4[145]|[59][14]|6[1-9]|7[1257]|8[1-57-9])|2(?:1[257]|3[013]|4[01]|5[0137]|6[058]|78|8[1568]|9[14])|3(?:26|4[1-3]|5[34]|6[01489]|7[02-46]|8[159])|4(?:1[36]|2[1-47]|3[15]|5[12]|6[0-26-9]|7[0-24-9]|8[013-57]|9[014-7])|5(?:1[025]|22|[36][25]|4[28]|[578]1|9[15])|6(?:12(?:[2-6]|7[0-8])|74[2-7])|7(?:3171|5[15][2-6]|61[346]|88(?:[2-7]|82))|8(?:70[2-6]|84(?:[2356]|7[19])|91(?:[3-6]|7[19]))|73[134][2-6]|8(?:16|2[014]|3[126]|6[136]|7[78]|83)(?:[2-6]|7[19])|(?:1(?:29|60|8[06])|261|552|6(?:[2-4]1|5[17]|6[13]|7(?:1|4[0189])|80)|7(?:12|88[01]))[2-7]"
        ],
        "0$1",
        ,
        1
      ],
      [
        ,
        "(\\d{4})(\\d{3})(\\d{3})",
        "$1 $2 $3",
        ["1(?:[2-479]|5[0235-9])|[2-5]|6(?:1[1358]|2[2457-9]|3[2-5]|4[235-7]|5[2-689]|6[24578]|7[235689]|8[1-6])|7(?:1[013-9]|3[129]|5[29]|6[02-5]|70)|807", "1(?:[2-479]|5[0235-9])|[2-5]|6(?:1[1358]|2(?:[2457]|84|95)|3(?:[2-4]|55)|4[235-7]|5[2-689]|6[24578]|7(?:[23569]|8[0-57-9])|8[1-6])|7(?:1(?:[013-8]|9[6-9])|3(?:17|2[0-49]|9[2-57])|5(?:2[1-3]|9[0-6])|6(?:0[5689]|2[5-9]|3[02-8]|4|5[0-367])|70[13-7])|807[19]", "1(?:[2-479]|5(?:[0236-9]|5[013-9]))|[2-5]|6(?:2(?:84|95)|355|8(?:28[235-7]|3))|73179|807(?:1|9[1-3])|(?:1552|6(?:(?:1[1358]|2[2457]|3[2-4]|4[235-7]|5[2-689]|6[24578])\\d|7(?:[23569]\\d|8[0-57-9])|8(?:[14-6]\\d|2[0-79]))|7(?:1(?:[013-8]\\d|9[6-9])|3(?:2[0-49]|9[2-57])|5(?:2[1-3]|9[0-6])|6(?:0[5689]|2[5-9]|3[02-8]|4\\d|5[0-367])|70[13-7]))[2-7]"],
        "0$1",
        ,
        1
      ],
      [, "(\\d{5})(\\d{5})", "$1 $2", ["16|[6-9]"], "0$1", , 1],
      [, "(\\d{4})(\\d{2,4})(\\d{4})", "$1 $2 $3", ["18[06]", "18[06]0"], , , 1],
      [, "(\\d{4})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["18"], , , 1]
    ], [, , , , , , , , , [-1]], , , [, , "1800\\d{4,9}|(?:000800|18(?:03\\d\\d|6(?:0|[12]\\d\\d)))\\d{7}"], [, , "140\\d{7}", , , , "1409305260", , , [10]], , , [, , , , , , , , , [-1]]],
    IO: [
      ,
      [, , "3\\d{6}", , , , , , , [7]],
      [, , "37\\d{5}", , , , "3709100"],
      [, , "38\\d{5}", , , , "3801234"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "IO",
      246,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{4})", "$1 $2", ["3"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    IQ: [, [, , "(?:1|7\\d\\d)\\d{7}|[2-6]\\d{7,8}", , , , , , , [8, 9, 10], [6, 7]], [, , "1\\d{7}|(?:2[13-5]|3[02367]|4[023]|5[03]|6[026])\\d{6,7}", , , , "12345678", , , [8, 9], [6, 7]], [, , "7[3-9]\\d{8}", , , , "7912345678", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "IQ", 964, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["1"], "0$1"], [
      ,
      "(\\d{2})(\\d{3})(\\d{3,4})",
      "$1 $2 $3",
      ["[2-6]"],
      "0$1"
    ], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["7"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    IR: [, [, , "[1-9]\\d{9}|(?:[1-8]\\d\\d|9)\\d{3,4}", , , , , , , [4, 5, 6, 7, 10], [8]], [, , "(?:1[137]|2[13-68]|3[1458]|4[145]|5[1468]|6[16]|7[1467]|8[13467])(?:[03-57]\\d{7}|[16]\\d{3}(?:\\d{4})?|[289]\\d{3}(?:\\d(?:\\d{3})?)?)|94(?:000[09]|(?:12\\d|30[0-2])\\d|2(?:[02689]0\\d|121)|4(?:111|40\\d))\\d{4}", , , , "2123456789", , , [6, 7, 10], [4, 5, 8]], [
      ,
      ,
      "9(?:(?:0[0-5]|[13]\\d|2[0-3])\\d\\d|9(?:[0-46]\\d\\d|5(?:10|5\\d)|8(?:[12]\\d|3[0-2]|88)|9(?:[01359]\\d|21|69|77|8[7-9])))\\d{5}",
      ,
      ,
      ,
      "9123456789",
      ,
      ,
      [10]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "IR", 98, "00", "0", , , "0", , , , [[, "(\\d{4,5})", "$1", ["96"], "0$1"], [, "(\\d{2})(\\d{4,5})", "$1 $2", ["(?:1[137]|2[13-68]|3[1458]|4[145]|5[1468]|6[16]|7[1467]|8[13467])[12689]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["9"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["[1-8]"], "0$1"]], , [, , , , , , , , , [-1]], , , [
      ,
      ,
      "9(?:4440\\d{5}|6(?:0[12]|2[16-8]|3(?:08|[14]5|[23]|66)|4(?:0|80)|5[01]|6[89]|86|9[19]))",
      ,
      ,
      ,
      ,
      ,
      ,
      [4, 5, 10]
    ], [, , "96(?:0[12]|2[16-8]|3(?:08|[14]5|[23]|66)|4(?:0|80)|5[01]|6[89]|86|9[19])", , , , "9601", , , [4, 5]], , , [, , , , , , , , , [-1]]],
    IS: [, [, , "(?:38\\d|[4-9])\\d{6}", , , , , , , [7, 9]], [, , "(?:4(?:1[0-24-69]|2[0-7]|[37][0-8]|4[0-24589]|5[0-68]|6\\d|8[0-36-8])|5(?:05|[156]\\d|2[02578]|3[0-579]|4[03-7]|7[0-2578]|8[0-35-9]|9[013-689])|872)\\d{4}", , , , "4101234", , , [7]], [
      ,
      ,
      "(?:38[589]\\d\\d|6(?:1[1-8]|2[0-6]|3[026-9]|4[014679]|5[0159]|6[0-69]|70|8[06-8]|9\\d)|7(?:5[057]|[6-9]\\d)|8(?:2[0-59]|[3-69]\\d|8[238]))\\d{4}",
      ,
      ,
      ,
      "6111234"
    ], [, , "80[0-8]\\d{4}", , , , "8001234", , , [7]], [, , "90(?:0\\d|1[5-79]|2[015-79]|3[135-79]|4[125-7]|5[25-79]|7[1-37]|8[0-35-7])\\d{3}", , , , "9001234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "49[0-24-79]\\d{4}", , , , "4921234", , , [7]], "IS", 354, "00|1(?:0(?:01|[12]0)|100)", , , , , , "00", , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[4-9]"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["3"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "809\\d{4}", , , , "8091234", , , [7]], , , [, , "(?:689|8(?:7[18]|80)|95[48])\\d{4}", , , , "6891234", , , [7]]],
    IT: [, [, , "0\\d{5,11}|1\\d{8,10}|3(?:[0-8]\\d{7,10}|9\\d{7,8})|(?:43|55|70)\\d{8}|8\\d{5}(?:\\d{2,4})?", , , , , , , [6, 7, 8, 9, 10, 11, 12]], [
      ,
      ,
      "0(?:669[0-79]\\d{1,6}|831\\d{2,8})|0(?:1(?:[0159]\\d|[27][1-5]|31|4[1-4]|6[1356]|8[2-57])|2\\d\\d|3(?:[0159]\\d|2[1-4]|3[12]|[48][1-6]|6[2-59]|7[1-7])|4(?:[0159]\\d|[23][1-9]|4[245]|6[1-5]|7[1-4]|81)|5(?:[0159]\\d|2[1-5]|3[2-6]|4[1-79]|6[4-6]|7[1-578]|8[3-8])|6(?:[0-57-9]\\d|6[0-8])|7(?:[0159]\\d|2[12]|3[1-7]|4[2-46]|6[13569]|7[13-6]|8[1-59])|8(?:[0159]\\d|2[3-578]|3[2356]|[6-8][1-5])|9(?:[0159]\\d|[238][1-5]|4[12]|6[1-8]|7[1-6]))\\d{2,7}",
      ,
      ,
      ,
      "0212345678"
    ], [, , "3[2-9]\\d{7,8}|(?:31|43)\\d{8}", , , , "3123456789", , , [9, 10]], [, , "80(?:0\\d{3}|3)\\d{3}", , , , "800123456", , , [6, 9]], [, , "(?:0878\\d{3}|89(?:2\\d|3[04]|4(?:[0-4]|[5-9]\\d\\d)|5[0-4]))\\d\\d|(?:1(?:44|6[346])|89(?:38|5[5-9]|9))\\d{6}", , , , "899123456", , , [6, 8, 9, 10]], [, , "84(?:[08]\\d{3}|[17])\\d{3}", , , , "848123456", , , [6, 9]], [, , "1(?:78\\d|99)\\d{6}", , , , "1781234567", , , [9, 10]], [, , "55\\d{8}", , , , "5512345678", , , [10]], "IT", 39, "00", , , , , , , , [
      [, "(\\d{4,5})", "$1", ["1(?:0|9[246])", "1(?:0|9(?:2[2-9]|[46]))"]],
      [, "(\\d{6})", "$1", ["1(?:1|92)"]],
      [, "(\\d{2})(\\d{4,6})", "$1 $2", ["0[26]"]],
      [, "(\\d{3})(\\d{3,6})", "$1 $2", ["0[13-57-9][0159]|8(?:03|4[17]|9[2-5])", "0[13-57-9][0159]|8(?:03|4[17]|9(?:2|3[04]|[45][0-4]))"]],
      [, "(\\d{4})(\\d{2,6})", "$1 $2", ["0(?:[13-579][2-46-8]|8[236-8])"]],
      [, "(\\d{4})(\\d{4})", "$1 $2", ["894"]],
      [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["0[26]|5"]],
      [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["1(?:44|[679])|[378]|43"]],
      [, "(\\d{3})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["0[13-57-9][0159]|14"]],
      [, "(\\d{2})(\\d{4})(\\d{5})", "$1 $2 $3", ["0[26]"]],
      [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["0"]],
      [, "(\\d{3})(\\d{4})(\\d{4,5})", "$1 $2 $3", ["[03]"]]
    ], [[, "(\\d{2})(\\d{4,6})", "$1 $2", ["0[26]"]], [, "(\\d{3})(\\d{3,6})", "$1 $2", ["0[13-57-9][0159]|8(?:03|4[17]|9[2-5])", "0[13-57-9][0159]|8(?:03|4[17]|9(?:2|3[04]|[45][0-4]))"]], [, "(\\d{4})(\\d{2,6})", "$1 $2", ["0(?:[13-579][2-46-8]|8[236-8])"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["894"]], [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["0[26]|5"]], [
      ,
      "(\\d{3})(\\d{3})(\\d{3,4})",
      "$1 $2 $3",
      ["1(?:44|[679])|[378]|43"]
    ], [, "(\\d{3})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["0[13-57-9][0159]|14"]], [, "(\\d{2})(\\d{4})(\\d{5})", "$1 $2 $3", ["0[26]"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["0"]], [, "(\\d{3})(\\d{4})(\\d{4,5})", "$1 $2 $3", ["[03]"]]], [, , , , , , , , , [-1]], 1, , [, , "848\\d{6}", , , , , , , [9]], [, , , , , , , , , [-1]], , , [, , "3[2-8]\\d{9,10}", , , , "33101234501", , , [11, 12]]],
    JE: [, [, , "1534\\d{6}|(?:[3578]\\d|90)\\d{8}", , , , , , , [10], [6]], [, , "1534[0-24-8]\\d{5}", , , , "1534456789", , , , [6]], [
      ,
      ,
      "7(?:(?:(?:50|82)9|937)\\d|7(?:00[378]|97\\d))\\d{5}",
      ,
      ,
      ,
      "7797712345"
    ], [, , "80(?:07(?:35|81)|8901)\\d{4}", , , , "8007354567"], [, , "(?:8(?:4(?:4(?:4(?:05|42|69)|703)|5(?:041|800))|7(?:0002|1206))|90(?:066[59]|1810|71(?:07|55)))\\d{4}", , , , "9018105678"], [, , , , , , , , , [-1]], [, , "701511\\d{4}", , , , "7015115678"], [, , "56\\d{8}", , , , "5612345678"], "JE", 44, "00", "0", , , "([0-24-8]\\d{5})$|0|180020", "1534$1", , , , , [, , "76(?:464|652)\\d{5}|76(?:0[0-28]|2[356]|34|4[01347]|5[49]|6[0-369]|77|8[14]|9[139])\\d{6}", , , , "7640123456"], , , [, , , , , , , , , [-1]], [
      ,
      ,
      "(?:3(?:0(?:07(?:35|81)|8901)|3\\d{4}|4(?:4(?:4(?:05|42|69)|703)|5(?:041|800))|7(?:0002|1206))|55\\d{4})\\d{4}",
      ,
      ,
      ,
      "5512345678"
    ], , , [, , , , , , , , , [-1]]],
    JM: [, [, , "(?:[58]\\d\\d|658|900)\\d{7}", , , , , , , [10], [7]], [, , "8766060\\d{3}|(?:658(?:2(?:[5-8]\\d|9[0-46-9])|[3-9]\\d\\d)|876(?:52[35]|6(?:0[1-3579]|1[0235-9]|[23]\\d|40|5[06]|6[2-589]|7[0-25-9]|8[04]|9[4-9])|7(?:0[2-689]|[1-6]\\d|8[056]|9[45])|9(?:0[1-8]|1[02378]|[2-8]\\d|9[2-468])))\\d{4}", , , , "8765230123", , , , [7]], [
      ,
      ,
      "(?:6582(?:[0-4]\\d|95)|876(?:2(?:0[1-9]|[13-9]\\d|2[013-9])|[348]\\d\\d|5(?:0[1-9]|[1-9]\\d)|6(?:4[89]|6[67])|7(?:0[07]|7\\d|8[1-47-9]|9[0-36-9])|9(?:[01]9|9[0579])))\\d{4}",
      ,
      ,
      ,
      "8762101234",
      ,
      ,
      ,
      [7]
    ], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "JM", 1, "011", "1", , , "1", , , , , , [, , , , , , , , , [-1]], , "658|876", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ]],
    JO: [, [, , "(?:(?:[2689]|7\\d)\\d|32|427|53)\\d{6}", , , , , , , [8, 9]], [
      ,
      ,
      "87(?:000|90[01])\\d{3}|(?:2(?:6(?:2[0-35-9]|3[0-578]|4[24-7]|5[0-24-8]|[6-8][023]|9[0-3])|7(?:0[1-79]|10|2[014-7]|3[0-689]|4[019]|5[0-3578]))|32(?:0[1-69]|1[1-35-7]|2[024-7]|3\\d|4[0-3]|[5-7][023])|53(?:0[0-3]|[13][023]|2[0-59]|49|5[0-35-9]|6[15]|7[45]|8[1-6]|9[0-36-9])|6(?:2(?:[05]0|22)|3(?:00|33)|4(?:0[0-25]|1[2-7]|2[0569]|[38][07-9]|4[025689]|6[0-589]|7\\d|9[0-2])|5(?:[01][056]|2[034]|3[0-57-9]|4[178]|5[0-69]|6[0-35-9]|7[1-379]|8[0-68]|9[0239]))|87(?:20|7[078]|99))\\d{4}",
      ,
      ,
      ,
      "62001234",
      ,
      ,
      [8]
    ], [, , "(?:427|7(?:11|[29]\\d|[78][0-25-9]))\\d{6}", , , , "790123456", , , [9]], [, , "80\\d{6}", , , , "80012345", , , [8]], [, , "9\\d{7}", , , , "90012345", , , [8]], [, , "85\\d{6}", , , , "85012345", , , [8]], [, , "70\\d{7}", , , , "700123456", , , [9]], [, , , , , , , , , [-1]], "JO", 962, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["[2356]|87"], "(0$1)"], [, "(\\d{3})(\\d{5,6})", "$1 $2", ["[89]"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["70"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["[47]"], "0$1"]], , [
      ,
      ,
      "74(?:66|77)\\d{5}",
      ,
      ,
      ,
      "746612345",
      ,
      ,
      [9]
    ], , , [, , , , , , , , , [-1]], [, , "8(?:10|8\\d)\\d{5}", , , , "88101234", , , [8]], , , [, , , , , , , , , [-1]]],
    JP: [
      ,
      [, , "00[1-9]\\d{6,14}|[25-9]\\d{9}|(?:00|[1-9]\\d\\d)\\d{6}", , , , , , , [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]],
      [, , "(?:1(?:1[235-8]|2[3-6]|3[3-9]|4[2-6]|[58][2-8]|6[2-7]|7[2-9]|9[1-9])|(?:2[2-9]|[36][1-9])\\d|4(?:[2-578]\\d|6[02-8]|9[2-59])|5(?:[2-589]\\d|6[1-9]|7[2-8])|7(?:[25-9]\\d|3[4-9]|4[02-9])|8(?:[2679]\\d|3[2-9]|4[5-9]|5[1-9]|8[03-9])|9(?:[2-58]\\d|[679][1-9]))\\d{6}", , , , "312345678", , , [9]],
      [
        ,
        ,
        "[6-9]0[1-9]\\d{7}",
        ,
        ,
        ,
        "9012345678",
        ,
        ,
        [10]
      ],
      [, , "00777(?:[01]|5\\d)\\d\\d|(?:00(?:7778|882[1245])|(?:120|800\\d)\\d\\d)\\d{4}|00(?:37|66|78)\\d{6,13}", , , , "120123456"],
      [, , "990\\d{6}", , , , "990123456", , , [9]],
      [, , , , , , , , , [-1]],
      [, , "60\\d{7}", , , , "601234567", , , [9]],
      [, , "50[1-9]\\d{7}", , , , "5012345678", , , [10]],
      "JP",
      81,
      "010",
      "0",
      ,
      ,
      "(000[2569]\\d{4,6})$|(?:(?:003768)0?)|0",
      "$1",
      ,
      ,
      [[, "(\\d{4})(\\d{4})", "$1-$2", ["007", "0077", "00777", "00777[01]"]], [, "(\\d{8,10})", "$1", ["000"]], [
        ,
        "(\\d{3})(\\d{3})(\\d{3})",
        "$1-$2-$3",
        ["(?:12|57|99)0"],
        "0$1"
      ], [, "(\\d{4})(\\d)(\\d{4})", "$1-$2-$3", ["1(?:26|3[79]|4[56]|5[4-68]|6[3-5])|499|5(?:76|97)|746|8(?:3[89]|47|51)|9(?:80|9[16])", "1(?:267|3(?:7[247]|9[278])|466|5(?:47|58|64)|6(?:3[245]|48|5[4-68]))|499[2468]|5(?:76|97)9|7468|8(?:3(?:8[7-9]|96)|477|51[2-9])|9(?:802|9(?:1[23]|69))|1(?:45|58)[67]", "1(?:267|3(?:7[247]|9[278])|466|5(?:47|58|64)|6(?:3[245]|48|5[4-68]))|499[2468]|5(?:769|979[2-69])|7468|8(?:3(?:8[7-9]|96[2457-9])|477|51[2-9])|9(?:802|9(?:1[23]|69))|1(?:45|58)[67]"], "0$1"], [
        ,
        "(\\d{2})(\\d{3})(\\d{4})",
        "$1-$2-$3",
        ["60"],
        "0$1"
      ], [, "(\\d)(\\d{4})(\\d{4})", "$1-$2-$3", ["3|4(?:2[09]|7[01])|6[1-9]", "3|4(?:2(?:0|9[02-69])|7(?:0[019]|1))|6[1-9]"], "0$1"], [
        ,
        "(\\d{2})(\\d{3})(\\d{4})",
        "$1-$2-$3",
        [
          "1(?:1|5[45]|77|88|9[69])|2(?:2[1-37]|3[0-269]|4[59]|5|6[24]|7[1-358]|8[1369]|9[0-38])|4(?:[28][1-9]|3[0-57]|[45]|6[248]|7[2-579]|9[29])|5(?:2|3[0459]|4[0-369]|5[29]|8[02389]|9[0-389])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9[2-6])|8(?:2[124589]|3[26-9]|49|51|6|7[0-468]|8[68]|9[019])|9(?:[23][1-9]|4[15]|5[138]|6[1-3]|7[156]|8[189]|9[1-489])",
          "1(?:1|5(?:4[018]|5[017])|77|88|9[69])|2(?:2(?:[127]|3[014-9])|3[0-269]|4[59]|5(?:[1-3]|5[0-69]|9[19])|62|7(?:[1-35]|8[0189])|8(?:[16]|3[0134]|9[0-5])|9(?:[028]|17))|4(?:2(?:[13-79]|8[014-6])|3[0-57]|[45]|6[248]|7[2-47]|8[1-9]|9[29])|5(?:2|3(?:[045]|9[0-8])|4[0-369]|5[29]|8[02389]|9[0-3])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9(?:[23]|4[0-59]|5[01569]|6[0167]))|8(?:2(?:[1258]|4[0-39]|9[0-2469])|3(?:[29]|60)|49|51|6(?:[0-24]|36|5[0-3589]|7[23]|9[01459])|7[0-468]|8[68])|9(?:[23][1-9]|4[15]|5[138]|6[1-3]|7[156]|8[189]|9(?:[1289]|3[34]|4[0178]))|(?:264|837)[016-9]|2(?:57|93)[015-9]|(?:25[0468]|422|838)[01]|(?:47[59]|59[89]|8(?:6[68]|9))[019]",
          "1(?:1|5(?:4[018]|5[017])|77|88|9[69])|2(?:2[127]|3[0-269]|4[59]|5(?:[1-3]|5[0-69]|9(?:17|99))|6(?:2|4[016-9])|7(?:[1-35]|8[0189])|8(?:[16]|3[0134]|9[0-5])|9(?:[028]|17))|4(?:2(?:[13-79]|8[014-6])|3[0-57]|[45]|6[248]|7[2-47]|9[29])|5(?:2|3(?:[045]|9(?:[0-58]|6[4-9]|7[0-35689]))|4[0-369]|5[29]|8[02389]|9[0-3])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9(?:[23]|4[0-59]|5[01569]|6[0167]))|8(?:2(?:[1258]|4[0-39]|9[0169])|3(?:[29]|60|7(?:[017-9]|6[6-8]))|49|51|6(?:[0-24]|36[2-57-9]|5(?:[0-389]|5[23])|6(?:[01]|9[178])|7(?:2[2-468]|3[78])|9[0145])|7[0-468]|8[68])|9(?:4[15]|5[138]|7[156]|8[189]|9(?:[1289]|3(?:31|4[357])|4[0178]))|(?:8294|96)[1-3]|2(?:57|93)[015-9]|(?:223|8699)[014-9]|(?:25[0468]|422|838)[01]|(?:48|8292|9[23])[1-9]|(?:47[59]|59[89]|8(?:68|9))[019]"
        ],
        "0$1"
      ], [, "(\\d{3})(\\d{2})(\\d{4})", "$1-$2-$3", ["[14]|[289][2-9]|5[3-9]|7[2-4679]"], "0$1"], [, "(\\d{4})(\\d{2})(\\d{3,4})", "$1-$2-$3", ["007", "0077"]], [, "(\\d{4})(\\d{2})(\\d{4})", "$1-$2-$3", ["008"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["800"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1-$2-$3", ["[25-9]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3,4})", "$1-$2-$3", ["0"]], [, "(\\d{4})(\\d{4})(\\d{4,5})", "$1-$2-$3", ["0"]], [, "(\\d{4})(\\d{5})(\\d{5,6})", "$1-$2-$3", ["0"]], [, "(\\d{4})(\\d{6})(\\d{6,7})", "$1-$2-$3", ["0"]]],
      [[, "(\\d{3})(\\d{3})(\\d{3})", "$1-$2-$3", ["(?:12|57|99)0"], "0$1"], [
        ,
        "(\\d{4})(\\d)(\\d{4})",
        "$1-$2-$3",
        ["1(?:26|3[79]|4[56]|5[4-68]|6[3-5])|499|5(?:76|97)|746|8(?:3[89]|47|51)|9(?:80|9[16])", "1(?:267|3(?:7[247]|9[278])|466|5(?:47|58|64)|6(?:3[245]|48|5[4-68]))|499[2468]|5(?:76|97)9|7468|8(?:3(?:8[7-9]|96)|477|51[2-9])|9(?:802|9(?:1[23]|69))|1(?:45|58)[67]", "1(?:267|3(?:7[247]|9[278])|466|5(?:47|58|64)|6(?:3[245]|48|5[4-68]))|499[2468]|5(?:769|979[2-69])|7468|8(?:3(?:8[7-9]|96[2457-9])|477|51[2-9])|9(?:802|9(?:1[23]|69))|1(?:45|58)[67]"],
        "0$1"
      ], [, "(\\d{2})(\\d{3})(\\d{4})", "$1-$2-$3", ["60"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1-$2-$3", ["3|4(?:2[09]|7[01])|6[1-9]", "3|4(?:2(?:0|9[02-69])|7(?:0[019]|1))|6[1-9]"], "0$1"], [
        ,
        "(\\d{2})(\\d{3})(\\d{4})",
        "$1-$2-$3",
        [
          "1(?:1|5[45]|77|88|9[69])|2(?:2[1-37]|3[0-269]|4[59]|5|6[24]|7[1-358]|8[1369]|9[0-38])|4(?:[28][1-9]|3[0-57]|[45]|6[248]|7[2-579]|9[29])|5(?:2|3[0459]|4[0-369]|5[29]|8[02389]|9[0-389])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9[2-6])|8(?:2[124589]|3[26-9]|49|51|6|7[0-468]|8[68]|9[019])|9(?:[23][1-9]|4[15]|5[138]|6[1-3]|7[156]|8[189]|9[1-489])",
          "1(?:1|5(?:4[018]|5[017])|77|88|9[69])|2(?:2(?:[127]|3[014-9])|3[0-269]|4[59]|5(?:[1-3]|5[0-69]|9[19])|62|7(?:[1-35]|8[0189])|8(?:[16]|3[0134]|9[0-5])|9(?:[028]|17))|4(?:2(?:[13-79]|8[014-6])|3[0-57]|[45]|6[248]|7[2-47]|8[1-9]|9[29])|5(?:2|3(?:[045]|9[0-8])|4[0-369]|5[29]|8[02389]|9[0-3])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9(?:[23]|4[0-59]|5[01569]|6[0167]))|8(?:2(?:[1258]|4[0-39]|9[0-2469])|3(?:[29]|60)|49|51|6(?:[0-24]|36|5[0-3589]|7[23]|9[01459])|7[0-468]|8[68])|9(?:[23][1-9]|4[15]|5[138]|6[1-3]|7[156]|8[189]|9(?:[1289]|3[34]|4[0178]))|(?:264|837)[016-9]|2(?:57|93)[015-9]|(?:25[0468]|422|838)[01]|(?:47[59]|59[89]|8(?:6[68]|9))[019]",
          "1(?:1|5(?:4[018]|5[017])|77|88|9[69])|2(?:2[127]|3[0-269]|4[59]|5(?:[1-3]|5[0-69]|9(?:17|99))|6(?:2|4[016-9])|7(?:[1-35]|8[0189])|8(?:[16]|3[0134]|9[0-5])|9(?:[028]|17))|4(?:2(?:[13-79]|8[014-6])|3[0-57]|[45]|6[248]|7[2-47]|9[29])|5(?:2|3(?:[045]|9(?:[0-58]|6[4-9]|7[0-35689]))|4[0-369]|5[29]|8[02389]|9[0-3])|7(?:2[02-46-9]|34|[58]|6[0249]|7[57]|9(?:[23]|4[0-59]|5[01569]|6[0167]))|8(?:2(?:[1258]|4[0-39]|9[0169])|3(?:[29]|60|7(?:[017-9]|6[6-8]))|49|51|6(?:[0-24]|36[2-57-9]|5(?:[0-389]|5[23])|6(?:[01]|9[178])|7(?:2[2-468]|3[78])|9[0145])|7[0-468]|8[68])|9(?:4[15]|5[138]|7[156]|8[189]|9(?:[1289]|3(?:31|4[357])|4[0178]))|(?:8294|96)[1-3]|2(?:57|93)[015-9]|(?:223|8699)[014-9]|(?:25[0468]|422|838)[01]|(?:48|8292|9[23])[1-9]|(?:47[59]|59[89]|8(?:68|9))[019]"
        ],
        "0$1"
      ], [, "(\\d{3})(\\d{2})(\\d{4})", "$1-$2-$3", ["[14]|[289][2-9]|5[3-9]|7[2-4679]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["800"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1-$2-$3", ["[25-9]"], "0$1"]],
      [, , "20\\d{8}", , , , "2012345678", , , [10]],
      ,
      ,
      [, , "00(?:777(?:[01]|(?:5|8\\d)\\d)|882[1245]\\d\\d)\\d\\d|00(?:37|66|78)\\d{6,13}"],
      [, , "570\\d{6}", , , , "570123456", , , [9]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    KE: [, [, , "(?:[17]\\d\\d|900)\\d{6}|(?:2|80)0\\d{6,7}|[4-6]\\d{6,8}", , , , , , , [7, 8, 9, 10]], [
      ,
      ,
      "(?:4[245]|5[1-79]|6[01457-9])\\d{5,7}|(?:4[136]|5[08]|62)\\d{7}|(?:[24]0|66)\\d{6,7}",
      ,
      ,
      ,
      "202012345",
      ,
      ,
      [7, 8, 9]
    ], [, , "(?:1(?:0[0-8]|[18]\\d|2[014]|30|4[0-5])|7\\d\\d)\\d{6}", , , , "712123456", , , [9]], [, , "800[02-8]\\d{5,6}", , , , "800223456", , , [9, 10]], [, , "900[02-9]\\d{5}", , , , "900223456", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "KE", 254, "000", "0", , , "0", , , , [[, "(\\d{2})(\\d{5,7})", "$1 $2", ["[24-6]"], "0$1"], [, "(\\d{3})(\\d{6})", "$1 $2", ["[17]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[89]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KG: [
      ,
      [, , "8\\d{9}|[235-9]\\d{8}", , , , , , , [9, 10], [5, 6]],
      [, , "312(?:5[0-79]\\d|9(?:[0-689]\\d|7[0-24-9]))\\d{3}|(?:3(?:1(?:2[0-46-8]|3[1-9]|47|[56]\\d)|2(?:22|3[0-479]|6[0-7])|4(?:22|5[6-9]|6\\d)|5(?:22|3[4-7]|59|6\\d)|6(?:22|5[35-7]|6\\d)|7(?:22|3[468]|4[1-9]|59|[67]\\d)|9(?:22|4[1-8]|6\\d))|6(?:09|12|2[2-4])\\d)\\d{5}", , , , "312123456", , , [9], [5, 6]],
      [, , "312(?:58\\d|973)\\d{3}|(?:2(?:0[0-35]|2\\d)|5[0-24-7]\\d|600|7(?:[07]\\d|55)|88[08]|9(?:12|9[05-9]))\\d{6}", , , , "700123456", , , [9]],
      [, , "800\\d{6,7}", , , , "800123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "KG",
      996,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{4})(\\d{5})", "$1 $2", ["3(?:1[346]|[24-79])"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[235-79]|88"], "0$1"], [, "(\\d{3})(\\d{3})(\\d)(\\d{2,3})", "$1 $2 $3 $4", ["8"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    KH: [
      ,
      [, , "1\\d{9}|[1-9]\\d{7,8}", , , , , , , [8, 9, 10], [6, 7]],
      [
        ,
        ,
        "23(?:4(?:[2-4]|[56]\\d)|[568]\\d\\d)\\d{4}|23[236-9]\\d{5}|(?:2[4-6]|3[2-6]|4[2-4]|[5-7][2-5])(?:(?:[237-9]|4[56]|5\\d)\\d{5}|6\\d{5,6})",
        ,
        ,
        ,
        "23756789",
        ,
        ,
        [8, 9],
        [6, 7]
      ],
      [, , "(?:(?:1[28]|3[18]|9[67])\\d|6[016-9]|7(?:[07-9]|[16]\\d)|8(?:[013-79]|8\\d))\\d{6}|(?:1\\d|9[0-57-9])\\d{6}|(?:2[3-6]|3[2-6]|4[2-4]|[5-7][2-5])48\\d{5}", , , , "91234567", , , [8, 9]],
      [, , "1800(?:1\\d|2[019])\\d{4}", , , , "1800123456", , , [10]],
      [, , "1900(?:1\\d|2[09])\\d{4}", , , , "1900123456", , , [10]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "KH",
      855,
      "00[14-9]",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[1-9]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    KI: [, [, , "(?:[37]\\d|6[0-79])\\d{6}|(?:[2-48]\\d|50)\\d{3}", , , , , , , [5, 8]], [, , "(?:[24]\\d|3[1-9]|50|65(?:02[12]|12[56]|22[89]|[3-5]00)|7(?:27\\d\\d|3100|5(?:02[12]|12[56]|22[89]|[34](?:00|81)|500))|8[0-5])\\d{3}", , , , "31234"], [
      ,
      ,
      "(?:6200[01]|7(?:310[1-9]|5(?:02[03-9]|12[0-47-9]|22[0-7]|[34](?:0[1-9]|8[02-9])|50[1-9])))\\d{3}|(?:63\\d\\d|7(?:(?:[0146-9]\\d|2[0-689])\\d|3(?:[02-9]\\d|1[1-9])|5(?:[0-2][013-9]|[34][1-79]|5[1-9]|[6-9]\\d)))\\d{4}",
      ,
      ,
      ,
      "72001234",
      ,
      ,
      [8]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "30(?:0[01]\\d\\d|12(?:11|20))\\d\\d", , , , "30010000", , , [8]], "KI", 686, "00", "0", , , "0", , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KM: [, [, , "[3478]\\d{6}", , , , , , , [7], [4]], [, , "7[4-7]\\d{5}", , , , "7712345", , , , [4]], [, , "[34]\\d{6}", , , , "3212345"], [, , , , , , , , , [-1]], [, , "8\\d{6}", , , , "8001234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "KM", 269, "00", , , , , , , , [[
      ,
      "(\\d{3})(\\d{2})(\\d{2})",
      "$1 $2 $3",
      ["[3478]"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KN: [, [, , "(?:[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [, , "869(?:2(?:29|36)|302|4(?:6[015-9]|70)|56[5-7])\\d{4}", , , , "8692361234", , , , [7]], [, , "869(?:48[89]|55[6-8]|66\\d|76[02-7])\\d{4}", , , , "8697652917", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "KN", 1, "011", "1", , , "([2-7]\\d{6})$|1", "869$1", , , , , [, , , , , , , , , [-1]], , "869", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KP: [, [, , "85\\d{6}|(?:19\\d|[2-7])\\d{7}", , , , , , , [8, 10], [6, 7]], [, , "(?:(?:195|2)\\d|3[19]|4[159]|5[37]|6[17]|7[39]|85)\\d{6}", , , , "21234567", , , , [6, 7]], [, , "19[1-3]\\d{7}", , , , "1921234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "KP", 850, "00|99", "0", , , "0", , , , [[
      ,
      "(\\d{2})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["8"],
      "0$1"
    ], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["[2-7]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , "238[02-9]\\d{4}|2(?:[0-24-9]\\d|3[0-79])\\d{5}", , , , , , , [8]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KR: [, [, , "00[1-9]\\d{8,11}|(?:[12]|5\\d{3})\\d{7}|[13-6]\\d{9}|(?:[1-6]\\d|80)\\d{7}|[3-6]\\d{4,5}|(?:00|7)0\\d{8}", , , , , , , [5, 6, 8, 9, 10, 11, 12, 13, 14], [3, 4, 7]], [
      ,
      ,
      "(?:2|3[1-3]|[46][1-4]|5[1-5])[1-9]\\d{6,7}|(?:3[1-3]|[46][1-4]|5[1-5])1\\d{2,3}",
      ,
      ,
      ,
      "22123456",
      ,
      ,
      [5, 6, 8, 9, 10],
      [3, 4, 7]
    ], [, , "1(?:05(?:[0-8]\\d|9[0-6])|22[13]\\d)\\d{4,5}|1(?:0[0-46-9]|[16-9]\\d|2[013-9])\\d{6,7}", , , , "1020000000", , , [9, 10]], [, , "00(?:308\\d{6,7}|798\\d{7,9})|(?:00368|[38]0)\\d{7}", , , , "801234567", , , [9, 11, 12, 13, 14]], [, , "60[2-9]\\d{6}", , , , "602345678", , , [9]], [, , , , , , , , , [-1]], [, , "50\\d{8,9}", , , , "5012345678", , , [10, 11]], [, , "70\\d{8}", , , , "7012345678", , , [10]], "KR", 82, "00(?:[125689]|3(?:[46]5|91)|7(?:00|27|3|55|6[126]))", "0", , , "0(8(?:[1-46-8]|5\\d\\d))?", , , , [[
      ,
      "(\\d{5})",
      "$1",
      ["1[016-9]1", "1[016-9]11", "1[016-9]114"],
      "0$1"
    ], [, "(\\d{2})(\\d{3,4})", "$1-$2", ["(?:3[1-3]|[46][1-4]|5[1-5])1"], "0$1", "0$CC-$1"], [, "(\\d{4})(\\d{4})", "$1-$2", ["1"]], [, "(\\d)(\\d{3,4})(\\d{4})", "$1-$2-$3", ["2"], "0$1", "0$CC-$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1-$2-$3", ["[36]0|8"], "0$1", "0$CC-$1"], [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1-$2-$3", ["[1346]|5[1-5]"], "0$1", "0$CC-$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1-$2-$3", ["[57]"], "0$1", "0$CC-$1"], [, "(\\d{5})(\\d{3})(\\d{3})", "$1 $2 $3", ["003", "0030"]], [
      ,
      "(\\d{2})(\\d{5})(\\d{4})",
      "$1-$2-$3",
      ["5"],
      "0$1",
      "0$CC-$1"
    ], [, "(\\d{5})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["0"]], [, "(\\d{5})(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["0"]]], [
      [, "(\\d{2})(\\d{3,4})", "$1-$2", ["(?:3[1-3]|[46][1-4]|5[1-5])1"], "0$1", "0$CC-$1"],
      [, "(\\d{4})(\\d{4})", "$1-$2", ["1"]],
      [, "(\\d)(\\d{3,4})(\\d{4})", "$1-$2-$3", ["2"], "0$1", "0$CC-$1"],
      [, "(\\d{2})(\\d{3})(\\d{4})", "$1-$2-$3", ["[36]0|8"], "0$1", "0$CC-$1"],
      [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1-$2-$3", ["[1346]|5[1-5]"], "0$1", "0$CC-$1"],
      [, "(\\d{2})(\\d{4})(\\d{4})", "$1-$2-$3", ["[57]"], "0$1", "0$CC-$1"],
      [, "(\\d{2})(\\d{5})(\\d{4})", "$1-$2-$3", ["5"], "0$1", "0$CC-$1"]
    ], [, , "15\\d{7,8}", , , , "1523456789", , , [9, 10]], , , [, , "00(?:3(?:08\\d{6,7}|68\\d{7})|798\\d{7,9})", , , , , , , [11, 12, 13, 14]], [, , "1(?:5(?:22|33|44|66|77|88|99)|6(?:[07]0|44|6[0168]|88)|8(?:00|33|55|77|99))\\d{4}", , , , "15441234", , , [8]], , , [, , , , , , , , , [-1]]],
    KW: [, [, , "18\\d{5}|(?:[2569]\\d|41)\\d{6}", , , , , , , [7, 8]], [, , "2(?:[23]\\d\\d|4(?:[1-35-9]\\d|44)|5(?:0[034]|[2-46]\\d|5[1-3]|7[1-7]))\\d{4}", , , , "22345678", , , [8]], [
      ,
      ,
      "(?:41\\d\\d|5(?:(?:[05]\\d|1[0-7]|6[56])\\d|2(?:22|5[25])|7(?:55|77)|88[58])|6(?:(?:0[034679]|5[015-9]|6\\d)\\d|1(?:00|11|6[16])|2[26]2|3[36]3|4[46]4|7(?:0[013-9]|[67]\\d)|8[68]8|9(?:[069]\\d|3[039]))|9(?:(?:[04679]\\d|8[057-9])\\d|1(?:00|1[01]|99)|2(?:00|2\\d)|3(?:00|3[03])|5(?:00|5\\d)))\\d{4}",
      ,
      ,
      ,
      "50012345",
      ,
      ,
      [8]
    ], [, , "18\\d{5}", , , , "1801234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "KW", 965, "00", , , , , , , , [[, "(\\d{4})(\\d{3,4})", "$1 $2", ["[169]|2(?:[235]|4[1-35-9])|52"]], [, "(\\d{3})(\\d{5})", "$1 $2", ["[245]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KY: [, [, , "(?:345|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [
      ,
      ,
      "345(?:2(?:22|3[23]|44|66)|333|444|6(?:23|38|40)|7(?:30|4[35-79]|6[6-9]|77)|8(?:00|1[45]|4[89]|88)|9(?:14|4[035-9]))\\d{4}",
      ,
      ,
      ,
      "3452221234",
      ,
      ,
      ,
      [7]
    ], [, , "345(?:32[1-9]|4(?:1[2-6]|2[0-4])|5(?:1[67]|2[5-79]|4[6-9]|50|76)|649|82[56]|9(?:1[679]|2[2-9]|3[06-9]|90))\\d{4}", , , , "3453231234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"], [, , "(?:345976|900[2-9]\\d\\d)\\d{4}", , , , "9002345678"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "KY", 1, "011", "1", , , "([2-9]\\d{6})$|1", "345$1", , , , , [, , , , , , , , , [-1]], , "345", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    KZ: [, [, , "8\\d{13}|[78]\\d{9}", , , , , , , [10, 14], [5, 6, 7]], [
      ,
      ,
      "7(?:1(?:0(?:[23]\\d|4[0-3]|59|63)|1(?:[23]\\d|4[0-79]|59)|2(?:[23]\\d|59)|3(?:2\\d|3[0-79]|4[0-35-9]|59)|4(?:[24]\\d|3[013-9]|5[1-9]|97)|5(?:2\\d|3[1-9]|4[0-7]|59)|6(?:[2-4]\\d|5[19]|61)|72\\d|8(?:[27]\\d|3[1-46-9]|4[0-5]|59))|2(?:1(?:[23]\\d|4[46-9]|5[3469])|2(?:2\\d|3[0679]|46|5[12679])|3(?:[2-4]\\d|5[139])|4(?:2\\d|3[1-35-9]|59)|5(?:[23]\\d|4[0-8]|59|61)|6(?:2\\d|3[1-9]|4[0-4]|59)|7(?:[2379]\\d|40|5[279])|8(?:[23]\\d|4[0-3]|59)|9(?:2\\d|3[124578]|59)))\\d{5}",
      ,
      ,
      ,
      "7123456789",
      ,
      ,
      [10],
      [5, 6, 7]
    ], [, , "7(?:0[0-25-8]|47|6[0-4]|7[15-8]|85)\\d{7}", , , , "7710009998", , , [10]], [, , "8(?:00|108\\d{3})\\d{7}", , , , "8001234567"], [, , "809\\d{7}", , , , "8091234567", , , [10]], [, , , , , , , , , [-1]], [, , "808\\d{7}", , , , "8081234567", , , [10]], [, , "751\\d{7}", , , , "7511234567", , , [10]], "KZ", 7, "810", "8", , , "8", , "8~10", , , , [, , , , , , , , , [-1]], , "7", [, , "751\\d{7}", , , , , , , [10]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LA: [, [, , "[23]\\d{9}|3\\d{8}|(?:[235-8]\\d|41)\\d{6}", , , , , , , [8, 9, 10], [6]], [
      ,
      ,
      "(?:2[13]|[35-7][14]|41|8[1468])\\d{6}",
      ,
      ,
      ,
      "21212862",
      ,
      ,
      [8],
      [6]
    ], [, , "(?:20(?:[23579]\\d|8[78])|30[24]\\d)\\d{6}|30\\d{7}", , , , "2023123456", , , [9, 10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LA", 856, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["2[13]|3[14]|[4-8]"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["3"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["[23]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LB: [, [
      ,
      ,
      "[27-9]\\d{7}|[13-9]\\d{6}",
      ,
      ,
      ,
      ,
      ,
      ,
      [7, 8]
    ], [, , "7(?:62|8[0-6]|9[04-9])\\d{4}|(?:[14-69]\\d|2(?:[14-69]\\d|[78][1-9])|7[2-57]|8[02-9])\\d{5}", , , , "1123456"], [, , "(?:(?:3|81)\\d|7(?:[01]\\d|6[013-9]|8[7-9]|9[0-4]))\\d{5}", , , , "71123456"], [, , , , , , , , , [-1]], [, , "9[01]\\d{6}", , , , "90123456", , , [8]], [, , "80\\d{6}", , , , "80123456", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LB", 961, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["[13-69]|7(?:[2-57]|62|8[0-6]|9[04-9])|8[02-9]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[27-9]"]]], , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LC: [, [, , "(?:[58]\\d\\d|758|900)\\d{7}", , , , , , , [10], [7]], [, , "758(?:234|4(?:30|5\\d|6[2-9]|8[0-2])|57[0-2]|(?:63|75)8)\\d{4}", , , , "7584305678", , , , [7]], [, , "758(?:28[4-7]|384|4(?:6[01]|8[4-9])|5(?:1[89]|20|84)|7(?:1[2-9]|2\\d|3[0-3])|812)\\d{4}", , , , "7582845678", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "LC", 1, "011", "1", , , "([2-8]\\d{6})$|1", "758$1", , , , , [, , , , , , , , , [-1]], , "758", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LI: [, [, , "[68]\\d{8}|(?:[2378]\\d|90)\\d{5}", , , , , , , [7, 9]], [, , "(?:2(?:01|1[27]|2[024]|3\\d|6[02-578]|96)|3(?:[24]0|33|7[0135-7]|8[048]|9[0269]))\\d{4}", , , , "2345678", , , [7]], [, , "(?:6(?:(?:4[5-9]|5\\d)\\d|6(?:[024-68]\\d|1[01]|3[7-9]|7[02]))\\d|7(?:[37-9]\\d|42|56))\\d{4}", , , , "660234567"], [, , "8002[28]\\d\\d|80(?:05\\d|9)\\d{4}", , , , "8002222"], [
      ,
      ,
      "90(?:02[258]|1(?:23|3[14])|66[136])\\d\\d",
      ,
      ,
      ,
      "9002222",
      ,
      ,
      [7]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LI", 423, "00", "0", , , "(1001)|0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3", ["[2379]|8(?:0[09]|7)", "[2379]|8(?:0(?:02|9)|7)"], , "$CC $1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["8"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["69"], , "$CC $1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["6"], , "$CC $1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "870(?:28|87)\\d\\d", , , , "8702812", , , [7]], , , [, , "697(?:42|56|[78]\\d)\\d{4}", , , , "697861234", , , [9]]],
    LK: [
      ,
      [, , "[1-9]\\d{8}", , , , , , , [9], [7]],
      [, , "(?:12[2-9]|602|8[12]\\d|9(?:1\\d|22|9[245]))\\d{6}|(?:11|2[13-7]|3[1-8]|4[157]|5[12457]|6[35-7])[2-57]\\d{6}", , , , "112345678", , , , [7]],
      [, , "7(?:[0-25-8]\\d|4[0-4])\\d{6}", , , , "712345678"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "LK",
      94,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["7"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[1-689]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "1973\\d{5}", , , , "197312345"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    LR: [, [, , "(?:[2457]\\d|33|88)\\d{7}|(?:2\\d|[4-6])\\d{6}", , , , , , , [7, 8, 9]], [, , "2\\d{7}", , , , "21234567", , , [8]], [, , "(?:(?:(?:22|33)0|555|7(?:6[01]|7\\d)|88\\d)\\d|4(?:240|[67]))\\d{5}|[56]\\d{6}", , , , "770123456", , , [7, 9]], [, , , , , , , , , [-1]], [, , "332(?:02|[34]\\d)\\d{4}", , , , "332021234", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LR", 231, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["4[67]|[56]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["2"], "0$1"], [
      ,
      "(\\d{2})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["[2-578]"],
      "0$1"
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LS: [, [, , "(?:[256]\\d\\d|800)\\d{5}", , , , , , , [8]], [, , "2\\d{7}", , , , "22123456"], [, , "[56]\\d{7}", , , , "50123456"], [, , "800[1256]\\d{4}", , , , "80021234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LS", 266, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[2568]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LT: [
      ,
      [, , "(?:[3469]\\d|52|[78]0)\\d{6}", , , , , , , [8]],
      [
        ,
        ,
        "(?:3[1478]|4[124-6]|52)\\d{6}",
        ,
        ,
        ,
        "31234567"
      ],
      [, , "6\\d{7}", , , , "61234567"],
      [, , "80[02]\\d{5}", , , , "80012345"],
      [, , "9(?:0[0239]|10)\\d{5}", , , , "90012345"],
      [, , "808\\d{5}", , , , "80812345"],
      [, , "70[05]\\d{5}", , , , "70012345"],
      [, , "[89]01\\d{5}", , , , "80123456"],
      "LT",
      370,
      "00",
      "0",
      ,
      ,
      "[08]",
      ,
      ,
      ,
      [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["52[0-7]"], "(0-$1)", , 1], [, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["[7-9]"], "0 $1", , 1], [, "(\\d{2})(\\d{6})", "$1 $2", ["37|4(?:[15]|6[1-8])"], "(0-$1)", , 1], [, "(\\d{3})(\\d{5})", "$1 $2", ["[3-6]"], "(0-$1)", , 1]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "70[67]\\d{5}", , , , "70712345"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    LU: [, [, , "35[013-9]\\d{4,8}|6\\d{8}|35\\d{2,4}|(?:[2457-9]\\d|3[0-46-9])\\d{2,9}", , , , , , , [4, 5, 6, 7, 8, 9, 10, 11]], [, , "(?:35[013-9]|80[2-9]|90[89])\\d{1,8}|(?:2[2-9]|3[0-46-9]|[457]\\d|8[13-9]|9[2-579])\\d{2,9}", , , , "27123456"], [, , "6(?:[26][18]|5[1568]|7[189]|81|9[128])\\d{6}", , , , "628123456", , , [9]], [, , "800\\d{5}", , , , "80012345", , , [8]], [, , "90[015]\\d{5}", , , , "90012345", , , [8]], [, , "801\\d{5}", , , , "80112345", , , [8]], [, , , , , , , , , [-1]], [
      ,
      ,
      "20(?:1\\d{5}|[2-689]\\d{1,7})",
      ,
      ,
      ,
      "20201234",
      ,
      ,
      [4, 5, 6, 7, 8, 9, 10]
    ], "LU", 352, "00", , , , "(15(?:0[06]|1[12]|[35]5|4[04]|6[26]|77|88|99)\\d)", , , , [[, "(\\d{2})(\\d{3})", "$1 $2", ["2(?:0[2-689]|[2-9])|[3-57]|8(?:0[2-9]|[13-9])|9(?:0[89]|[2-579])"], , "$CC $1"], [, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["2(?:0[2-689]|[2-9])|[3-57]|8(?:0[2-9]|[13-9])|9(?:0[89]|[2-579])"], , "$CC $1"], [, "(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3", ["20[2-689]"], , "$CC $1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{1,2})", "$1 $2 $3 $4", ["20"], , "$CC $1"], [
      ,
      "(\\d{2})(\\d{2})(\\d{2})(\\d{1,5})",
      "$1 $2 $3 $4",
      ["[3-57]|8[13-9]|9(?:0[89]|[2-579])|(?:2|80)[2-9]"],
      ,
      "$CC $1"
    ], [, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["80[01]|90[015]"], , "$CC $1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["20"], , "$CC $1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["6"], , "$CC $1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})(\\d{1,2})", "$1 $2 $3 $4 $5", ["20"], , "$CC $1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LV: [, [, , "(?:[268]\\d|78|90)\\d{6}", , , , , , , [8]], [, , "6\\d{7}", , , , "63123456"], [
      ,
      ,
      "2333[0-8]\\d{3}|2(?:[0-24-9]\\d\\d|3(?:0[07]|[14-9]\\d|2[02-9]|3[0-24-9]))\\d{4}",
      ,
      ,
      ,
      "21234567"
    ], [, , "80\\d{6}", , , , "80123456"], [, , "90\\d{6}", , , , "90123456"], [, , "81\\d{6}", , , , "81123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LV", 371, "00", , , , , , , , [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2679]|8[01]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    LY: [, [, , "[2-9]\\d{8}", , , , , , , [9], [7]], [
      ,
      ,
      "(?:2(?:0[56]|[1-6]\\d|7[124579]|8[124])|3(?:1\\d|2[2356])|4(?:[17]\\d|2[1-357]|5[2-4]|8[124])|5(?:[1347]\\d|2[1-469]|5[13-5]|8[1-4])|6(?:[1-479]\\d|5[2-57]|8[1-5])|7(?:[13]\\d|2[13-79])|8(?:[124]\\d|5[124]|84))\\d{6}",
      ,
      ,
      ,
      "212345678",
      ,
      ,
      ,
      [7]
    ], [, , "9[1-6]\\d{7}", , , , "912345678"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "LY", 218, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{7})", "$1-$2", ["[2-9]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MA: [, [, , "[5-8]\\d{8}", , , , , , , [9]], [, , "5(?:(?:18|4[0679]|5[03])\\d|2(?:[0-25-79]\\d|3[1-578]|4[02-46-8]|8[0235-9])|3(?:[0-47]\\d|5[02-9]|6[02-8]|8[014-9]|9[3-9]))\\d{5}", , , , "520123456"], [
      ,
      ,
      "(?:6(?:[0-79]\\d|8[0-247-9])|7(?:[016-8]\\d|2[0-8]|3[01]|5[0-5]))\\d{6}",
      ,
      ,
      ,
      "650123456"
    ], [, , "80[0-7]\\d{6}", , , , "801234567"], [, , "89\\d{7}", , , , "891234567"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:592(?:4[0-2]|93)|80[89]\\d\\d)\\d{4}", , , , "592401234"], "MA", 212, "00", "0", , , "0", , , , [[, "(\\d{4})(\\d{5})", "$1-$2", ["892"], "0$1"], [, "(\\d{2})(\\d{7})", "$1-$2", ["8(?:0[0-7]|9)"], "0$1"], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[5-8]"], "0$1"]], , [, , , , , , , , , [-1]], 1, "[5-8]", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MC: [
      ,
      [, , "(?:[3489]|[67]\\d)\\d{7}", , , , , , , [8, 9]],
      [, , "(?:870|9[2-47-9]\\d)\\d{5}", , , , "99123456", , , [8]],
      [, , "4(?:[46]\\d|5[1-9])\\d{5}|(?:3|[67]\\d)\\d{7}", , , , "612345678"],
      [, , "(?:800|90\\d)\\d{5}", , , , "90123456", , , [8]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "MC",
      377,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3", ["87"]], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["4"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[389]"]], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[67]"], "0$1"]],
      [[
        ,
        "(\\d{2})(\\d{3})(\\d{3})",
        "$1 $2 $3",
        ["4"],
        "0$1"
      ], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[389]"]], [, "(\\d)(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[67]"], "0$1"]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "8[07]0\\d{5}", , , , , , , [8]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    MD: [
      ,
      [, , "(?:[235-7]\\d|[89]0)\\d{6}", , , , , , , [8]],
      [, , "(?:(?:2[1-9]|3[1-79])\\d|5(?:33|5[257]))\\d{5}", , , , "22212345"],
      [, , "562\\d{5}|(?:6\\d|7[16-9])\\d{6}", , , , "62112345"],
      [, , "800\\d{5}", , , , "80012345"],
      [, , "90[056]\\d{5}", , , , "90012345"],
      [, , "808\\d{5}", , , , "80812345"],
      [, , , , , , , , , [-1]],
      [, , "3[08]\\d{6}", , , , "30123456"],
      "MD",
      373,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{5})", "$1 $2", ["[89]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["22|3"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{3})", "$1 $2 $3", ["[25-7]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "803\\d{5}", , , , "80312345"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    ME: [
      ,
      [, , "(?:20|[3-79]\\d)\\d{6}|80\\d{6,7}", , , , , , , [8, 9], [6]],
      [, , "(?:20[2-8]|3(?:[0-2][2-7]|3[24-7])|4(?:0[2-467]|1[2467])|5(?:0[2467]|1[24-7]|2[2-467]))\\d{5}", , , , "30234567", , , [8], [6]],
      [, , "6(?:[07-9]\\d|3[024]|6[0-25])\\d{5}", , , , "60123456", , , [8]],
      [, , "80(?:[0-2578]|9\\d)\\d{5}", , , , "80080002"],
      [, , "9(?:4[1568]|5[178])\\d{5}", , , , "94515151", , , [8]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "78[1-49]\\d{5}", , , , "78108780", , , [8]],
      "ME",
      382,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[2-9]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "77[1-9]\\d{5}", , , , "77273012", , , [8]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    MF: [, [, , "7090\\d{5}|(?:[56]9|[89]\\d)\\d{7}", , , , , , , [9]], [
      ,
      ,
      "(?:59(?:0(?:0[079]|[14]3|[27][79]|3[03-7]|5[0-268]|87)|87\\d)|80[6-9]\\d\\d)\\d{4}",
      ,
      ,
      ,
      "590271234"
    ], [, , "(?:69(?:0\\d\\d|1(?:2[2-9]|3[0-5]))|7090[0-4])\\d{4}", , , , "690001234"], [, , "80[0-5]\\d{6}", , , , "800012345"], [, , "8[129]\\d{7}", , , , "810123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:(?:39[5-7]|76[018])\\d|475[0-6])\\d{4}", , , , "976012345"], "MF", 590, "00", "0", , , "0", , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MG: [, [, , "[23]\\d{8}", , , , , , , [9], [7]], [, , "2072[29]\\d{4}|20(?:2\\d|4[47]|5[3467]|6[279]|7[356]|8[268]|9[2457])\\d{5}", , , , "202123456", , , , [7]], [
      ,
      ,
      "3[2-9]\\d{7}",
      ,
      ,
      ,
      "321234567"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "22\\d{7}", , , , "221234567"], "MG", 261, "00", "0", , , "([24-9]\\d{6})$|0", "20$1", , , [[, "(\\d{2})(\\d{2})(\\d{3})(\\d{2})", "$1 $2 $3 $4", ["[23]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MH: [, [, , "329\\d{4}|(?:[256]\\d|45)\\d{5}", , , , , , , [7]], [, , "(?:247|528|625)\\d{4}", , , , "2471234"], [, , "(?:(?:23|54)5|329|45[35-8])\\d{4}", , , , "2351234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , "635\\d{4}", , , , "6351234"], "MH", 692, "011", "1", , , "1", , , , [[, "(\\d{3})(\\d{4})", "$1-$2", ["[2-6]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MK: [, [, , "[2-578]\\d{7}", , , , , , , [8], [6, 7]], [, , "(?:(?:2(?:62|77)0|3444)\\d|4[56]440)\\d{3}|(?:34|4[357])700\\d{3}|(?:2(?:[0-3]\\d|5[0-578]|6[01]|82)|3(?:1[3-68]|[23][2-68]|4[23568])|4(?:[23][2-68]|4[3-68]|5[2568]|6[25-8]|7[24-68]|8[4-68]))\\d{5}", , , , "22012345", , , , [6, 7]], [
      ,
      ,
      "7(?:3555|(?:474|9[019]7)7)\\d{3}|7(?:[0-25-8]\\d\\d|3(?:[1-478]\\d|6[01])|4(?:2\\d|60|7[01578])|9(?:[2-4]\\d|5[01]|7[015]))\\d{4}",
      ,
      ,
      ,
      "72345678"
    ], [, , "800\\d{5}", , , , "80012345"], [, , "5\\d{7}", , , , "50012345"], [, , "8(?:0[1-9]|[1-9]\\d)\\d{5}", , , , "80123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "MK", 389, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["2|34[47]|4(?:[37]7|5[47]|64)"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[347]"], "0$1"], [, "(\\d{3})(\\d)(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[58]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    ML: [, [, , "[24-9]\\d{7}", , , , , , , [8]], [
      ,
      ,
      "2(?:07[0-8]|12[67])\\d{4}|(?:2(?:02|1[4-689])|4(?:0[0-4]|4[1-69]))\\d{5}",
      ,
      ,
      ,
      "20212345"
    ], [, , "2(?:0(?:01|79)|17\\d)\\d{4}|(?:5[0-3]|[679]\\d|8[2-59])\\d{6}", , , , "65012345"], [, , "80\\d{6}", , , , "80012345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "ML", 223, "00", , , , , , , , [[, "(\\d{4})", "$1", ["67[057-9]|74[045]", "67(?:0[09]|[59]9|77|8[89])|74(?:0[02]|44|55)"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[24-9]"]]], [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[24-9]"]]], [, , , , , , , , , [-1]], , , [, , "80\\d{6}"], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MM: [
      ,
      [, , "1\\d{5,7}|95\\d{6}|(?:[4-7]|9[0-46-9])\\d{6,8}|(?:2|8\\d)\\d{5,8}", , , , , , , [6, 7, 8, 9, 10], [5]],
      [
        ,
        ,
        "(?:1(?:(?:12|[28]\\d|3[56]|7[3-6]|9[0-6])\\d|4(?:2[29]|7[0-2]|83)|6)|2(?:2(?:00|8[34])|4(?:0\\d|22|7[0-2]|83)|51\\d\\d)|4(?:2(?:2\\d\\d|48[013])|3(?:20\\d|4(?:70|83)|56)|420\\d|5(?:2\\d|470))|6(?:0(?:[23]|88\\d)|(?:124|[56]2\\d)\\d|2472|3(?:20\\d|470)|4(?:2[04]\\d|472)|7(?:3\\d\\d|4[67]0|8(?:[01459]\\d|8))))\\d{4}|5(?:2(?:2\\d{5,6}|47[02]\\d{4})|(?:3472|4(?:2(?:1|86)|470)|522\\d|6(?:20\\d|483)|7(?:20\\d|48[01])|8(?:20\\d|47[02])|9(?:20\\d|470))\\d{4})|7(?:(?:0470|4(?:25\\d|470)|5(?:202|470|96\\d))\\d{4}|1(?:20\\d{4,5}|4(?:70|83)\\d{4}))|8(?:1(?:2\\d{5,6}|4(?:10|7[01]\\d)\\d{3})|2(?:2\\d{5,6}|(?:320|490\\d)\\d{3})|(?:3(?:2\\d\\d|470)|4[24-7]|5(?:(?:2\\d|51)\\d|4(?:[1-35-9]\\d|4[0-57-9]))|6[23])\\d{4})|(?:1[2-6]\\d|4(?:2[24-8]|3[2-7]|[46][2-6]|5[3-5])|5(?:[27][2-8]|3[2-68]|4[24-8]|5[23]|6[2-4]|8[24-7]|9[2-7])|6(?:[19]20|42[03-6]|(?:52|7[45])\\d)|7(?:[04][24-8]|[15][2-7]|22|3[2-4])|8(?:1[2-689]|2[2-8]|(?:[35]2|64)\\d))\\d{4}|25\\d{5,6}|(?:2[2-9]|6(?:1[2356]|[24][2-6]|3[24-6]|5[2-4]|6[2-8]|7[235-7]|8[245]|9[24])|8(?:3[24]|5[245]))\\d{4}",
        ,
        ,
        ,
        "1234567",
        ,
        ,
        [6, 7, 8, 9],
        [5]
      ],
      [, , "(?:17[01]|9(?:2(?:[0-4]|[56]\\d\\d)|(?:3(?:[0-36]|4\\d)|(?:6\\d|8[89]|9[4-8])\\d|7(?:3|40|[5-9]\\d))\\d|4(?:(?:[0245]\\d|[1379])\\d|88)|5[0-6])\\d)\\d{4}|9[69]1\\d{6}|9(?:[68]\\d|9[089])\\d{5}", , , , "92123456", , , [7, 8, 9, 10]],
      [, , "80080(?:0[1-9]|2\\d)\\d{3}", , , , "8008001234", , , [10]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "1333\\d{4}", , , , "13331234", , , [8]],
      "MM",
      95,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d)(\\d{2})(\\d{3})", "$1 $2 $3", ["16|2"], "0$1"], [
        ,
        "(\\d{2})(\\d{2})(\\d{3})",
        "$1 $2 $3",
        ["4(?:[2-46]|5[3-5])|5|6(?:[1-689]|7[235-7])|7(?:[0-4]|5[2-7])|8[1-5]|(?:60|86)[23]"],
        "0$1"
      ], [, "(\\d)(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[12]|452|678|86", "[12]|452|6788|86"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[4-7]|8[1-35]"], "0$1"], [, "(\\d)(\\d{3})(\\d{4,6})", "$1 $2 $3", ["9(?:2[0-4]|[35-9]|4[137-9])"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"], "0$1"], [, "(\\d)(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["92"], "0$1"], [
        ,
        "(\\d)(\\d{5})(\\d{4})",
        "$1 $2 $3",
        ["9"],
        "0$1"
      ]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    MN: [, [, , "[12]\\d{7,9}|[5-9]\\d{7}", , , , , , , [8, 9, 10], [4, 5, 6]], [, , "[12](?:2[1-3]|(?:3[2-8]|4[2-68]|5[1-4689])\\d)\\d{5,6}|7(?:0(?:[0-5]\\d|7[078]|80)|128)\\d{4}|[12]27\\d{6}|(?:11|2[16]|5[368])\\d{6}", , , , "53123456", , , , [4, 5, 6]], [, , "(?:87[01]|92[0139])\\d{5}|(?:5[05]|6[069]|7[28]|8[0135689]|9[013-9])\\d{6}", , , , "88123456", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , "712[0-79]\\d{4}|7(?:1[013-9]|[5-79]\\d)\\d{5}", , , , "75123456", , , [8]], "MN", 976, "001", "0", , , "0", , , , [[, "(\\d{2})(\\d{2})(\\d{4})", "$1 $2 $3", ["11|2[16]"], "0$1"], [, "(\\d{4})(\\d{4})", "$1 $2", ["[5-9]"]], [, "(\\d{3})(\\d{5,6})", "$1 $2", ["[12]2[1-3]"], "0$1"], [, "(\\d{4})(\\d{5,6})", "$1 $2", ["[12](?:27|3[2-8]|4[2-68]|5[1-4689])", "[12](?:27|3[2-8]|4[2-68]|5[1-4689])[0-3]"], "0$1"], [, "(\\d{5})(\\d{4,5})", "$1 $2", ["[12]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MO: [
      ,
      [, , "0800\\d{3}|(?:28|[68]\\d)\\d{6}", , , , , , , [7, 8]],
      [, , "(?:28[2-9]|8(?:11|[2-57-9]\\d))\\d{5}", , , , "28212345", , , [8]],
      [, , "6800[0-79]\\d{3}|6(?:[235]\\d\\d|6(?:0[0-5]|[1-9]\\d)|8(?:0[1-9]|[14-8]\\d|2[5-9]|[39][0-4]))\\d{4}", , , , "66123456", , , [8]],
      [, , "0800\\d{3}", , , , "0800501", , , [7]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "MO",
      853,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{4})(\\d{3})", "$1 $2", ["0"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[268]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        [-1]
      ]
    ],
    MP: [, [, , "[58]\\d{9}|(?:67|90)0\\d{7}", , , , , , , [10], [7]], [, , "670(?:2(?:3[3-7]|56|8[4-8])|32[1-38]|4(?:33|8[348])|5(?:32|55|88)|6(?:64|70|82)|78[3589]|8[3-9]8|989)\\d{4}", , , , "6702345678", , , , [7]], [, , "670(?:2(?:3[3-7]|56|8[4-8])|32[1-38]|4(?:33|8[348])|5(?:32|55|88)|6(?:64|70|82)|78[3589]|8[3-9]8|989)\\d{4}", , , , "6702345678", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "MP", 1, "011", "1", , , "([2-9]\\d{6})$|1", "670$1", , 1, , , [, , , , , , , , , [-1]], , "670", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MQ: [, [, , "7091\\d{5}|(?:[56]9|[89]\\d)\\d{7}", , , , , , , [9]], [, , "(?:59(?:6(?:[03-7]\\d|1[05]|2[7-9]|8[0-39]|9[04-9])|89\\d)|80[6-9]\\d\\d|9(?:477[6-9]|767[4589]))\\d{4}", , , , "596301234"], [, , "(?:69[67]\\d\\d|7091[0-3])\\d{4}", , , , "696201234"], [, , "80[0-5]\\d{6}", , , , "800012345"], [, , "8[129]\\d{7}", , , , "810123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "9(?:397[0-3]|477[0-5]|76(?:6\\d|7[0-367]))\\d{4}",
      ,
      ,
      ,
      "976612345"
    ], "MQ", 596, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-79]|8(?:0[6-9]|[36])"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MR: [
      ,
      [, , "(?:[2-4]\\d\\d|800)\\d{5}", , , , , , , [8]],
      [, , "(?:25[08]|35\\d|45[1-7])\\d{5}", , , , "35123456"],
      [, , "[2-4][0-46-9]\\d{6}", , , , "22123456"],
      [, , "800\\d{5}", , , , "80012345"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "MR",
      222,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2-48]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    MS: [, [, , "(?:[58]\\d\\d|664|900)\\d{7}", , , , , , , [10], [7]], [, , "6644(?:1[0-3]|91)\\d{4}", , , , "6644912345", , , , [7]], [, , "664(?:3(?:49|9[1-6])|49[2-6])\\d{4}", , , , "6644923456", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"], [, , "900[2-9]\\d{6}", , , , "9002123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "MS", 1, "011", "1", , , "([34]\\d{6})$|1", "664$1", , , , , [, , , , , , , , , [-1]], , "664", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MT: [, [, , "3550\\d{4}|(?:[2579]\\d\\d|800)\\d{5}", , , , , , , [8]], [, , "20(?:3[1-4]|6[059])\\d{4}|2(?:0[19]|[1-357]\\d|60)\\d{5}", , , , "21001234"], [, , "(?:7(?:210|[79]\\d\\d)|9(?:[29]\\d\\d|69[67]|8(?:1[1-3]|89|97)))\\d{4}", , , , "96961234"], [, , "800(?:02|[3467]\\d)\\d{3}", , , , "80071234"], [
      ,
      ,
      "5(?:0(?:0(?:37|43)|(?:6\\d|70|9[0168])\\d)|[12]\\d0[1-5])\\d{3}",
      ,
      ,
      ,
      "50037123"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "3550\\d{4}", , , , "35501234"], "MT", 356, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[2357-9]"]]], , [, , "7117\\d{4}", , , , "71171234"], , , [, , , , , , , , , [-1]], [, , "501\\d{5}", , , , "50112345"], , , [, , , , , , , , , [-1]]],
    MU: [, [, , "(?:[57]|8\\d\\d)\\d{7}|[2-468]\\d{6}", , , , , , , [7, 8, 10]], [, , "(?:2(?:[0346-8]\\d|1[0-8])|4(?:[013568]\\d|2[0-24-8]|71|90)|54(?:[3-5]\\d|71)|6\\d\\d|8(?:14|3[129]))\\d{4}", , , , "54480123", , , [7, 8]], [
      ,
      ,
      "5(?:4(?:2[1-389]|7[1-9])|87[15-8])\\d{4}|(?:5(?:2[5-9]|4[3-689]|[57]\\d|8[0-689]|9[0-8])|7(?:0[0-7]|3[013]))\\d{5}",
      ,
      ,
      ,
      "52512345",
      ,
      ,
      [8]
    ], [, , "802\\d{7}|80[0-2]\\d{4}", , , , "8001234", , , [7, 10]], [, , "30\\d{5}", , , , "3012345", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "3(?:20|9\\d)\\d{4}", , , , "3201234", , , [7]], "MU", 230, "0(?:0|[24-7]0|3[03])", , , , , , "020", , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[2-46]|8[013]"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[57]"]], [, "(\\d{5})(\\d{5})", "$1 $2", ["8"]]], , [, , "219\\d{4}", , , , "2190123", , , [7]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MV: [, [, , "(?:800|9[0-57-9]\\d)\\d{7}|[34679]\\d{6}", , , , , , , [
      7,
      10
    ]], [, , "(?:3(?:0[0-4]|3[0-59])|6(?:[58][024689]|6[024-68]|7[02468]))\\d{4}", , , , "6701234", , , [7]], [, , "(?:46[46]|[79]\\d\\d)\\d{4}", , , , "7712345", , , [7]], [, , "800\\d{7}", , , , "8001234567", , , [10]], [, , "900\\d{7}", , , , "9001234567", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "MV", 960, "0(?:0|19)", , , , , , "00", , [[, "(\\d{3})(\\d{4})", "$1-$2", ["[34679]"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[89]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "4(?:0[01]|50)\\d{4}", , , , "4001234", , , [7]], , , [, , , , , , , , , [-1]]],
    MW: [, [, , "(?:[1289]\\d|31|77)\\d{7}|1\\d{6}", , , , , , , [7, 9]], [, , "1[2-9]\\d{5}", , , , "1234567", , , [7]], [, , "111\\d{6}|(?:2[12]|31|77|[89][89])\\d{7}", , , , "991234567", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "MW", 265, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["1[2-9]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[1-37-9]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    MX: [
      ,
      [
        ,
        ,
        "[2-9]\\d{9}",
        ,
        ,
        ,
        ,
        ,
        ,
        [10],
        [7, 8]
      ],
      [, , "(?:2(?:0[01]|2\\d|3[1-35-8]|4[13-9]|7[1-689]|8[1-578]|9[467])|3(?:1[1-79]|[2458][1-9]|3\\d|7[1-8]|9[1-5])|4(?:1[1-57-9]|[267][1-9]|3[1-8]|[45]\\d|8[1-35-9]|9[2-689])|5(?:[56]\\d|88|9[1-79])|6(?:1[2-68]|[2-4][1-9]|5[1-36-9]|6[0-57-9]|7[1-7]|8[67]|9[4-8])|7(?:[1346][1-9]|[27]\\d|5[13-9]|8[1-69]|9[17])|8(?:1\\d|2[13-689]|3[1-6]|4[124-6]|6[1246-9]|7[0-378]|9[12479])|9(?:1[346-9]|2[1-4]|3[2-46-8]|5[1348]|[69]\\d|7[12]|8[1-8]))\\d{7}", , , , "2001234567", , , , [7, 8]],
      [
        ,
        ,
        "(?:2(?:2\\d|3[1-35-8]|4[13-9]|7[1-689]|8[1-578]|9[467])|3(?:1[1-79]|[2458][1-9]|3\\d|7[1-8]|9[1-5])|4(?:1[1-57-9]|[267][1-9]|3[1-8]|[45]\\d|8[1-35-9]|9[2-689])|5(?:[56]\\d|88|9[1-79])|6(?:1[2-68]|[2-4][1-9]|5[1-36-9]|6[0-57-9]|7[1-7]|8[67]|9[4-8])|7(?:[1346][1-9]|[27]\\d|5[13-9]|8[1-69]|9[17])|8(?:1\\d|2[13-689]|3[1-6]|4[124-6]|6[1246-9]|7[0-378]|9[12479])|9(?:1[346-9]|2[1-4]|3[2-46-8]|5[1348]|[69]\\d|7[12]|8[1-8]))\\d{7}",
        ,
        ,
        ,
        "2221234567",
        ,
        ,
        ,
        [7, 8]
      ],
      [, , "8(?:00|88)\\d{7}", , , , "8001234567"],
      [, , "900\\d{7}", , , , "9001234567"],
      [, , "300\\d{7}", , , , "3001234567"],
      [, , "500\\d{7}", , , , "5001234567"],
      [, , , , , , , , , [-1]],
      "MX",
      52,
      "0[09]",
      ,
      ,
      ,
      ,
      ,
      "00",
      ,
      [[, "(\\d{5})", "$1", ["53"]], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["33|5[56]|81"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2-9]"]]],
      [[, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["33|5[56]|81"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[2-9]"]]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    MY: [, [, , "1\\d{8,9}|(?:3\\d|[4-9])\\d{7}", , , , , , , [8, 9, 10], [6, 7]], [, , "427[01]\\d{4}|(?:3(?:2[0-36-9]|3[0-368]|4[0-278]|5[0-24-8]|6[0-467]|7[1246-9]|8\\d|9[0-57])\\d|4(?:2[0-689]|[3-79]\\d|8[1-35689])|5(?:2[0-589]|[3468]\\d|5[0-489]|7[1-9]|9[23])|6(?:2[2-9]|3[1357-9]|[46]\\d|5[0-6]|7[0-35-9]|85|9[015-8])|7(?:[2579]\\d|3[03-68]|4[0-8]|6[5-9]|8[0-35-9])|8(?:[24][2-8]|3[2-5]|5[2-7]|6[2-589]|7[2-578]|[89][2-9])|9(?:0[57]|13|[25-7]\\d|[3489][0-8]))\\d{5}", , , , "323856789", , , [8, 9], [6, 7]], [
      ,
      ,
      "1(?:(?:1888[689]|4400|8(?:47|8[27])[0-4])\\d{4}|9\\d{7,8})|1(?:0(?:[23568]\\d|4[0-6]|7[016-9]|9[0-8])|1(?:[1-5]\\d\\d|6(?:0[5-9]|[1-9]\\d)|7(?:[0-4]\\d|5[0-79]|6[02-4]|8[02-5]))|(?:[26]\\d|[37][1-9]|4[235-9])\\d|5(?:31|9\\d\\d)|8(?:1[23]|[236]\\d|4[06]|5(?:46|[7-9])|7[016-9]|8[01]|9[0-8]))\\d{5}",
      ,
      ,
      ,
      "123456789",
      ,
      ,
      [9, 10]
    ], [, , "1[378]00\\d{6}", , , , "1300123456", , , [10]], [, , "1600\\d{6}", , , , "1600123456", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "15(?:4(?:6[0-4]\\d|8(?:0[125]|[17]\\d|21|3[01]|4[01589]|5[014]|6[02]))|6(?:32[0-6]|78\\d))\\d{4}",
      ,
      ,
      ,
      "1546012345",
      ,
      ,
      [10]
    ], "MY", 60, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1-$2 $3", ["[4-79]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1-$2 $3", ["1(?:[02469]|[378][1-9]|53)|8", "1(?:[02469]|[37][1-9]|53|8(?:[1-46-9]|5[7-9]))|8"], "0$1"], [, "(\\d)(\\d{4})(\\d{4})", "$1-$2 $3", ["3"], "0$1"], [, "(\\d)(\\d{3})(\\d{2})(\\d{4})", "$1-$2-$3-$4", ["1(?:[367]|80)"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2 $3", ["15"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4})", "$1-$2 $3", ["1"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    MZ: [, [, , "(?:2|8\\d)\\d{7}", , , , , , , [8, 9]], [, , "2(?:[1346]\\d|5[0-2]|[78][12]|93)\\d{5}", , , , "21123456", , , [8]], [, , "8[2-9]\\d{7}", , , , "821234567", , , [9]], [, , "800\\d{6}", , , , "800123456", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "MZ", 258, "00", , , , , , , , [[, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["2|8[2-9]"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["8"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NA: [, [
      ,
      ,
      "[68]\\d{7,8}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8, 9]
    ], [, , "64426\\d{3}|6(?:1(?:2[2-7]|3[01378]|4[0-4])|254|32[0237]|4(?:27|41|5[25])|52[236-8]|626|7(?:2[2-4]|30))\\d{4,5}|6(?:1(?:(?:0\\d|2[0189]|3[24-69]|4[5-9])\\d|17|69|7[014])|2(?:17|5[0-36-8]|69|70)|3(?:17|2[14-689]|34|6[289]|7[01]|81)|4(?:17|2[0-2]|4[06]|5[0137]|69|7[01])|5(?:17|2[0459]|69|7[01])|6(?:17|25|38|42|69|7[01])|7(?:17|2[569]|3[13]|6[89]|7[01]))\\d{4}", , , , "61221234"], [, , "(?:60|8[1245])\\d{7}", , , , "811234567", , , [9]], [, , "80\\d{7}", , , , "800123456", , , [9]], [
      ,
      ,
      "8701\\d{5}",
      ,
      ,
      ,
      "870123456",
      ,
      ,
      [9]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "8(?:3\\d\\d|86)\\d{5}", , , , "88612345"], "NA", 264, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["88"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["6"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["87"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NC: [, [, , "(?:050|[2-57-9]\\d\\d)\\d{3}", , , , , , , [6]], [, , "(?:2[03-9]|3[0-5]|4[1-7]|88)\\d{4}", , , , "201234"], [
      ,
      ,
      "(?:[579]\\d|8[0-79])\\d{4}",
      ,
      ,
      ,
      "751234"
    ], [, , "050\\d{3}", , , , "050012"], [, , "36\\d{4}", , , , "366711"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NC", 687, "00", , , , , , , , [[, "(\\d{3})", "$1", ["5[6-8]"]], [, "(\\d{2})(\\d{2})(\\d{2})", "$1.$2.$3", ["[02-57-9]"]]], [[, "(\\d{2})(\\d{2})(\\d{2})", "$1.$2.$3", ["[02-57-9]"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NE: [, [, , "[027-9]\\d{7}", , , , , , , [8]], [
      ,
      ,
      "2(?:0(?:20|3[1-8]|4[13-5]|5[14]|6[14578]|7[1-578])|1(?:4[145]|5[14]|6[14-68]|7[169]|88))\\d{4}",
      ,
      ,
      ,
      "20201234"
    ], [, , "(?:23|7[0467]|[89]\\d)\\d{6}", , , , "93123456"], [, , "08\\d{6}", , , , "08123456"], [, , "09\\d{6}", , , , "09123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NE", 227, "00", , , , , , , , [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["08"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[089]|2[013]|7[0467]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NF: [, [, , "[13]\\d{5}", , , , , , , [6], [5]], [, , "(?:1(?:06|17|28|39)|3[0-2]\\d)\\d{3}", , , , "106609", , , , [5]], [
      ,
      ,
      "(?:14|3[58])\\d{4}",
      ,
      ,
      ,
      "381234",
      ,
      ,
      ,
      [5]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NF", 672, "00", , , , "([0-258]\\d{4})$", "3$1", , , [[, "(\\d{2})(\\d{4})", "$1 $2", ["1[0-3]"]], [, "(\\d)(\\d{5})", "$1 $2", ["[13]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NG: [
      ,
      [, , "(?:20|9\\d)\\d{8}|[78]\\d{9,13}", , , , , , , [10, 11, 12, 13, 14], [6, 7]],
      [, , "20(?:[1259]\\d|3[013-9]|4[1-8]|6[024-689]|7[1-79]|8[2-9])\\d{6}", , , , "2033123456", , , [10], [6, 7]],
      [
        ,
        ,
        "(?:702[0-24-9]|819[01])\\d{6}|(?:7(?:0[13-9]|[12]\\d)|8(?:0[1-9]|1[0-8])|9(?:0[1-9]|1[1-6]))\\d{7}",
        ,
        ,
        ,
        "8021234567",
        ,
        ,
        [10]
      ],
      [, , "800\\d{7,11}", , , , "80017591759"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "NG",
      234,
      "009",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[7-9]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["20[129]"], "0$1"], [, "(\\d{4})(\\d{2})(\\d{4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{3})(\\d{4})(\\d{4,5})", "$1 $2 $3", ["[78]"], "0$1"], [, "(\\d{3})(\\d{5})(\\d{5,6})", "$1 $2 $3", ["[78]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "700\\d{7,11}", , , , "7001234567"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    NI: [, [, , "(?:1800|[25-8]\\d{3})\\d{4}", , , , , , , [8]], [, , "2\\d{7}", , , , "21234567"], [, , "(?:5(?:5[0-7]|[78]\\d)|6(?:20|3[035]|4[045]|5[05]|77|8[1-9]|9[059])|(?:7[5-8]|8\\d)\\d)\\d{5}", , , , "81234567"], [, , "1800\\d{4}", , , , "18001234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NI", 505, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[125-8]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NL: [, [
      ,
      ,
      "(?:[124-7]\\d\\d|3(?:[02-9]\\d|1[0-8]))\\d{6}|8\\d{6,9}|9\\d{6,10}|1\\d{4,5}",
      ,
      ,
      ,
      ,
      ,
      ,
      [5, 6, 7, 8, 9, 10, 11]
    ], [, , "(?:1(?:[035]\\d|1[13-578]|6[124-8]|7[24]|8[0-467])|2(?:[0346]\\d|2[2-46-9]|5[125]|9[479])|3(?:[03568]\\d|1[3-8]|2[01]|4[1-8])|4(?:[0356]\\d|1[1-368]|7[58]|8[15-8]|9[23579])|5(?:[0358]\\d|[19][1-9]|2[1-57-9]|4[13-8]|6[126]|7[0-3578])|7\\d\\d)\\d{6}", , , , "101234567", , , [9]], [, , "(?:6[1-58]|970\\d)\\d{7}", , , , "612345678", , , [9, 11]], [, , "800\\d{4,7}", , , , "8001234", , , [7, 8, 9, 10]], [, , "90[069]\\d{4,7}", , , , "9061234", , , [7, 8, 9, 10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "(?:85|91)\\d{7}",
      ,
      ,
      ,
      "851234567",
      ,
      ,
      [9]
    ], "NL", 31, "00", "0", , , "0", , , , [[, "(\\d{4})", "$1", ["1[238]|[34]"]], [, "(\\d{2})(\\d{3,4})", "$1 $2", ["14"]], [, "(\\d{6})", "$1", ["1"]], [, "(\\d{3})(\\d{4,7})", "$1 $2", ["[89]0"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["66"], "0$1"], [, "(\\d)(\\d{8})", "$1 $2", ["6"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["1[16-8]|2[259]|3[124]|4[17-9]|5[124679]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[1-578]|91"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{5})", "$1 $2 $3", ["9"], "0$1"]], [[
      ,
      "(\\d{3})(\\d{4,7})",
      "$1 $2",
      ["[89]0"],
      "0$1"
    ], [, "(\\d{2})(\\d{7})", "$1 $2", ["66"], "0$1"], [, "(\\d)(\\d{8})", "$1 $2", ["6"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["1[16-8]|2[259]|3[124]|4[17-9]|5[124679]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[1-578]|91"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{5})", "$1 $2 $3", ["9"], "0$1"]], [, , "66\\d{7}", , , , "662345678", , , [9]], , , [, , "140(?:1[035]|2[0346]|3[03568]|4[0356]|5[0358]|8[458])|140(?:1[16-8]|2[259]|3[124]|4[17-9]|5[124679]|7)\\d", , , , , , , [5, 6]], [
      ,
      ,
      "140(?:1[035]|2[0346]|3[03568]|4[0356]|5[0358]|8[458])|(?:140(?:1[16-8]|2[259]|3[124]|4[17-9]|5[124679]|7)|8[478]\\d{6})\\d",
      ,
      ,
      ,
      "14020",
      ,
      ,
      [5, 6, 9]
    ], , , [, , , , , , , , , [-1]]],
    NO: [, [, , "(?:0|[2-9]\\d{3})\\d{4}", , , , , , , [5, 8]], [, , "(?:2[1-4]|3[1-3578]|5[1-35-7]|6[1-46-9]|7[0-8])\\d{6}", , , , "21234567", , , [8]], [, , "45(?:[0-24-9]\\d|3[0-57-9])\\d{4}|(?:4[016-8]|9\\d)\\d{6}", , , , "40612345", , , [8]], [, , "80[01]\\d{5}", , , , "80012345", , , [8]], [, , "82[09]\\d{5}", , , , "82012345", , , [8]], [, , "810(?:0[0-6]|[2-8]\\d)\\d{3}", , , , "81021234", , , [8]], [, , "880\\d{5}", , , , "88012345", , , [8]], [, , "85[0-5]\\d{5}", , , , "85012345", , , [8]], "NO", 47, "00", , , , , , , , [[
      ,
      "(\\d{3})(\\d{2})(\\d{3})",
      "$1 $2 $3",
      ["8"]
    ], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[2-79]"]]], , [, , , , , , , , , [-1]], 1, "[02-689]|7[0-8]", [, , , , , , , , , [-1]], [, , "(?:0[235-9]|81(?:0(?:0[7-9]|1\\d)|5\\d\\d))\\d{3}", , , , "02000"], , , [, , "81[23]\\d{5}", , , , "81212345", , , [8]]],
    NP: [, [, , "(?:1\\d|9)\\d{9}|[1-9]\\d{7}", , , , , , , [8, 10, 11], [6, 7]], [, , "(?:1[0-6]\\d|99[02-6])\\d{5}|(?:2[13-79]|3[135-8]|4[146-9]|5[135-7]|6[13-9]|7[15-9]|8[1-46-9]|9[1-7])[2-6]\\d{5}", , , , "14567890", , , [8], [6, 7]], [
      ,
      ,
      "9(?:00|6[0-3]|7[0-24-6]|8[0-24-68])\\d{7}",
      ,
      ,
      ,
      "9841234567",
      ,
      ,
      [10]
    ], [, , "1(?:66001|800\\d\\d)\\d{5}", , , , "16600101234", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NP", 977, "00", "0", , , "0", , , , [[, "(\\d)(\\d{7})", "$1-$2", ["1[2-6]"], "0$1"], [, "(\\d{2})(\\d{6})", "$1-$2", ["1[01]|[2-8]|9(?:[1-59]|[67][2-6])"], "0$1"], [, "(\\d{3})(\\d{7})", "$1-$2", ["9"]], [, "(\\d{4})(\\d{2})(\\d{5})", "$1-$2-$3", ["1"]]], [[, "(\\d)(\\d{7})", "$1-$2", ["1[2-6]"], "0$1"], [, "(\\d{2})(\\d{6})", "$1-$2", ["1[01]|[2-8]|9(?:[1-59]|[67][2-6])"], "0$1"], [
      ,
      "(\\d{3})(\\d{7})",
      "$1-$2",
      ["9"]
    ]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NR: [, [, , "(?:222|444|(?:55|8\\d)\\d|666|777|999)\\d{4}", , , , , , , [7]], [, , "444\\d{4}", , , , "4441234"], [, , "(?:222|55[3-9]|666|777|8\\d\\d|999)\\d{4}", , , , "5551234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "NR", 674, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[24-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    NU: [
      ,
      [, , "(?:[4-7]|888\\d)\\d{3}", , , , , , , [4, 7]],
      [, , "[47]\\d{3}", , , , "7012", , , [4]],
      [, , "(?:[56]|888[1-9])\\d{3}", , , , "8884012"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "NU",
      683,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{4})", "$1 $2", ["8"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    NZ: [, [, , "[1289]\\d{9}|50\\d{5}(?:\\d{2,3})?|[27-9]\\d{7,8}|(?:[34]\\d|6[0-35-9])\\d{6}|8\\d{4,6}", , , , , , , [5, 6, 7, 8, 9, 10]], [, , "240\\d{5}|(?:3[2-79]|[49][2-9]|6[235-9]|7[2-57-9])\\d{6}", , , , "32345678", , , [8], [7]], [
      ,
      ,
      "2(?:[0-27-9]\\d|6)\\d{6,7}|2(?:1\\d|75)\\d{5}",
      ,
      ,
      ,
      "211234567",
      ,
      ,
      [8, 9, 10]
    ], [, , "508\\d{6,7}|80\\d{6,8}", , , , "800123456", , , [8, 9, 10]], [, , "(?:1[13-57-9]\\d{5}|50(?:0[08]|30|66|77|88))\\d{3}|90\\d{6,8}", , , , "900123456", , , [7, 8, 9, 10]], [, , , , , , , , , [-1]], [, , "70\\d{7}", , , , "701234567", , , [9]], [, , , , , , , , , [-1]], "NZ", 64, "0(?:0|161)", "0", , , "0", , "00", , [[, "(\\d{2})(\\d{3,8})", "$1 $2", ["8[1-79]"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2,3})", "$1 $2 $3", ["50[036-8]|8|90", "50(?:[0367]|88)|8|90"], "0$1"], [, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["24|[346]|7[2-57-9]|9[2-9]"], "0$1"], [
      ,
      "(\\d{3})(\\d{3})(\\d{3,4})",
      "$1 $2 $3",
      ["2(?:10|74)|[589]"],
      "0$1"
    ], [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["1|2[028]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,5})", "$1 $2 $3", ["2(?:[169]|7[0-35-9])|7"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "8(?:1[16-9]|22|3\\d|4[045]|5[459]|6[235-9]|7[0-3579]|90)\\d{2,7}", , , , "83012378"], , , [, , , , , , , , , [-1]]],
    OM: [, [, , "(?:1505|[279]\\d{3}|500)\\d{4}|800\\d{5,6}", , , , , , , [7, 8, 9]], [, , "2[1-6]\\d{6}", , , , "23123456", , , [8]], [
      ,
      ,
      "(?:1505|90[1-9]\\d)\\d{4}|(?:7[124-9]|9[1-9])\\d{6}",
      ,
      ,
      ,
      "92123456",
      ,
      ,
      [8]
    ], [, , "8007\\d{4,5}|(?:500|800[05])\\d{4}", , , , "80071234"], [, , "900\\d{5}", , , , "90012345", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "OM", 968, "00", , , , , , , , [[, "(\\d{3})(\\d{4,6})", "$1 $2", ["[58]"]], [, "(\\d{2})(\\d{6})", "$1 $2", ["2"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[179]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PA: [, [, , "(?:00800|8\\d{3})\\d{6}|[68]\\d{7}|[1-57-9]\\d{6}", , , , , , , [7, 8, 10, 11]], [
      ,
      ,
      "(?:1(?:0\\d|1[0479]|2[37]|3[0137]|4[147]|5[05]|6[058]|7[0167]|8[2358]|9[1389])|2(?:[0235-79]\\d|1[0-7]|4[013-9]|8[02-9])|3(?:[0147-9]\\d|[25][0-5]|33|6[068])|4(?:00|3[0-579]|4\\d|7[0-57-9])|5(?:[01]\\d|2[0-7]|[56]0|79)|7(?:0[09]|2[0-26-8]|3[03]|4[04]|5[05-9]|6[0156]|7[0-24-9]|8[4-9]|90)|8(?:09|2[89]|3\\d|4[0-24-689]|5[014]|8[02])|9(?:0[5-9]|1[0135-8]|2[036-9]|3[35-79]|40|5[0457-9]|6[05-9]|7[04-9]|8[235-8]|9\\d))\\d{4}",
      ,
      ,
      ,
      "2001234",
      ,
      ,
      [7]
    ], [, , "(?:1[16]1|21[89]|6\\d{3}|8(?:1[01]|7[23]))\\d{4}", , , , "61234567", , , [7, 8]], [, , "800\\d{4,5}|(?:00800|800\\d)\\d{6}", , , , "8001234"], [, , "(?:8(?:22|55|60|7[78]|86)|9(?:00|81))\\d{4}", , , , "8601234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "PA", 507, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1-$2", ["[1-57-9]"]], [, "(\\d{4})(\\d{4})", "$1-$2", ["[68]"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PE: [, [
      ,
      ,
      "(?:[14-8]|9\\d)\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8, 9],
      [6, 7]
    ], [, , "(?:(?:19[02-68]|(?:4[34]|5[14])[0-8]|687)\\d|7(?:173|(?:3[0-8]|55)\\d)|8(?:10[05689]|6(?:0[06-9]|1[6-9]|29)|7(?:0[0569]|[56]0)))\\d{4}|(?:1[0-8]|4[12]|5[236]|6[1-7]|7[246]|8[2-4])\\d{6}", , , , "11234567", , , [8], [6, 7]], [, , "9\\d{8}", , , , "912345678", , , [9]], [, , "800\\d{5}", , , , "80012345", , , [8]], [, , "805\\d{5}", , , , "80512345", , , [8]], [, , "801\\d{5}", , , , "80112345", , , [8]], [, , "80[24]\\d{5}", , , , "80212345", , , [8]], [, , , , , , , , , [-1]], "PE", 51, "00|19(?:1[124]|77|90)00", "0", " Anexo ", , "0", , "00", , [[
      ,
      "(\\d{3})(\\d{5})",
      "$1 $2",
      ["80"],
      "(0$1)"
    ], [, "(\\d)(\\d{7})", "$1 $2", ["1"], "(0$1)"], [, "(\\d{2})(\\d{6})", "$1 $2", ["[4-8]"], "(0$1)"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["9"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PF: [
      ,
      [, , "4\\d{5}(?:\\d{2})?|8\\d{7,8}", , , , , , , [6, 8, 9]],
      [, , "4(?:0[4-689]|9[4-68])\\d{5}", , , , "40412345", , , [8]],
      [, , "8[7-9]\\d{6}", , , , "87123456", , , [8]],
      [, , "80[0-5]\\d{6}", , , , "800012345", , , [9]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "499\\d{5}", , , , "49901234", , , [8]],
      "PF",
      689,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["44"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["4|8[7-9]"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "44\\d{4}", , , , , , , [6]],
      [, , "44\\d{4}", , , , "440123", , , [6]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    PG: [, [, , "(?:180|[78]\\d{3})\\d{4}|(?:[2-589]\\d|64)\\d{5}", , , , , , , [7, 8]], [, , "(?:(?:3[0-2]|4[257]|5[34]|9[78])\\d|64[1-9]|85[02-46-9])\\d{4}", , , , "3123456", , , [7]], [, , "(?:7\\d|8[1-58])\\d{6}", , , , "70123456", , , [8]], [
      ,
      ,
      "180\\d{4}",
      ,
      ,
      ,
      "1801234",
      ,
      ,
      [7]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "2(?:0[0-57]|7[568])\\d{4}", , , , "2751234", , , [7]], "PG", 675, "00|140[1-3]", , , , , , "00", , [[, "(\\d{3})(\\d{4})", "$1 $2", ["18|[2-69]|85[02-46-9]"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[78]"]]], , [, , "27[01]\\d{4}", , , , "2700123", , , [7]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PH: [, [, , "(?:[2-7]|9\\d)\\d{8}|2\\d{5}|(?:1800|8)\\d{7,9}", , , , , , , [6, 8, 9, 10, 11, 12, 13], [4, 5, 7]], [
      ,
      ,
      "(?:(?:2[3-8]|3[2-68]|4[2-9]|5[2-6]|6[2-58]|7[24578])\\d{3}|88(?:22\\d\\d|42))\\d{4}|(?:2|8[2-8]\\d\\d)\\d{5}",
      ,
      ,
      ,
      "232345678",
      ,
      ,
      [6, 8, 9, 10],
      [4, 5, 7]
    ], [, , "(?:8(?:1[37]|9[5-8])|9(?:0[5-9]|1[0-24-9]|[235-7]\\d|4[2-9]|8[135-9]|9[1-9]))\\d{7}", , , , "9051234567", , , [10]], [, , "1800\\d{7,9}", , , , "180012345678", , , [11, 12, 13]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "PH", 63, "00", "0", , , "0", , , , [[, "(\\d)(\\d{5})", "$1 $2", ["2"], "(0$1)"], [
      ,
      "(\\d{4})(\\d{4,6})",
      "$1 $2",
      ["3(?:23|39|46)|4(?:2[3-6]|[35]9|4[26]|76)|544|88[245]|(?:52|64|86)2", "3(?:230|397|461)|4(?:2(?:35|[46]4|51)|396|4(?:22|63)|59[347]|76[15])|5(?:221|446)|642[23]|8(?:622|8(?:[24]2|5[13]))"],
      "(0$1)"
    ], [, "(\\d{5})(\\d{4})", "$1 $2", ["346|4(?:27|9[35])|883", "3469|4(?:279|9(?:30|56))|8834"], "(0$1)"], [, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["2"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[3-7]|8[2-8]"], "(0$1)"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["[89]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]], [, "(\\d{4})(\\d{1,2})(\\d{3})(\\d{4})", "$1 $2 $3 $4", ["1"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PK: [, [
      ,
      ,
      "122\\d{6}|[24-8]\\d{10,11}|9(?:[013-9]\\d{8,10}|2(?:[01]\\d\\d|2(?:[06-8]\\d|1[01]))\\d{7})|(?:[2-8]\\d{3}|92(?:[0-7]\\d|8[1-9]))\\d{6}|[24-9]\\d{8}|[89]\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8, 9, 10, 11, 12],
      [5, 6, 7]
    ], [, , "(?:(?:21|42)[2-9]|58[126])\\d{7}|(?:2[25]|4[0146-9]|5[1-35-7]|6[1-8]|7[14]|8[16]|91)[2-9]\\d{6,7}|(?:2(?:3[2358]|4[2-4]|9[2-8])|45[3479]|54[2-467]|60[468]|72[236]|8(?:2[2-689]|3[23578]|4[3478]|5[2356])|9(?:2[2-8]|3[27-9]|4[2-6]|6[3569]|9[25-8]))[2-9]\\d{5,6}", , , , "2123456789", , , [9, 10], [5, 6, 7, 8]], [, , "3(?:[0-247]\\d|3[0-79]|55|64)\\d{7}", , , , "3012345678", , , [10]], [, , "800\\d{5}(?:\\d{3})?", , , , "80012345", , , [8, 11]], [, , "900\\d{5}", , , , "90012345", , , [8]], [, , , , , , , , , [-1]], [
      ,
      ,
      "122\\d{6}",
      ,
      ,
      ,
      "122044444",
      ,
      ,
      [9]
    ], [, , , , , , , , , [-1]], "PK", 92, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3})(\\d{2,7})", "$1 $2 $3", ["[89]0"], "0$1"], [, "(\\d{4})(\\d{5})", "$1 $2", ["1"]], [
      ,
      "(\\d{3})(\\d{6,7})",
      "$1 $2",
      ["2(?:3[2358]|4[2-4]|9[2-8])|45[3479]|54[2-467]|60[468]|72[236]|8(?:2[2-689]|3[23578]|4[3478]|5[2356])|9(?:2[2-8]|3[27-9]|4[2-6]|6[3569]|9[25-8])", "9(?:2[3-8]|98)|(?:2(?:3[2358]|4[2-4]|9[2-8])|45[3479]|54[2-467]|60[468]|72[236]|8(?:2[2-689]|3[23578]|4[3478]|5[2356])|9(?:22|3[27-9]|4[2-6]|6[3569]|9[25-7]))[2-9]"],
      "(0$1)"
    ], [, "(\\d{2})(\\d{7,8})", "$1 $2", ["(?:2[125]|4[0-246-9]|5[1-35-7]|6[1-8]|7[14]|8[16]|91)[2-9]"], "(0$1)"], [, "(\\d{5})(\\d{5})", "$1 $2", ["58"], "(0$1)"], [, "(\\d{3})(\\d{7})", "$1 $2", ["3"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["2[125]|4[0-246-9]|5[1-35-7]|6[1-8]|7[14]|8[16]|91"], "(0$1)"], [, "(\\d{3})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["[24-9]"], "(0$1)"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [
      ,
      ,
      "(?:2(?:[125]|3[2358]|4[2-4]|9[2-8])|4(?:[0-246-9]|5[3479])|5(?:[1-35-7]|4[2-467])|6(?:0[468]|[1-8])|7(?:[14]|2[236])|8(?:[16]|2[2-689]|3[23578]|4[3478]|5[2356])|9(?:1|22|3[27-9]|4[2-6]|6[3569]|9[2-7]))111\\d{6}",
      ,
      ,
      ,
      "21111825888",
      ,
      ,
      [11, 12]
    ], , , [, , , , , , , , , [-1]]],
    PL: [, [, , "(?:6|8\\d\\d)\\d{7}|[1-9]\\d{6}(?:\\d{2})?|[26]\\d{5}", , , , , , , [6, 7, 8, 9, 10]], [, , "(?:30|47\\d\\d)\\d{5}|(?:1[2-8]|2[2-69]|3[2-4]|4[1-468]|5[24-689]|6[1-3578]|7[14-7]|8[1-79]|9[145])(?:[02-9]\\d{6}|1(?:[0-8]\\d{5}|9\\d{3}(?:\\d{2})?))", , , , "123456789", , , [7, 9]], [, , "21(?:1[013-5]|2\\d|3[1-9])\\d{5}|(?:45|5[0137]|6[069]|7[2389]|88)\\d{7}", , , , "512345678", , , [9]], [, , "800\\d{6,7}", , , , "800123456", , , [9, 10]], [, , "70[01346-8]\\d{6}", , , , "701234567", , , [9]], [
      ,
      ,
      "801\\d{6}",
      ,
      ,
      ,
      "801234567",
      ,
      ,
      [9]
    ], [, , , , , , , , , [-1]], [, , "39\\d{7}", , , , "391234567", , , [9]], "PL", 48, "00", , , , , , , , [
      [, "(\\d{5})", "$1", ["19"]],
      [, "(\\d{3})(\\d{3})", "$1 $2", ["11|20|64"]],
      [, "(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3", ["30|(?:1[2-8]|2[2-69]|3[2-4]|4[1-468]|5[24-689]|6[1-3578]|7[14-7]|8[1-79]|9[145])1", "30|(?:1[2-8]|2[2-69]|3[2-4]|4[1-468]|5[24-689]|6[1-3578]|7[14-7]|8[1-79]|9[145])19"]],
      [, "(\\d{3})(\\d{2})(\\d{2,3})", "$1 $2 $3", ["64"]],
      [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["21|39|45|5[0137]|6[0469]|7[02389]|8(?:0[14]|8)"]],
      [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[2-8]|[2-7]|8[1-79]|9[145]"]],
      [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["8"]]
    ], , [, , "64\\d{4,7}", , , , "641234567", , , [6, 7, 8, 9]], , , [, , , , , , , , , [-1]], [, , "804\\d{6}", , , , "804123456", , , [9]], , , [, , , , , , , , , [-1]]],
    PM: [, [, , "[78]\\d{8}|[2-9]\\d{5}", , , , , , , [6, 9]], [, , "80[6-9]\\d{6}|(?:[236-9]\\d|4[1-35-9]|5[0-47-9])\\d{4}", , , , "430123"], [, , "708(?:4[0-5]|5[0-6])\\d{4}|(?:[236-9]\\d|4[02-489]|5[02-9])\\d{4}", , , , "551234"], [, , "80[0-5]\\d{6}", , , , "800012345", , , [9]], [
      ,
      ,
      "8[129]\\d{7}",
      ,
      ,
      ,
      "810123456",
      ,
      ,
      [9]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "PM", 508, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["[2-9]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["7"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PR: [, [, , "(?:[589]\\d\\d|787)\\d{7}", , , , , , , [10], [7]], [, , "(?:787|939)[2-9]\\d{6}", , , , "7872345678", , , , [7]], [, , "(?:787|939)[2-9]\\d{6}", , , , "7872345678", , , , [7]], [
      ,
      ,
      "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "8002345678"
    ], [, , "900[2-9]\\d{6}", , , , "9002345678"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "PR", 1, "011", "1", , , "1", , , 1, , , [, , , , , , , , , [-1]], , "787|939", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PS: [, [, , "[2489]2\\d{6}|(?:1\\d|5)\\d{8}", , , , , , , [
      8,
      9,
      10
    ], [7]], [, , "(?:22[2-47-9]|42[45]|82[014-68]|92[3569])\\d{5}", , , , "22234567", , , [8], [7]], [, , "5[69]\\d{7}", , , , "599123456", , , [9]], [, , "1800\\d{6}", , , , "1800123456", , , [10]], [, , , , , , , , , [-1]], [, , "1700\\d{6}", , , , "1700123456", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "PS", 970, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["[2489]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["5"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ]],
    PT: [
      ,
      [, , "1693\\d{5}|(?:[26-9]\\d|30)\\d{7}", , , , , , , [9]],
      [, , "2(?:[12]\\d|3[1-689]|4[1-59]|[57][1-9]|6[1-35689]|8[1-69]|9[1256])\\d{6}", , , , "212345678"],
      [, , "6(?:[06]92(?:30|9\\d)|[35]92(?:[049]\\d|3[034]))\\d{3}|(?:(?:16|6[0356])93|9(?:[1-36]\\d\\d|480))\\d{5}", , , , "912345678"],
      [, , "80[02]\\d{6}", , , , "800123456"],
      [, , "(?:6(?:0[178]|4[68])\\d|76(?:0[1-57]|1[2-47]|2[1-37]))\\d{5}", , , , "760123456"],
      [, , "80(?:8\\d|9[1579])\\d{5}", , , , "808123456"],
      [, , "884[0-4689]\\d{5}", , , , "884123456"],
      [, , "30\\d{7}", , , , "301234567"],
      "PT",
      351,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["2[12]"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["16|[236-9]"]]],
      ,
      [, , "6(?:222\\d|89(?:00|88|99))\\d{4}", , , , "622212345"],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "70(?:38[01]|596|(?:7\\d|8[17])\\d)\\d{4}", , , , "707123456"],
      ,
      ,
      [, , "600\\d{6}|6[06]92(?:0\\d|3[349]|49)\\d{3}", , , , "600110000"]
    ],
    PW: [, [, , "(?:[24-8]\\d\\d|345|900)\\d{4}", , , , , , , [7]], [, , "(?:2(?:55|77)|345|488|5(?:35|44|87)|6(?:22|54|79)|7(?:33|47)|8(?:24|55|76)|900)\\d{4}", , , , "2771234"], [
      ,
      ,
      "(?:(?:46|83)[0-5]|(?:6[2-4689]|78)0)\\d{4}|(?:45|77|88)\\d{5}",
      ,
      ,
      ,
      "6201234"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "PW", 680, "01[12]", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[2-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    PY: [, [, , "[36-8]\\d{5,8}|4\\d{6,8}|59\\d{6}|9\\d{5,10}|(?:2\\d|5[0-8])\\d{6,7}", , , , , , , [6, 7, 8, 9, 10, 11], [5]], [
      ,
      ,
      "(?:3[289]|4[246-8]|61|7[1-3]|8[1-36])\\d{5,7}|(?:2(?:[14-68]\\d|2[4-68]|7[15]|9[1-5])|3(?:18|3[167]|4[2357]|51|[67]\\d)|4(?:1\\d|3[12]|5[13]|9[1-47])|5(?:[1-4]\\d|5[02-4])|6(?:3[1-3]|44|7[1-8])|7(?:4[0-4]|5\\d|6[1-578]|75|8[0-8])|858)\\d{5,6}",
      ,
      ,
      ,
      "212345678",
      ,
      ,
      [7, 8, 9],
      [5, 6]
    ], [, , "9(?:51|6[129]|7[1-6]|8[1-7]|9[1-5])\\d{6}", , , , "961456789", , , [9]], [, , "9800\\d{5,7}", , , , "98000123456", , , [9, 10, 11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "8700[0-4]\\d{4}", , , , "870012345", , , [9]], "PY", 595, "00", "0", , , "0", , , , [[, "(\\d{6,7})", "$1", ["[125]|4[01]"]], [, "(\\d{3})(\\d{3,6})", "$1 $2", ["[2-9]0"], "0$1"], [, "(\\d{2})(\\d{5})", "$1 $2", ["3[289]|4[246-8]|61|7[1-3]|8[1-36]"], "(0$1)"], [
      ,
      "(\\d{3})(\\d{4,5})",
      "$1 $2",
      ["2[279]|3[13-5]|4[359]|5|6(?:[34]|7[1-46-8])|7[46-8]|85"],
      "(0$1)"
    ], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["2[14-68]|3[26-9]|4[1246-8]|6(?:1|75)|7[1-35]|8[1-36]"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["87"]], [, "(\\d{3})(\\d{6})", "$1 $2", ["9(?:[5-79]|8[1-7])"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-8]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["9"]]], [[, "(\\d{3})(\\d{3,6})", "$1 $2", ["[2-9]0"], "0$1"], [, "(\\d{2})(\\d{5})", "$1 $2", ["3[289]|4[246-8]|61|7[1-3]|8[1-36]"], "(0$1)"], [
      ,
      "(\\d{3})(\\d{4,5})",
      "$1 $2",
      ["2[279]|3[13-5]|4[359]|5|6(?:[34]|7[1-46-8])|7[46-8]|85"],
      "(0$1)"
    ], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["2[14-68]|3[26-9]|4[1246-8]|6(?:1|75)|7[1-35]|8[1-36]"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["87"]], [, "(\\d{3})(\\d{6})", "$1 $2", ["9(?:[5-79]|8[1-7])"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-8]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["9"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "[245]0\\d{6,7}|[36-9]0\\d{4,7}", , , , "201234567", , , [6, 7, 8, 9]], , , [, , , , , , , , , [-1]]],
    QA: [, [
      ,
      ,
      "800\\d{4}|(?:2|800)\\d{6}|(?:0080|[3-7])\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [7, 8, 9, 11]
    ], [, , "4(?:(?:[014]\\d\\d|999)\\d|2022)\\d{3}", , , , "44123456", , , [8]], [, , "[35-7]\\d{7}", , , , "33123456", , , [8]], [, , "800\\d{4}|(?:0080[01]|800)\\d{6}", , , , "8001234", , , [7, 9, 11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "QA", 974, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["2[136]|8"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[3-7]"]]], , [, , "2[136]\\d{5}", , , , "2123456", , , [7]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    RE: [, [, , "709\\d{6}|(?:26|[689]\\d)\\d{7}", , , , , , , [9]], [
      ,
      ,
      "2631[0-6]\\d{4}|26(?:2\\d|30|88)\\d{5}",
      ,
      ,
      ,
      "262161234"
    ], [, , "(?:69(?:2\\d\\d|3(?:[06][0-6]|1[0-3]|2[0-2]|3[0-39]|4\\d|5[0-5]|7[0-37]|8[0-8]|9[0-479]))|7092[0-3])\\d{4}", , , , "692123456"], [, , "80\\d{7}", , , , "801234567"], [, , "89[1-37-9]\\d{6}", , , , "891123456"], [, , "8(?:1[019]|2[0156]|84|90)\\d{6}", , , , "810123456"], [, , , , , , , , , [-1]], [, , "9(?:399[0-3]|479[0-6]|76(?:2[278]|3[0-37]))\\d{4}", , , , "939901234"], "RE", 262, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[26-9]"], "0$1"]], , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], 1, , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    RO: [, [, , "(?:[236-8]\\d|90)\\d{7}|[23]\\d{5}", , , , , , , [6, 9]], [, , "[23][13-6]\\d{7}|(?:2(?:19\\d|[3-6]\\d9)|31\\d\\d)\\d\\d", , , , "211234567"], [, , "(?:630|702)0\\d{5}|(?:6(?:00|2\\d)|7(?:0[013-9]|1[0-3]|[2-7]\\d|8[03-8]|9[0-39]))\\d{6}", , , , "712034567", , , [9]], [, , "800\\d{6}", , , , "800123456", , , [9]], [, , "90[0136]\\d{6}", , , , "900123456", , , [9]], [, , "801\\d{6}", , , , "801123456", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "RO", 40, "00", "0", " int ", , "0", , , , [[
      ,
      "(\\d{3})(\\d{3})",
      "$1 $2",
      ["2[3-6]", "2[3-6]\\d9"],
      "0$1"
    ], [, "(\\d{2})(\\d{4})", "$1 $2", ["219|31"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[23]1"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[236-9]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "(?:37\\d|80[578])\\d{6}", , , , "372123456", , , [9]], , , [, , , , , , , , , [-1]]],
    RS: [, [, , "38[02-9]\\d{6,9}|6\\d{7,9}|90\\d{4,8}|38\\d{5,6}|(?:7\\d\\d|800)\\d{3,9}|(?:[12]\\d|3[0-79])\\d{5,10}", , , , , , , [6, 7, 8, 9, 10, 11, 12], [4, 5]], [
      ,
      ,
      "(?:11[1-9]\\d|(?:2[389]|39)(?:0[2-9]|[2-9]\\d))\\d{3,8}|(?:1[02-9]|2[0-24-7]|3[0-8])[2-9]\\d{4,9}",
      ,
      ,
      ,
      "10234567",
      ,
      ,
      [7, 8, 9, 10, 11, 12],
      [4, 5, 6]
    ], [, , "6(?:[0-689]|7\\d)\\d{6,7}", , , , "601234567", , , [8, 9, 10]], [, , "800\\d{3,9}", , , , "80012345"], [, , "(?:78\\d|90[0169])\\d{3,7}", , , , "90012345", , , [6, 7, 8, 9, 10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "RS", 381, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3,9})", "$1 $2", ["(?:2[389]|39)0|[7-9]"], "0$1"], [, "(\\d{2})(\\d{5,10})", "$1 $2", ["[1-36]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "7[06]\\d{4,10}", , , , "700123456"], , , [, , , , , , , , , [-1]]],
    RU: [, [
      ,
      ,
      "8\\d{13}|[347-9]\\d{9}",
      ,
      ,
      ,
      ,
      ,
      ,
      [10, 14],
      [7]
    ], [, , "(?:3(?:0[12]|36|4[1-35-79]|5[1-3]|65|8[1-58]|9[0145])|4(?:01|1[1356]|2[13467]|7[1-5]|8[1-7]|9[1-689])|8(?:1[1-8]|2[01]|3[13-6]|4[0-8]|5[15-7]|6[0-35-79]|7[1-37-9]))\\d{7}", , , , "3011234567", , , [10], [7]], [, , "9\\d{9}", , , , "9123456789", , , [10]], [, , "8(?:0[04]|108\\d{3})\\d{7}", , , , "8001234567"], [, , "80[39]\\d{7}", , , , "8091234567", , , [10]], [, , , , , , , , , [-1]], [, , "808\\d{7}", , , , "8081234567", , , [10]], [, , , , , , , , , [-1]], "RU", 7, "810", "8", , , "8", , "8~10", , [
      [, "(\\d{3})(\\d{2})(\\d{2})", "$1-$2-$3", ["[0-79]"]],
      [, "(\\d{4})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["7(?:1[0-8]|2[1-9])", "7(?:1(?:[0-356]2|4[29]|7|8[27])|2(?:1[23]|[2-9]2))", "7(?:1(?:[0-356]2|4[29]|7|8[27])|2(?:13[03-69]|62[013-9]))|72[1-57-9]2"], "8 ($1)", , 1],
      [
        ,
        "(\\d{5})(\\d)(\\d{2})(\\d{2})",
        "$1 $2 $3 $4",
        ["7(?:1[0-68]|2[1-9])", "7(?:1(?:[06][3-6]|[18]|2[35]|[3-5][3-5])|2(?:[13][3-5]|[24-689]|7[457]))", "7(?:1(?:0(?:[356]|4[023])|[18]|2(?:3[013-9]|5)|3[45]|43[013-79]|5(?:3[1-8]|4[1-7]|5)|6(?:3[0-35-9]|[4-6]))|2(?:1(?:3[178]|[45])|[24-689]|3[35]|7[457]))|7(?:14|23)4[0-8]|71(?:33|45)[1-79]"],
        "8 ($1)",
        ,
        1
      ],
      [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["7"], "8 ($1)", , 1],
      [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["[349]|8(?:[02-7]|1[1-8])"], "8 ($1)", , 1],
      [, "(\\d{4})(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["8"], "8 ($1)"]
    ], [[, "(\\d{4})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["7(?:1[0-8]|2[1-9])", "7(?:1(?:[0-356]2|4[29]|7|8[27])|2(?:1[23]|[2-9]2))", "7(?:1(?:[0-356]2|4[29]|7|8[27])|2(?:13[03-69]|62[013-9]))|72[1-57-9]2"], "8 ($1)", , 1], [, "(\\d{5})(\\d)(\\d{2})(\\d{2})", "$1 $2 $3 $4", [
      "7(?:1[0-68]|2[1-9])",
      "7(?:1(?:[06][3-6]|[18]|2[35]|[3-5][3-5])|2(?:[13][3-5]|[24-689]|7[457]))",
      "7(?:1(?:0(?:[356]|4[023])|[18]|2(?:3[013-9]|5)|3[45]|43[013-79]|5(?:3[1-8]|4[1-7]|5)|6(?:3[0-35-9]|[4-6]))|2(?:1(?:3[178]|[45])|[24-689]|3[35]|7[457]))|7(?:14|23)4[0-8]|71(?:33|45)[1-79]"
    ], "8 ($1)", , 1], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["7"], "8 ($1)", , 1], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["[349]|8(?:[02-7]|1[1-8])"], "8 ($1)", , 1], [, "(\\d{4})(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["8"], "8 ($1)"]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], 1, "[3489]", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    RW: [, [, , "(?:06|[27]\\d\\d|[89]00)\\d{6}", , , , , , , [8, 9]], [, , "(?:06|2[23568]\\d)\\d{6}", , , , "250123456"], [, , "7[237-9]\\d{7}", , , , "720123456", , , [9]], [, , "800\\d{6}", , , , "800123456", , , [9]], [, , "900\\d{6}", , , , "900123456", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "RW", 250, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["0"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["2"]], [
      ,
      "(\\d{3})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["[7-9]"],
      "0$1"
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SA: [, [, , "(?:[15]\\d|800|92)\\d{7}", , , , , , , [9, 10], [7]], [, , "1(?:1\\d|2[24-8]|3[35-8]|4[3-68]|6[2-5]|7[235-7])\\d{6}", , , , "112345678", , , [9], [7]], [, , "579[0-8]\\d{5}|5(?:[013-689]\\d|7[0-8])\\d{6}", , , , "512345678", , , [9]], [, , "800\\d{7}", , , , "8001234567", , , [10]], [, , "925\\d{6}", , , , "925012345", , , [9]], [, , "920\\d{6}", , , , "920012345", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SA", 966, "00", "0", , , "0", , , , [[
      ,
      "(\\d{4})(\\d{5})",
      "$1 $2",
      ["9"]
    ], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["5"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SB: [, [, , "[6-9]\\d{6}|[1-6]\\d{4}", , , , , , , [5, 7]], [, , "(?:1[4-79]|[23]\\d|4[0-2]|5[03]|6[0-37])\\d{3}", , , , "40123", , , [5]], [, , "48\\d{3}|(?:(?:6[89]|7[1-9]|8[4-9])\\d|9(?:1[2-9]|2[013-9]|3[0-2]|[46]\\d|5[0-46-9]|7[0-689]|8[0-79]|9[0-8]))\\d{4}", , , , "7421234"], [
      ,
      ,
      "1[38]\\d{3}",
      ,
      ,
      ,
      "18123",
      ,
      ,
      [5]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "5[12]\\d{3}", , , , "51123", , , [5]], "SB", 677, "0[01]", , , , , , , , [[, "(\\d{2})(\\d{5})", "$1 $2", ["6[89]|7|8[4-9]|9(?:[1-8]|9[0-8])"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SC: [, [, , "(?:[2489]\\d|64)\\d{5}", , , , , , , [7]], [, , "4[2-46]\\d{5}", , , , "4217123"], [, , "2[125-8]\\d{5}", , , , "2510123"], [, , "800[08]\\d{3}", , , , "8000000"], [, , "85\\d{5}", , , , "8512345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "971\\d{4}|(?:64|95)\\d{5}",
      ,
      ,
      ,
      "6412345"
    ], "SC", 248, "010|0[0-2]", , , , , , "00", , [[, "(\\d)(\\d{3})(\\d{3})", "$1 $2 $3", ["[246]|9[57]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SD: [, [, , "[19]\\d{8}", , , , , , , [9]], [, , "1(?:5\\d|8[35-7])\\d{6}", , , , "153123456"], [, , "(?:1[0-2]|9[0-3569])\\d{7}", , , , "911231234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SD", 249, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[19]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    SE: [, [, , "(?:[26]\\d\\d|9)\\d{9}|[1-9]\\d{8}|[1-689]\\d{7}|[1-4689]\\d{6}|2\\d{5}", , , , , , , [6, 7, 8, 9, 10, 12]], [
      ,
      ,
      "(?:(?:[12][136]|3[356]|4[0246]|6[03]|8\\d)\\d|90[1-9])\\d{4,6}|(?:1(?:2[0-35]|4[0-4]|5[0-25-9]|7[13-6]|[89]\\d)|2(?:2[0-7]|4[0136-8]|5[0138]|7[018]|8[01]|9[0-57])|3(?:0[0-4]|1\\d|2[0-25]|4[056]|7[0-2]|8[0-3]|9[023])|4(?:1[013-8]|3[0135]|5[14-79]|7[0-246-9]|8[0156]|9[0-689])|5(?:0[0-6]|[15][0-5]|2[0-68]|3[0-4]|4\\d|6[03-5]|7[013]|8[0-79]|9[01])|6(?:1[1-3]|2[0-4]|4[02-57]|5[0-37]|6[0-3]|7[0-2]|8[0247]|9[0-356])|9(?:1[0-68]|2\\d|3[02-5]|4[0-3]|5[0-4]|[68][01]|7[0135-8]))\\d{5,6}",
      ,
      ,
      ,
      "8123456",
      ,
      ,
      [7, 8, 9]
    ], [, , "7[023689]\\d{7}", , , , "701234567", , , [9]], [, , "20\\d{4,7}", , , , "20123456", , , [6, 7, 8, 9]], [, , "649\\d{6}|99[1-59]\\d{4}(?:\\d{3})?|9(?:00|39|44)[1-8]\\d{3,6}", , , , "9001234567", , , [7, 8, 9, 10]], [, , "77[0-7]\\d{6}", , , , "771234567", , , [9]], [, , "75[1-8]\\d{6}", , , , "751234567", , , [9]], [, , , , , , , , , [-1]], "SE", 46, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{2,3})(\\d{2})", "$1-$2 $3", ["20"], "0$1"], [, "(\\d{3})(\\d{4})", "$1-$2", ["9(?:00|39|44|9)"], "0$1"], [
      ,
      "(\\d{2})(\\d{3})(\\d{2})",
      "$1-$2 $3",
      ["[12][136]|3[356]|4[0246]|6[03]|90[1-9]"],
      "0$1"
    ], [, "(\\d)(\\d{2,3})(\\d{2})(\\d{2})", "$1-$2 $3 $4", ["8"], "0$1"], [, "(\\d{3})(\\d{2,3})(\\d{2})", "$1-$2 $3", ["1[2457]|2(?:[247-9]|5[0138])|3[0247-9]|4[1357-9]|5[0-35-9]|6(?:[125689]|4[02-57]|7[0-2])|9(?:[125-8]|3[02-5]|4[0-3])"], "0$1"], [, "(\\d{3})(\\d{2,3})(\\d{3})", "$1-$2 $3", ["9(?:00|39|44)"], "0$1"], [, "(\\d{2})(\\d{2,3})(\\d{2})(\\d{2})", "$1-$2 $3 $4", ["1[13689]|2[0136]|3[1356]|4[0246]|54|6[03]|90[1-9]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1-$2 $3 $4", ["10|7"], "0$1"], [
      ,
      "(\\d)(\\d{3})(\\d{3})(\\d{2})",
      "$1-$2 $3 $4",
      ["8"],
      "0$1"
    ], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1-$2 $3 $4", ["[13-5]|2(?:[247-9]|5[0138])|6(?:[124-689]|7[0-2])|9(?:[125-8]|3[02-5]|4[0-3])"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{3})", "$1-$2 $3 $4", ["9"], "0$1"], [, "(\\d{3})(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1-$2 $3 $4 $5", ["[26]"], "0$1"]], [[, "(\\d{2})(\\d{2,3})(\\d{2})", "$1 $2 $3", ["20"]], [, "(\\d{3})(\\d{4})", "$1 $2", ["9(?:00|39|44|9)"]], [, "(\\d{2})(\\d{3})(\\d{2})", "$1 $2 $3", ["[12][136]|3[356]|4[0246]|6[03]|90[1-9]"]], [
      ,
      "(\\d)(\\d{2,3})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["8"]
    ], [, "(\\d{3})(\\d{2,3})(\\d{2})", "$1 $2 $3", ["1[2457]|2(?:[247-9]|5[0138])|3[0247-9]|4[1357-9]|5[0-35-9]|6(?:[125689]|4[02-57]|7[0-2])|9(?:[125-8]|3[02-5]|4[0-3])"]], [, "(\\d{3})(\\d{2,3})(\\d{3})", "$1 $2 $3", ["9(?:00|39|44)"]], [, "(\\d{2})(\\d{2,3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[13689]|2[0136]|3[1356]|4[0246]|54|6[03]|90[1-9]"]], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["10|7"]], [, "(\\d)(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3 $4", ["8"]], [
      ,
      "(\\d{3})(\\d{2})(\\d{2})(\\d{2})",
      "$1 $2 $3 $4",
      ["[13-5]|2(?:[247-9]|5[0138])|6(?:[124-689]|7[0-2])|9(?:[125-8]|3[02-5]|4[0-3])"]
    ], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{3})", "$1 $2 $3 $4", ["9"]], [, "(\\d{3})(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4 $5", ["[26]"]]], [, , "74[02-9]\\d{6}", , , , "740123456", , , [9]], , , [, , , , , , , , , [-1]], [, , "10[1-8]\\d{6}", , , , "102345678", , , [9]], , , [, , "(?:25[245]|67[3-68])\\d{9}", , , , "254123456789", , , [12]]],
    SG: [, [, , "(?:(?:1\\d|8)\\d\\d|7000)\\d{7}|[3689]\\d{7}", , , , , , , [8, 10, 11]], [
      ,
      ,
      "662[0-24-9]\\d{4}|6(?:[0-578]\\d|6[013-57-9]|9[0-35-9])\\d{5}",
      ,
      ,
      ,
      "61234567",
      ,
      ,
      [8]
    ], [, , "80[1-9]\\d{5}|(?:8[1-9]|9[0-8])\\d{6}", , , , "81234567", , , [8]], [, , "(?:18|8)00\\d{7}", , , , "18001234567", , , [10, 11]], [, , "1900\\d{7}", , , , "19001234567", , , [11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:3[12]\\d|666)\\d{5}", , , , "31234567", , , [8]], "SG", 65, "0[0-3]\\d", , , , , , , , [[, "(\\d{4,5})", "$1", ["1[013-9]|77", "1(?:[013-8]|9(?:0[1-9]|[1-9]))|77"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[369]|8(?:0[1-9]|[1-9])"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"]], [
      ,
      "(\\d{4})(\\d{4})(\\d{3})",
      "$1 $2 $3",
      ["7"]
    ], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]]], [[, "(\\d{4})(\\d{4})", "$1 $2", ["[369]|8(?:0[1-9]|[1-9])"]], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"]], [, "(\\d{4})(\\d{4})(\\d{3})", "$1 $2 $3", ["7"]], [, "(\\d{4})(\\d{3})(\\d{4})", "$1 $2 $3", ["1"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "7000\\d{7}", , , , "70001234567", , , [11]], , , [, , , , , , , , , [-1]]],
    SH: [, [, , "(?:[256]\\d|8)\\d{3}", , , , , , , [4, 5]], [, , "2(?:[0-57-9]\\d|6[4-9])\\d\\d", , , , "22158"], [, , "[56]\\d{4}", , , , "51234", , , [5]], [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "262\\d\\d", , , , "26212", , , [5]], "SH", 290, "00", , , , , , , , , , [, , , , , , , , , [-1]], 1, "[256]", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SI: [, [, , "[1-7]\\d{7}|8\\d{4,7}|90\\d{4,6}", , , , , , , [5, 6, 7, 8]], [, , "(?:[1-357][2-8]|4[24-8])\\d{6}", , , , "12345678", , , [8], [7]], [, , "65(?:[178]\\d|5[56]|6[01])\\d{4}|(?:[37][01]|4[013]|51|6[489])\\d{6}", , , , "31234567", , , [8]], [, , "80\\d{4,6}", , , , "80123456", , , [6, 7, 8]], [, , "89[1-3]\\d{2,5}|90\\d{4,6}", , , , "90123456"], [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , "(?:59\\d\\d|8(?:1(?:[67]\\d|8[0-589])|2(?:0\\d|2[0-37-9]|8[0-2489])|3[389]\\d))\\d{4}", , , , "59012345", , , [8]], "SI", 386, "00|10(?:22|66|88|99)", "0", , , "0", , "00", , [[, "(\\d{2})(\\d{3,6})", "$1 $2", ["8[09]|9"], "0$1"], [, "(\\d{3})(\\d{5})", "$1 $2", ["59|8"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[37][01]|4[013]|51|6"], "0$1"], [, "(\\d)(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[1-57]"], "(0$1)"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SJ: [, [
      ,
      ,
      "0\\d{4}|(?:[489]\\d|79)\\d{6}",
      ,
      ,
      ,
      ,
      ,
      ,
      [5, 8]
    ], [, , "79\\d{6}", , , , "79123456", , , [8]], [, , "45(?:[0-24-9]\\d|3[0-57-9])\\d{4}|(?:4[016-8]|9\\d)\\d{6}", , , , "41234567", , , [8]], [, , "80[01]\\d{5}", , , , "80012345", , , [8]], [, , "82[09]\\d{5}", , , , "82012345", , , [8]], [, , "810(?:0[0-6]|[2-8]\\d)\\d{3}", , , , "81021234", , , [8]], [, , "880\\d{5}", , , , "88012345", , , [8]], [, , "85[0-5]\\d{5}", , , , "85012345", , , [8]], "SJ", 47, "00", , , , , , , , , , [, , , , , , , , , [-1]], , "79", [, , , , , , , , , [-1]], [, , "(?:0[235-9]|81(?:0(?:0[7-9]|1\\d)|5\\d\\d))\\d{3}", , , , "02000"], , , [
      ,
      ,
      "81[23]\\d{5}",
      ,
      ,
      ,
      "81212345",
      ,
      ,
      [8]
    ]],
    SK: [
      ,
      [, , "[2-689]\\d{8}|[2-59]\\d{6}|[2-5]\\d{5}", , , , , , , [6, 7, 9]],
      [, , "(?:2(?:16|[2-9]\\d{3})|(?:(?:[3-5][1-8]\\d|819)\\d|601[1-5])\\d)\\d{4}|(?:2|[3-5][1-8])1[67]\\d{3}|[3-5][1-8]16\\d\\d", , , , "221234567"],
      [, , "909[1-9]\\d{5}|9(?:0[1-8]|1[0-24-9]|4[03-57-9]|5\\d)\\d{6}", , , , "912123456", , , [9]],
      [, , "800\\d{6}", , , , "800123456", , , [9]],
      [, , "9(?:00|[78]\\d)\\d{6}", , , , "900123456", , , [9]],
      [, , "8[5-9]\\d{7}", , , , "850123456", , , [9]],
      [, , , , , , , , , [-1]],
      [, , "6(?:02|5[0-4]|9[0-6])\\d{6}", , , , "690123456", , , [9]],
      "SK",
      421,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d)(\\d{2})(\\d{3,4})", "$1 $2 $3", ["21"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2,3})", "$1 $2 $3", ["[3-5][1-8]1", "[3-5][1-8]1[67]"], "0$1"], [, "(\\d{4})(\\d{3})", "$1 $2", ["909", "9090"], "0$1"], [, "(\\d)(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3 $4", ["2"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[689]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[3-5]"], "0$1"]],
      [[, "(\\d)(\\d{2})(\\d{3,4})", "$1 $2 $3", ["21"], "0$1"], [, "(\\d{2})(\\d{2})(\\d{2,3})", "$1 $2 $3", [
        "[3-5][1-8]1",
        "[3-5][1-8]1[67]"
      ], "0$1"], [, "(\\d)(\\d{3})(\\d{3})(\\d{2})", "$1 $2 $3 $4", ["2"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[689]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[3-5]"], "0$1"]],
      [, , "9090\\d{3}", , , , "9090123", , , [7]],
      ,
      ,
      [, , "9090\\d{3}|(?:602|8(?:00|[5-9]\\d)|9(?:00|[78]\\d))\\d{6}", , , , , , , [7, 9]],
      [, , "96\\d{7}", , , , "961234567", , , [9]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    SL: [, [, , "(?:[237-9]\\d|66)\\d{6}", , , , , , , [8], [6]], [, , "22[2-4][2-9]\\d{4}", , , , "22221234", , , , [6]], [
      ,
      ,
      "(?:25|3[0-5]|66|7\\d|8[08]|9[09])\\d{6}",
      ,
      ,
      ,
      "25123456"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SL", 232, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{6})", "$1 $2", ["[236-9]"], "(0$1)"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SM: [, [, , "(?:0549|[5-7]\\d)\\d{6}", , , , , , , [8, 10], [6]], [, , "0549(?:8[0157-9]|9\\d)\\d{4}", , , , "0549886377", , , [10], [6]], [, , "6[16]\\d{6}", , , , "66661212", , , [8]], [, , , , , , , , , [-1]], [, , "7[178]\\d{6}", , , , "71123456", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      "5[158]\\d{6}",
      ,
      ,
      ,
      "58001110",
      ,
      ,
      [8]
    ], "SM", 378, "00", , , , "([89]\\d{5})$", "0549$1", , , [[, "(\\d{6})", "$1", ["[89]"]], [, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-7]"]], [, "(\\d{4})(\\d{6})", "$1 $2", ["0"]]], [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[5-7]"]], [, "(\\d{4})(\\d{6})", "$1 $2", ["0"]]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SN: [
      ,
      [, , "(?:[378]\\d|93)\\d{7}", , , , , , , [9]],
      [, , "3(?:[026]\\d|3[89])\\d{6}", , , , "301012345"],
      [, , "7(?:[015-8]\\d|21|90)\\d{6}", , , , "701234567"],
      [, , "800\\d{6}", , , , "800123456"],
      [, , "88[4689]\\d{6}", , , , "884123456"],
      [, , "81[02468]\\d{6}", , , , "810123456"],
      [, , , , , , , , , [-1]],
      [, , "(?:39|93)\\d{7}", , , , "933301234"],
      "SN",
      221,
      "00",
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"]], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[379]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    SO: [, [, , "[346-9]\\d{8}|[12679]\\d{7}|[1-5]\\d{6}|[1348]\\d{5}", , , , , , , [6, 7, 8, 9]], [
      ,
      ,
      "(?:1\\d|2[0-79]|3[0-46-8]|4[0-7]|5[57-9])\\d{5}|(?:[134]\\d|8[125])\\d{4}",
      ,
      ,
      ,
      "4012345",
      ,
      ,
      [6, 7]
    ], [, , "(?:(?:15|(?:3[59]|4[89]|6\\d|7[0-35-9]|8[08])\\d|9(?:0\\d|[2-9]))\\d|2(?:4\\d|8))\\d{5}|(?:[67]\\d\\d|904)\\d{5}", , , , "71123456", , , [7, 8, 9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SO", 252, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{4})", "$1 $2", ["8[125]"]], [, "(\\d{6})", "$1", ["[134]"]], [, "(\\d)(\\d{6})", "$1 $2", ["[15]|2[0-79]|3[0-46-8]|4[0-7]"]], [, "(\\d{2})(\\d{5,7})", "$1 $2", ["1|28|9[2-9]"]], [, "(\\d)(\\d{7})", "$1 $2", ["[267]|904"]], [
      ,
      "(\\d{2})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["[346-9]"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SR: [, [, , "(?:[2-5]|[6-9]\\d)\\d{5}", , , , , , , [6, 7]], [, , "(?:2[1-3]|3[0-7]|4\\d|5[2-578])\\d{4}", , , , "211234", , , [6]], [, , "(?:6[08]|7[1-7]|8[1-9])\\d{5}", , , , "7412345", , , [7]], [, , "80\\d{5}", , , , "8012345", , , [7]], [, , "90\\d{5}", , , , "9012345", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:56|91\\d)\\d{4}", , , , "561234"], "SR", 597, "00", , , , , , , , [
      [, "(\\d{2})(\\d{2})(\\d{2})", "$1-$2-$3", ["56"]],
      [, "(\\d{3})(\\d{3})", "$1-$2", ["[2-5]"]],
      [, "(\\d{3})(\\d{4})", "$1-$2", ["[6-9]"]]
    ], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SS: [, [, , "[19]\\d{8}", , , , , , , [9]], [, , "1[89]\\d{7}", , , , "181234567"], [, , "(?:12|9[1257-9])\\d{7}", , , , "977123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SS", 211, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[19]"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    ST: [, [, , "(?:22|9\\d)\\d{5}", , , , , , , [7]], [
      ,
      ,
      "22\\d{5}",
      ,
      ,
      ,
      "2221234"
    ], [, , "900[5-9]\\d{3}|9(?:0[1-9]|[89]\\d)\\d{4}", , , , "9812345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "ST", 239, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[29]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SV: [, [, , "[25-7]\\d{7}|(?:80\\d|900)\\d{4}(?:\\d{4})?", , , , , , , [7, 8, 11]], [, , "2(?:79(?:0[0347-9]|[1-9]\\d)|89(?:0[024589]|[1-9]\\d))\\d{3}|2(?:[1-69]\\d|[78][0-8])\\d{5}", , , , "21234567", , , [8]], [
      ,
      ,
      "[5-7]\\d{7}",
      ,
      ,
      ,
      "70123456",
      ,
      ,
      [8]
    ], [, , "800\\d{8}|80[01]\\d{4}", , , , "8001234", , , [7, 11]], [, , "900\\d{4}(?:\\d{4})?", , , , "9001234", , , [7, 11]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SV", 503, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[89]"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["[25-7]"]], [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["[89]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SX: [
      ,
      [, , "7215\\d{6}|(?:[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]],
      [, , "7215(?:4[2-8]|8[39]|9[056])\\d{4}", , , , "7215425678", , , , [7]],
      [, , "7215(?:1[02]|2\\d|5[034679]|8[0-24-8])\\d{4}", , , , "7215205678", , , , [7]],
      [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002123456"],
      [, , "900[2-9]\\d{6}", , , , "9002123456"],
      [, , , , , , , , , [-1]],
      [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"],
      [, , , , , , , , , [-1]],
      "SX",
      1,
      "011",
      "1",
      ,
      ,
      "(5\\d{6})$|1",
      "721$1",
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      "721",
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    SY: [, [, , "[1-359]\\d{8}|[1-5]\\d{7}", , , , , , , [8, 9], [6, 7]], [, , "(?:1(?:[1478]\\d|[2356])|21\\d|3(?:[13]\\d|4)|4[134]|5[1-3])\\d{6}|2[1-5]\\d{6}", , , , "112345678", , , , [6, 7]], [, , "(?:50|9[03-689])\\d{7}", , , , "944567890", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "SY", 963, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[1-4]|5[1-3]"], "0$1", , 1], [
      ,
      "(\\d{3})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["[59]"],
      "0$1",
      ,
      1
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    SZ: [, [, , "0800\\d{4}|(?:[237]\\d|900)\\d{6}", , , , , , , [8, 9]], [, , "[23][2-5]\\d{6}", , , , "22171234", , , [8]], [, , "7[5-9]\\d{6}", , , , "76123456", , , [8]], [, , "0800\\d{4}", , , , "08001234", , , [8]], [, , "900\\d{6}", , , , "900012345", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "70\\d{6}", , , , "70012345", , , [8]], "SZ", 268, "00", , , , , , , , [[, "(\\d{4})(\\d{4})", "$1 $2", ["[0237]"]], [, "(\\d{5})(\\d{4})", "$1 $2", ["9"]]], , [, , , , , , , , , [-1]], , , [
      ,
      ,
      "0800\\d{4}",
      ,
      ,
      ,
      ,
      ,
      ,
      [8]
    ], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TA: [, [, , "8\\d{3}", , , , , , , [4]], [, , "8\\d{3}", , , , "8999"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TA", 290, "00", , , , , , , , , , [, , , , , , , , , [-1]], , "8", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TC: [, [, , "(?:[58]\\d\\d|649|900)\\d{7}", , , , , , , [10], [7]], [, , "649(?:266|712|9(?:4\\d|50))\\d{4}", , , , "6497121234", , , , [7]], [, , "649(?:2(?:3[129]|4[1-79])|3\\d\\d|4[34][1-3])\\d{4}", , , , "6492311234", , , , [7]], [
      ,
      ,
      "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "8002345678"
    ], [, , "900[2-9]\\d{6}", , , , "9002345678"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , "649(?:71[01]|966)\\d{4}", , , , "6497101234", , , , [7]], "TC", 1, "011", "1", , , "([2-479]\\d{6})$|1", "649$1", , , , , [, , , , , , , , , [-1]], , "649", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TD: [, [, , "(?:22|[3689]\\d|77)\\d{6}", , , , , , , [8]], [, , "22(?:[37-9]0|5[0-5]|6[89])\\d{4}", , , , "22501234"], [, , "(?:3[01]|[69]\\d|77|8[5-7])\\d{6}", , , , "63012345"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TD", 235, "00|16", , , , , , "00", , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[236-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TG: [, [, , "[279]\\d{7}", , , , , , , [8]], [, , "2(?:2[2-7]|3[23]|4[45]|55|6[67]|77)\\d{5}", , , , "22212345"], [
      ,
      ,
      "(?:7[0-389]|9[0-36-9])\\d{6}",
      ,
      ,
      ,
      "90112345"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TG", 228, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[279]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TH: [, [, , "(?:001800|[2-57]|[689]\\d)\\d{7}|1\\d{7,9}", , , , , , , [8, 9, 10, 13]], [, , "(?:1[0689]|2\\d|3[2-9]|4[2-5]|5[2-6]|7[3-7])\\d{6}", , , , "21234567", , , [8]], [, , "(?:(?:14|[89]\\d)\\d\\d|6(?:[1-6]\\d\\d|7(?:1[0-8]|2[4-7]|3[1-6])))\\d{5}", , , , "812345678", , , [9]], [
      ,
      ,
      "(?:001800\\d|1800)\\d{6}",
      ,
      ,
      ,
      "1800123456",
      ,
      ,
      [10, 13]
    ], [, , "1900\\d{6}", , , , "1900123456", , , [10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "6[08]\\d{7}", , , , "601234567", , , [9]], "TH", 66, "00[1-9]", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{4})", "$1 $2 $3", ["2"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[13-9]"], "0$1"], [, "(\\d{4})(\\d{3})(\\d{3})", "$1 $2 $3", ["1"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TJ: [
      ,
      [, , "(?:[0-57-9]\\d|66)\\d{7}", , , , , , , [9], [3, 5, 6, 7]],
      [
        ,
        ,
        "(?:3(?:1[3-5]|2[245]|3[12]|4[24-7]|5[25]|72)|4(?:46|74|87))\\d{6}",
        ,
        ,
        ,
        "372123456",
        ,
        ,
        ,
        [3, 5, 6, 7]
      ],
      [, , "(?:33[03-9]|4(?:1[18]|4[02-479])|81[1-9])\\d{6}|(?:[09]\\d|1[0-27-9]|2[0-27]|3[08]|40|5[05]|66|7[0157-9]|8[07-9])\\d{7}", , , , "917123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "TJ",
      992,
      "810",
      ,
      ,
      ,
      ,
      ,
      "8~10",
      ,
      [[, "(\\d{6})(\\d)(\\d{2})", "$1 $2 $3", ["331", "3317"]], [, "(\\d{3})(\\d{2})(\\d{4})", "$1 $2 $3", ["44[02-479]|[34]7"]], [, "(\\d{4})(\\d)(\\d{4})", "$1 $2 $3", ["3(?:[1245]|3[12])"]], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["\\d"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    TK: [, [, , "[2-47]\\d{3,6}", , , , , , , [4, 5, 6, 7]], [, , "(?:2[2-4]|[34]\\d)\\d{2,5}", , , , "3101"], [, , "7[2-4]\\d{2,5}", , , , "7290"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TK", 690, "00", , , , , , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TL: [, [, , "7\\d{7}|(?:[2-47]\\d|[89]0)\\d{5}", , , , , , , [7, 8]], [, , "(?:2[1-5]|3[1-9]|4[1-4])\\d{5}", , , , "2112345", , , [7]], [
      ,
      ,
      "7[2-8]\\d{6}",
      ,
      ,
      ,
      "77212345",
      ,
      ,
      [8]
    ], [, , "80\\d{5}", , , , "8012345", , , [7]], [, , "90\\d{5}", , , , "9012345", , , [7]], [, , , , , , , , , [-1]], [, , "70\\d{5}", , , , "7012345", , , [7]], [, , , , , , , , , [-1]], "TL", 670, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[2-489]|70"]], [, "(\\d{4})(\\d{4})", "$1 $2", ["7"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TM: [, [, , "[1-7]\\d{7}", , , , , , , [8]], [, , "(?:1(?:2\\d|3[1-9])|2(?:22|4[0-35-8])|3(?:22|4[03-9])|4(?:22|3[128]|4\\d|6[15])|5(?:22|5[7-9]|6[014-689]))\\d{5}", , , , "12345678"], [
      ,
      ,
      "(?:6\\d|7[12])\\d{6}",
      ,
      ,
      ,
      "66123456"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TM", 993, "810", "8", , , "8", , "8~10", , [[, "(\\d{2})(\\d{2})(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["12"], "(8 $1)"], [, "(\\d{3})(\\d)(\\d{2})(\\d{2})", "$1 $2-$3-$4", ["[1-5]"], "(8 $1)"], [, "(\\d{2})(\\d{6})", "$1 $2", ["[67]"], "8 $1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TN: [, [, , "[2-57-9]\\d{7}", , , , , , , [8]], [, , "81200\\d{3}|(?:3[0-2]|7\\d)\\d{6}", , , , "30010123"], [
      ,
      ,
      "3(?:001|[12]40)\\d{4}|(?:(?:[259]\\d|4[0-8])\\d|3(?:1[1-35]|6[0-4]|91))\\d{5}",
      ,
      ,
      ,
      "20123456"
    ], [, , "8010\\d{4}", , , , "80101234"], [, , "88\\d{6}", , , , "88123456"], [, , "8[12]10\\d{4}", , , , "81101234"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TN", 216, "00", , , , , , , , [[, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-57-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TO: [, [, , "(?:0800|(?:[5-8]\\d\\d|999)\\d)\\d{3}|[2-8]\\d{4}", , , , , , , [5, 7]], [, , "(?:2\\d|3[0-8]|4[0-4]|50|6[09]|7[0-24-69]|8[05])\\d{3}", , , , "20123", , , [5]], [
      ,
      ,
      "(?:5(?:4[0-5]|5[4-6])|6(?:[09]\\d|3[02]|8[15-9])|(?:7\\d|8[46-9])\\d|999)\\d{4}",
      ,
      ,
      ,
      "7715123",
      ,
      ,
      [7]
    ], [, , "0800\\d{3}", , , , "0800222", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "55[0-37-9]\\d{4}", , , , "5510123", , , [7]], "TO", 676, "00", , , , , , , , [[, "(\\d{2})(\\d{3})", "$1-$2", ["[2-4]|50|6[09]|7[0-24-69]|8[05]"]], [, "(\\d{4})(\\d{3})", "$1 $2", ["0"]], [, "(\\d{3})(\\d{4})", "$1 $2", ["[5-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TR: [
      ,
      [, , "4\\d{6}|8\\d{11,12}|(?:[2-58]\\d\\d|900)\\d{7}", , , , , , , [7, 10, 12, 13]],
      [
        ,
        ,
        "(?:2(?:1[26]|[28][2468]|[3-5][268]|[67][246])|3(?:[13][28]|[24-6][2468]|[78][02468]|92)|4(?:[16][246]|[23578][2468]|4[26]))\\d{7}",
        ,
        ,
        ,
        "2123456789",
        ,
        ,
        [10]
      ],
      [, , "5(?:61(?:011|61\\d)|82[2-5]\\d\\d)\\d{4}|5(?:[03-5]\\d|1[06]|24|6[24]|7[245]|9[46])\\d{7}", , , , "5012345678", , , [10]],
      [, , "8(?:00\\d{7}(?:\\d{2,3})?|11\\d{7})", , , , "8001234567", , , [10, 12, 13]],
      [, , "(?:8[89]8|900)\\d{7}", , , , "9001234567", , , [10]],
      [, , , , , , , , , [-1]],
      [, , "592(?:21[12]|461)\\d{4}", , , , "5922121234", , , [10]],
      [, , "850\\d{7}", , , , "8500123456", , , [10]],
      "TR",
      90,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d)(\\d{3})", "$1 $2 $3", ["444"], , , 1], [
        ,
        "(\\d{3})(\\d{3})(\\d{4})",
        "$1 $2 $3",
        ["512|8[01589]|90"],
        "0$1",
        ,
        1
      ], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["5"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[24][1-8]|3[1-9]"], "(0$1)", , 1], [, "(\\d{3})(\\d{3})(\\d{6,7})", "$1 $2 $3", ["80"], "0$1", , 1]],
      [[, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["512|8[01589]|90"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["5"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[24][1-8]|3[1-9]"], "(0$1)", , 1], [, "(\\d{3})(\\d{3})(\\d{6,7})", "$1 $2 $3", ["80"], "0$1", , 1]],
      [, , "512\\d{7}", , , , "5123456789", , , [10]],
      ,
      ,
      [, , "(?:444|811\\d{3})\\d{4}", , , , , , , [7, 10]],
      [, , "444\\d{4}", , , , "4441444", , , [7]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    TT: [
      ,
      [, , "(?:[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]],
      [, , "868(?:2(?:01|1[5-9]|[23]\\d|4[0-2])|6(?:0[7-9]|1[02-8]|2[1-9]|[3-69]\\d|7[0-79])|82[124])\\d{4}", , , , "8682211234", , , , [7]],
      [, , "868(?:(?:2[5-9]|3\\d)\\d|4(?:3[0-6]|[6-9]\\d)|6(?:20|78|8\\d)|7(?:0[1-9]|1[02-9]|[2-9]\\d))\\d{4}", , , , "8682911234", , , , [7]],
      [, , "868800\\d{4}|8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"],
      [, , "900[2-9]\\d{6}", , , , "9002345678"],
      [, , , , , , , , , [-1]],
      [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"],
      [, , , , , , , , , [-1]],
      "TT",
      1,
      "011",
      "1",
      ,
      ,
      "([2-46-8]\\d{6})$|1",
      "868$1",
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      "868",
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "868619\\d{4}", , , , "8686191234", , , , [7]]
    ],
    TV: [, [
      ,
      ,
      "(?:2|7\\d\\d|90)\\d{4}",
      ,
      ,
      ,
      ,
      ,
      ,
      [5, 6, 7]
    ], [, , "2[02-9]\\d{3}", , , , "20123", , , [5]], [, , "(?:7[01]\\d|90)\\d{4}", , , , "901234", , , [6, 7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "TV", 688, "00", , , , , , , , [[, "(\\d{2})(\\d{3})", "$1 $2", ["2"]], [, "(\\d{2})(\\d{4})", "$1 $2", ["90"]], [, "(\\d{2})(\\d{5})", "$1 $2", ["7"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    TW: [, [, , "[2-689]\\d{8}|7\\d{9,10}|[2-8]\\d{7}|2\\d{6}", , , , , , , [7, 8, 9, 10, 11]], [
      ,
      ,
      "(?:2[2-8]\\d|370|55[01]|7[1-9])\\d{6}|4(?:(?:0(?:0[1-9]|[2-48]\\d)|1[023]\\d)\\d{4,5}|(?:[239]\\d\\d|4(?:0[56]|12|49))\\d{5})|6(?:[01]\\d{7}|4(?:0[56]|12|24|4[09])\\d{4,5})|8(?:(?:2(?:3\\d|4[0-269]|[578]0|66)|36[24-9]|90\\d\\d)\\d{4}|4(?:0[56]|12|24|4[09])\\d{4,5})|(?:2(?:2(?:0\\d\\d|4(?:0[68]|[249]0|3[0-467]|5[0-25-9]|6[0235689]))|(?:3(?:[09]\\d|1[0-4])|(?:4\\d|5[0-49]|6[0-29]|7[0-5])\\d)\\d)|(?:(?:3[2-9]|5[2-8]|6[0-35-79]|8[7-9])\\d\\d|4(?:2(?:[089]\\d|7[1-9])|(?:3[0-4]|[78]\\d|9[01])\\d))\\d)\\d{3}",
      ,
      ,
      ,
      "221234567",
      ,
      ,
      [8, 9]
    ], [, , "(?:40001[0-2]|9[0-8]\\d{4})\\d{3}", , , , "912345678", , , [9]], [, , "80[0-79]\\d{6}|800\\d{5}", , , , "800123456", , , [8, 9]], [, , "20(?:[013-9]\\d\\d|2)\\d{4}", , , , "203123456", , , [7, 9]], [, , , , , , , , , [-1]], [, , "99\\d{7}", , , , "990123456", , , [9]], [, , "7010(?:[0-2679]\\d|3[0-7]|8[0-5])\\d{5}|70\\d{8}", , , , "7012345678", , , [10, 11]], "TW", 886, "0(?:0[25-79]|19)", "0", "#", , "0", , , , [[, "(\\d{2})(\\d)(\\d{4})", "$1 $2 $3", ["202"], "0$1"], [, "(\\d{3})(\\d{5})", "$1 $2", ["826"], "0$1"], [
      ,
      "(\\d{3})(\\d{2})(\\d{3})",
      "$1 $2 $3",
      ["83"],
      "0$1"
    ], [, "(\\d{2})(\\d{2})(\\d{4})", "$1 $2 $3", ["82"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[25]0|37|49|8[09]"], "0$1"], [, "(\\d)(\\d{3,4})(\\d{4})", "$1 $2 $3", ["[23568]|4(?:0[02-48]|[1-478])|7[1-9]", "[23568]|4(?:0[2-48]|[1-478])|(?:400|7)[1-9]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[49]"], "0$1"], [, "(\\d{2})(\\d{4})(\\d{4,5})", "$1 $2 $3", ["7"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "50[0-46-9]\\d{6}", , , , "500123456", , , [9]], , , [, , , , , , , , , [-1]]],
    TZ: [, [
      ,
      ,
      "(?:[25-8]\\d|41|90)\\d{7}",
      ,
      ,
      ,
      ,
      ,
      ,
      [9]
    ], [, , "2[2-8]\\d{7}", , , , "222345678"], [, , "(?:6[0-35-9]|7\\d)\\d{7}", , , , "621234567"], [, , "80[08]\\d{6}", , , , "800123456"], [, , "90\\d{7}", , , , "900123456"], [, , "8(?:40|6[01])\\d{6}", , , , "840123456"], [, , , , , , , , , [-1]], [, , "41\\d{7}", , , , "412345678"], "TZ", 255, "00[056]", "0", , , "0", , , , [[, "(\\d{3})(\\d{2})(\\d{4})", "$1 $2 $3", ["[89]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[24]"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["5"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[67]"], "0$1"]], , [, , , , , , , , , [-1]], , , [
      ,
      ,
      "(?:8(?:[04]0|6[01])|90\\d)\\d{6}"
    ], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    UA: [
      ,
      [, , "[89]\\d{9}|[3-9]\\d{8}", , , , , , , [9, 10], [5, 6, 7]],
      [, , "(?:3[1-8]|4[13-8]|5[1-7]|6[12459])\\d{7}", , , , "311234567", , , [9], [5, 6, 7]],
      [, , "790\\d{6}|(?:39|50|6[36-8]|7[1-357]|9[1-9])\\d{7}", , , , "501234567", , , [9]],
      [, , "800[1-8]\\d{5,6}", , , , "800123456"],
      [, , "900[239]\\d{5,6}", , , , "900212345"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "89[1-579]\\d{6}", , , , "891234567", , , [9]],
      "UA",
      380,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      "0~0",
      ,
      [[
        ,
        "(\\d{3})(\\d{3})(\\d{3})",
        "$1 $2 $3",
        ["6[12][29]|(?:3[1-8]|4[136-8]|5[12457]|6[49])2|(?:56|65)[24]", "6[12][29]|(?:35|4[1378]|5[12457]|6[49])2|(?:56|65)[24]|(?:3[1-46-8]|46)2[013-9]"],
        "0$1"
      ], [, "(\\d{4})(\\d{5})", "$1 $2", ["3[1-8]|4(?:[1367]|[45][6-9]|8[4-6])|5(?:[1-5]|6[0135689]|7[4-6])|6(?:[12][3-7]|[459])", "3[1-8]|4(?:[1367]|[45][6-9]|8[4-6])|5(?:[1-5]|6(?:[015689]|3[02389])|7[4-6])|6(?:[12][3-7]|[459])"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["[3-7]|89|9[1-9]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[89]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    UG: [
      ,
      [, , "800\\d{6}|(?:[29]0|[347]\\d)\\d{7}", , , , , , , [9], [5, 6, 7]],
      [, , "20(?:(?:24[09]|30[67])\\d|6(?:00[0-2]|30[0-4]))\\d{3}|(?:20(?:[017]\\d|2[5-9]|3[1-4]|5[0-4]|6[15-9])|[34]\\d{3})\\d{5}", , , , "312345678", , , , [5, 6, 7]],
      [, , "7(?:28|34)0\\d{5}|7(?:[014-8]\\d|2[01467]|3[0167]|9[0-589])\\d{6}", , , , "712345678"],
      [, , "800[1-3]\\d{5}", , , , "800123456"],
      [, , "90[1-3]\\d{6}", , , , "901123456"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "UG",
      256,
      "00[057]",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{4})(\\d{5})", "$1 $2", ["202", "2024", "20240"], "0$1"], [, "(\\d{3})(\\d{6})", "$1 $2", ["20[0-35-7]|4(?:6[45]|[7-9])|[7-9]", "20(?:[0135-7]|2[5-9])|4(?:6[45]|[7-9])|[7-9]"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["[2-4]"], "0$1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    US: [, [, , "[2-9]\\d{9}|3\\d{6}", , , , , , , [10], [7]], [
      ,
      ,
      "(?:472[2-47-9]|983[2-57-9])\\d{6}|(?:2(?:0[1-35-9]|1[02-9]|2[03-57-9]|3[1459]|4[08]|5[1-46]|6[0279]|7[02469]|8[13])|3(?:0[1-57-9]|1[02-9]|2[013-79]|3[0-24679]|4[167]|5[0-3]|6[01349]|8[056])|4(?:0[124-9]|1[02-579]|2[3-5]|3[0245]|4[023578]|58|6[349]|7[0589]|8[04])|5(?:0[1-57-9]|1[0235-8]|20|3[0149]|4[01]|5[179]|6[1-47]|7[0-5]|8[0256])|6(?:0[1-35-9]|1[024-9]|2[03689]|3[016]|4[0156]|5[01679]|6[0-279]|78|8[0-269])|7(?:0[1-46-8]|1[2-9]|2[04-8]|3[0-2478]|4[0378]|5[47]|6[02359]|7[0-59]|8[156])|8(?:0[1-68]|1[02-8]|2[0168]|3[0-2589]|4[03578]|5[046-9]|6[02-5]|7[028])|9(?:0[1346-9]|1[02-9]|2[0589]|3[0146-8]|4[01357-9]|5[12469]|7[0-3589]|8[04-69]))[2-9]\\d{6}",
      ,
      ,
      ,
      "2015550123",
      ,
      ,
      ,
      [7]
    ], [
      ,
      ,
      "(?:472[2-47-9]|983[2-57-9])\\d{6}|(?:2(?:0[1-35-9]|1[02-9]|2[03-57-9]|3[1459]|4[08]|5[1-46]|6[0279]|7[02469]|8[13])|3(?:0[1-57-9]|1[02-9]|2[013-79]|3[0-24679]|4[167]|5[0-3]|6[01349]|8[056])|4(?:0[124-9]|1[02-579]|2[3-5]|3[0245]|4[023578]|58|6[349]|7[0589]|8[04])|5(?:0[1-57-9]|1[0235-8]|20|3[0149]|4[01]|5[179]|6[1-47]|7[0-5]|8[0256])|6(?:0[1-35-9]|1[024-9]|2[03689]|3[016]|4[0156]|5[01679]|6[0-279]|78|8[0-269])|7(?:0[1-46-8]|1[2-9]|2[04-8]|3[0-2478]|4[0378]|5[47]|6[02359]|7[0-59]|8[156])|8(?:0[1-68]|1[02-8]|2[0168]|3[0-2589]|4[03578]|5[046-9]|6[02-5]|7[028])|9(?:0[1346-9]|1[02-9]|2[0589]|3[0146-8]|4[01357-9]|5[12469]|7[0-3589]|8[04-69]))[2-9]\\d{6}",
      ,
      ,
      ,
      "2015550123",
      ,
      ,
      ,
      [7]
    ], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"], [, , "900[2-9]\\d{6}", , , , "9002345678"], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "US", 1, "011", "1", , , "1", , , 1, [[, "(\\d{3})(\\d{4})", "$1-$2", ["310"], , , 1], [
      ,
      "(\\d{3})(\\d{4})",
      "$1-$2",
      ["[24-9]|3(?:[02-9]|1[1-9])"]
    ], [, "(\\d{3})(\\d{3})(\\d{4})", "($1) $2-$3", ["[2-9]"], , , 1]], [[, "(\\d{3})(\\d{4})", "$1-$2", ["310"], , , 1], [, "(\\d{3})(\\d{3})(\\d{4})", "$1-$2-$3", ["[2-9]"]]], [, , , , , , , , , [-1]], 1, , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    UY: [, [, , "0004\\d{2,9}|[1249]\\d{7}|2\\d{3,4}|(?:[49]\\d|80)\\d{5}", , , , , , , [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]], [, , "(?:1(?:770|9(?:20|[89]7))|(?:2\\d|4[2-7])\\d\\d)\\d{4}", , , , "21231234", , , [8], [7]], [, , "9[1-9]\\d{6}", , , , "94231234", , , [8]], [
      ,
      ,
      "0004\\d{2,9}|(?:405|80[05])\\d{4}",
      ,
      ,
      ,
      "8001234",
      ,
      ,
      [6, 7, 8, 9, 10, 11, 12, 13]
    ], [, , "90[0-8]\\d{4}", , , , "9001234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "UY", 598, "0(?:0|1[3-9]\\d)", "0", " int. ", , "0", , "00", , [[, "(\\d{4,5})", "$1", ["21"]], [, "(\\d{3})(\\d{3,4})", "$1 $2", ["0"]], [, "(\\d{3})(\\d{4})", "$1 $2", ["[49]0|8"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["9"], "0$1"], [, "(\\d{4})(\\d{4})", "$1 $2", ["[124]"]], [, "(\\d{3})(\\d{3})(\\d{2,4})", "$1 $2 $3", ["0"]], [, "(\\d{3})(\\d{3})(\\d{3})(\\d{2,4})", "$1 $2 $3 $4", ["0"]]], , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]], [, , "21\\d{2,3}", , , , "21123", , , [4, 5]], , , [, , , , , , , , , [-1]]],
    UZ: [, [, , "(?:20|33|[5-9]\\d)\\d{7}", , , , , , , [9]], [, , "(?:55\\d\\d|6(?:1(?:22|3[124]|4[1-4]|5[1-3578]|64)|2(?:22|3[0-57-9]|41)|5(?:22|3[3-7]|5[024-8])|[69]\\d\\d|7(?:[23]\\d|7[69]))|7(?:[168]\\d\\d|2(?:22|3[13-57-9]|4[1-3579]|5[14])|3(?:2\\d|3[1578]|4[1-35-7]|5[1-57]|61)|4(?:2\\d|3[1-579]|7[1-79])|5(?:22|5[1-9]|6[1457])|9(?:22|5[1-9])))\\d{5}", , , , "669050123"], [
      ,
      ,
      "(?:(?:[25]0|33|8[078]|9[0-57-9])\\d{3}|6(?:1(?:2(?:2[01]|98)|35[0-4]|50\\d|61[23]|7(?:[01][017]|4\\d|55|9[5-9]))|2(?:(?:11|7\\d)\\d|2(?:[12]1|9[01379])|5(?:[126]\\d|3[0-4]))|5(?:19[01]|2(?:27|9[26])|(?:30|59|7\\d)\\d)|6(?:2(?:1[5-9]|2[0367]|38|41|52|60)|(?:3[79]|9[0-3])\\d|4(?:56|83)|7(?:[07]\\d|1[017]|3[07]|4[047]|5[057]|67|8[0178]|9[79]))|7(?:2(?:24|3[237]|4[5-9]|7[15-8])|5(?:7[12]|8[0589])|7(?:0\\d|[39][07])|9(?:0\\d|7[079])))|7(?:[07]\\d{3}|2(?:2(?:2[79]|95)|3(?:2[5-9]|6[0-6])|57\\d|7(?:0\\d|1[17]|2[27]|3[37]|44|5[057]|66|88))|3(?:2(?:1[0-6]|21|3[469]|7[159])|(?:33|9[4-6])\\d|5(?:0[0-4]|5[579]|9\\d)|7(?:[0-3579]\\d|4[0467]|6[67]|8[078]))|4(?:2(?:29|5[0257]|6[0-7]|7[1-57])|5(?:1[0-4]|8\\d|9[5-9])|7(?:0\\d|1[024589]|2[0-27]|3[0137]|[46][07]|5[01]|7[5-9]|9[079])|9(?:7[015-9]|[89]\\d))|5(?:112|2(?:0\\d|2[29]|[49]4)|3[1568]\\d|52[6-9]|7(?:0[01578]|1[017]|[23]7|4[047]|[5-7]\\d|8[78]|9[079]))|9(?:22[128]|3(?:2[0-4]|7\\d)|57[02569]|7(?:2[05-9]|3[37]|4\\d|60|7[2579]|87|9[07]))))\\d{4}",
      ,
      ,
      ,
      "912345678"
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "UZ", 998, "00", , , , , , , , [[, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["[235-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    VA: [, [, , "0\\d{5,10}|3[0-8]\\d{7,10}|55\\d{8}|8\\d{5}(?:\\d{2,4})?|(?:1\\d|39)\\d{7,8}", , , , , , , [6, 7, 8, 9, 10, 11, 12]], [, , "06698\\d{1,6}", , , , "0669812345", , , [6, 7, 8, 9, 10, 11]], [, , "3[1-9]\\d{8}|3[2-9]\\d{7}", , , , "3123456789", , , [9, 10]], [
      ,
      ,
      "80(?:0\\d{3}|3)\\d{3}",
      ,
      ,
      ,
      "800123456",
      ,
      ,
      [6, 9]
    ], [, , "(?:0878\\d{3}|89(?:2\\d|3[04]|4(?:[0-4]|[5-9]\\d\\d)|5[0-4]))\\d\\d|(?:1(?:44|6[346])|89(?:38|5[5-9]|9))\\d{6}", , , , "899123456", , , [6, 8, 9, 10]], [, , "84(?:[08]\\d{3}|[17])\\d{3}", , , , "848123456", , , [6, 9]], [, , "1(?:78\\d|99)\\d{6}", , , , "1781234567", , , [9, 10]], [, , "55\\d{8}", , , , "5512345678", , , [10]], "VA", 39, "00", , , , , , , , , , [, , , , , , , , , [-1]], , "06698", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , "3[2-8]\\d{9,10}", , , , "33101234501", , , [11, 12]]],
    VC: [
      ,
      [, , "(?:[58]\\d\\d|784|900)\\d{7}", , , , , , , [10], [7]],
      [, , "784(?:266|3(?:6[6-9]|7\\d|8[0-6])|4(?:38|5[0-36-8]|8[0-8])|5(?:55|7[0-2]|93)|638|784)\\d{4}", , , , "7842661234", , , , [7]],
      [, , "784(?:4(?:3[0-5]|5[45]|89|9[0-8])|5(?:2[6-9]|3[0-4])|720)\\d{4}", , , , "7844301234", , , , [7]],
      [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"],
      [, , "900[2-9]\\d{6}", , , , "9002345678"],
      [, , , , , , , , , [-1]],
      [
        ,
        ,
        "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
        ,
        ,
        ,
        "5002345678"
      ],
      [, , "78451[0-2]\\d{4}", , , , "7845101234", , , , [7]],
      "VC",
      1,
      "011",
      "1",
      ,
      ,
      "([2-7]\\d{6})$|1",
      "784$1",
      ,
      ,
      ,
      ,
      [, , , , , , , , , [-1]],
      ,
      "784",
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    VE: [
      ,
      [, , "[68]00\\d{7}|(?:[24]\\d|[59]0)\\d{8}", , , , , , , [10], [7]],
      [, , "(?:2(?:12|3[457-9]|[467]\\d|[58][1-9]|9[1-6])|[4-6]00)\\d{7}", , , , "2121234567", , , , [7]],
      [, , "4(?:1[24-8]|2[246])\\d{7}", , , , "4121234567"],
      [, , "800\\d{7}", , , , "8001234567"],
      [, , "90[01]\\d{7}", , , , "9001234567"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "VE",
      58,
      "00",
      "0",
      ,
      ,
      "0",
      ,
      ,
      ,
      [[, "(\\d{3})(\\d{7})", "$1-$2", ["[24-689]"], "0$1", "$CC $1"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "501\\d{7}", , , , "5010123456", , , , [7]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    VG: [, [, , "(?:284|[58]\\d\\d|900)\\d{7}", , , , , , , [10], [7]], [, , "284(?:229|4(?:22|9[45])|774|8(?:52|6[459]))\\d{4}", , , , "2842291234", , , , [7]], [, , "284(?:245|3(?:0[0-3]|4[0-7]|68|9[34])|4(?:4[0-6]|68|9[69])|5(?:4[0-7]|68|9[69]))\\d{4}", , , , "2843001234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"], [
      ,
      ,
      "900[2-9]\\d{6}",
      ,
      ,
      ,
      "9002345678"
    ], [, , , , , , , , , [-1]], [, , "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}", , , , "5002345678"], [, , , , , , , , , [-1]], "VG", 1, "011", "1", , , "([2-578]\\d{6})$|1", "284$1", , , , , [, , , , , , , , , [-1]], , "284", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    VI: [, [, , "[58]\\d{9}|(?:34|90)0\\d{7}", , , , , , , [10], [7]], [
      ,
      ,
      "340(?:2(?:0\\d|10|2[06-8]|4[49]|77)|3(?:32|44)|4(?:2[23]|44|7[34]|89)|5(?:1[34]|55)|6(?:2[56]|4[23]|77|9[023])|7(?:1[2-57-9]|2[57]|7\\d)|884|998)\\d{4}",
      ,
      ,
      ,
      "3406421234",
      ,
      ,
      ,
      [7]
    ], [, , "340(?:2(?:0\\d|10|2[06-8]|4[49]|77)|3(?:32|44)|4(?:2[23]|44|7[34]|89)|5(?:1[34]|55)|6(?:2[56]|4[23]|77|9[023])|7(?:1[2-57-9]|2[57]|7\\d)|884|998)\\d{4}", , , , "3406421234", , , , [7]], [, , "8(?:00|33|44|55|66|77|88)[2-9]\\d{6}", , , , "8002345678"], [, , "900[2-9]\\d{6}", , , , "9002345678"], [, , , , , , , , , [-1]], [
      ,
      ,
      "52(?:3(?:[2-46-9][02-9]\\d|5(?:[02-46-9]\\d|5[0-46-9]))|4(?:[2-478][02-9]\\d|5(?:[034]\\d|2[024-9]|5[0-46-9])|6(?:0[1-9]|[2-9]\\d)|9(?:[05-9]\\d|2[0-5]|49)))\\d{4}|52[34][2-9]1[02-9]\\d{4}|5(?:00|2[125-9]|3[23]|44|66|77|88)[2-9]\\d{6}",
      ,
      ,
      ,
      "5002345678"
    ], [, , , , , , , , , [-1]], "VI", 1, "011", "1", , , "([2-9]\\d{6})$|1", "340$1", , 1, , , [, , , , , , , , , [-1]], , "340", [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    VN: [, [, , "[12]\\d{9}|[135-9]\\d{8}|[16]\\d{6,7}|7\\d{6}", , , , , , , [7, 8, 9, 10]], [, , "2(?:0[3-9]|1[0-689]|2[0-25-9]|[38][2-9]|4[2-8]|5[124-9]|6[0-39]|7[0-7]|9[0-4679])\\d{7}", , , , "2101234567", , , [10]], [, , "121[0-3]\\d{5}|(?:160|(?:3\\d|7[06-9])\\d|5(?:[1689]\\d|2[238]|59)|8(?:[1-8]\\d|9[6-9])|9(?:[0-8]\\d|9[013-9]))\\d{6}", , , , "912345678", , , [9]], [
      ,
      ,
      "1800\\d{4,6}|12(?:0[13]|28)\\d{4}",
      ,
      ,
      ,
      "1800123456",
      ,
      ,
      [8, 9, 10]
    ], [, , "1900\\d{4,6}", , , , "1900123456", , , [8, 9, 10]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "672\\d{6}", , , , "672012345", , , [9]], "VN", 84, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[17]99"], "0$1", , 1], [, "(\\d{3})(\\d{4,5})", "$1 $2", ["69"], "0$1", , 1], [, "(\\d{4})(\\d{4,6})", "$1 $2", ["1(?:2[02]|[89])"], , , 1], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[26]|6"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[357-9]"], "0$1", , 1], [
      ,
      "(\\d{2})(\\d{4})(\\d{4})",
      "$1 $2 $3",
      ["2[48]"],
      "0$1",
      ,
      1
    ], [, "(\\d{3})(\\d{4})(\\d{3})", "$1 $2 $3", ["2"], "0$1", , 1]], [[, "(\\d{4})(\\d{4,6})", "$1 $2", ["1(?:2[02]|[89])"], , , 1], [, "(\\d{2})(\\d{3})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["1[26]|6"], "0$1", , 1], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[357-9]"], "0$1", , 1], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["2[48]"], "0$1", , 1], [, "(\\d{3})(\\d{4})(\\d{3})", "$1 $2 $3", ["2"], "0$1", , 1]], [, , , , , , , , , [-1]], , , [, , "[17]99\\d{4}|69\\d{5,6}", , , , , , , [7, 8]], [, , "[17]99\\d{4}|69\\d{5,6}", , , , "1992000", , , [7, 8]], , , [, , , , , , , , , [-1]]],
    VU: [, [, , "[57-9]\\d{6}|(?:[238]\\d|48)\\d{3}", , , , , , , [5, 7]], [, , "(?:38[0-8]|48[4-9])\\d\\d|(?:2[02-9]|3[4-7]|88)\\d{3}", , , , "22123", , , [5]], [, , "(?:[58]\\d|7[0-7])\\d{5}", , , , "5912345", , , [7]], [, , "81[18]\\d\\d", , , , "81123", , , [5]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:0[1-9]|1[01])\\d{4}", , , , "9010123", , , [7]], "VU", 678, "00", , , , , , , , [[, "(\\d{3})(\\d{4})", "$1 $2", ["[57-9]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "(?:3[03]|900\\d)\\d{3}", , , , "30123"], , , [, , , , , , , , , [-1]]],
    WF: [, [
      ,
      ,
      "(?:40|72|8\\d{4})\\d{4}|[89]\\d{5}",
      ,
      ,
      ,
      ,
      ,
      ,
      [6, 9]
    ], [, , "72\\d{4}", , , , "721234", , , [6]], [, , "(?:72|8[23])\\d{4}", , , , "821234", , , [6]], [, , "80[0-5]\\d{6}", , , , "800012345", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9[23]\\d{4}", , , , "921234", , , [6]], "WF", 681, "00", , , , , , , , [[, "(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3", ["[47-9]"]], [, "(\\d{3})(\\d{2})(\\d{2})(\\d{2})", "$1 $2 $3 $4", ["8"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , "[48]0\\d{4}", , , , "401234", , , [6]]],
    WS: [, [, , "(?:[2-6]|8\\d{5})\\d{4}|[78]\\d{6}|[68]\\d{5}", , , , , , , [
      5,
      6,
      7,
      10
    ]], [, , "6[1-9]\\d{3}|(?:[2-5]|60)\\d{4}", , , , "22123", , , [5, 6]], [, , "(?:7[1-35-8]|8(?:[3-7]|9\\d{3}))\\d{5}", , , , "7212345", , , [7, 10]], [, , "800\\d{3}", , , , "800123", , , [6]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "WS", 685, "0", , , , , , , , [[, "(\\d{5})", "$1", ["[2-5]|6[1-9]"]], [, "(\\d{3})(\\d{3,7})", "$1 $2", ["[68]"]], [, "(\\d{2})(\\d{5})", "$1 $2", ["7"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    XK: [, [, , "2\\d{7,8}|3\\d{7,11}|(?:4\\d\\d|[89]00)\\d{5}", , , , , , , [
      8,
      9,
      10,
      11,
      12
    ]], [, , "38\\d{6,10}|(?:2[89]|39)(?:0\\d{5,6}|[1-9]\\d{5})", , , , "28012345"], [, , "4[3-9]\\d{6}", , , , "43201234", , , [8]], [, , "800\\d{5}", , , , "80001234", , , [8]], [, , "900\\d{5}", , , , "90001234", , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "XK", 383, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{5})", "$1 $2", ["[89]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3})", "$1 $2 $3", ["[2-4]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["2|39"], "0$1"], [, "(\\d{2})(\\d{7,10})", "$1 $2", ["3"], "0$1"]], , [, , , , , , , , , [-1]], , , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    YE: [, [, , "(?:1|7\\d)\\d{7}|[1-7]\\d{6}", , , , , , , [7, 8, 9], [6]], [, , "78[0-7]\\d{4}|17\\d{6}|(?:[12][2-68]|3[2358]|4[2-58]|5[2-6]|6[3-58]|7[24-6])\\d{5}", , , , "1234567", , , [7, 8], [6]], [, , "7[01378]\\d{7}", , , , "712345678", , , [9]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "YE", 967, "00", "0", , , "0", , , , [[, "(\\d)(\\d{3})(\\d{3,4})", "$1 $2 $3", ["[1-6]|7(?:[24-6]|8[0-7])"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["7"], "0$1"]], , [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    YT: [, [, , "(?:639\\d|7093)\\d{5}|(?:26|80|9\\d)\\d{7}", , , , , , , [9]], [, , "26(?:89\\d|9(?:0[0-467]|15|5[0-4]|6\\d|[78]0))\\d{4}", , , , "269601234"], [, , "(?:639(?:0[0-79]|1[019]|[267]\\d|3[09]|40|5[05-9]|9[04-79])|7093[5-7])\\d{4}", , , , "639012345"], [, , "80\\d{7}", , , , "801234567"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "9(?:(?:39|47)8[01]|769\\d)\\d{4}", , , , "939801234"], "YT", 262, "00", "0", , , "0", , , , , , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], , , [, , , , , , , , , [-1]]],
    ZA: [, [, , "[1-79]\\d{8}|8\\d{4,9}", , , , , , , [5, 6, 7, 8, 9, 10]], [, , "(?:2(?:0330|4302)|52087)0\\d{3}|(?:1[0-8]|2[1-378]|3[1-69]|4\\d|5[1346-8])\\d{7}", , , , "101234567", , , [9]], [, , "(?:1(?:3492[0-25]|4495[0235]|549(?:20|5[01]))|4[34]492[01])\\d{3}|8[1-4]\\d{3,7}|(?:2[27]|47|54)4950\\d{3}|(?:1(?:049[2-4]|9[12]\\d\\d)|(?:50[0-2]|[67]\\d\\d)\\d\\d|8(?:5\\d{3}|7(?:08[67]|158|28[5-9]|310)))\\d{4}|(?:1[6-8]|28|3[2-69]|4[025689]|5[36-8])4920\\d{3}|(?:12|[2-5]1)492\\d{4}", , , , "711234567", , , [
      5,
      6,
      7,
      8,
      9
    ]], [, , "80\\d{7}", , , , "801234567", , , [9]], [, , "(?:86[2-9]|9[0-2]\\d)\\d{6}", , , , "862345678", , , [9]], [, , "860\\d{6}", , , , "860123456", , , [9]], [, , , , , , , , , [-1]], [, , "87(?:08[0-589]|15[0-79]|28[0-4]|31[1-9])\\d{4}|87(?:[02][0-79]|1[0-46-9]|3[02-9]|[4-9]\\d)\\d{5}", , , , "871234567", , , [9]], "ZA", 27, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3,4})", "$1 $2", ["8[1-4]"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{2,3})", "$1 $2 $3", ["8[1-4]"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["860"], "0$1"], [
      ,
      "(\\d{2})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["[1-9]"],
      "0$1"
    ], [, "(\\d{3})(\\d{3})(\\d{4})", "$1 $2 $3", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , "861\\d{6,7}", , , , "861123456", , , [9, 10]], , , [, , , , , , , , , [-1]]],
    ZM: [, [, , "800\\d{6}|(?:21|[579]\\d|63)\\d{7}", , , , , , , [9], [6]], [, , "21[1-8]\\d{6}", , , , "211234567", , , , [6]], [, , "(?:[59][5-8]|7[5-9])\\d{7}", , , , "955123456"], [, , "800\\d{6}", , , , "800123456"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "63\\d{7}", , , , "630123456"], "ZM", 260, "00", "0", , , "0", , , , [[, "(\\d{3})(\\d{3})", "$1 $2", ["[1-9]"]], [
      ,
      "(\\d{3})(\\d{3})(\\d{3})",
      "$1 $2 $3",
      ["[28]"],
      "0$1"
    ], [, "(\\d{2})(\\d{7})", "$1 $2", ["[579]"], "0$1"]], [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[28]"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["[579]"], "0$1"]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    ZW: [, [, , "(?:13|8\\d{4})\\d{5}|[235-8]\\d{8}|[2-689]\\d{6}", , , , , , , [7, 9, 10], [3, 4, 5, 6]], [
      ,
      ,
      "(?:2(?:(?:(?:02[014]|72[03])\\d|48)\\d|2(?:[278]\\d|92)|583)|(?:37[56]|6[78]21\\d)\\d|5(?:483|525\\d\\d))\\d{3}|(?:2(?:0\\d|7[1-7])|(?:55|6[78])\\d)\\d{4}|(?:13|2(?:(?:42|9\\d)\\d|[56]20)|3(?:123|92\\d)|(?:4|542)\\d|6(?:[16]21|52[013])|8(?:[1349]28|523)|9[2-9])\\d{5}",
      ,
      ,
      ,
      "1312345",
      ,
      ,
      [7, 9],
      [3, 4, 5, 6]
    ], [, , "7(?:[1278]\\d|3[1-9]|9[01])\\d{6}", , , , "712345678", , , [9]], [, , "80(?:[01]\\d|20|8[0-8])\\d{3}", , , , "8001234", , , [7]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "86(?:1[12]|22|30|44|55|77|8[368])\\d{6}", , , , "8686123456", , , [10]], "ZW", 263, "00", "0", , , "0", , , , [[, "(\\d{2})(\\d{3,5})", "$1 $2", ["1|2(?:0[0-36-9]|29|58)|67[0-46-9]|(?:55|68)[0-69]"], "0$1"], [, "(\\d{3})(\\d{3,5})", "$1 $2", ["2(?:0[45]|[27]|48)|37|675|(?:55|68)[78]"], "0$1"], [
      ,
      "(\\d)(\\d{3})(\\d{2,4})",
      "$1 $2 $3",
      ["[49]"],
      "0$1"
    ], [, "(\\d{3})(\\d{4})", "$1 $2", ["80"], "0$1"], [, "(\\d{4})(\\d{3,5})", "$1 $2", ["548"], "0$1"], [, "(\\d{2})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["29[013-9]"], "0$1"], [, "(\\d{2})(\\d{7})", "$1 $2", ["[256]|39|8[13-59]"], "(0$1)"], [, "(\\d{2})(\\d{3})(\\d{4})", "$1 $2 $3", ["7"], "0$1"], [, "(\\d{3})(\\d{3})(\\d{3,4})", "$1 $2 $3", ["3"], "0$1"], [, "(\\d{4})(\\d{6})", "$1 $2", ["8"], "0$1"]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    800: [, [, , "(?:00|[1-9]\\d)\\d{6}", , , , , , , [8]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], [, , "(?:00|[1-9]\\d)\\d{6}", , , , "12345678"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "001", 800, , , , , , , , 1, [[, "(\\d{4})(\\d{4})", "$1 $2", ["\\d"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    808: [
      ,
      [, , "[1-9]\\d{7}", , , , , , , [8]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , "[1-9]\\d{7}", , , , "12345678"],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "001",
      808,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      1,
      [[, "(\\d{4})(\\d{4})", "$1 $2", ["[1-9]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    870: [, [, , "7\\d{11}|[235-7]\\d{8}", , , , , , , [9, 12]], [, , , , , , , , , [-1]], [, , "(?:[356]|774[45])\\d{8}|7[6-8]\\d{7}", , , , "301234567"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "2\\d{8}", , , , "201234567", , , [9]], "001", 870, , , , , , , , , [[, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["[235-7]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    878: [, [, , "10\\d{10}", , , , , , , [12]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [-1]
    ], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "10\\d{10}", , , , "101234567890"], "001", 878, , , , , , , , 1, [[, "(\\d{2})(\\d{5})(\\d{5})", "$1 $2 $3", ["1"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    881: [, [, , "6\\d{9}|[0-36-9]\\d{8}", , , , , , , [9, 10]], [, , , , , , , , , [-1]], [, , "6\\d{9}|[0-36-9]\\d{8}", , , , "612345678"], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "001", 881, , , , , , , , , [[, "(\\d)(\\d{3})(\\d{5})", "$1 $2 $3", ["[0-37-9]"]], [
      ,
      "(\\d)(\\d{3})(\\d{5,6})",
      "$1 $2 $3",
      ["6"]
    ]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    882: [
      ,
      [, , "[13]\\d{6}(?:\\d{2,5})?|[19]\\d{7}|(?:[25]\\d\\d|4)\\d{7}(?:\\d{2})?", , , , , , , [7, 8, 9, 10, 11, 12]],
      [, , , , , , , , , [-1]],
      [, , "342\\d{4}|(?:337|49)\\d{6}|(?:3(?:2|47|7\\d{3})|5(?:0\\d{3}|2[0-2]))\\d{7}", , , , "3421234", , , [7, 8, 9, 10, 12]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [
        ,
        ,
        "1(?:3(?:0[0347]|[13][0139]|2[035]|4[013568]|6[0459]|7[06]|8[15-8]|9[0689])\\d{4}|6\\d{5,10})|(?:345\\d|9[89])\\d{6}|(?:10|2(?:3|85\\d)|3(?:[15]|[69]\\d\\d)|4[15-8]|51)\\d{8}",
        ,
        ,
        ,
        "390123456789"
      ],
      "001",
      882,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      [[, "(\\d{2})(\\d{5})", "$1 $2", ["16|342"]], [, "(\\d{2})(\\d{6})", "$1 $2", ["49"]], [, "(\\d{2})(\\d{2})(\\d{4})", "$1 $2 $3", ["1[36]|9"]], [, "(\\d{2})(\\d{4})(\\d{3})", "$1 $2 $3", ["3[23]"]], [, "(\\d{2})(\\d{3,4})(\\d{4})", "$1 $2 $3", ["16"]], [, "(\\d{2})(\\d{4})(\\d{4})", "$1 $2 $3", ["10|23|3(?:[15]|4[57])|4|5[12]"]], [, "(\\d{3})(\\d{4})(\\d{4})", "$1 $2 $3", ["34"]], [, "(\\d{2})(\\d{4,5})(\\d{5})", "$1 $2 $3", ["[1-35]"]]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , "348[57]\\d{7}", , , , "34851234567", , , [11]]
    ],
    883: [, [, , "(?:[1-4]\\d|51)\\d{6,10}", , , , , , , [8, 9, 10, 11, 12]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "(?:2(?:00\\d\\d|10)|(?:370[1-9]|51\\d0)\\d)\\d{7}|51(?:00\\d{5}|[24-9]0\\d{4,7})|(?:1[0-79]|2[24-689]|3[02-689]|4[0-4])0\\d{5,9}", , , , "510012345"], "001", 883, , , , , , , , 1, [[, "(\\d{3})(\\d{3})(\\d{2,8})", "$1 $2 $3", ["[14]|2[24-689]|3[02-689]|51[24-9]"]], [, "(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3", ["510"]], [
      ,
      "(\\d{3})(\\d{3})(\\d{4})",
      "$1 $2 $3",
      ["21"]
    ], [, "(\\d{4})(\\d{4})(\\d{4})", "$1 $2 $3", ["51[13]"]], [, "(\\d{3})(\\d{3})(\\d{3})(\\d{3})", "$1 $2 $3 $4", ["[235]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]],
    888: [
      ,
      [, , "\\d{11}", , , , , , , [11]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      [, , , , , , , , , [-1]],
      "001",
      888,
      ,
      ,
      ,
      ,
      ,
      ,
      ,
      1,
      [[, "(\\d{3})(\\d{3})(\\d{5})", "$1 $2 $3"]],
      ,
      [, , , , , , , , , [-1]],
      ,
      ,
      [, , , , , , , , , [-1]],
      [, , "\\d{11}", , , , "12345678901"],
      ,
      ,
      [, , , , , , , , , [-1]]
    ],
    979: [, [, , "[1359]\\d{8}", , , , , , , [9], [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , "[1359]\\d{8}", , , , "123456789", , , , [8]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], "001", 979, , , , , , , , 1, [[, "(\\d)(\\d{4})(\\d{4})", "$1 $2 $3", ["[1359]"]]], , [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]], [, , , , , , , , , [-1]], , , [, , , , , , , , , [-1]]]
  };
  function J() {
    this.g = {};
  }
  J.h = void 0;
  J.g = function() {
    return J.h ? J.h : J.h = new J();
  };
  var Fa = { 0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", "\uFF10": "0", "\uFF11": "1", "\uFF12": "2", "\uFF13": "3", "\uFF14": "4", "\uFF15": "5", "\uFF16": "6", "\uFF17": "7", "\uFF18": "8", "\uFF19": "9", "\u0660": "0", "\u0661": "1", "\u0662": "2", "\u0663": "3", "\u0664": "4", "\u0665": "5", "\u0666": "6", "\u0667": "7", "\u0668": "8", "\u0669": "9", "\u06F0": "0", "\u06F1": "1", "\u06F2": "2", "\u06F3": "3", "\u06F4": "4", "\u06F5": "5", "\u06F6": "6", "\u06F7": "7", "\u06F8": "8", "\u06F9": "9" }, Ga = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    "+": "+",
    "*": "*",
    "#": "#"
  }, Ha = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    "\uFF10": "0",
    "\uFF11": "1",
    "\uFF12": "2",
    "\uFF13": "3",
    "\uFF14": "4",
    "\uFF15": "5",
    "\uFF16": "6",
    "\uFF17": "7",
    "\uFF18": "8",
    "\uFF19": "9",
    "\u0660": "0",
    "\u0661": "1",
    "\u0662": "2",
    "\u0663": "3",
    "\u0664": "4",
    "\u0665": "5",
    "\u0666": "6",
    "\u0667": "7",
    "\u0668": "8",
    "\u0669": "9",
    "\u06F0": "0",
    "\u06F1": "1",
    "\u06F2": "2",
    "\u06F3": "3",
    "\u06F4": "4",
    "\u06F5": "5",
    "\u06F6": "6",
    "\u06F7": "7",
    "\u06F8": "8",
    "\u06F9": "9",
    A: "2",
    B: "2",
    C: "2",
    D: "3",
    E: "3",
    F: "3",
    G: "4",
    H: "4",
    I: "4",
    J: "5",
    K: "5",
    L: "5",
    M: "6",
    N: "6",
    O: "6",
    P: "7",
    Q: "7",
    R: "7",
    S: "7",
    T: "8",
    U: "8",
    V: "8",
    W: "9",
    X: "9",
    Y: "9",
    Z: "9"
  }, Ia = RegExp("[+\uFF0B]+"), K = RegExp("^[+\uFF0B]+"), Ja = RegExp("([0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9])"), Ka = RegExp("[+\uFF0B0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]"), La = /[\\\/] *x/, Ma = RegExp("[^0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9A-Za-z#]+$"), Na = /(?:.*?[A-Za-z]){3}.*/, Oa = RegExp("^\\+([0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]|[\\-\\.\\(\\)]?)*[0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]([0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]|[\\-\\.\\(\\)]?)*$"), Pa = RegExp("^([A-Za-z0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]+((\\-)*[A-Za-z0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9])*\\.)*[A-Za-z]+((\\-)*[A-Za-z0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9])*\\.?$");
  function L(a) {
    return "([0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]{1," + a + "})";
  }
  function Qa() {
    return ";ext=" + L("20") + "|[ \xA0\\t,]*(?:e?xt(?:ensi(?:o\u0301?|\xF3))?n?|\uFF45?\uFF58\uFF54\uFF4E?|\u0434\u043E\u0431|anexo)[:\\.\uFF0E]?[ \xA0\\t,-]*" + (L("20") + "#?|[ \xA0\\t,]*(?:[x\uFF58#\uFF03~\uFF5E]|int|\uFF49\uFF4E\uFF54)[:\\.\uFF0E]?[ \xA0\\t,-]*") + (L("9") + "#?|[- ]+") + (L("6") + "#|[ \xA0\\t]*(?:,{2}|;)[:\\.\uFF0E]?[ \xA0\\t,-]*") + (L("15") + "#?|[ \xA0\\t]*(?:,)+[:\\.\uFF0E]?[ \xA0\\t,-]*") + (L("9") + "#?");
  }
  var Ra = new RegExp("(?:" + Qa() + ")$", "i"), Sa = new RegExp("^[0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]{2}$|^[+\uFF0B]*(?:[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E*]*[0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]){3,}[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E*A-Za-z0-9\uFF10-\uFF19\u0660-\u0669\u06F0-\u06F9]*(?:" + Qa() + ")?$", "i"), Ta = /(\$\d)/, Ua = /^\(?\$1\)?$/;
  function Va(a) {
    return a.length < 2 ? false : M(Sa, a);
  }
  function Wa(a) {
    return M(Na, a) ? N(a, Ha) : N(a, Fa);
  }
  function Xa(a) {
    var b = Wa(a.toString());
    C(a);
    a.g(b);
  }
  function Ya(a) {
    return a != null && (w(a, 9) != 1 || F(a)[0] != -1);
  }
  function N(a, b) {
    for (var c = new B(), d, e = a.length, f = 0; f < e; ++f) d = a.charAt(f), d = b[d.toUpperCase()], d != null && c.g(d);
    return c.toString();
  }
  function Za(a) {
    return a.length == 0 || Ua.test(a);
  }
  function O(a) {
    return a != null && isNaN(a) && a.toUpperCase() in Ea;
  }
  J.prototype.format = function(a, b) {
    if (r(a, 2) == 0 && q(a, 5)) {
      var c = v(a, 5);
      if (c.length > 0 && q(a, 1) && r(a, 6) == 20 && b == 0) return a = v(a, 1), $a(a, b, c, "");
      if (c.length > 0 || !q(a, 1)) return c;
    }
    c = v(a, 1);
    var d = P(a);
    if (b == 0) return $a(c, 0, d, "");
    if (!(c in I)) return d;
    var e = Q(this, c, R(c));
    a = q(a, 3) && r(a, 3).length != 0 ? b == 3 ? ";ext=" + r(a, 3) : q(e, 13) ? r(e, 13) + v(a, 3) : " ext. " + v(a, 3) : "";
    a: {
      e = (u(e, 20) || []).length == 0 || b == 2 ? u(e, 19) || [] : u(e, 20) || [];
      for (var f, g = e.length, h = 0; h < g; ++h) {
        f = e[h];
        var l = w(f, 3);
        if (l == 0 || d.search(r(f, 3, l - 1)) == 0) {
          if (l = new RegExp(r(
            f,
            1
          )), M(l, d)) {
            e = f;
            break a;
          }
        }
      }
      e = null;
    }
    e != null && (g = e, e = v(g, 2), f = new RegExp(r(g, 1)), v(g, 5), g = v(g, 4), d = b == 2 && g != null && g.length > 0 ? d.replace(f, e.replace(Ta, g)) : d.replace(f, e), b == 3 && (d = d.replace(RegExp("^[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E]+"), ""), d = d.replace(RegExp("[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E]+", "g"), "-")));
    return $a(
      c,
      b,
      d,
      a
    );
  };
  function Q(a, b, c) {
    return "001" == c ? S(a, "" + b) : S(a, c);
  }
  function P(a) {
    if (!q(a, 2)) return "";
    var b = "" + r(a, 2);
    return q(a, 4) && r(a, 4) && v(a, 8) > 0 ? Array(v(a, 8) + 1).join("0") + b : b;
  }
  function $a(a, b, c, d) {
    switch (b) {
      case 0:
        return "+" + a + c + d;
      case 1:
        return "+" + a + " " + c + d;
      case 3:
        return "tel:+" + a + "-" + c + d;
      default:
        return c + d;
    }
  }
  function T(a, b) {
    switch (b) {
      case 4:
        return r(a, 5);
      case 3:
        return r(a, 4);
      case 1:
        return r(a, 3);
      case 0:
      case 2:
        return r(a, 2);
      case 5:
        return r(a, 6);
      case 6:
        return r(a, 8);
      case 7:
        return r(a, 7);
      case 8:
        return r(a, 21);
      case 9:
        return r(a, 25);
      case 10:
        return r(a, 28);
      default:
        return r(a, 1);
    }
  }
  function ab(a, b) {
    var c = bb(a, b);
    a = Q(a, v(b, 1), c);
    if (a == null) return -1;
    b = P(b);
    return cb(b, a);
  }
  function cb(a, b) {
    return U(a, r(b, 1)) ? U(a, r(b, 5)) ? 4 : U(a, r(b, 4)) ? 3 : U(a, r(b, 6)) ? 5 : U(a, r(b, 8)) ? 6 : U(a, r(b, 7)) ? 7 : U(a, r(b, 21)) ? 8 : U(a, r(b, 25)) ? 9 : U(a, r(b, 28)) ? 10 : U(a, r(b, 2)) ? r(b, 18) || U(a, r(b, 3)) ? 2 : 0 : !r(b, 18) && U(a, r(b, 3)) ? 1 : -1 : -1;
  }
  function S(a, b) {
    if (b == null) return null;
    b = b.toUpperCase();
    var c = a.g[b];
    if (c == null) {
      c = Ea[b];
      if (c == null) return null;
      c = new z().g(G.m(), c);
      a.g[b] = c;
    }
    return c;
  }
  function U(a, b) {
    var c = a.length;
    return w(b, 9) > 0 && F(b).indexOf(c) == -1 ? false : M(v(b, 2), a);
  }
  function db(a, b) {
    var c = bb(a, b);
    var d = v(b, 1);
    var e = Q(a, d, c);
    e == null || "001" != c && d != eb(a, c) ? e = false : (a = P(b), e = cb(a, e) != -1);
    return e;
  }
  function bb(a, b) {
    if (b == null) return null;
    var c = v(b, 1);
    c = I[c];
    if (c == null) a = null;
    else if (c.length == 1) a = c[0];
    else a: {
      b = P(b);
      for (var d, e = c.length, f = 0; f < e; f++) {
        d = c[f];
        var g = S(a, d);
        if (q(g, 23)) {
          if (b.search(r(g, 23)) == 0) {
            a = d;
            break a;
          }
        } else if (cb(b, g) != -1) {
          a = d;
          break a;
        }
      }
      a = null;
    }
    return a;
  }
  function R(a) {
    a = I[a];
    return a == null ? "ZZ" : a[0];
  }
  function eb(a, b) {
    a = S(a, b);
    if (a == null) throw Error("Invalid region code: " + b);
    return v(a, 10);
  }
  function V(a, b, c, d) {
    var e = T(c, d), f = w(e, 9) == 0 ? F(r(c, 1)) : F(e);
    e = u(e, 10) || [];
    if (d == 2) if (Ya(T(c, 0))) a = T(c, 1), Ya(a) && (f = f.concat(w(a, 9) == 0 ? F(r(c, 1)) : F(a)), f.sort(), e.length == 0 ? e = u(a, 10) || [] : (e = e.concat(u(a, 10) || []), e.sort()));
    else return V(a, b, c, 1);
    if (f[0] == -1) return 5;
    b = b.length;
    if (e.indexOf(b) > -1) return 4;
    c = f[0];
    return c == b ? 0 : c > b ? 2 : f[f.length - 1] < b ? 3 : f.indexOf(b, 1) > -1 ? 0 : 5;
  }
  function W(a, b, c) {
    var d = P(b);
    b = v(b, 1);
    if (!(b in I)) return 1;
    b = Q(a, b, R(b));
    return V(a, d, b, c);
  }
  function fb(a, b) {
    a = a.toString();
    if (a.length == 0 || a.charAt(0) == "0") return 0;
    for (var c, d = a.length, e = 1; e <= 3 && e <= d; ++e) if (c = parseInt(a.substring(0, e), 10), c in I) return b.g(a.substring(e)), c;
    return 0;
  }
  function gb(a, b, c, d, e, f) {
    if (b.length == 0) return 0;
    b = new B(b);
    var g;
    c != null && (g = r(c, 11));
    g == null && (g = "NonMatch");
    var h = b.toString();
    if (h.length == 0) g = 20;
    else if (K.test(h)) h = h.replace(K, ""), C(b), b.g(Wa(h)), g = 1;
    else {
      h = new RegExp(g);
      Xa(b);
      g = b.toString();
      if (g.search(h) == 0) {
        h = g.match(h)[0].length;
        var l = g.substring(h).match(Ja);
        l && l[1] != null && l[1].length > 0 && N(l[1], Fa) == "0" ? g = false : (C(b), b.g(g.substring(h)), g = true);
      } else g = false;
      g = g ? 5 : 20;
    }
    e && t(f, 6, g);
    if (g != 20) {
      if (b.h.length <= 2) throw Error("Phone number too short after IDD");
      a = fb(b, d);
      if (a != 0) return t(f, 1, a), a;
      throw Error("Invalid country calling code");
    }
    if (c != null && (g = v(c, 10), h = "" + g, l = b.toString(), l.lastIndexOf(h, 0) == 0 && (h = new B(l.substring(h.length)), l = r(c, 1), l = new RegExp(v(l, 2)), hb(h, c, null), h = h.toString(), !M(l, b.toString()) && M(l, h) || V(a, b.toString(), c, -1) == 3))) return d.g(h), e && t(f, 6, 10), t(f, 1, g), g;
    t(f, 1, 0);
    return 0;
  }
  function hb(a, b, c) {
    var d = a.toString(), e = d.length, f = r(b, 15);
    if (e != 0 && f != null && f.length != 0 && (f = new RegExp("^(?:" + f + ")"), e = f.exec(d))) {
      var g = RegExp;
      var h = r(b, 1);
      h = v(h, 2);
      g = new g(h);
      h = M(g, d);
      var l = e.length - 1;
      b = r(b, 16);
      if (b == null || b.length == 0 || e[l] == null || e[l].length == 0) {
        if (!h || M(g, d.substring(e[0].length))) c != null && l > 0 && e[l] != null && c.g(e[1]), a.set(d.substring(e[0].length));
      } else if (d = d.replace(f, b), !h || M(g, d)) c != null && l > 0 && c.g(e[1]), a.set(d);
    }
  }
  function X(a, b, c) {
    if (!O(c) && b.length > 0 && b.charAt(0) != "+") throw Error("Invalid country calling code");
    return ib(a, b, c, true);
  }
  function ib(a, b, c, d) {
    if (b == null) throw Error("The string supplied did not seem to be a phone number");
    if (b.length > 250) throw Error("The string supplied is too long to be a phone number");
    var e = new B();
    var f = b.indexOf(";phone-context=");
    if (f === -1) f = null;
    else if (f += 15, f >= b.length) f = "";
    else {
      var g = b.indexOf(";", f);
      f = g !== -1 ? b.substring(f, g) : b.substring(f);
    }
    var h = f;
    h == null ? g = true : h.length === 0 ? g = false : (g = Oa.exec(h), h = Pa.exec(h), g = g !== null || h !== null);
    if (!g) throw Error("The string supplied did not seem to be a phone number");
    f != null ? (f.charAt(0) === "+" && e.g(f), f = b.indexOf("tel:"), e.g(b.substring(f >= 0 ? f + 4 : 0, b.indexOf(";phone-context=")))) : (f = e.g, g = b ?? "", h = g.search(Ka), h >= 0 ? (g = g.substring(h), g = g.replace(Ma, ""), h = g.search(La), h >= 0 && (g = g.substring(0, h))) : g = "", f.call(e, g));
    f = e.toString();
    g = f.indexOf(";isub=");
    g > 0 && (C(e), e.g(f.substring(0, g)));
    if (!Va(e.toString())) throw Error("The string supplied did not seem to be a phone number");
    f = e.toString();
    if (!(O(c) || f != null && f.length > 0 && K.test(f))) throw Error("Invalid country calling code");
    f = new H();
    d && t(f, 5, b);
    a: {
      b = e.toString();
      g = b.search(Ra);
      if (g >= 0 && Va(b.substring(0, g))) {
        h = b.match(Ra);
        for (var l = h.length, A = 1; A < l; ++A) if (h[A] != null && h[A].length > 0) {
          C(e);
          e.g(b.substring(0, g));
          b = h[A];
          break a;
        }
      }
      b = "";
    }
    b.length > 0 && t(f, 3, b);
    g = S(a, c);
    b = new B();
    h = 0;
    l = e.toString();
    try {
      h = gb(a, l, g, b, d, f);
    } catch (ea) {
      if (ea.message == "Invalid country calling code" && K.test(l)) {
        if (l = l.replace(K, ""), h = gb(a, l, g, b, d, f), h == 0) throw ea;
      } else throw ea;
    }
    h != 0 ? (e = R(h), e != c && (g = Q(a, h, e))) : (Xa(e), b.g(e.toString()), c != null ? (h = v(g, 10), t(
      f,
      1,
      h
    )) : d && (delete f.h[6], f.g && delete f.g[6]));
    if (b.h.length < 2) throw Error("The string supplied is too short to be a phone number");
    g != null && (c = new B(), e = new B(b.toString()), hb(e, g, c), a = V(a, e.toString(), g, -1), a != 2 && a != 4 && a != 5 && (b = e, d && c.toString().length > 0 && t(f, 7, c.toString())));
    d = b.toString();
    a = d.length;
    if (a < 2) throw Error("The string supplied is too short to be a phone number");
    if (a > 17) throw Error("The string supplied is too long to be a phone number");
    if (d.length > 1 && d.charAt(0) == "0") {
      t(f, 4, true);
      for (a = 1; a < d.length - 1 && d.charAt(a) == "0"; ) a++;
      a != 1 && t(f, 8, a);
    }
    t(f, 2, parseInt(d, 10));
    return f;
  }
  function M(a, b) {
    return (a = b.match(new RegExp("^(?:" + (typeof a == "string" ? a : a.source) + ")$", "i"))) && a[0].length == b.length ? true : false;
  }
  ;
  function jb(a) {
    this.ga = RegExp("\u2008");
    this.ka = "";
    this.$ = new B();
    this.ea = "";
    this.u = new B();
    this.da = new B();
    this.v = true;
    this.fa = this.aa = this.ma = false;
    this.ha = J.g();
    this.ba = 0;
    this.h = new B();
    this.ia = false;
    this.o = "";
    this.g = new B();
    this.j = [];
    this.la = a;
    this.l = kb(this, this.la);
  }
  var lb = new G();
  t(lb, 11, "NA");
  var mb = RegExp("^[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E]*\\$1[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E]*(\\$\\d[-x\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F \xA0\xAD\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E]*)*$"), nb = /[- ]/;
  function kb(a, b) {
    var c = a.ha;
    b = O(b) ? eb(c, b) : 0;
    a = S(a.ha, R(b));
    return a != null ? a : lb;
  }
  function ob(a) {
    for (var b = a.j.length, c = 0; c < b; ++c) {
      var d = a.j[c], e = v(d, 1);
      if (a.ea == e) return false;
      var f = a;
      var g = d, h = v(g, 1);
      C(f.$);
      var l = f;
      g = v(g, 2);
      var A = "999999999999999".match(h)[0];
      A.length < l.g.h.length ? l = "" : (l = A.replace(new RegExp(h, "g"), g), l = l.replace(RegExp("9", "g"), "\u2008"));
      l.length > 0 ? (f.$.g(l), f = true) : f = false;
      if (f) return a.ea = e, a.ia = nb.test(r(d, 4)), a.ba = 0, true;
    }
    return a.v = false;
  }
  function pb(a, b) {
    for (var c = [], d = b.length - 3, e = a.j.length, f = 0; f < e; ++f) {
      var g = a.j[f];
      w(g, 3) == 0 ? c.push(a.j[f]) : (g = r(g, 3, Math.min(d, w(g, 3) - 1)), b.search(g) == 0 && c.push(a.j[f]));
    }
    a.j = c;
  }
  function qb(a, b) {
    a.u.g(b);
    var c = b;
    Ja.test(c) || a.u.h.length == 1 && Ia.test(c) ? (b == "+" ? (c = b, a.da.g(b)) : (c = Fa[b], a.da.g(c), a.g.g(c)), b = c) : (a.v = false, a.ma = true);
    if (!a.v) {
      if (!a.ma) {
        if (rb(a)) {
          if (sb(a)) return tb(a);
        } else if (a.o.length > 0 && (b = a.g.toString(), C(a.g), a.g.g(a.o), a.g.g(b), b = a.h.toString(), c = b.lastIndexOf(a.o), C(a.h), a.h.g(b.substring(0, c))), a.o != ub(a)) return a.h.g(" "), tb(a);
      }
      return a.u.toString();
    }
    switch (a.da.h.length) {
      case 0:
      case 1:
      case 2:
        return a.u.toString();
      case 3:
        if (rb(a)) a.fa = true;
        else return a.o = ub(a), vb(a);
      default:
        if (a.fa) return sb(a) && (a.fa = false), a.h.toString() + a.g.toString();
        if (a.j.length > 0) {
          b = wb(a, b);
          c = xb(a);
          if (c.length > 0) return c;
          pb(a, a.g.toString());
          return ob(a) ? yb(a) : a.v ? Y(a, b) : a.u.toString();
        }
        return vb(a);
    }
  }
  function tb(a) {
    a.v = true;
    a.fa = false;
    a.j = [];
    a.ba = 0;
    C(a.$);
    a.ea = "";
    return vb(a);
  }
  function xb(a) {
    for (var b = a.g.toString(), c = a.j.length, d = 0; d < c; ++d) {
      var e = a.j[d], f = v(e, 1);
      if (new RegExp("^(?:" + f + ")$").test(b) && (a.ia = nb.test(r(e, 4)), e = b.replace(new RegExp(f, "g"), r(e, 2)), e = Y(a, e), N(e, Ga) == a.da)) return e;
    }
    return "";
  }
  function Y(a, b) {
    var c = a.h.h.length;
    return a.ia && c > 0 && a.h.toString().charAt(c - 1) != " " ? a.h + " " + b : a.h + b;
  }
  function vb(a) {
    var b = a.g.toString();
    if (b.length >= 3) {
      for (var c = a.aa && a.o.length == 0 && w(a.l, 20) > 0 ? u(a.l, 20) || [] : u(a.l, 19) || [], d = c.length, e = 0; e < d; ++e) {
        var f = c[e];
        a.o.length > 0 && Za(v(f, 4)) && !r(f, 6) && !q(f, 5) || (a.o.length != 0 || a.aa || Za(v(f, 4)) || r(f, 6)) && mb.test(v(f, 2)) && a.j.push(f);
      }
      pb(a, b);
      b = xb(a);
      return b.length > 0 ? b : ob(a) ? yb(a) : a.u.toString();
    }
    return Y(a, b);
  }
  function yb(a) {
    var b = a.g.toString(), c = b.length;
    if (c > 0) {
      for (var d = "", e = 0; e < c; e++) d = wb(a, b.charAt(e));
      return a.v ? Y(a, d) : a.u.toString();
    }
    return a.h.toString();
  }
  function ub(a) {
    var b = a.g.toString(), c = 0;
    if (r(a.l, 10) != 1) var d = false;
    else d = a.g.toString(), d = d.charAt(0) == "1" && d.charAt(1) != "0" && d.charAt(1) != "1";
    d ? (c = 1, a.h.g("1").g(" "), a.aa = true) : q(a.l, 15) && (d = new RegExp("^(?:" + r(a.l, 15) + ")"), d = b.match(d), d != null && d[0] != null && d[0].length > 0 && (a.aa = true, c = d[0].length, a.h.g(b.substring(0, c))));
    C(a.g);
    a.g.g(b.substring(c));
    return b.substring(0, c);
  }
  function rb(a) {
    var b = a.da.toString(), c = new RegExp("^(?:\\+|" + r(a.l, 11) + ")");
    c = b.match(c);
    return c != null && c[0] != null && c[0].length > 0 ? (a.aa = true, c = c[0].length, C(a.g), a.g.g(b.substring(c)), C(a.h), a.h.g(b.substring(0, c)), b.charAt(0) != "+" && a.h.g(" "), true) : false;
  }
  function sb(a) {
    if (a.g.h.length == 0) return false;
    var b = new B(), c = fb(a.g, b);
    if (c == 0) return false;
    C(a.g);
    a.g.g(b.toString());
    b = R(c);
    "001" == b ? a.l = S(a.ha, "" + c) : b != a.la && (a.l = kb(a, b));
    a.h.g("" + c).g(" ");
    a.o = "";
    return true;
  }
  function wb(a, b) {
    var c = a.$.toString();
    if (c.substring(a.ba).search(a.ga) >= 0) {
      var d = c.search(a.ga);
      b = c.replace(a.ga, b);
      C(a.$);
      a.$.g(b);
      a.ba = d;
      return b.substring(0, a.ba + 1);
    }
    a.j.length == 1 && (a.v = false);
    a.ea = "";
    return a.u.toString();
  }
  ;
  const zb = {};
  ["E164", "INTERNATIONAL", "NATIONAL", "RFC3966"].forEach((a, b) => {
    zb[a] = b;
  });
  const Z = {};
  "FIXED_LINE MOBILE FIXED_LINE_OR_MOBILE TOLL_FREE PREMIUM_RATE SHARED_COST VOIP PERSONAL_NUMBER PAGER UAN VOICEMAIL UNKNOWN".split(" ").forEach((a, b) => {
    Z[a] = b;
  });
  Z.UNKNOWN = -1;
  const Ab = {};
  "IS_POSSIBLE INVALID_COUNTRY_CODE TOO_SHORT TOO_LONG IS_POSSIBLE_LOCAL_ONLY INVALID_LENGTH".split(" ").forEach((a, b) => {
    Ab[a] = b;
  });
  const Bb = {};
  Object.keys(Z).forEach((a) => {
    Bb[Z[a]] = a;
  });
  const Cb = {};
  Object.keys(Ab).forEach((a) => {
    Cb[Ab[a]] = a;
  });
  const Db = (a) => {
    const b = [];
    a.includes("FIXED_LINE_OR_MOBILE") ? (a.includes("MOBILE") || b.push("MOBILE"), a.includes("FIXED_LINE") || b.push("FIXED_LINE")) : (a.includes("MOBILE") || a.includes("FIXED_LINE")) && b.push("FIXED_LINE_OR_MOBILE");
    return a.concat(b);
  };
  m("utils", {});
  m("utils.formatNumberAsYouType", (a, b) => {
    try {
      const c = a.replace(/[^+0-9]/g, ""), d = new jb(b);
      b = "";
      for (let e = 0; e < c.length; e++) d.ka = qb(d, c.charAt(e)), b = d.ka;
      return b;
    } catch {
      return a;
    }
  });
  m("utils.formatNumber", (a, b, c) => {
    try {
      const e = J.g(), f = X(e, a, b);
      var d = W(e, f, -1);
      return d == 0 || d == 4 ? e.format(f, typeof c === "undefined" ? 0 : zb[c]) : a;
    } catch {
      return a;
    }
  });
  m("utils.getExampleNumber", (a, b, c) => {
    try {
      const l = J.g();
      a: {
        var d = l, e = Z[b];
        if (O(a)) {
          var f = T(S(d, a), e);
          try {
            if (q(f, 6)) {
              var g = r(f, 6);
              var h = ib(d, g, a, false);
              break a;
            }
          } catch (A) {
          }
        }
        h = null;
      }
      return l.format(h, zb[c]);
    } catch {
      return "";
    }
  });
  m("utils.getExtension", (a, b) => {
    try {
      var c = X(J.g(), a, b);
      return r(c, 3);
    } catch {
      return "";
    }
  });
  m("utils.getNumberType", (a, b) => {
    try {
      const c = J.g(), d = X(c, a, b), e = ab(c, d);
      return Bb[e] || null;
    } catch {
      return null;
    }
  });
  m("utils.getValidationError", (a, b) => {
    if (!b) return "INVALID_COUNTRY_CODE";
    try {
      const c = J.g(), d = X(c, a, b), e = W(c, d, -1);
      return Cb[e] || null;
    } catch (c) {
      return c.message === "Invalid country calling code" ? "INVALID_COUNTRY_CODE" : a.length <= 3 || c.message === "Phone number too short after IDD" || c.message === "The string supplied is too short to be a phone number" ? "TOO_SHORT" : c.message === "The string supplied is too long to be a phone number" ? "TOO_LONG" : null;
    }
  });
  m("utils.isValidNumber", (a, b, c) => {
    try {
      const d = J.g(), e = X(d, a, b);
      if (c) {
        const f = Db(c);
        for (let g of f) if (W(d, e, Z[g]) === 0) return true;
        return false;
      }
      return W(d, e, -1) === 0;
    } catch {
      return false;
    }
  });
  m("utils.isValidNumberPrecise", (a, b, c) => {
    try {
      const d = J.g(), e = X(d, a, b), f = db(d, e);
      if (c) {
        const g = Db(c).map((h) => Z[h]);
        return f && g.includes(ab(d, e));
      }
      return f;
    } catch {
      return false;
    }
  });
  m("utils.getCoreNumber", (a, b) => {
    try {
      var c = X(J.g(), a, b);
      return r(c, 2).toString();
    } catch {
      return "";
    }
  });
}).call(_scope);
var utils_default = _scope.utils;

// packages/core/src/js/intlTelInputWithUtils.ts
intlTelInput_default.utils = utils_default;
var intlTelInputWithUtils_default = intlTelInput_default;
export {
  intlTelInputWithUtils_default as default
};
