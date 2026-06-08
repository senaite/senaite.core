/*
 * International Telephone Input v26.8.1
 * https://github.com/jackocnr/intl-tel-input.git
 * Licensed under the MIT license
 */

// UMD
(function(factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    window.intlTelInput = factory();
  }
}(() => {

var factoryOutput = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // src/js/intl-tel-input.ts
  var intl_tel_input_exports = {};
  __export(intl_tel_input_exports, {
    Iti: () => Iti,
    default: () => intl_tel_input_default
  });

  // src/js/intl-tel-input/data.ts
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
      // Åland Islands
      "358",
      1,
      ["18", "4"],
      // (4 is a mobile range shared with FI)
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
      ["204", "226", "236", "249", "250", "257", "263", "289", "306", "343", "354", "365", "367", "368", "382", "403", "416", "418", "428", "431", "437", "438", "450", "468", "474", "506", "514", "519", "548", "579", "581", "584", "587", "604", "613", "639", "647", "672", "683", "705", "709", "742", "753", "778", "780", "782", "807", "819", "825", "867", "873", "879", "902", "905", "942"],
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
      ["4"],
      // (mobile range shared with AX)
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
      ["1481", "7781", "7839", "7911"],
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
      ["1534", "7509", "7700", "7797", "7829", "7937"],
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
      ["269", "639"],
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
      // populated in the plugin
      iso2: c[0],
      dialCode: c[1],
      priority: c[2] || 0,
      areaCodes: c[3] || null,
      nodeById: {},
      // populated by the plugin
      nationalPrefix: c[4] || null,
      normalisedName: "",
      // populated in the plugin
      initials: "",
      // populated in the plugin
      dialCodePlus: ""
      // populated in the plugin
    });
  }
  var data_default = allCountries;

  // src/js/modules/constants.ts
  var EVENTS = {
    OPEN_COUNTRY_DROPDOWN: "open:countrydropdown",
    CLOSE_COUNTRY_DROPDOWN: "close:countrydropdown",
    COUNTRY_CHANGE: "countrychange",
    INPUT: "input"
    // used for synthetic input trigger
  };
  var CLASSES = {
    HIDE: "iti__hide",
    V_HIDE: "iti__v-hide",
    ARROW_UP: "iti__arrow--up",
    GLOBE: "iti__globe",
    FLAG: "iti__flag",
    LOADING: "iti__loading",
    COUNTRY_ITEM: "iti__country",
    HIGHLIGHT: "iti__highlight"
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
    DELETE_FWD: "deleteContentForward"
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
  var SENTINELS = {
    UNKNOWN_NUMBER_TYPE: -99,
    UNKNOWN_VALIDATION_ERROR: -99
  };
  var LAYOUT = {
    NARROW_VIEWPORT_WIDTH: 500,
    // keep in sync with .iti__country-list CSS media query
    SANE_SELECTED_WITH_DIAL_WIDTH: 78,
    // px width fallback when separateDialCode enabled
    SANE_SELECTED_NO_DIAL_WIDTH: 42,
    // px width fallback when no separate dial code
    INPUT_PADDING_EXTRA_LEFT: 6,
    // px gap between selected country container and input text
    DROPDOWN_MARGIN: 3,
    // px margin between dropdown and tel input
    SANE_DROPDOWN_HEIGHT: 200
    // px height fallback for dropdown
  };
  var DIAL = {
    PLUS: "+",
    NANP: "1"
    // North American Numbering Plan
  };
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
  var PLACEHOLDER_MODES = {
    AGGRESSIVE: "aggressive",
    POLITE: "polite",
    OFF: "off"
  };
  var INITIAL_COUNTRY = {
    AUTO: "auto"
  };
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
  var NUMBER_TYPE_SET = new Set(NUMBER_TYPES);
  var DATA_KEYS = {
    COUNTRY_CODE: "countryCode",
    DIAL_CODE: "dialCode"
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

  // src/js/intl-tel-input/i18n/en/index.ts
  var interfaceTranslations = {
    selectedCountryAriaLabel: "Change country, selected ${countryName} (${dialCode})",
    noCountrySelected: "Select country",
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

  // src/js/modules/core/options.ts
  var mq = (q) => typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia(q).matches;
  var isNarrowViewport = () => mq(`(max-width: ${LAYOUT.NARROW_VIEWPORT_WIDTH}px)`);
  var computeDefaultUseFullscreenPopup = () => {
    if (typeof navigator !== "undefined" && typeof window !== "undefined") {
      const isShortViewport = mq("(max-height: 600px)");
      const isCoarsePointer = mq("(pointer: coarse)");
      return isNarrowViewport() || isCoarsePointer && isShortViewport;
    }
    return false;
  };
  var defaults = {
    //* Whether or not to allow the dropdown.
    allowDropdown: true,
    //* The number type to enforce during validation.
    allowedNumberTypes: ["MOBILE", "FIXED_LINE"],
    //* Whether or not to allow extensions after the main number.
    allowNumberExtensions: false,
    // Allow alphanumeric "phonewords" (e.g. +1 800 FLOWERS) as valid numbers
    allowPhonewords: false,
    //* Add a placeholder in the input with an example number for the selected country.
    autoPlaceholder: PLACEHOLDER_MODES.POLITE,
    //* Add a custom class to the (injected) container element.
    containerClass: "",
    //* Locale for localising country names via Intl.DisplayNames.
    countryNameLocale: "en",
    //* The order of the countries in the dropdown. Defaults to alphabetical.
    countryOrder: null,
    //* Add a country search input at the top of the dropdown.
    countrySearch: true,
    //* Modify the auto placeholder.
    customPlaceholder: null,
    //* Always show the dropdown
    dropdownAlwaysOpen: false,
    //* Append menu to specified element.
    dropdownContainer: null,
    //* Don't display these countries.
    excludeCountries: [],
    //* Fix the dropdown width to the input width (rather than being as wide as the longest country name).
    fixDropdownWidth: true,
    //* Format the number as the user types
    formatAsYouType: true,
    //* Format the input value during initialisation and on setNumber.
    formatOnDisplay: true,
    //* geoIp lookup function.
    geoIpLookup: null,
    //* Inject a hidden input with the name returned from this function, and on submit, populate it with the result of getNumber.
    hiddenInput: null,
    //* Internationalise the plugin text e.g. search input placeholder, country names.
    i18n: {},
    //* Initial country.
    initialCountry: "",
    //* A function to load the utils script.
    loadUtils: null,
    //* National vs international formatting for numbers e.g. placeholders and displaying existing numbers.
    nationalMode: true,
    //* Display only these countries.
    onlyCountries: [],
    //* Number type to use for placeholders.
    placeholderNumberType: "MOBILE",
    //* Add custom classes to the search input element.
    searchInputClass: "",
    //* Display the international dial code next to the selected flag.
    separateDialCode: false,
    //* Show flags - for both the selected country, and in the country dropdown
    showFlags: true,
    //* Only allow certain chars e.g. a plus followed by numeric digits, and cap at max valid length.
    strictMode: false,
    //* Use full screen popup instead of dropdown for country list.
    useFullscreenPopup: computeDefaultUseFullscreenPopup()
  };
  var toString = (val) => JSON.stringify(val);
  var isPlainObject = (val) => Boolean(val) && typeof val === "object" && !Array.isArray(val);
  var isFn = (val) => typeof val === "function";
  var isElLike = (val) => {
    if (!val || typeof val !== "object") return false;
    const v = val;
    return v.nodeType === 1 && typeof v.tagName === "string" && typeof v.appendChild === "function";
  };
  var iso2Set = new Set(data_default.map((c) => c.iso2));
  var isIso2 = (val) => iso2Set.has(val);
  var placeholderModeSet = new Set(Object.values(PLACEHOLDER_MODES));
  var warn = (message) => {
    console.warn(`[intl-tel-input] ${message}`);
  };
  var warnOption = (optionName, expectedType, actualValue) => {
    warn(`Option '${optionName}' must be ${expectedType}; got ${toString(actualValue)}. Ignoring.`);
  };
  var hasOwn = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
  var validateIso2Array = (key, value) => {
    const expectedType = "an array of ISO2 country code strings";
    if (!Array.isArray(value)) {
      warnOption(key, expectedType, value);
      return false;
    }
    for (const v of value) {
      if (typeof v !== "string") {
        warnOption(key, expectedType, value);
        return false;
      }
      const lower = v.toLowerCase();
      if (!isIso2(lower)) {
        warn(`Invalid country code in '${key}': '${v}'. Ignoring.`);
        return false;
      }
    }
    return true;
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
      if (!hasOwn(defaults, key)) {
        warn(`Unknown option '${key}'. Ignoring.`);
        continue;
      }
      switch (key) {
        case "allowDropdown":
        case "allowNumberExtensions":
        case "allowPhonewords":
        case "countrySearch":
        case "dropdownAlwaysOpen":
        case "fixDropdownWidth":
        case "formatAsYouType":
        case "formatOnDisplay":
        case "nationalMode":
        case "showFlags":
        case "separateDialCode":
        case "strictMode":
        case "useFullscreenPopup":
          if (typeof value !== "boolean") {
            warnOption(key, "a boolean", value);
            break;
          }
          validatedOptions[key] = value;
          break;
        case "autoPlaceholder":
          if (typeof value !== "string" || !placeholderModeSet.has(value)) {
            const validModes = Array.from(placeholderModeSet).join(", ");
            warnOption("autoPlaceholder", `one of ${validModes}`, value);
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
        case "countryOrder":
          if (value === null || validateIso2Array(key, value)) {
            validatedOptions[key] = value;
          }
          break;
        case "customPlaceholder":
        case "geoIpLookup":
        case "hiddenInput":
        case "loadUtils":
          if (value !== null && !isFn(value)) {
            warnOption(key, "a function or null", value);
            break;
          }
          validatedOptions[key] = value;
          break;
        case "dropdownContainer":
          if (value !== null && !isElLike(value)) {
            warnOption("dropdownContainer", "an HTMLElement or null", value);
            break;
          }
          validatedOptions[key] = value;
          break;
        case "excludeCountries":
        case "onlyCountries":
          if (validateIso2Array(key, value)) {
            validatedOptions[key] = value;
          }
          break;
        case "i18n":
          if (value && !isPlainObject(value)) {
            warnOption("i18n", "an object", value);
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
          if (lower && (lower !== INITIAL_COUNTRY.AUTO && !isIso2(lower))) {
            warnOption("initialCountry", "a valid ISO2 country code or 'auto'", value);
            break;
          }
          validatedOptions[key] = value;
          break;
        }
        case "placeholderNumberType":
          if (typeof value !== "string" || !NUMBER_TYPE_SET.has(value)) {
            const validTypes = Array.from(NUMBER_TYPE_SET).join(", ");
            warnOption("placeholderNumberType", `one of ${validTypes}`, value);
            break;
          }
          validatedOptions[key] = value;
          break;
        case "allowedNumberTypes":
          if (value !== null) {
            if (!Array.isArray(value)) {
              warnOption("allowedNumberTypes", "an array of number types or null", value);
              break;
            }
            let allValid = true;
            for (const v of value) {
              if (typeof v !== "string" || !NUMBER_TYPE_SET.has(v)) {
                const validTypes = Array.from(NUMBER_TYPE_SET).join(", ");
                warnOption("allowedNumberTypes", `an array of valid number types (${validTypes})`, v);
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
  var applyOptionSideEffects = (o) => {
    if (o.dropdownAlwaysOpen) {
      o.useFullscreenPopup = false;
      o.allowDropdown = true;
    }
    if (o.useFullscreenPopup) {
      o.fixDropdownWidth = false;
    } else {
      if (isNarrowViewport()) {
        o.fixDropdownWidth = true;
      }
    }
    if (o.onlyCountries.length === 1) {
      o.initialCountry = o.onlyCountries[0];
    }
    if (o.separateDialCode) {
      o.nationalMode = false;
    }
    if (o.allowDropdown && !o.showFlags && !o.separateDialCode) {
      o.nationalMode = false;
    }
    if (o.useFullscreenPopup && !o.dropdownContainer) {
      o.dropdownContainer = document.body;
    }
    o.i18n = { ...en_default, ...o.i18n };
  };

  // src/js/modules/utils/string.ts
  var getNumeric = (s) => s.replace(/\D/g, "");
  var normaliseString = (s = "") => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  // src/js/modules/utils/isAndroid.ts
  var getIsAndroid = () => typeof navigator !== "undefined" ? /Android/i.test(navigator.userAgent) : false;

  // src/js/modules/core/countrySearch.ts
  var getMatchedCountries = (countries, query) => {
    const normalisedQuery = normaliseString(query);
    const iso2Matches = [];
    const nameStartWith = [];
    const nameContains = [];
    const dialCodeMatches = [];
    const dialCodeContains = [];
    const initialsMatches = [];
    for (const c of countries) {
      if (c.iso2 === normalisedQuery) {
        iso2Matches.push(c);
      } else if (c.normalisedName.startsWith(normalisedQuery)) {
        nameStartWith.push(c);
      } else if (c.normalisedName.includes(normalisedQuery)) {
        nameContains.push(c);
      } else if (normalisedQuery === c.dialCode || normalisedQuery === c.dialCodePlus) {
        dialCodeMatches.push(c);
      } else if (c.dialCodePlus.includes(normalisedQuery)) {
        dialCodeContains.push(c);
      } else if (c.initials.includes(normalisedQuery)) {
        initialsMatches.push(c);
      }
    }
    const sortByPriority = (a, b) => a.priority - b.priority;
    return [
      ...iso2Matches.sort(sortByPriority),
      ...nameStartWith.sort(sortByPriority),
      ...nameContains.sort(sortByPriority),
      ...dialCodeMatches.sort(sortByPriority),
      ...dialCodeContains.sort(sortByPriority),
      ...initialsMatches.sort(sortByPriority)
    ];
  };
  var findFirstCountryStartingWith = (countries, query) => {
    const lowerQuery = query.toLowerCase();
    for (const c of countries) {
      const lowerName = c.name.toLowerCase();
      if (lowerName.startsWith(lowerQuery)) {
        return c;
      }
    }
    return null;
  };

  // src/js/modules/utils/dom.ts
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

  // src/js/modules/core/icons.ts
  var buildSearchIcon = () => `
  <svg class="iti__search-icon-svg" width="14" height="14" viewBox="0 0 24 24" focusable="false" ${ARIA.HIDDEN}="true">
    <circle cx="11" cy="11" r="7" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>`;
  var buildClearIcon = (id2) => {
    const maskId = `iti-${id2}-clear-mask`;
    return `
    <svg class="iti__search-clear-svg" width="12" height="12" viewBox="0 0 16 16" ${ARIA.HIDDEN}="true" focusable="false">
      <mask id="${maskId}" maskUnits="userSpaceOnUse">
        <rect width="16" height="16" fill="white" />
        <path d="M5.2 5.2 L10.8 10.8 M10.8 5.2 L5.2 10.8" stroke="black" stroke-linecap="round" class="iti__search-clear-x" />
      </mask>
      <circle cx="8" cy="8" r="8" class="iti__search-clear-bg" mask="url(#${maskId})" />
    </svg>`;
  };
  var buildCheckIcon = () => `
  <svg class="iti__country-check-svg" width="14" height="14" viewBox="0 0 16 16" fill="currentColor" focusable="false" ${ARIA.HIDDEN}="true">
    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
  </svg>`;
  var buildGlobeIcon = () => `
  <svg width="256" height="256" viewBox="0 0 512 512" class="iti__globe-svg">
    <path d="M508 213a240 240 0 0 0-449-87l-2 5-2 5c-8 14-13 30-17 46a65 65 0 0 1 56 4c16-10 35-19 56-27l9-3c-6 23-10 48-10 74h-16l4 6c3 4 5 8 6 13h6c0 22 3 44 8 65l2 10-25-10-4 5 12 18 9 3 6 2 8 3 9 26 1 2 16-7h1l-5-13-1-2c24 6 49 9 75 10v26l11 10 7 7v-30l1-13c22 0 44-3 65-8l10-2-21 48-1 1a317 317 0 0 1-14 23l-21 5h-2c6 16 7 33 1 50a240 240 0 0 0 211-265m-401-56-11 6c19-44 54-79 98-98-11 20-21 44-29 69-21 6-40 15-58 23m154 182v4c-29-1-57-6-81-13-7-25-12-52-13-81h94zm0-109h-94c1-29 6-56 13-81 24-7 52-12 81-13zm0-112c-22 1-44 4-65 8l-10 2 12-30 9-17 1-2a332 332 0 0 1 13-23c13-4 26-6 40-7zm187 69 6 4c4 12 6 25 6 38v1h-68c-1-26-4-51-10-74l48 20 1 1 14 8zm-14-44 10 20c-20-11-43-21-68-29-8-25-18-49-29-69 37 16 67 44 87 78M279 49h1c13 1 27 3 39 7l14 23 1 2a343 343 0 0 1 12 26l2 5 6 16c-23-6-48-9-74-10h-1zm0 87h1c29 1 56 6 81 13 7 24 12 51 12 80v1h-94zm2 207h-2v-94h95c-1 29-6 56-13 81-24 7-51 12-80 13m86 60-20 10c11-20 21-43 29-68 25-8 48-18 68-29-16 37-43 67-77 87m87-115-7 5-16 9-2 1a337 337 0 0 1-47 21c6-24 9-49 10-75h68c0 13-2 27-6 39"/>
    <path d="m261 428-2-2-22-21a40 40 0 0 0-32-11h-1a37 37 0 0 0-18 8l-1 1-4 2-2 2-5 4c-9-3-36-31-47-44s-32-45-34-55l3-2a151 151 0 0 0 11-9v-1a39 39 0 0 0 5-48l-3-3-11-19-3-4-5-7h-1l-3-3-4-3-5-2a35 35 0 0 0-16-3h-5c-4 1-14 5-24 11l-4 2-4 3-4 2c-9 8-17 17-18 27a380 380 0 0 0 212 259h3c12 0 25-10 36-21l10-12 6-11a39 39 0 0 0-8-40"/>
  </svg>`;

  // src/js/modules/core/ui.ts
  var UI = class _UI {
    constructor(input, options, id2) {
      this.#searchKeyupTimer = null;
      this.#inlineDropdownHeight = null;
      this.#dropdownForContainer = null;
      this.#selectedItem = null;
      this.highlightedItem = null;
      input.dataset.intlTelInputId = id2.toString();
      this.telInput = input;
      this.#options = options;
      this.#id = id2;
      this.hadInitialPlaceholder = Boolean(input.getAttribute("placeholder"));
      this.#isRTL = !!this.telInput.closest("[dir=rtl]");
      if (this.#options.separateDialCode) {
        this.#originalPaddingLeft = this.telInput.style.paddingLeft;
      }
    }
    // private
    #options;
    #id;
    #isRTL;
    #originalPaddingLeft;
    #countries;
    #searchKeyupTimer;
    #inlineDropdownHeight;
    #selectedDialCode;
    #dropdownArrow;
    #dropdownContent;
    #searchIcon;
    #searchNoResults;
    #searchResultsA11yText;
    #dropdownForContainer;
    #selectedItem;
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
    //* Generate all of the markup for the plugin: the selected country overlay, and the dropdown.
    generateMarkup(countries) {
      this.#countries = countries;
      this.telInput.classList.add("iti__tel-input");
      if (!this.telInput.hasAttribute("autocomplete")) {
        this.telInput.setAttribute("autocomplete", "tel");
      }
      if (!this.telInput.hasAttribute("inputmode")) {
        this.telInput.setAttribute("inputmode", "tel");
      }
      const wrapper = this.#createWrapperAndInsert();
      this.#maybeBuildCountryContainer(wrapper);
      wrapper.appendChild(this.telInput);
      this.#maybeUpdateInputPaddingAndReveal();
      this.#maybeBuildHiddenInputs(wrapper);
    }
    #createWrapperAndInsert() {
      const {
        allowDropdown,
        showFlags,
        containerClass,
        useFullscreenPopup
      } = this.#options;
      const parentClasses = buildClassNames({
        iti: true,
        "iti--allow-dropdown": allowDropdown,
        "iti--show-flags": showFlags,
        "iti--inline-dropdown": !useFullscreenPopup,
        [containerClass]: Boolean(containerClass)
      });
      const wrapper = createEl("div", { class: parentClasses });
      if (this.#isRTL) {
        wrapper.setAttribute("dir", "ltr");
      }
      this.telInput.before(wrapper);
      return wrapper;
    }
    #maybeBuildCountryContainer(wrapper) {
      const { allowDropdown, separateDialCode, showFlags } = this.#options;
      if (allowDropdown || showFlags || separateDialCode) {
        this.countryContainer = createEl(
          "div",
          // visibly hidden until we measure it's width to set the input padding correctly
          { class: `iti__country-container ${CLASSES.V_HIDE}` },
          wrapper
        );
        if (allowDropdown) {
          this.selectedCountry = createEl(
            "button",
            {
              type: "button",
              class: "iti__selected-country",
              [ARIA.EXPANDED]: "false",
              [ARIA.LABEL]: this.#options.i18n.noCountrySelected,
              [ARIA.HASPOPUP]: "dialog",
              [ARIA.CONTROLS]: `iti-${this.#id}__dropdown-content`
            },
            this.countryContainer
          );
          if (this.telInput.disabled) {
            this.selectedCountry.setAttribute("disabled", "true");
          }
        } else {
          this.selectedCountry = createEl(
            "div",
            { class: "iti__selected-country" },
            this.countryContainer
          );
        }
        const selectedCountryPrimary = createEl(
          "div",
          { class: "iti__selected-country-primary" },
          this.selectedCountry
        );
        this.selectedCountryInner = createEl(
          "div",
          { class: CLASSES.FLAG },
          selectedCountryPrimary
        );
        if (allowDropdown) {
          this.#dropdownArrow = createEl(
            "div",
            { class: "iti__arrow", [ARIA.HIDDEN]: "true" },
            selectedCountryPrimary
          );
        }
        if (separateDialCode) {
          this.#selectedDialCode = createEl(
            "div",
            { class: "iti__selected-dial-code" },
            this.selectedCountry
          );
        }
        if (allowDropdown) {
          this.#buildDropdownContent();
        }
      }
    }
    #maybeEnsureDropdownWidthSet() {
      const { fixDropdownWidth } = this.#options;
      if (fixDropdownWidth && !this.#dropdownContent.style.width) {
        const inputWidth = this.telInput.offsetWidth;
        if (inputWidth > 0) {
          this.#dropdownContent.style.width = `${inputWidth}px`;
        }
      }
    }
    #buildDropdownContent() {
      const {
        fixDropdownWidth,
        useFullscreenPopup,
        countrySearch,
        i18n,
        dropdownContainer,
        containerClass
      } = this.#options;
      const extraClasses = fixDropdownWidth ? "" : "iti--flexible-dropdown-width";
      this.#dropdownContent = createEl("div", {
        id: `iti-${this.#id}__dropdown-content`,
        class: `iti__dropdown-content ${CLASSES.HIDE} ${extraClasses}`,
        role: "dialog",
        [ARIA.MODAL]: "true"
      });
      if (this.#isRTL) {
        this.#dropdownContent.setAttribute("dir", "rtl");
      }
      if (countrySearch) {
        this.#buildSearchUI();
      }
      this.countryList = createEl(
        "ul",
        {
          class: "iti__country-list",
          id: `iti-${this.#id}__country-listbox`,
          role: "listbox",
          [ARIA.LABEL]: i18n.countryListAriaLabel
        },
        this.#dropdownContent
      );
      this.#appendListItems();
      if (countrySearch) {
        this.#updateSearchResultsA11yText();
      }
      if (!useFullscreenPopup) {
        this.#maybeEnsureDropdownWidthSet();
        this.#inlineDropdownHeight = this.#getHiddenInlineDropdownHeight();
        if (countrySearch) {
          this.#dropdownContent.style.height = `${this.#inlineDropdownHeight}px`;
        }
      }
      if (dropdownContainer) {
        const dropdownClasses = buildClassNames({
          iti: true,
          "iti--container": true,
          "iti--fullscreen-popup": useFullscreenPopup,
          "iti--inline-dropdown": !useFullscreenPopup,
          [containerClass]: Boolean(containerClass)
        });
        this.#dropdownForContainer = createEl("div", { class: dropdownClasses });
        this.#dropdownForContainer.appendChild(this.#dropdownContent);
      } else {
        this.countryContainer.appendChild(this.#dropdownContent);
      }
    }
    #buildSearchUI() {
      const { i18n, searchInputClass } = this.#options;
      const searchWrapper = createEl(
        "div",
        { class: "iti__search-input-wrapper" },
        this.#dropdownContent
      );
      this.#searchIcon = createEl(
        "span",
        {
          class: "iti__search-icon",
          [ARIA.HIDDEN]: "true"
        },
        searchWrapper
      );
      this.#searchIcon.innerHTML = buildSearchIcon();
      this.searchInput = createEl(
        "input",
        {
          id: `iti-${this.#id}__search-input`,
          // Chrome says inputs need either a name or an id
          type: "search",
          class: `iti__search-input ${searchInputClass}`,
          placeholder: i18n.searchPlaceholder,
          // role=combobox + aria-autocomplete=list + aria-activedescendant allows maintaining focus on the search input while allowing users to navigate search results with up/down keyboard keys
          role: "combobox",
          [ARIA.EXPANDED]: "true",
          [ARIA.LABEL]: i18n.searchPlaceholder,
          [ARIA.CONTROLS]: `iti-${this.#id}__country-listbox`,
          [ARIA.AUTOCOMPLETE]: "list",
          autocomplete: "off"
        },
        searchWrapper
      );
      this.searchClearButton = createEl(
        "button",
        {
          type: "button",
          class: `iti__search-clear ${CLASSES.HIDE}`,
          [ARIA.LABEL]: i18n.clearSearchAriaLabel,
          tabindex: "-1"
        },
        searchWrapper
      );
      this.searchClearButton.innerHTML = buildClearIcon(this.#id);
      this.#searchResultsA11yText = createEl(
        "span",
        { class: "iti__a11y-text" },
        this.#dropdownContent
      );
      this.#searchNoResults = createEl(
        "div",
        {
          class: `iti__no-results ${CLASSES.HIDE}`,
          [ARIA.HIDDEN]: "true"
          // all a11y messaging happens in this.#searchResultsA11yText
        },
        this.#dropdownContent
      );
      this.#searchNoResults.textContent = i18n.searchEmptyState;
    }
    #maybeUpdateInputPaddingAndReveal() {
      if (this.countryContainer) {
        this.#updateInputPadding();
        this.countryContainer.classList.remove(CLASSES.V_HIDE);
      }
    }
    #maybeBuildHiddenInputs(wrapper) {
      const { hiddenInput } = this.#options;
      if (hiddenInput) {
        const telInputName = this.telInput.getAttribute("name") || "";
        const names = hiddenInput(telInputName);
        if (names.phone) {
          const existingInput = this.telInput.form?.querySelector(
            `input[name="${names.phone}"]`
          );
          if (existingInput) {
            this.hiddenInput = existingInput;
          } else {
            this.hiddenInput = createEl("input", {
              type: "hidden",
              name: names.phone
            });
            wrapper.appendChild(this.hiddenInput);
          }
        }
        if (names.country) {
          const existingInput = this.telInput.form?.querySelector(
            `input[name="${names.country}"]`
          );
          if (existingInput) {
            this.hiddenInputCountry = existingInput;
          } else {
            this.hiddenInputCountry = createEl("input", {
              type: "hidden",
              name: names.country
            });
            wrapper.appendChild(this.hiddenInputCountry);
          }
        }
      }
    }
    //* For each country: add a country list item <li> to the countryList <ul> container.
    #appendListItems() {
      const frag = document.createDocumentFragment();
      for (let i = 0; i < this.#countries.length; i++) {
        const c = this.#countries[i];
        const liClass = buildClassNames({
          [CLASSES.COUNTRY_ITEM]: true
        });
        const listItem = createEl("li", {
          id: `iti-${this.#id}__item-${c.iso2}`,
          class: liClass,
          tabindex: "-1",
          role: "option",
          [ARIA.SELECTED]: "false"
        });
        listItem.dataset.dialCode = c.dialCode;
        listItem.dataset.countryCode = c.iso2;
        c.nodeById[this.#id] = listItem;
        if (this.#options.showFlags) {
          createEl("div", { class: `${CLASSES.FLAG} iti__${c.iso2}` }, listItem);
        }
        const nameEl = createEl("span", { class: "iti__country-name" }, listItem);
        nameEl.textContent = `${c.name} `;
        const dialEl = createEl("span", { class: "iti__dial-code" }, nameEl);
        if (this.#isRTL) {
          dialEl.setAttribute("dir", "ltr");
        }
        dialEl.textContent = `(+${c.dialCode})`;
        frag.appendChild(listItem);
      }
      this.countryList.appendChild(frag);
    }
    //* Update the input padding to make space for the selected country/dial code.
    #updateInputPadding() {
      if (this.selectedCountry) {
        const fallbackWidth = this.#options.separateDialCode ? LAYOUT.SANE_SELECTED_WITH_DIAL_WIDTH : LAYOUT.SANE_SELECTED_NO_DIAL_WIDTH;
        const selectedCountryWidth = this.selectedCountry.offsetWidth || this.#getHiddenSelectedCountryWidth() || fallbackWidth;
        const inputPadding = selectedCountryWidth + LAYOUT.INPUT_PADDING_EXTRA_LEFT;
        this.telInput.style.paddingLeft = `${inputPadding}px`;
      }
    }
    static #getBody() {
      let body;
      try {
        body = window.top.document.body;
      } catch (e) {
        body = document.body;
      }
      return body;
    }
    //* When input is in a hidden container during init, we cannot calculate the selected country width.
    //* Fix: clone the markup, make it invisible, add it to the end of the DOM, and then measure it's width.
    //* To get the right styling to apply, all we need is a shallow clone of the container,
    //* and then to inject a deep clone of the selectedCountry element.
    #getHiddenSelectedCountryWidth() {
      if (this.telInput.parentNode) {
        const body = _UI.#getBody();
        const containerClone = this.telInput.parentNode.cloneNode(
          false
        );
        containerClone.style.visibility = "hidden";
        body.appendChild(containerClone);
        const countryContainerClone = this.countryContainer.cloneNode();
        containerClone.appendChild(countryContainerClone);
        const selectedCountryClone = this.selectedCountry.cloneNode(
          true
        );
        countryContainerClone.appendChild(selectedCountryClone);
        const width = selectedCountryClone.offsetWidth;
        body.removeChild(containerClone);
        return width;
      }
      return 0;
    }
    // this is run before we add the dropdown to the DOM
    #getHiddenInlineDropdownHeight() {
      const body = _UI.#getBody();
      this.#dropdownContent.classList.remove(CLASSES.HIDE);
      const tempContainer = createEl("div", { class: "iti iti--inline-dropdown" });
      tempContainer.appendChild(this.#dropdownContent);
      tempContainer.style.visibility = "hidden";
      body.appendChild(tempContainer);
      const height = this.#dropdownContent.offsetHeight;
      body.removeChild(tempContainer);
      tempContainer.style.visibility = "";
      this.#dropdownContent.classList.add(CLASSES.HIDE);
      return height > 0 ? height : LAYOUT.SANE_DROPDOWN_HEIGHT;
    }
    //* Update search results text (for a11y).
    #updateSearchResultsA11yText() {
      const { i18n } = this.#options;
      const count = this.countryList.childElementCount;
      this.#searchResultsA11yText.textContent = i18n.searchSummaryAria(count);
    }
    //* Country search: Filter the countries according to the search query.
    filterCountriesByQuery(query) {
      let matchedCountries;
      if (query === "") {
        matchedCountries = this.#countries;
      } else {
        matchedCountries = getMatchedCountries(this.#countries, query);
      }
      this.#filterCountries(matchedCountries);
    }
    // Search input handlers
    #doFilter() {
      const inputQuery = this.searchInput.value.trim();
      this.filterCountriesByQuery(inputQuery);
      if (this.searchInput.value) {
        this.searchClearButton.classList.remove(CLASSES.HIDE);
      } else {
        this.searchClearButton.classList.add(CLASSES.HIDE);
      }
    }
    handleSearchChange() {
      if (this.#searchKeyupTimer) {
        clearTimeout(this.#searchKeyupTimer);
      }
      this.#searchKeyupTimer = setTimeout(() => {
        this.#doFilter();
        this.#searchKeyupTimer = null;
      }, TIMINGS.SEARCH_DEBOUNCE_MS);
    }
    handleSearchClear() {
      this.searchInput.value = "";
      this.searchInput.focus();
      this.#doFilter();
    }
    //* Check if an element is visible within it's container, else scroll until it is.
    scrollTo(element) {
      const container = this.countryList;
      const scrollTop = document.documentElement.scrollTop;
      const containerHeight = container.offsetHeight;
      const containerTop = container.getBoundingClientRect().top + scrollTop;
      const containerBottom = containerTop + containerHeight;
      const elementHeight = element.offsetHeight;
      const elementTop = element.getBoundingClientRect().top + scrollTop;
      const elementBottom = elementTop + elementHeight;
      const newScrollTop = elementTop - containerTop + container.scrollTop;
      if (elementTop < containerTop) {
        container.scrollTop = newScrollTop;
      } else if (elementBottom > containerBottom) {
        const heightDifference = containerHeight - elementHeight;
        container.scrollTop = newScrollTop - heightDifference;
      }
    }
    //* Remove highlighting from the previous list item and highlight the new one.
    highlightListItem(listItem, shouldFocus) {
      const prevItem = this.highlightedItem;
      if (prevItem) {
        prevItem.classList.remove(CLASSES.HIGHLIGHT);
      }
      this.highlightedItem = listItem;
      if (this.highlightedItem) {
        this.highlightedItem.classList.add(CLASSES.HIGHLIGHT);
        if (this.#options.countrySearch) {
          const activeDescendant = this.highlightedItem.getAttribute("id") || "";
          this.searchInput.setAttribute(ARIA.ACTIVE_DESCENDANT, activeDescendant);
        }
      }
      if (shouldFocus) {
        this.highlightedItem.focus();
      }
    }
    //* Highlight the next/prev item in the list (and ensure it is visible).
    handleUpDownKey(key) {
      let next = key === KEYS.ARROW_UP ? this.highlightedItem?.previousElementSibling : this.highlightedItem?.nextElementSibling;
      if (!next && this.countryList.childElementCount > 1) {
        next = key === KEYS.ARROW_UP ? this.countryList.lastElementChild : this.countryList.firstElementChild;
      }
      if (next) {
        this.scrollTo(next);
        this.highlightListItem(next, false);
      }
    }
    // Update the selected list item in the dropdown
    #updateSelectedItem(iso2) {
      if (this.#selectedItem && this.#selectedItem.dataset.countryCode !== iso2) {
        this.#selectedItem.setAttribute(ARIA.SELECTED, "false");
        this.#selectedItem.querySelector(".iti__country-check")?.remove();
        this.#selectedItem = null;
      }
      if (iso2 && !this.#selectedItem) {
        const newListItem = this.countryList.querySelector(
          `[data-country-code="${iso2}"]`
        );
        if (newListItem) {
          newListItem.setAttribute(ARIA.SELECTED, "true");
          const checkIcon = createEl(
            "span",
            { class: "iti__country-check", [ARIA.HIDDEN]: "true" },
            newListItem
          );
          checkIcon.innerHTML = buildCheckIcon();
          this.#selectedItem = newListItem;
        }
      }
    }
    //* Country search: Filter the country list to the given array of countries.
    #filterCountries(matchedCountries) {
      this.countryList.innerHTML = "";
      let noCountriesAddedYet = true;
      for (const c of matchedCountries) {
        const listItem = c.nodeById[this.#id];
        if (listItem) {
          this.countryList.appendChild(listItem);
          if (noCountriesAddedYet) {
            this.highlightListItem(listItem, false);
            noCountriesAddedYet = false;
          }
        }
      }
      if (noCountriesAddedYet) {
        this.highlightListItem(null, false);
        if (this.#searchNoResults) {
          this.#searchNoResults.classList.remove(CLASSES.HIDE);
        }
      } else if (this.#searchNoResults) {
        this.#searchNoResults.classList.add(CLASSES.HIDE);
      }
      this.countryList.scrollTop = 0;
      this.#updateSearchResultsA11yText();
    }
    destroy() {
      this.telInput.iti = void 0;
      delete this.telInput.dataset.intlTelInputId;
      if (this.#options.separateDialCode) {
        this.telInput.style.paddingLeft = this.#originalPaddingLeft;
      }
      const wrapper = this.telInput.parentNode;
      wrapper.before(this.telInput);
      wrapper.remove();
      this.telInput = null;
      this.countryContainer = null;
      this.selectedCountry = null;
      this.selectedCountryInner = null;
      this.searchInput = null;
      this.searchClearButton = null;
      this.countryList = null;
      this.hiddenInput = null;
      this.hiddenInputCountry = null;
      this.highlightedItem = null;
      this.#selectedDialCode = null;
      this.#dropdownArrow = null;
      this.#dropdownContent = null;
      this.#searchIcon = null;
      this.#searchNoResults = null;
      this.#searchResultsA11yText = null;
      this.#dropdownForContainer = null;
      this.#selectedItem = null;
      for (const c of this.#countries) {
        delete c.nodeById[this.#id];
      }
      this.#countries = null;
    }
    // UI: Open the dropdown (DOM only).
    openDropdown() {
      const {
        countrySearch,
        dropdownAlwaysOpen,
        dropdownContainer
      } = this.#options;
      this.#maybeEnsureDropdownWidthSet();
      if (dropdownContainer) {
        this.#handleDropdownContainer();
      } else {
        const positionBelow = this.#shouldPositionInlineDropdownBelowInput();
        const distance = this.telInput.offsetHeight + LAYOUT.DROPDOWN_MARGIN;
        if (positionBelow) {
          this.#dropdownContent.style.top = `${distance}px`;
        } else {
          this.#dropdownContent.style.bottom = `${distance}px`;
        }
      }
      this.#dropdownContent.classList.remove(CLASSES.HIDE);
      this.selectedCountry.setAttribute(ARIA.EXPANDED, "true");
      if (countrySearch) {
        const firstCountryItem = this.countryList.firstElementChild;
        if (firstCountryItem) {
          this.highlightListItem(firstCountryItem, false);
          this.countryList.scrollTop = 0;
        }
        if (!dropdownAlwaysOpen) {
          this.searchInput.focus();
        }
      }
      this.#dropdownArrow.classList.add(CLASSES.ARROW_UP);
    }
    // UI: Close the dropdown (DOM only).
    closeDropdown() {
      const { countrySearch, dropdownContainer } = this.#options;
      this.#dropdownContent.classList.add(CLASSES.HIDE);
      this.selectedCountry.setAttribute(ARIA.EXPANDED, "false");
      if (countrySearch) {
        this.searchInput.removeAttribute(ARIA.ACTIVE_DESCENDANT);
        if (this.highlightedItem) {
          this.highlightedItem.classList.remove(CLASSES.HIGHLIGHT);
          this.highlightedItem = null;
        }
      }
      this.#dropdownArrow.classList.remove(CLASSES.ARROW_UP);
      if (dropdownContainer) {
        this.#dropdownForContainer.remove();
        this.#dropdownForContainer.style.top = "";
        this.#dropdownForContainer.style.bottom = "";
        this.#dropdownForContainer.style.paddingLeft = "";
        this.#dropdownForContainer.style.paddingRight = "";
      } else {
        this.#dropdownContent.style.top = "";
        this.#dropdownContent.style.bottom = "";
      }
    }
    #shouldPositionInlineDropdownBelowInput() {
      if (this.#options.dropdownAlwaysOpen) {
        return true;
      }
      const inputPos = this.telInput.getBoundingClientRect();
      const spaceAbove = inputPos.top;
      const spaceBelow = window.innerHeight - inputPos.bottom;
      return spaceBelow >= this.#inlineDropdownHeight || spaceBelow >= spaceAbove;
    }
    // inject dropdown into container and apply positioning styles
    #handleDropdownContainer() {
      const { dropdownContainer, useFullscreenPopup } = this.#options;
      if (useFullscreenPopup) {
        if (window.innerWidth >= 500) {
          const inputPos = this.telInput.getBoundingClientRect();
          this.#dropdownForContainer.style.paddingLeft = `${inputPos.left}px`;
          this.#dropdownForContainer.style.paddingRight = `${window.innerWidth - inputPos.right}px`;
        }
      } else {
        const inputPos = this.telInput.getBoundingClientRect();
        this.#dropdownForContainer.style.left = `${inputPos.left}px`;
        const positionBelow = this.#shouldPositionInlineDropdownBelowInput();
        if (positionBelow) {
          this.#dropdownForContainer.style.top = `${inputPos.bottom + LAYOUT.DROPDOWN_MARGIN}px`;
        } else {
          this.#dropdownForContainer.style.top = "unset";
          this.#dropdownForContainer.style.bottom = `${window.innerHeight - inputPos.top + LAYOUT.DROPDOWN_MARGIN}px`;
        }
      }
      dropdownContainer.appendChild(this.#dropdownForContainer);
    }
    // UI: Whether the dropdown is currently closed (hidden).
    isDropdownClosed() {
      return this.#dropdownContent.classList.contains(CLASSES.HIDE);
    }
    setCountry(selectedCountryData) {
      const { allowDropdown, showFlags, separateDialCode, i18n } = this.#options;
      const { name, dialCode, iso2 = "" } = selectedCountryData;
      if (allowDropdown) {
        this.#updateSelectedItem(iso2);
      }
      if (this.selectedCountry) {
        const flagClass = iso2 && showFlags ? `${CLASSES.FLAG} iti__${iso2}` : `${CLASSES.FLAG} ${CLASSES.GLOBE}`;
        let ariaLabel, title, selectedCountryInner;
        if (iso2) {
          title = name;
          ariaLabel = i18n.selectedCountryAriaLabel.replace("${countryName}", name).replace("${dialCode}", `+${dialCode}`);
          selectedCountryInner = showFlags ? "" : buildGlobeIcon();
        } else {
          title = i18n.noCountrySelected;
          ariaLabel = i18n.noCountrySelected;
          selectedCountryInner = buildGlobeIcon();
        }
        this.selectedCountryInner.className = flagClass;
        this.selectedCountry.setAttribute("title", title);
        this.selectedCountry.setAttribute(ARIA.LABEL, ariaLabel);
        this.selectedCountryInner.innerHTML = selectedCountryInner;
      }
      if (separateDialCode) {
        const fullDialCode = dialCode ? `+${dialCode}` : "";
        this.#selectedDialCode.textContent = fullDialCode;
        this.#updateInputPadding();
      }
    }
  };

  // src/js/modules/data/country-data.ts
  var processAllCountries = (options) => {
    const { onlyCountries, excludeCountries } = options;
    if (onlyCountries?.length) {
      const lowerCaseOnlyCountries = onlyCountries.map(
        (country) => country.toLowerCase()
      );
      return data_default.filter(
        (country) => lowerCaseOnlyCountries.includes(country.iso2)
      );
    } else if (excludeCountries?.length) {
      const lowerCaseExcludeCountries = excludeCountries.map(
        (country) => country.toLowerCase()
      );
      return data_default.filter(
        (country) => !lowerCaseExcludeCountries.includes(country.iso2)
      );
    }
    return data_default;
  };
  var generateCountryNames = (countries, options) => {
    const { countryNameLocale, i18n } = options;
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
      c.name = i18n[c.iso2] || displayNames?.of(c.iso2.toUpperCase()) || "";
    }
  };
  var processDialCodes = (countries) => {
    const dialCodes = /* @__PURE__ */ new Set();
    let dialCodeMaxLen = 0;
    const dialCodeToIso2Map = {};
    const addToDialCodeMap = (iso2, dialCode) => {
      if (!iso2 || !dialCode) {
        return;
      }
      if (dialCode.length > dialCodeMaxLen) {
        dialCodeMaxLen = dialCode.length;
      }
      if (!dialCodeToIso2Map.hasOwnProperty(dialCode)) {
        dialCodeToIso2Map[dialCode] = [];
      }
      const iso2List = dialCodeToIso2Map[dialCode];
      if (iso2List.includes(iso2)) {
        return;
      }
      iso2List.push(iso2);
    };
    const countriesSortedByPriority = [...countries].sort((a, b) => a.priority - b.priority);
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
    return { dialCodes, dialCodeMaxLen, dialCodeToIso2Map };
  };
  var sortCountries = (countries, options) => {
    if (options.countryOrder) {
      options.countryOrder = options.countryOrder.map(
        (iso2) => iso2.toLowerCase()
      );
    }
    countries.sort((a, b) => {
      const { countryOrder } = options;
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
  var cacheSearchTokens = (countries) => {
    for (const c of countries) {
      c.normalisedName = normaliseString(c.name);
      c.initials = c.normalisedName.split(/[^a-z]/).map((word) => word[0]).join("");
      c.dialCodePlus = `+${c.dialCode}`;
    }
  };

  // src/js/modules/data/intl-regionless.ts
  var REGIONLESS_DIAL_CODES = /* @__PURE__ */ new Set([
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
    return number.startsWith("+") && REGIONLESS_DIAL_CODES.has(dialCode);
  };

  // src/js/modules/format/formatting.ts
  var beforeSetNumber = (fullNumber, hasValidDialCode, separateDialCode, selectedCountryData) => {
    let number = fullNumber;
    if (separateDialCode) {
      if (hasValidDialCode) {
        const dialCode = `+${selectedCountryData.dialCode}`;
        const start = number[dialCode.length] === " " || number[dialCode.length] === "-" ? dialCode.length + 1 : dialCode.length;
        number = number.substring(start);
      }
    }
    return number;
  };
  var formatNumberAsYouType = (fullNumber, telInputValue, utils, selectedCountryData, separateDialCode) => {
    const result = utils ? utils.formatNumberAsYouType(fullNumber, selectedCountryData.iso2) : fullNumber;
    const { dialCode } = selectedCountryData;
    if (separateDialCode && telInputValue.charAt(0) !== "+" && result.includes(`+${dialCode}`)) {
      const afterDialCode = result.split(`+${dialCode}`)[1] || "";
      return afterDialCode.trim();
    }
    return result;
  };

  // src/js/modules/format/caret.ts
  var translateCursorPosition = (relevantChars, formattedValue, prevCaretPos, isDeleteForwards) => {
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

  // src/js/modules/data/nanp-regionless.ts
  var regionlessNanpNumbers = [
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
  ];
  var isRegionlessNanp = (number) => {
    const numeric = getNumeric(number);
    if (numeric.startsWith(DIAL.NANP) && numeric.length >= 4) {
      const areaCode = numeric.substring(1, 4);
      return regionlessNanpNumbers.includes(areaCode);
    }
    return false;
  };

  // src/js/modules/core/numerals.ts
  var Numerals = class {
    #userNumeralSet;
    constructor() {
    }
    // If any Arabic-Indic digits, then label it as that set. Same for Persian. Otherwise assume ASCII.
    #updateNumeralSet(str) {
      if (/[\u0660-\u0669]/.test(str)) {
        this.#userNumeralSet = "arabic-indic";
      } else if (/[\u06F0-\u06F9]/.test(str)) {
        this.#userNumeralSet = "persian";
      } else {
        this.#userNumeralSet = "ascii";
      }
    }
    // Denormalise ASCII 0-9 to the user's numeral set, if known. If not known, return the string as-is.
    denormalise(str, currentInputValue) {
      if (!this.#userNumeralSet) {
        this.#updateNumeralSet(currentInputValue);
      }
      if (this.#userNumeralSet === "ascii") {
        return str;
      }
      const base = this.#userNumeralSet === "arabic-indic" ? 1632 : 1776;
      return str.replace(/[0-9]/g, (d) => String.fromCharCode(base + Number(d)));
    }
    // Normalize Eastern Arabic (U+0660-0669) and Persian/Extended Arabic-Indic (U+06F0-06F9) numerals to ASCII 0-9
    normalise(str) {
      if (!str) {
        return "";
      }
      this.#updateNumeralSet(str);
      if (this.#userNumeralSet === "ascii") {
        return str;
      }
      const base = this.#userNumeralSet === "arabic-indic" ? 1632 : 1776;
      const regex = this.#userNumeralSet === "arabic-indic" ? /[\u0660-\u0669]/g : /[\u06F0-\u06F9]/g;
      return str.replace(regex, (ch) => String.fromCharCode(48 + (ch.charCodeAt(0) - base)));
    }
    isAscii() {
      return this.#userNumeralSet === "ascii";
    }
  };

  // src/js/intl-tel-input.ts
  var id = 0;
  var iso2Set2 = new Set(data_default.map((c) => c.iso2));
  var isIso22 = (val) => iso2Set2.has(val);
  var Iti = class _Iti {
    //* PRIVATE FIELDS
    #ui;
    #options;
    #isAndroid;
    // country data
    #countries;
    #dialCodeMaxLen;
    #dialCodeToIso2Map;
    #dialCodes;
    #countryByIso2;
    #selectedCountryData;
    #maxCoreNumberLength;
    #defaultCountry;
    #abortController;
    #dropdownAbortController;
    #numerals;
    #resolveAutoCountryPromise;
    #rejectAutoCountryPromise;
    #resolveUtilsScriptPromise;
    #rejectUtilsScriptPromise;
    constructor(input, customOptions = {}) {
      this.id = id++;
      UI.validateInput(input);
      const validatedOptions = validateOptions(customOptions);
      this.#options = { ...defaults, ...validatedOptions };
      applyOptionSideEffects(this.#options);
      this.#ui = new UI(input, this.#options, this.id);
      this.#isAndroid = getIsAndroid();
      this.#numerals = new Numerals();
      this.promise = this.#createInitPromises(this.#options);
      this.#countries = processAllCountries(this.#options);
      const { dialCodes, dialCodeMaxLen, dialCodeToIso2Map } = processDialCodes(
        this.#countries
      );
      this.#dialCodes = dialCodes;
      this.#dialCodeMaxLen = dialCodeMaxLen;
      this.#dialCodeToIso2Map = dialCodeToIso2Map;
      this.#countryByIso2 = new Map(this.#countries.map((c) => [c.iso2, c]));
      this.#init();
    }
    #getTelInputValue() {
      const inputValue = this.#ui.telInput.value.trim();
      return this.#numerals.normalise(inputValue);
    }
    #setTelInputValue(asciiValue) {
      const currentValue = this.#ui.telInput.value;
      this.#ui.telInput.value = this.#numerals.denormalise(asciiValue, currentValue);
    }
    #createInitPromises(options) {
      const { initialCountry, geoIpLookup, loadUtils } = options;
      const needsAutoCountryPromise = initialCountry === INITIAL_COUNTRY.AUTO && Boolean(geoIpLookup);
      const needsUtilsScriptPromise = Boolean(loadUtils) && !intlTelInput.utils;
      let autoCountryPromise;
      if (needsAutoCountryPromise) {
        autoCountryPromise = new Promise((resolve, reject) => {
          this.#resolveAutoCountryPromise = resolve;
          this.#rejectAutoCountryPromise = reject;
        });
      } else {
        autoCountryPromise = Promise.resolve(void 0);
        this.#resolveAutoCountryPromise = () => {
        };
        this.#rejectAutoCountryPromise = () => {
        };
      }
      let utilsScriptPromise;
      if (needsUtilsScriptPromise) {
        utilsScriptPromise = new Promise((resolve, reject) => {
          this.#resolveUtilsScriptPromise = resolve;
          this.#rejectUtilsScriptPromise = reject;
        });
      } else {
        utilsScriptPromise = Promise.resolve(void 0);
        this.#resolveUtilsScriptPromise = () => {
        };
        this.#rejectUtilsScriptPromise = () => {
        };
      }
      return Promise.all([autoCountryPromise, utilsScriptPromise]);
    }
    #init() {
      this.#selectedCountryData = {};
      this.#abortController = new AbortController();
      this.#processCountryData();
      this.#ui.generateMarkup(this.#countries);
      this.#setInitialState();
      this.#initListeners();
      this.#initRequests();
      if (this.#options.dropdownAlwaysOpen) {
        this.#openDropdown();
      }
    }
    //********************
    //*  PRIVATE METHODS
    //********************
    //* Prepare all of the country data, including onlyCountries, excludeCountries, countryOrder options.
    #processCountryData() {
      generateCountryNames(this.#countries, this.#options);
      sortCountries(this.#countries, this.#options);
      cacheSearchTokens(this.#countries);
    }
    //* Set the initial state of the input value and the selected country by:
    //* 1. Extracting a dial code from the given number
    //* 2. Using explicit initialCountry
    #setInitialState(overrideAutoCountry = false) {
      const attributeValueRaw = this.#ui.telInput.getAttribute("value");
      const attributeValue = this.#numerals.normalise(attributeValueRaw);
      const inputValue = this.#getTelInputValue();
      const useAttribute = attributeValue && attributeValue.startsWith("+") && (!inputValue || !inputValue.startsWith("+"));
      const val = useAttribute ? attributeValue : inputValue;
      const dialCode = this.#getDialCode(val);
      const isRegionlessNanpNumber = isRegionlessNanp(val);
      const { initialCountry, geoIpLookup } = this.#options;
      const isAutoCountry = initialCountry === INITIAL_COUNTRY.AUTO && geoIpLookup;
      const doingAutoCountryLookup = isAutoCountry && !overrideAutoCountry;
      const initialCountryLower = initialCountry.toLowerCase();
      const isValidInitialCountry = isIso22(initialCountryLower);
      if (dialCode) {
        if (isRegionlessNanpNumber) {
          if (isValidInitialCountry) {
            this.#setCountry(initialCountryLower);
          } else if (!doingAutoCountryLookup) {
            this.#setCountry(US.ISO2);
          }
        } else {
          this.#updateCountryFromNumber(val);
        }
      } else if (isValidInitialCountry) {
        this.#setCountry(initialCountryLower);
      } else if (!doingAutoCountryLookup) {
        this.#setCountry("");
      }
      if (val) {
        this.#updateValFromNumber(val);
      }
    }
    //* Initialise the main event listeners: input keyup, and click selected country.
    #initListeners() {
      this.#initTelInputListeners();
      if (this.#options.allowDropdown) {
        this.#initDropdownListeners();
      }
      if ((this.#ui.hiddenInput || this.#ui.hiddenInputCountry) && this.#ui.telInput.form) {
        this.#initHiddenInputListener();
      }
    }
    //* Update hidden input on form submit.
    #initHiddenInputListener() {
      const handleHiddenInputSubmit = () => {
        if (this.#ui.hiddenInput) {
          this.#ui.hiddenInput.value = this.getNumber();
        }
        if (this.#ui.hiddenInputCountry) {
          this.#ui.hiddenInputCountry.value = this.#selectedCountryData.iso2 || "";
        }
      };
      this.#ui.telInput.form?.addEventListener("submit", handleHiddenInputSubmit, {
        signal: this.#abortController.signal
      });
    }
    //* initialise the dropdown listeners.
    #initDropdownListeners() {
      const signal = this.#abortController.signal;
      const handleLabelClick = (e) => {
        if (this.#ui.isDropdownClosed()) {
          this.#ui.telInput.focus();
        } else {
          e.preventDefault();
        }
      };
      const label = this.#ui.telInput.closest("label");
      if (label) {
        label.addEventListener("click", handleLabelClick, { signal });
      }
      const handleClickSelectedCountry = () => {
        if (this.#ui.isDropdownClosed() && !this.#ui.telInput.disabled && !this.#ui.telInput.readOnly) {
          this.#openDropdown();
        }
      };
      this.#ui.selectedCountry.addEventListener(
        "click",
        handleClickSelectedCountry,
        {
          signal
        }
      );
      const handleCountryContainerKeydown = (e) => {
        const allowedKeys = [KEYS.ARROW_UP, KEYS.ARROW_DOWN, KEYS.SPACE, KEYS.ENTER];
        if (this.#ui.isDropdownClosed() && allowedKeys.includes(e.key)) {
          e.preventDefault();
          e.stopPropagation();
          this.#openDropdown();
        }
        if (e.key === KEYS.TAB) {
          this.#closeDropdown();
        }
      };
      this.#ui.countryContainer.addEventListener(
        "keydown",
        handleCountryContainerKeydown,
        { signal }
      );
    }
    //* Init requests: utils script / geo ip lookup.
    #initRequests() {
      const { loadUtils, initialCountry, geoIpLookup } = this.#options;
      if (loadUtils && !intlTelInput.utils) {
        const doAttachUtils = () => {
          intlTelInput.attachUtils(loadUtils)?.catch(() => {
          });
        };
        if (intlTelInput.documentReady()) {
          doAttachUtils();
        } else {
          const handlePageLoad = () => {
            doAttachUtils();
          };
          window.addEventListener("load", handlePageLoad, {
            signal: this.#abortController.signal
          });
        }
      } else {
        this.#resolveUtilsScriptPromise();
      }
      const isAutoCountry = initialCountry === INITIAL_COUNTRY.AUTO && geoIpLookup;
      if (isAutoCountry) {
        if (this.#selectedCountryData.iso2) {
          this.#resolveAutoCountryPromise();
        } else {
          this.#loadAutoCountry();
        }
      }
    }
    //* Perform the geo ip lookup.
    #loadAutoCountry() {
      if (intlTelInput.autoCountry) {
        this.#handleAutoCountry();
      } else {
        this.#ui.selectedCountryInner.classList.add(CLASSES.LOADING);
        if (!intlTelInput.startedLoadingAutoCountry) {
          intlTelInput.startedLoadingAutoCountry = true;
          if (typeof this.#options.geoIpLookup === "function") {
            const successCallback = (iso2 = "") => {
              this.#ui.selectedCountryInner.classList.remove(CLASSES.LOADING);
              const iso2Lower = iso2.toLowerCase();
              if (isIso22(iso2Lower)) {
                intlTelInput.autoCountry = iso2Lower;
                setTimeout(() => _Iti.forEachInstance("handleAutoCountry"));
              } else {
                _Iti.forEachInstance("handleAutoCountryFailure");
              }
            };
            const failureCallback = () => {
              this.#ui.selectedCountryInner.classList.remove(CLASSES.LOADING);
              _Iti.forEachInstance("handleAutoCountryFailure");
            };
            this.#options.geoIpLookup(successCallback, failureCallback);
          }
        }
      }
    }
    #openDropdownWithPlus() {
      this.#openDropdown();
      this.#ui.searchInput.value = "+";
      this.#ui.filterCountriesByQuery("");
    }
    //* Initialize the tel input listeners.
    #initTelInputListeners() {
      this.#bindInputListener();
      this.#maybeBindKeydownListener();
      this.#maybeBindPasteListener();
    }
    #bindInputListener() {
      const {
        strictMode,
        formatAsYouType,
        separateDialCode,
        allowDropdown,
        countrySearch
      } = this.#options;
      let userOverrideFormatting = false;
      if (REGEX.ALPHA_UNICODE.test(this.#getTelInputValue())) {
        userOverrideFormatting = true;
      }
      const handleInputEvent = (e) => {
        const inputValue = this.#getTelInputValue();
        if (this.#isAndroid && e?.data === "+" && separateDialCode && allowDropdown && countrySearch) {
          const currentCaretPos = this.#ui.telInput.selectionStart || 0;
          const valueBeforeCaret = inputValue.substring(0, currentCaretPos - 1);
          const valueAfterCaret = inputValue.substring(currentCaretPos);
          this.#setTelInputValue(valueBeforeCaret + valueAfterCaret);
          this.#openDropdownWithPlus();
          return;
        }
        if (this.#updateCountryFromNumber(inputValue)) {
          this.#triggerCountryChange();
        }
        const isFormattingChar = e?.data && REGEX.NON_PLUS_NUMERIC.test(e.data);
        const isPaste = e?.inputType === INPUT_TYPES.PASTE && inputValue;
        if (isFormattingChar || isPaste && !strictMode) {
          userOverrideFormatting = true;
        } else if (!REGEX.NON_PLUS_NUMERIC.test(inputValue)) {
          userOverrideFormatting = false;
        }
        const isSetNumber = e?.detail && e.detail["isSetNumber"];
        const isAscii = this.#numerals.isAscii();
        if (formatAsYouType && !userOverrideFormatting && !isSetNumber && isAscii) {
          const currentCaretPos = this.#ui.telInput.selectionStart || 0;
          const valueBeforeCaret = inputValue.substring(
            0,
            currentCaretPos
          );
          const relevantCharsBeforeCaret = valueBeforeCaret.replace(
            REGEX.NON_PLUS_NUMERIC_GLOBAL,
            ""
          ).length;
          const isDeleteForwards = e?.inputType === INPUT_TYPES.DELETE_FWD;
          const fullNumber = this.#getFullNumber();
          const formattedValue = formatNumberAsYouType(
            fullNumber,
            inputValue,
            intlTelInput.utils,
            this.#selectedCountryData,
            separateDialCode
          );
          const newCaretPos = translateCursorPosition(
            relevantCharsBeforeCaret,
            formattedValue,
            currentCaretPos,
            isDeleteForwards
          );
          this.#setTelInputValue(formattedValue);
          this.#ui.telInput.setSelectionRange(newCaretPos, newCaretPos);
        }
        if (separateDialCode && inputValue.startsWith("+") && this.#selectedCountryData.dialCode) {
          const cleanNumber = beforeSetNumber(
            inputValue,
            true,
            separateDialCode,
            this.#selectedCountryData
          );
          this.#setTelInputValue(cleanNumber);
        }
      };
      this.#ui.telInput.addEventListener(
        "input",
        handleInputEvent,
        {
          signal: this.#abortController.signal
        }
      );
    }
    #maybeBindKeydownListener() {
      const { strictMode, separateDialCode, allowDropdown, countrySearch } = this.#options;
      if (strictMode || separateDialCode) {
        const handleKeydownEvent = (e) => {
          if (e.key && e.key.length === 1 && !e.altKey && !e.ctrlKey && !e.metaKey) {
            if (separateDialCode && allowDropdown && countrySearch && e.key === "+") {
              e.preventDefault();
              this.#openDropdownWithPlus();
              return;
            }
            if (strictMode) {
              const inputValue = this.#getTelInputValue();
              const alreadyHasPlus = inputValue.startsWith("+");
              const isInitialPlus = !alreadyHasPlus && this.#ui.telInput.selectionStart === 0 && e.key === "+";
              const normalisedKey = this.#numerals.normalise(e.key);
              const isNumeric = /^[0-9]$/.test(normalisedKey);
              const isAllowedChar = separateDialCode ? isNumeric : isInitialPlus || isNumeric;
              const input = this.#ui.telInput;
              const selStart = input.selectionStart;
              const selEnd = input.selectionEnd;
              const before = inputValue.slice(0, selStart);
              const after = inputValue.slice(selEnd);
              const newValue = before + e.key + after;
              const newFullNumber = this.#getFullNumber(newValue);
              const coreNumber = intlTelInput.utils.getCoreNumber(
                newFullNumber,
                this.#selectedCountryData.iso2
              );
              const hasExceededMaxLength = this.#maxCoreNumberLength && coreNumber.length > this.#maxCoreNumberLength;
              const newCountry = this.#getNewCountryFromNumber(newFullNumber);
              const isChangingDialCode = newCountry !== null;
              if (!isAllowedChar || hasExceededMaxLength && !isChangingDialCode && !isInitialPlus) {
                e.preventDefault();
              }
            }
          }
        };
        this.#ui.telInput.addEventListener("keydown", handleKeydownEvent, {
          signal: this.#abortController.signal
        });
      }
    }
    #maybeBindPasteListener() {
      if (this.#options.strictMode) {
        const handlePasteEvent = (e) => {
          e.preventDefault();
          const input = this.#ui.telInput;
          const selStart = input.selectionStart;
          const selEnd = input.selectionEnd;
          const inputValue = this.#getTelInputValue();
          const before = inputValue.slice(0, selStart);
          const after = inputValue.slice(selEnd);
          const iso2 = this.#selectedCountryData.iso2;
          const pastedRaw = e.clipboardData.getData("text");
          const pasted = this.#numerals.normalise(pastedRaw);
          const initialCharSelected = selStart === 0 && selEnd > 0;
          const allowLeadingPlus = !inputValue.startsWith("+") || initialCharSelected;
          const allowedChars = pasted.replace(REGEX.NON_PLUS_NUMERIC_GLOBAL, "");
          const hasLeadingPlus = allowedChars.startsWith("+");
          const numerics = allowedChars.replace(/\+/g, "");
          const sanitised = hasLeadingPlus && allowLeadingPlus ? `+${numerics}` : numerics;
          let newVal = before + sanitised + after;
          if (newVal.length > 5) {
            let coreNumber = intlTelInput.utils.getCoreNumber(newVal, iso2);
            while (coreNumber.length === 0 && newVal.length > 0) {
              newVal = newVal.slice(0, -1);
              coreNumber = intlTelInput.utils.getCoreNumber(newVal, iso2);
            }
            if (!coreNumber) {
              return;
            }
            if (this.#maxCoreNumberLength && coreNumber.length > this.#maxCoreNumberLength) {
              if (input.selectionEnd === inputValue.length) {
                const trimLength = coreNumber.length - this.#maxCoreNumberLength;
                newVal = newVal.slice(0, newVal.length - trimLength);
              } else {
                return;
              }
            }
          }
          this.#setTelInputValue(newVal);
          const caretPos = selStart + sanitised.length;
          input.setSelectionRange(caretPos, caretPos);
          input.dispatchEvent(new InputEvent("input", { bubbles: true }));
        };
        this.#ui.telInput.addEventListener("paste", handlePasteEvent, {
          signal: this.#abortController.signal
        });
      }
    }
    //* Adhere to the input's maxlength attr.
    #cap(number) {
      const max = Number(this.#ui.telInput.getAttribute("maxlength"));
      return max && number.length > max ? number.substring(0, max) : number;
    }
    //* Trigger a custom event on the input (typed via ItiEventMap).
    #trigger(name, detailProps = {}) {
      const e = new CustomEvent(name, {
        bubbles: true,
        cancelable: true,
        detail: detailProps
      });
      this.#ui.telInput.dispatchEvent(e);
    }
    //* Open the dropdown.
    #openDropdown() {
      const { dropdownContainer, useFullscreenPopup } = this.#options;
      this.#dropdownAbortController = new AbortController();
      this.#ui.openDropdown();
      if (!useFullscreenPopup && dropdownContainer) {
        const handleWindowScroll = () => this.#closeDropdown();
        window.addEventListener("scroll", handleWindowScroll, {
          signal: this.#dropdownAbortController.signal
        });
      }
      this.#bindDropdownListeners();
      this.#trigger(EVENTS.OPEN_COUNTRY_DROPDOWN);
    }
    //* We only bind dropdown listeners when the dropdown is open.
    #bindDropdownListeners() {
      const signal = this.#dropdownAbortController.signal;
      this.#bindDropdownMouseoverListener(signal);
      this.#bindDropdownCountryClickListener(signal);
      if (!this.#options.dropdownAlwaysOpen) {
        this.#bindDropdownClickOffListener(signal);
      }
      this.#bindDropdownKeydownListener(signal);
      if (this.#options.countrySearch) {
        this.#bindDropdownSearchListeners(signal);
      }
    }
    //* When mouse over a list item, just highlight that one
    //* we add the class "highlight", so if they hit "enter" we know which one to select.
    #bindDropdownMouseoverListener(signal) {
      const handleMouseoverCountryList = (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          this.#ui.highlightListItem(listItem, false);
        }
      };
      this.#ui.countryList.addEventListener(
        "mouseover",
        handleMouseoverCountryList,
        {
          signal
        }
      );
    }
    //* Listen for country selection.
    #bindDropdownCountryClickListener(signal) {
      const handleClickCountryList = (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          this.#selectListItem(listItem);
        }
      };
      this.#ui.countryList.addEventListener("click", handleClickCountryList, {
        signal
      });
    }
    //* Click off to close (except when this initial opening click is bubbling up).
    //* We cannot just stopPropagation as it may be needed to close another instance.
    #bindDropdownClickOffListener(signal) {
      const handleClickOffToClose = (e) => {
        const target = e.target;
        const clickedInsideDropdown = !!target.closest(
          `#iti-${this.id}__dropdown-content`
        );
        if (!clickedInsideDropdown) {
          this.#closeDropdown();
        }
      };
      setTimeout(() => {
        document.documentElement.addEventListener(
          "click",
          handleClickOffToClose,
          { signal }
        );
      }, 0);
    }
    //* Listen for up/down scrolling, enter to select, or escape to close.
    //* Use keydown as keypress doesn't fire for non-char keys and we want to catch if they
    //* just hit down and hold it to scroll down (no keyup event).
    //* Listen on the document because that's where key events are triggered if no input has focus.
    #bindDropdownKeydownListener(signal) {
      let query = "";
      let queryTimer = null;
      const handleKeydownOnDropdown = (e) => {
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
            this.#ui.handleUpDownKey(e.key);
          } else if (e.key === KEYS.ENTER) {
            this.#handleEnterKey();
          } else if (e.key === KEYS.ESC) {
            this.#closeDropdown();
            this.#ui.selectedCountry.focus();
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
      document.addEventListener("keydown", handleKeydownOnDropdown, { signal });
    }
    //* Search input listeners when countrySearch enabled.
    #bindDropdownSearchListeners(signal) {
      this.#ui.searchInput.addEventListener(
        "input",
        () => this.#ui.handleSearchChange(),
        { signal }
      );
      this.#ui.searchClearButton.addEventListener(
        "click",
        () => this.#ui.handleSearchClear(),
        { signal }
      );
    }
    //* Hidden search (countrySearch disabled): Find the first list item whose name starts with the query string.
    #searchForCountry(query) {
      const match = findFirstCountryStartingWith(this.#countries, query);
      if (match) {
        const listItem = match.nodeById[this.id];
        this.#ui.highlightListItem(listItem, false);
        this.#ui.scrollTo(listItem);
      }
    }
    //* Select the currently highlighted item.
    #handleEnterKey() {
      if (this.#ui.highlightedItem) {
        this.#selectListItem(this.#ui.highlightedItem);
      }
    }
    //* Update the input's value to the given val (format first if possible)
    //* NOTE: this is called from _setInitialState, handleUtils and setNumber.
    #updateValFromNumber(fullNumber) {
      const { formatOnDisplay, nationalMode, separateDialCode } = this.#options;
      let number = fullNumber;
      if (formatOnDisplay && intlTelInput.utils && this.#selectedCountryData) {
        const isRegionless = hasRegionlessDialCode(fullNumber);
        const useNational = nationalMode && !isRegionless || !number.startsWith("+") && !separateDialCode;
        const { NATIONAL, INTERNATIONAL } = intlTelInput.utils.numberFormat;
        const format = useNational ? NATIONAL : INTERNATIONAL;
        number = intlTelInput.utils.formatNumber(
          number,
          this.#selectedCountryData.iso2,
          format
        );
      }
      number = this.#beforeSetNumber(number);
      this.#setTelInputValue(number);
    }
    //* Check if need to select a new country based on the given number
    //* Note: called from _setInitialState, keyup handler, setNumber.
    #updateCountryFromNumber(fullNumber) {
      const iso2 = this.#getNewCountryFromNumber(fullNumber);
      if (iso2 !== null) {
        return this.#setCountry(iso2);
      }
      return false;
    }
    // if there is a selected country, and the number doesn't start with a dial code, then add it
    #ensureHasDialCode(number) {
      const { dialCode, nationalPrefix } = this.#selectedCountryData;
      const alreadyHasPlus = number.startsWith("+");
      if (alreadyHasPlus || !dialCode) {
        return number;
      }
      const hasPrefix = nationalPrefix && number.startsWith(nationalPrefix) && !this.#options.separateDialCode;
      const cleanNumber = hasPrefix ? number.substring(1) : number;
      return `+${dialCode}${cleanNumber}`;
    }
    //* Get the new country based on the input number, or return null if no change, or empty string if should be empty (e.g. if they type an invalid dial code).
    #getNewCountryFromNumber(fullNumber) {
      const plusIndex = fullNumber.indexOf("+");
      let number = plusIndex ? fullNumber.substring(plusIndex) : fullNumber;
      const selectedIso2 = this.#selectedCountryData.iso2;
      const selectedDialCode = this.#selectedCountryData.dialCode;
      number = this.#ensureHasDialCode(number);
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
        if (!selectedIso2 && this.#defaultCountry && iso2Codes.includes(this.#defaultCountry)) {
          return this.#defaultCountry;
        }
        const isRegionlessNanpNumber = selectedDialCode === DIAL.NANP && isRegionlessNanp(numeric);
        if (isRegionlessNanpNumber) {
          return null;
        }
        const { areaCodes, priority } = this.#selectedCountryData;
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
      } else if (number.startsWith("+") && numeric.length) {
        const currentDial = this.#selectedCountryData.dialCode || "";
        if (currentDial && currentDial.startsWith(numeric)) {
          return null;
        }
        return "";
      } else if ((!number || number === "+") && !selectedIso2 && this.#defaultCountry) {
        return this.#defaultCountry;
      }
      return null;
    }
    //* Update the selected country, dial code (if separateDialCode), placeholder, title, and selected list item.
    //* Note: called from _setInitialState, _updateCountryFromNumber, _selectListItem, setCountry.
    #setCountry(iso2) {
      const prevIso2 = this.#selectedCountryData.iso2 || "";
      this.#selectedCountryData = iso2 ? this.#countryByIso2.get(iso2) : {};
      if (this.#selectedCountryData.iso2) {
        this.#defaultCountry = this.#selectedCountryData.iso2;
      }
      this.#ui.setCountry(this.#selectedCountryData);
      this.#updatePlaceholder();
      this.#updateMaxLength();
      return prevIso2 !== iso2;
    }
    //* Update the maximum valid number length for the currently selected country.
    #updateMaxLength() {
      const { strictMode, placeholderNumberType, allowedNumberTypes } = this.#options;
      const { iso2 } = this.#selectedCountryData;
      if (strictMode && intlTelInput.utils) {
        if (iso2) {
          const numberType = intlTelInput.utils.numberType[placeholderNumberType];
          let exampleNumber = intlTelInput.utils.getExampleNumber(
            iso2,
            false,
            numberType,
            true
          );
          let validNumber = exampleNumber;
          while (intlTelInput.utils.isPossibleNumber(
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
        } else {
          this.#maxCoreNumberLength = null;
        }
      }
    }
    //* Update the input placeholder to an example number from the currently selected country.
    #updatePlaceholder() {
      const {
        autoPlaceholder,
        placeholderNumberType,
        nationalMode,
        customPlaceholder
      } = this.#options;
      const shouldSetPlaceholder = autoPlaceholder === PLACEHOLDER_MODES.AGGRESSIVE || !this.#ui.hadInitialPlaceholder && autoPlaceholder === PLACEHOLDER_MODES.POLITE;
      if (intlTelInput.utils && shouldSetPlaceholder) {
        const numberType = intlTelInput.utils.numberType[placeholderNumberType];
        let placeholder = this.#selectedCountryData.iso2 ? intlTelInput.utils.getExampleNumber(
          this.#selectedCountryData.iso2,
          nationalMode,
          numberType
        ) : "";
        placeholder = this.#beforeSetNumber(placeholder);
        if (typeof customPlaceholder === "function") {
          placeholder = customPlaceholder(placeholder, this.#selectedCountryData);
        }
        this.#ui.telInput.setAttribute("placeholder", placeholder);
      }
    }
    //* Called when the user selects a list item from the dropdown.
    #selectListItem(listItem) {
      const iso2 = listItem.dataset[DATA_KEYS.COUNTRY_CODE];
      const countryChanged = this.#setCountry(iso2);
      this.#closeDropdown();
      const dialCode = listItem.dataset[DATA_KEYS.DIAL_CODE];
      this.#updateDialCode(dialCode);
      if (this.#options.formatOnDisplay) {
        const inputValue = this.#getTelInputValue();
        this.#updateValFromNumber(inputValue);
      }
      this.#ui.telInput.focus();
      if (countryChanged) {
        this.#triggerCountryChange();
      }
    }
    //* Close the dropdown and unbind any listeners.
    #closeDropdown(isDestroy) {
      if (this.#ui.isDropdownClosed() || this.#options.dropdownAlwaysOpen && !isDestroy) {
        return;
      }
      this.#ui.closeDropdown();
      this.#dropdownAbortController.abort();
      this.#dropdownAbortController = null;
      this.#trigger(EVENTS.CLOSE_COUNTRY_DROPDOWN);
    }
    //* Replace any existing dial code with the new one
    //* Note: called from _selectListItem and setCountry
    #updateDialCode(newDialCodeBare) {
      const inputVal = this.#getTelInputValue();
      const newDialCode = `+${newDialCodeBare}`;
      let newNumber;
      if (inputVal.startsWith("+")) {
        const prevDialCode = this.#getDialCode(inputVal);
        if (prevDialCode) {
          newNumber = inputVal.replace(prevDialCode, newDialCode);
        } else {
          newNumber = newDialCode;
        }
        this.#setTelInputValue(newNumber);
      }
    }
    //* Try and extract a valid international dial code from a full telephone number.
    //* Note: returns the raw string inc plus character and any whitespace/dots etc.
    #getDialCode(number, includeAreaCode) {
      let dialCode = "";
      if (number.startsWith("+")) {
        let numericChars = "";
        let foundBaseDialCode = false;
        for (let i = 0; i < number.length; i++) {
          const c = number.charAt(i);
          if (/[0-9]/.test(c)) {
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
            if (numericChars.length === this.#dialCodeMaxLen) {
              break;
            }
          }
        }
      }
      return dialCode;
    }
    //* Get the input val, adding the dial code if separateDialCode is enabled.
    #getFullNumber(overrideVal) {
      const val = overrideVal ? this.#numerals.normalise(overrideVal) : this.#getTelInputValue();
      const { dialCode } = this.#selectedCountryData;
      let prefix;
      const numericVal = getNumeric(val);
      if (this.#options.separateDialCode && !val.startsWith("+") && dialCode && numericVal) {
        prefix = `+${dialCode}`;
      } else {
        prefix = "";
      }
      return prefix + val;
    }
    //* Remove the dial code if separateDialCode is enabled also cap the length if the input has a maxlength attribute
    #beforeSetNumber(fullNumber) {
      const hasValidDialCode = Boolean(this.#getDialCode(fullNumber));
      const number = beforeSetNumber(
        fullNumber,
        hasValidDialCode,
        this.#options.separateDialCode,
        this.#selectedCountryData
      );
      return this.#cap(number);
    }
    //* Trigger the 'countrychange' event.
    #triggerCountryChange() {
      this.#trigger(EVENTS.COUNTRY_CHANGE);
    }
    //**************************
    //*  INTERNAL METHODS
    //**************************
    //* Called when the geoip call returns.
    #handleAutoCountry() {
      if (!this.#ui.telInput) {
        this.#resolveAutoCountryPromise?.();
        return;
      }
      if (this.#options.initialCountry === INITIAL_COUNTRY.AUTO && intlTelInput.autoCountry) {
        this.#defaultCountry = intlTelInput.autoCountry;
        const hasSelectedCountryOrGlobe = this.#selectedCountryData.iso2 || this.#ui.selectedCountryInner.classList.contains(CLASSES.GLOBE);
        if (!hasSelectedCountryOrGlobe) {
          this.setCountry(this.#defaultCountry);
        }
        this.#resolveAutoCountryPromise();
      }
    }
    //* Called when the geoip call fails or times out.
    #handleAutoCountryFailure() {
      if (!this.#ui.telInput) {
        this.#rejectAutoCountryPromise?.();
        return;
      }
      this.#setInitialState(true);
      this.#rejectAutoCountryPromise();
    }
    //* Called when the utils request completes.
    #handleUtils() {
      if (!this.#ui.telInput) {
        this.#resolveUtilsScriptPromise?.();
        return;
      }
      if (intlTelInput.utils) {
        const inputValue = this.#getTelInputValue();
        if (inputValue) {
          this.#updateValFromNumber(inputValue);
        }
        if (this.#selectedCountryData.iso2) {
          this.#updatePlaceholder();
          this.#updateMaxLength();
        }
      }
      this.#resolveUtilsScriptPromise();
    }
    //* Called when the utils request fails or times out.
    #handleUtilsFailure(error) {
      if (!this.#ui.telInput) {
        this.#rejectUtilsScriptPromise?.(error);
        return;
      }
      this.#rejectUtilsScriptPromise(error);
    }
    //********************
    //*  PUBLIC METHODS
    //********************
    //* Remove plugin.
    destroy() {
      if (!this.#ui.telInput) {
        return;
      }
      if (this.#options.allowDropdown) {
        this.#closeDropdown(true);
      }
      this.#abortController.abort();
      this.#abortController = null;
      this.#ui.destroy();
      if (intlTelInput.instances instanceof Map) {
        intlTelInput.instances.delete(this.id);
      } else {
        delete intlTelInput.instances[this.id];
      }
    }
    // check if the instance is still valid (not destroyed/unmounted)
    isActive() {
      return !!this.#ui?.telInput;
    }
    //* Get the extension from the current number.
    getExtension() {
      if (intlTelInput.utils && this.#ui.telInput) {
        return intlTelInput.utils.getExtension(
          this.#getFullNumber(),
          this.#selectedCountryData.iso2
        );
      }
      return "";
    }
    //* Format the number to the given format.
    getNumber(format) {
      if (intlTelInput.utils && this.#ui.telInput) {
        const { iso2 } = this.#selectedCountryData;
        const fullNumber = this.#getFullNumber();
        const formattedNumber = intlTelInput.utils.formatNumber(
          fullNumber,
          iso2,
          format
        );
        const currentVal = this.#ui.telInput.value;
        return this.#numerals.denormalise(formattedNumber, currentVal);
      }
      return "";
    }
    //* Get the type of the entered number e.g. landline/mobile.
    getNumberType() {
      if (intlTelInput.utils && this.#ui.telInput) {
        return intlTelInput.utils.getNumberType(
          this.#getFullNumber(),
          this.#selectedCountryData.iso2
        );
      }
      return SENTINELS.UNKNOWN_NUMBER_TYPE;
    }
    //* Get the country data for the currently selected country.
    getSelectedCountryData() {
      return this.#selectedCountryData;
    }
    //* Get the validation error.
    getValidationError() {
      if (intlTelInput.utils && this.#ui.telInput) {
        const { iso2 } = this.#selectedCountryData;
        return intlTelInput.utils.getValidationError(this.#getFullNumber(), iso2);
      }
      return SENTINELS.UNKNOWN_VALIDATION_ERROR;
    }
    //* Validate the input val using number length only
    isValidNumber() {
      const { dialCode, iso2 } = this.#selectedCountryData;
      if (intlTelInput.utils && this.#ui.telInput) {
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
      }
      return this.#validateNumber(false);
    }
    //* Validate the input val with precise validation
    isValidNumberPrecise() {
      return this.#validateNumber(true);
    }
    #utilsIsPossibleNumber(val) {
      return intlTelInput.utils ? intlTelInput.utils.isPossibleNumber(
        val,
        this.#selectedCountryData.iso2,
        this.#options.allowedNumberTypes
      ) : null;
    }
    //* Shared internal validation logic to handle alpha character extension rules.
    #validateNumber(precise) {
      if (!intlTelInput.utils || !this.#ui.telInput) {
        return null;
      }
      const { allowNumberExtensions, allowPhonewords } = this.#options;
      const testValidity = (s) => precise ? this.#utilsIsValidNumber(s) : this.#utilsIsPossibleNumber(s);
      const val = this.#getFullNumber();
      if (!this.#selectedCountryData.iso2) {
        const isRegionlessDialCode = hasRegionlessDialCode(val);
        if (!isRegionlessDialCode) {
          return false;
        }
      }
      if (!testValidity(val)) {
        return false;
      }
      const alphaCharPosition = val.search(REGEX.ALPHA_UNICODE);
      const hasAlphaChar = alphaCharPosition > -1;
      if (hasAlphaChar) {
        const selectedIso2 = this.#selectedCountryData.iso2;
        const hasExtension = Boolean(intlTelInput.utils.getExtension(val, selectedIso2));
        if (hasExtension) {
          return allowNumberExtensions;
        }
        return allowPhonewords;
      }
      return true;
    }
    #utilsIsValidNumber(val) {
      return intlTelInput.utils ? intlTelInput.utils.isValidNumber(
        val,
        this.#selectedCountryData.iso2,
        this.#options.allowedNumberTypes
      ) : null;
    }
    //* Update the selected country, and update the input val accordingly.
    setCountry(iso2) {
      if (!this.#ui.telInput) {
        return;
      }
      const iso2Lower = iso2?.toLowerCase();
      if (!isIso22(iso2Lower)) {
        throw new Error(`Invalid country code: '${iso2Lower}'`);
      }
      const currentCountry = this.#selectedCountryData.iso2;
      const isCountryChange = iso2 && iso2Lower !== currentCountry || !iso2 && currentCountry;
      if (isCountryChange) {
        this.#setCountry(iso2Lower);
        this.#updateDialCode(this.#selectedCountryData.dialCode);
        if (this.#options.formatOnDisplay) {
          const inputValue = this.#getTelInputValue();
          this.#updateValFromNumber(inputValue);
        }
        this.#triggerCountryChange();
      }
    }
    //* Set the input value and update the country.
    setNumber(number) {
      if (!this.#ui.telInput) {
        return;
      }
      const normalisedNumber = this.#numerals.normalise(number);
      const countryChanged = this.#updateCountryFromNumber(normalisedNumber);
      this.#updateValFromNumber(normalisedNumber);
      if (countryChanged) {
        this.#triggerCountryChange();
      }
      this.#trigger(EVENTS.INPUT, { isSetNumber: true });
    }
    //* Set the placeholder number typ
    setPlaceholderNumberType(type) {
      if (!this.#ui.telInput) {
        return;
      }
      this.#options.placeholderNumberType = type;
      this.#updatePlaceholder();
    }
    setDisabled(disabled) {
      if (!this.#ui.telInput) {
        return;
      }
      this.#ui.telInput.disabled = disabled;
      if (disabled) {
        this.#ui.selectedCountry.setAttribute("disabled", "true");
      } else {
        this.#ui.selectedCountry.removeAttribute("disabled");
      }
    }
    //********************
    //*  STATIC METHODS
    //********************
    // Internal instance notification used by utils/geoip loaders.
    // Kept public so module-level helpers (e.g. attachUtils) can call it, while still allowing
    // access to private instance methods.
    static forEachInstance(method, ...args) {
      const instances = intlTelInput.instances;
      const values = instances instanceof Map ? Array.from(instances.values()) : Object.values(instances);
      const arg = args[0];
      values.forEach((instance) => {
        if (!(instance instanceof _Iti)) {
          return;
        }
        switch (method) {
          case "handleUtils":
            instance.#handleUtils();
            break;
          case "handleUtilsFailure":
            instance.#handleUtilsFailure(arg);
            break;
          case "handleAutoCountry":
            instance.#handleAutoCountry();
            break;
          case "handleAutoCountryFailure":
            instance.#handleAutoCountryFailure();
            break;
        }
      });
    }
  };
  var attachUtils = (source) => {
    if (!intlTelInput.utils && !intlTelInput.startedLoadingUtilsScript) {
      let loadCall;
      if (typeof source === "function") {
        try {
          loadCall = Promise.resolve(source());
        } catch (error) {
          return Promise.reject(error);
        }
      } else {
        return Promise.reject(
          new TypeError(
            `The argument passed to attachUtils must be a function that returns a promise for the utilities module, not ${typeof source}`
          )
        );
      }
      intlTelInput.startedLoadingUtilsScript = true;
      return loadCall.then((module) => {
        const utils = module?.default;
        if (!utils || typeof utils !== "object") {
          throw new TypeError(
            "The loader function passed to attachUtils did not resolve to a module object with utils as its default export."
          );
        }
        intlTelInput.utils = utils;
        Iti.forEachInstance("handleUtils");
        return true;
      }).catch((error) => {
        Iti.forEachInstance("handleUtilsFailure", error);
        throw error;
      });
    }
    return null;
  };
  var intlTelInput = Object.assign(
    (input, options) => {
      const iti = new Iti(input, options);
      intlTelInput.instances[iti.id] = iti;
      input.iti = iti;
      return iti;
    },
    {
      defaults,
      //* Using a static var like this allows us to mock it in the tests.
      documentReady: () => document.readyState === "complete",
      //* Get the country data object.
      getCountryData: () => data_default,
      //* A getter for the plugin instance.
      getInstance: (input) => {
        const id2 = input.dataset.intlTelInputId;
        return id2 ? intlTelInput.instances[id2] : null;
      },
      //* A map from instance ID to instance object.
      instances: {},
      attachUtils,
      startedLoadingUtilsScript: false,
      startedLoadingAutoCountry: false,
      version: "26.8.1"
    }
  );
  var intl_tel_input_default = intlTelInput;
  return __toCommonJS(intl_tel_input_exports);
})();

// UMD
  return factoryOutput.default;
}));
