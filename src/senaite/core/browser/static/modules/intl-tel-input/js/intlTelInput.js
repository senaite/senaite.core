/*
 * International Telephone Input v25.15.1
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

  // src/js/intl-tel-input/i18n/en/countries.ts
  var countryTranslations = {
    ad: "Andorra",
    ae: "United Arab Emirates",
    af: "Afghanistan",
    ag: "Antigua & Barbuda",
    ai: "Anguilla",
    al: "Albania",
    am: "Armenia",
    ao: "Angola",
    ar: "Argentina",
    as: "American Samoa",
    at: "Austria",
    au: "Australia",
    aw: "Aruba",
    ax: "\xC5land Islands",
    az: "Azerbaijan",
    ba: "Bosnia & Herzegovina",
    bb: "Barbados",
    bd: "Bangladesh",
    be: "Belgium",
    bf: "Burkina Faso",
    bg: "Bulgaria",
    bh: "Bahrain",
    bi: "Burundi",
    bj: "Benin",
    bl: "St. Barth\xE9lemy",
    bm: "Bermuda",
    bn: "Brunei",
    bo: "Bolivia",
    bq: "Caribbean Netherlands",
    br: "Brazil",
    bs: "Bahamas",
    bt: "Bhutan",
    bw: "Botswana",
    by: "Belarus",
    bz: "Belize",
    ca: "Canada",
    cc: "Cocos (Keeling) Islands",
    cd: "Congo - Kinshasa",
    cf: "Central African Republic",
    cg: "Congo - Brazzaville",
    ch: "Switzerland",
    ci: "C\xF4te d\u2019Ivoire",
    ck: "Cook Islands",
    cl: "Chile",
    cm: "Cameroon",
    cn: "China",
    co: "Colombia",
    cr: "Costa Rica",
    cu: "Cuba",
    cv: "Cape Verde",
    cw: "Cura\xE7ao",
    cx: "Christmas Island",
    cy: "Cyprus",
    cz: "Czechia",
    de: "Germany",
    dj: "Djibouti",
    dk: "Denmark",
    dm: "Dominica",
    do: "Dominican Republic",
    dz: "Algeria",
    ec: "Ecuador",
    ee: "Estonia",
    eg: "Egypt",
    eh: "Western Sahara",
    er: "Eritrea",
    es: "Spain",
    et: "Ethiopia",
    fi: "Finland",
    fj: "Fiji",
    fk: "Falkland Islands",
    fm: "Micronesia",
    fo: "Faroe Islands",
    fr: "France",
    ga: "Gabon",
    gb: "United Kingdom",
    gd: "Grenada",
    ge: "Georgia",
    gf: "French Guiana",
    gg: "Guernsey",
    gh: "Ghana",
    gi: "Gibraltar",
    gl: "Greenland",
    gm: "Gambia",
    gn: "Guinea",
    gp: "Guadeloupe",
    gq: "Equatorial Guinea",
    gr: "Greece",
    gt: "Guatemala",
    gu: "Guam",
    gw: "Guinea-Bissau",
    gy: "Guyana",
    hk: "Hong Kong SAR China",
    hn: "Honduras",
    hr: "Croatia",
    ht: "Haiti",
    hu: "Hungary",
    id: "Indonesia",
    ie: "Ireland",
    il: "Israel",
    im: "Isle of Man",
    in: "India",
    io: "British Indian Ocean Territory",
    iq: "Iraq",
    ir: "Iran",
    is: "Iceland",
    it: "Italy",
    je: "Jersey",
    jm: "Jamaica",
    jo: "Jordan",
    jp: "Japan",
    ke: "Kenya",
    kg: "Kyrgyzstan",
    kh: "Cambodia",
    ki: "Kiribati",
    km: "Comoros",
    kn: "St. Kitts & Nevis",
    kp: "North Korea",
    kr: "South Korea",
    kw: "Kuwait",
    ky: "Cayman Islands",
    kz: "Kazakhstan",
    la: "Laos",
    lb: "Lebanon",
    lc: "St. Lucia",
    li: "Liechtenstein",
    lk: "Sri Lanka",
    lr: "Liberia",
    ls: "Lesotho",
    lt: "Lithuania",
    lu: "Luxembourg",
    lv: "Latvia",
    ly: "Libya",
    ma: "Morocco",
    mc: "Monaco",
    md: "Moldova",
    me: "Montenegro",
    mf: "St. Martin",
    mg: "Madagascar",
    mh: "Marshall Islands",
    mk: "North Macedonia",
    ml: "Mali",
    mm: "Myanmar (Burma)",
    mn: "Mongolia",
    mo: "Macao SAR China",
    mp: "Northern Mariana Islands",
    mq: "Martinique",
    mr: "Mauritania",
    ms: "Montserrat",
    mt: "Malta",
    mu: "Mauritius",
    mv: "Maldives",
    mw: "Malawi",
    mx: "Mexico",
    my: "Malaysia",
    mz: "Mozambique",
    na: "Namibia",
    nc: "New Caledonia",
    ne: "Niger",
    nf: "Norfolk Island",
    ng: "Nigeria",
    ni: "Nicaragua",
    nl: "Netherlands",
    no: "Norway",
    np: "Nepal",
    nr: "Nauru",
    nu: "Niue",
    nz: "New Zealand",
    om: "Oman",
    pa: "Panama",
    pe: "Peru",
    pf: "French Polynesia",
    pg: "Papua New Guinea",
    ph: "Philippines",
    pk: "Pakistan",
    pl: "Poland",
    pm: "St. Pierre & Miquelon",
    pr: "Puerto Rico",
    ps: "Palestinian Territories",
    pt: "Portugal",
    pw: "Palau",
    py: "Paraguay",
    qa: "Qatar",
    re: "R\xE9union",
    ro: "Romania",
    rs: "Serbia",
    ru: "Russia",
    rw: "Rwanda",
    sa: "Saudi Arabia",
    sb: "Solomon Islands",
    sc: "Seychelles",
    sd: "Sudan",
    se: "Sweden",
    sg: "Singapore",
    sh: "St. Helena",
    si: "Slovenia",
    sj: "Svalbard & Jan Mayen",
    sk: "Slovakia",
    sl: "Sierra Leone",
    sm: "San Marino",
    sn: "Senegal",
    so: "Somalia",
    sr: "Suriname",
    ss: "South Sudan",
    st: "S\xE3o Tom\xE9 & Pr\xEDncipe",
    sv: "El Salvador",
    sx: "Sint Maarten",
    sy: "Syria",
    sz: "Eswatini",
    tc: "Turks & Caicos Islands",
    td: "Chad",
    tg: "Togo",
    th: "Thailand",
    tj: "Tajikistan",
    tk: "Tokelau",
    tl: "Timor-Leste",
    tm: "Turkmenistan",
    tn: "Tunisia",
    to: "Tonga",
    tr: "Turkey",
    tt: "Trinidad & Tobago",
    tv: "Tuvalu",
    tw: "Taiwan",
    tz: "Tanzania",
    ua: "Ukraine",
    ug: "Uganda",
    us: "United States",
    uy: "Uruguay",
    uz: "Uzbekistan",
    va: "Vatican City",
    vc: "St. Vincent & Grenadines",
    ve: "Venezuela",
    vg: "British Virgin Islands",
    vi: "U.S. Virgin Islands",
    vn: "Vietnam",
    vu: "Vanuatu",
    wf: "Wallis & Futuna",
    ws: "Samoa",
    ye: "Yemen",
    yt: "Mayotte",
    za: "South Africa",
    zm: "Zambia",
    zw: "Zimbabwe"
  };
  var countries_default = countryTranslations;

  // src/js/intl-tel-input/i18n/en/interface.ts
  var interfaceTranslations = {
    selectedCountryAriaLabel: "Change country, selected ${countryName} (${dialCode})",
    noCountrySelected: "Select country",
    countryListAriaLabel: "List of countries",
    searchPlaceholder: "Search",
    clearSearchAriaLabel: "Clear search",
    zeroSearchResults: "No results found",
    oneSearchResult: "1 result found",
    multipleSearchResults: "${count} results found",
    // additional countries (not supported by country-list library)
    ac: "Ascension Island",
    xk: "Kosovo"
  };
  var interface_default = interfaceTranslations;

  // src/js/intl-tel-input/i18n/en/index.ts
  var allTranslations = { ...countries_default, ...interface_default };
  var en_default = allTranslations;

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
    SANE_SELECTED_WITH_DIAL_WIDTH: 78,
    // px width fallback when separateDialCode enabled
    SANE_SELECTED_NO_DIAL_WIDTH: 42,
    // px width fallback when no separate dial code
    INPUT_PADDING_EXTRA_LEFT: 6
    // px gap between selected country container and input text
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

  // src/js/modules/core/options.ts
  var mq = (q) => typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia(q).matches;
  var computeDefaultUseFullscreenPopup = () => {
    if (typeof navigator !== "undefined" && typeof window !== "undefined") {
      const isMobileUserAgent = /Android.+Mobile|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      );
      const isNarrowViewport = mq("(max-width: 500px)");
      const isShortViewport = mq("(max-height: 600px)");
      const isCoarsePointer = mq("(pointer: coarse)");
      return isMobileUserAgent || isNarrowViewport || isCoarsePointer && isShortViewport;
    }
    return false;
  };
  var defaults = {
    // Allow alphanumeric "phonewords" (e.g. +1 800 FLOWERS) as valid numbers
    allowPhonewords: false,
    //* Whether or not to allow the dropdown.
    allowDropdown: true,
    //* Add a placeholder in the input with an example number for the selected country.
    autoPlaceholder: PLACEHOLDER_MODES.POLITE,
    //* Modify the parentClass.
    containerClass: "",
    //* The order of the countries in the dropdown. Defaults to alphabetical.
    countryOrder: null,
    //* Add a country search input at the top of the dropdown.
    countrySearch: true,
    //* Modify the auto placeholder.
    customPlaceholder: null,
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
    //* Show flags - for both the selected country, and in the country dropdown
    showFlags: true,
    //* Display the international dial code next to the selected flag.
    separateDialCode: false,
    //* Only allow certain chars e.g. a plus followed by numeric digits, and cap at max valid length.
    strictMode: false,
    //* Use full screen popup instead of dropdown for country list.
    useFullscreenPopup: computeDefaultUseFullscreenPopup(),
    //* The number type to enforce during validation.
    validationNumberTypes: ["MOBILE"]
  };
  var applyOptionSideEffects = (o, defaultEnglishStrings) => {
    if (o.useFullscreenPopup) {
      o.fixDropdownWidth = false;
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
    o.i18n = { ...defaultEnglishStrings, ...o.i18n };
  };

  // src/js/modules/utils/string.ts
  var getNumeric = (s) => s.replace(/\D/g, "");
  var normaliseString = (s = "") => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

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

  // src/js/modules/core/ui.ts
  var UI = class {
    constructor(input, options, id2) {
      this.highlightedItem = null;
      this.selectedItem = null;
      input.dataset.intlTelInputId = id2.toString();
      this.telInput = input;
      this.options = options;
      this.id = id2;
      this.hadInitialPlaceholder = Boolean(input.getAttribute("placeholder"));
      this.isRTL = !!this.telInput.closest("[dir=rtl]");
      if (this.options.separateDialCode) {
        this.originalPaddingLeft = this.telInput.style.paddingLeft;
      }
    }
    //* Generate all of the markup for the plugin: the selected country overlay, and the dropdown.
    generateMarkup(countries) {
      this.countries = countries;
      this._prepareTelInput();
      const wrapper = this._createWrapperAndInsert();
      this._maybeBuildCountryContainer(wrapper);
      wrapper.appendChild(this.telInput);
      this._maybeUpdateInputPaddingAndReveal();
      this._maybeBuildHiddenInputs(wrapper);
    }
    _prepareTelInput() {
      this.telInput.classList.add("iti__tel-input");
      if (!this.telInput.hasAttribute("autocomplete") && !this.telInput.form?.hasAttribute("autocomplete")) {
        this.telInput.setAttribute("autocomplete", "off");
      }
    }
    _createWrapperAndInsert() {
      const { allowDropdown, showFlags, containerClass, useFullscreenPopup } = this.options;
      const parentClasses = buildClassNames({
        iti: true,
        "iti--allow-dropdown": allowDropdown,
        "iti--show-flags": showFlags,
        "iti--inline-dropdown": !useFullscreenPopup,
        [containerClass]: Boolean(containerClass)
      });
      const wrapper = createEl("div", { class: parentClasses });
      if (this.isRTL) {
        wrapper.setAttribute("dir", "ltr");
      }
      this.telInput.before(wrapper);
      return wrapper;
    }
    _maybeBuildCountryContainer(wrapper) {
      const { allowDropdown, separateDialCode, showFlags } = this.options;
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
              [ARIA.LABEL]: this.options.i18n.noCountrySelected,
              [ARIA.HASPOPUP]: "dialog",
              [ARIA.CONTROLS]: `iti-${this.id}__dropdown-content`
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
          this.dropdownArrow = createEl(
            "div",
            { class: "iti__arrow", [ARIA.HIDDEN]: "true" },
            selectedCountryPrimary
          );
        }
        if (separateDialCode) {
          this.selectedDialCode = createEl(
            "div",
            { class: "iti__selected-dial-code" },
            this.selectedCountry
          );
        }
        if (allowDropdown) {
          this._buildDropdownContent();
        }
      }
    }
    _buildDropdownContent() {
      const {
        fixDropdownWidth,
        useFullscreenPopup,
        countrySearch,
        i18n,
        dropdownContainer,
        containerClass
      } = this.options;
      const extraClasses = fixDropdownWidth ? "" : "iti--flexible-dropdown-width";
      this.dropdownContent = createEl("div", {
        id: `iti-${this.id}__dropdown-content`,
        class: `iti__dropdown-content ${CLASSES.HIDE} ${extraClasses}`,
        role: "dialog",
        [ARIA.MODAL]: "true"
      });
      if (this.isRTL) {
        this.dropdownContent.setAttribute("dir", "rtl");
      }
      if (countrySearch) {
        this._buildSearchUI();
      }
      this.countryList = createEl(
        "ul",
        {
          class: "iti__country-list",
          id: `iti-${this.id}__country-listbox`,
          role: "listbox",
          [ARIA.LABEL]: i18n.countryListAriaLabel
        },
        this.dropdownContent
      );
      this._appendListItems();
      if (countrySearch) {
        this.updateSearchResultsA11yText();
      }
      if (dropdownContainer) {
        const dropdownClasses = buildClassNames({
          iti: true,
          "iti--container": true,
          "iti--fullscreen-popup": useFullscreenPopup,
          "iti--inline-dropdown": !useFullscreenPopup,
          [containerClass]: Boolean(containerClass)
        });
        this.dropdown = createEl("div", { class: dropdownClasses });
        this.dropdown.appendChild(this.dropdownContent);
      } else {
        this.countryContainer.appendChild(this.dropdownContent);
      }
    }
    _buildSearchUI() {
      const { i18n } = this.options;
      const searchWrapper = createEl(
        "div",
        { class: "iti__search-input-wrapper" },
        this.dropdownContent
      );
      this.searchIcon = createEl(
        "span",
        {
          class: "iti__search-icon",
          [ARIA.HIDDEN]: "true"
        },
        searchWrapper
      );
      this.searchIcon.innerHTML = buildSearchIcon();
      this.searchInput = createEl(
        "input",
        {
          id: `iti-${this.id}__search-input`,
          // Chrome says inputs need either a name or an id
          type: "search",
          class: "iti__search-input",
          placeholder: i18n.searchPlaceholder,
          // role=combobox + aria-autocomplete=list + aria-activedescendant allows maintaining focus on the search input while allowing users to navigate search results with up/down keyboard keys
          role: "combobox",
          [ARIA.EXPANDED]: "true",
          [ARIA.LABEL]: i18n.searchPlaceholder,
          [ARIA.CONTROLS]: `iti-${this.id}__country-listbox`,
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
      this.searchClearButton.innerHTML = buildClearIcon(this.id);
      this.searchResultsA11yText = createEl(
        "span",
        { class: "iti__a11y-text" },
        this.dropdownContent
      );
      this.searchNoResults = createEl(
        "div",
        {
          class: `iti__no-results ${CLASSES.HIDE}`,
          [ARIA.HIDDEN]: "true"
          // all a11y messaging happens in this.searchResultsA11yText
        },
        this.dropdownContent
      );
      this.searchNoResults.textContent = i18n.zeroSearchResults;
    }
    _maybeUpdateInputPaddingAndReveal() {
      if (this.countryContainer) {
        this.updateInputPadding();
        this.countryContainer.classList.remove(CLASSES.V_HIDE);
      }
    }
    _maybeBuildHiddenInputs(wrapper) {
      const { hiddenInput } = this.options;
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
    _appendListItems() {
      const frag = document.createDocumentFragment();
      for (let i = 0; i < this.countries.length; i++) {
        const c = this.countries[i];
        const liClass = buildClassNames({
          [CLASSES.COUNTRY_ITEM]: true
        });
        const listItem = createEl("li", {
          id: `iti-${this.id}__item-${c.iso2}`,
          class: liClass,
          tabindex: "-1",
          role: "option",
          [ARIA.SELECTED]: "false"
        });
        listItem.dataset.dialCode = c.dialCode;
        listItem.dataset.countryCode = c.iso2;
        c.nodeById[this.id] = listItem;
        if (this.options.showFlags) {
          createEl("div", { class: `${CLASSES.FLAG} iti__${c.iso2}` }, listItem);
        }
        const nameEl = createEl("span", { class: "iti__country-name" }, listItem);
        nameEl.textContent = c.name;
        const dialEl = createEl("span", { class: "iti__dial-code" }, listItem);
        if (this.isRTL) {
          dialEl.setAttribute("dir", "ltr");
        }
        dialEl.textContent = `+${c.dialCode}`;
        frag.appendChild(listItem);
      }
      this.countryList.appendChild(frag);
    }
    //* Update the input padding to make space for the selected country/dial code.
    updateInputPadding() {
      if (this.selectedCountry) {
        const fallbackWidth = this.options.separateDialCode ? LAYOUT.SANE_SELECTED_WITH_DIAL_WIDTH : LAYOUT.SANE_SELECTED_NO_DIAL_WIDTH;
        const selectedCountryWidth = this.selectedCountry.offsetWidth || this._getHiddenSelectedCountryWidth() || fallbackWidth;
        const inputPadding = selectedCountryWidth + LAYOUT.INPUT_PADDING_EXTRA_LEFT;
        this.telInput.style.paddingLeft = `${inputPadding}px`;
      }
    }
    //* When input is in a hidden container during init, we cannot calculate the selected country width.
    //* Fix: clone the markup, make it invisible, add it to the end of the DOM, and then measure it's width.
    //* To get the right styling to apply, all we need is a shallow clone of the container,
    //* and then to inject a deep clone of the selectedCountry element.
    _getHiddenSelectedCountryWidth() {
      if (this.telInput.parentNode) {
        let body;
        try {
          body = window.top.document.body;
        } catch (e) {
          body = document.body;
        }
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
    //* Update search results text (for a11y).
    updateSearchResultsA11yText() {
      const { i18n } = this.options;
      const count = this.countryList.childElementCount;
      let searchText;
      if (count === 0) {
        searchText = i18n.zeroSearchResults;
      } else {
        if (i18n.searchResultsText) {
          searchText = i18n.searchResultsText(count);
        } else if (count === 1) {
          searchText = i18n.oneSearchResult;
        } else {
          searchText = i18n.multipleSearchResults.replace(
            "${count}",
            count.toString()
          );
        }
      }
      this.searchResultsA11yText.textContent = searchText;
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
        if (this.options.countrySearch) {
          const activeDescendant = this.highlightedItem.getAttribute("id") || "";
          this.searchInput.setAttribute(ARIA.ACTIVE_DESCENDANT, activeDescendant);
        }
      }
      if (shouldFocus) {
        this.highlightedItem.focus();
      }
    }
    updateSelectedItem(iso2) {
      if (this.selectedItem && this.selectedItem.dataset.countryCode !== iso2) {
        this.selectedItem.setAttribute(ARIA.SELECTED, "false");
        this.selectedItem = null;
      }
      if (iso2 && !this.selectedItem) {
        const newListItem = this.countryList.querySelector(
          `[data-country-code="${iso2}"]`
        );
        if (newListItem) {
          newListItem.setAttribute(ARIA.SELECTED, "true");
          this.selectedItem = newListItem;
        }
      }
    }
    //* Country search: Filter the country list to the given array of countries.
    filterCountries(matchedCountries) {
      this.countryList.innerHTML = "";
      let noCountriesAddedYet = true;
      for (const c of matchedCountries) {
        const listItem = c.nodeById[this.id];
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
        if (this.searchNoResults) {
          this.searchNoResults.classList.remove(CLASSES.HIDE);
        }
      } else if (this.searchNoResults) {
        this.searchNoResults.classList.add(CLASSES.HIDE);
      }
      this.countryList.scrollTop = 0;
      this.updateSearchResultsA11yText();
    }
    destroy() {
      this.telInput.iti = void 0;
      delete this.telInput.dataset.intlTelInputId;
      if (this.options.separateDialCode) {
        this.telInput.style.paddingLeft = this.originalPaddingLeft;
      }
      const wrapper = this.telInput.parentNode;
      wrapper.before(this.telInput);
      wrapper.remove();
      this.telInput = null;
      this.countryContainer = null;
      this.selectedCountry = null;
      this.selectedCountryInner = null;
      this.selectedDialCode = null;
      this.dropdownArrow = null;
      this.dropdownContent = null;
      this.searchInput = null;
      this.searchIcon = null;
      this.searchClearButton = null;
      this.searchNoResults = null;
      this.searchResultsA11yText = null;
      this.countryList = null;
      this.dropdown = null;
      this.hiddenInput = null;
      this.hiddenInputCountry = null;
      this.highlightedItem = null;
      this.selectedItem = null;
      for (const c of this.countries) {
        delete c.nodeById[this.id];
      }
      this.countries = null;
    }
  };

  // src/js/modules/data/country-data.ts
  var processAllCountries = (options) => {
    const { onlyCountries, excludeCountries } = options;
    if (onlyCountries.length) {
      const lowerCaseOnlyCountries = onlyCountries.map(
        (country) => country.toLowerCase()
      );
      return data_default.filter(
        (country) => lowerCaseOnlyCountries.includes(country.iso2)
      );
    } else if (excludeCountries.length) {
      const lowerCaseExcludeCountries = excludeCountries.map(
        (country) => country.toLowerCase()
      );
      return data_default.filter(
        (country) => !lowerCaseExcludeCountries.includes(country.iso2)
      );
    }
    return data_default;
  };
  var translateCountryNames = (countries, options) => {
    for (const c of countries) {
      const iso2 = c.iso2.toLowerCase();
      if (options.i18n[iso2]) {
        c.name = options.i18n[iso2];
      }
    }
  };
  var processDialCodes = (countries) => {
    const dialCodes = /* @__PURE__ */ new Set();
    let dialCodeMaxLen = 0;
    const dialCodeToIso2Map = {};
    const _addToDialCodeMap = (iso2, dialCode) => {
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
        _addToDialCodeMap(c.iso2, partialDialCode);
      }
      _addToDialCodeMap(c.iso2, c.dialCode);
      if (c.areaCodes) {
        const rootIso2Code = dialCodeToIso2Map[c.dialCode][0];
        for (const areaCode of c.areaCodes) {
          for (let k = 1; k < areaCode.length; k++) {
            const partialAreaCode = areaCode.substring(0, k);
            const partialDialCode = c.dialCode + partialAreaCode;
            _addToDialCodeMap(rootIso2Code, partialDialCode);
            _addToDialCodeMap(c.iso2, partialDialCode);
          }
          _addToDialCodeMap(c.iso2, c.dialCode + areaCode);
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

  // src/js/modules/format/formatting.ts
  var beforeSetNumber = (fullNumber, dialCode, separateDialCode, selectedCountryData) => {
    let number = fullNumber;
    if (separateDialCode) {
      if (dialCode) {
        dialCode = `+${selectedCountryData.dialCode}`;
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

  // src/js/intl-tel-input.ts
  for (const c of data_default) {
    c.name = en_default[c.iso2];
  }
  var id = 0;
  var iso2Set = new Set(data_default.map((c) => c.iso2));
  var isIso2 = (val) => iso2Set.has(val);
  var Iti = class _Iti {
    constructor(input, customOptions = {}) {
      this.id = id++;
      this.options = { ...defaults, ...customOptions };
      applyOptionSideEffects(this.options, en_default);
      this.ui = new UI(input, this.options, this.id);
      this.isAndroid = _Iti._getIsAndroid();
      this.promise = this._createInitPromises();
      this.countries = processAllCountries(this.options);
      const { dialCodes, dialCodeMaxLen, dialCodeToIso2Map } = processDialCodes(
        this.countries
      );
      this.dialCodes = dialCodes;
      this.dialCodeMaxLen = dialCodeMaxLen;
      this.dialCodeToIso2Map = dialCodeToIso2Map;
      this.countryByIso2 = new Map(this.countries.map((c) => [c.iso2, c]));
      this._init();
    }
    static _getIsAndroid() {
      return typeof navigator !== "undefined" ? /Android/i.test(navigator.userAgent) : false;
    }
    _updateNumeralSet(str) {
      if (/[\u0660-\u0669]/.test(str)) {
        this.userNumeralSet = "arabic-indic";
      } else if (/[\u06F0-\u06F9]/.test(str)) {
        this.userNumeralSet = "persian";
      } else {
        this.userNumeralSet = "ascii";
      }
    }
    _mapAsciiToUserNumerals(str) {
      if (!this.userNumeralSet) {
        this._updateNumeralSet(this.ui.telInput.value);
      }
      if (this.userNumeralSet === "ascii") {
        return str;
      }
      const base = this.userNumeralSet === "arabic-indic" ? 1632 : 1776;
      return str.replace(/[0-9]/g, (d) => String.fromCharCode(base + Number(d)));
    }
    // Normalize Eastern Arabic (U+0660-0669) and Persian/Extended Arabic-Indic (U+06F0-06F9) numerals to ASCII 0-9
    _normaliseNumerals(str) {
      if (!str) {
        return "";
      }
      this._updateNumeralSet(str);
      if (this.userNumeralSet === "ascii") {
        return str;
      }
      const base = this.userNumeralSet === "arabic-indic" ? 1632 : 1776;
      const regex = this.userNumeralSet === "arabic-indic" ? /[\u0660-\u0669]/g : /[\u06F0-\u06F9]/g;
      return str.replace(regex, (ch) => String.fromCharCode(48 + (ch.charCodeAt(0) - base)));
    }
    _getTelInputValue() {
      const inputValue = this.ui.telInput.value.trim();
      return this._normaliseNumerals(inputValue);
    }
    _setTelInputValue(asciiValue) {
      this.ui.telInput.value = this._mapAsciiToUserNumerals(asciiValue);
    }
    _createInitPromises() {
      const autoCountryPromise = new Promise((resolve, reject) => {
        this.resolveAutoCountryPromise = resolve;
        this.rejectAutoCountryPromise = reject;
      });
      const utilsScriptPromise = new Promise((resolve, reject) => {
        this.resolveUtilsScriptPromise = resolve;
        this.rejectUtilsScriptPromise = reject;
      });
      return Promise.all([autoCountryPromise, utilsScriptPromise]);
    }
    //* Can't be private as it's called from intlTelInput convenience wrapper.
    _init() {
      this.selectedCountryData = {};
      this.abortController = new AbortController();
      this._processCountryData();
      this.ui.generateMarkup(this.countries);
      this._setInitialState();
      this._initListeners();
      this._initRequests();
    }
    //********************
    //*  PRIVATE METHODS
    //********************
    //* Prepare all of the country data, including onlyCountries, excludeCountries, countryOrder options.
    _processCountryData() {
      translateCountryNames(this.countries, this.options);
      sortCountries(this.countries, this.options);
      cacheSearchTokens(this.countries);
    }
    //* Set the initial state of the input value and the selected country by:
    //* 1. Extracting a dial code from the given number
    //* 2. Using explicit initialCountry
    _setInitialState(overrideAutoCountry = false) {
      const attributeValueRaw = this.ui.telInput.getAttribute("value");
      const attributeValue = this._normaliseNumerals(attributeValueRaw);
      const inputValue = this._getTelInputValue();
      const useAttribute = attributeValue && attributeValue.startsWith("+") && (!inputValue || !inputValue.startsWith("+"));
      const val = useAttribute ? attributeValue : inputValue;
      const dialCode = this._getDialCode(val);
      const isRegionlessNanpNumber = isRegionlessNanp(val);
      const { initialCountry, geoIpLookup } = this.options;
      const isAutoCountry = initialCountry === INITIAL_COUNTRY.AUTO && geoIpLookup;
      if (dialCode && !isRegionlessNanpNumber) {
        this._updateCountryFromNumber(val);
      } else if (!isAutoCountry || overrideAutoCountry) {
        const lowerInitialCountry = initialCountry ? initialCountry.toLowerCase() : "";
        if (isIso2(lowerInitialCountry)) {
          this._setCountry(lowerInitialCountry);
        } else {
          if (dialCode && isRegionlessNanpNumber) {
            this._setCountry(US.ISO2);
          } else {
            this._setCountry("");
          }
        }
      }
      if (val) {
        this._updateValFromNumber(val);
      }
    }
    //* Initialise the main event listeners: input keyup, and click selected country.
    _initListeners() {
      this._initTelInputListeners();
      if (this.options.allowDropdown) {
        this._initDropdownListeners();
      }
      if ((this.ui.hiddenInput || this.ui.hiddenInputCountry) && this.ui.telInput.form) {
        this._initHiddenInputListener();
      }
    }
    //* Update hidden input on form submit.
    _initHiddenInputListener() {
      const handleHiddenInputSubmit = () => {
        if (this.ui.hiddenInput) {
          this.ui.hiddenInput.value = this.getNumber();
        }
        if (this.ui.hiddenInputCountry) {
          this.ui.hiddenInputCountry.value = this.selectedCountryData.iso2 || "";
        }
      };
      this.ui.telInput.form?.addEventListener("submit", handleHiddenInputSubmit, {
        signal: this.abortController.signal
      });
    }
    //* initialise the dropdown listeners.
    _initDropdownListeners() {
      const signal = this.abortController.signal;
      const handleLabelClick = (e) => {
        if (this.ui.dropdownContent.classList.contains(CLASSES.HIDE)) {
          this.ui.telInput.focus();
        } else {
          e.preventDefault();
        }
      };
      const label = this.ui.telInput.closest("label");
      if (label) {
        label.addEventListener("click", handleLabelClick, { signal });
      }
      const handleClickSelectedCountry = () => {
        const dropdownClosed = this.ui.dropdownContent.classList.contains(
          CLASSES.HIDE
        );
        if (dropdownClosed && !this.ui.telInput.disabled && !this.ui.telInput.readOnly) {
          this._openDropdown();
        }
      };
      this.ui.selectedCountry.addEventListener(
        "click",
        handleClickSelectedCountry,
        {
          signal
        }
      );
      const handleCountryContainerKeydown = (e) => {
        const isDropdownHidden = this.ui.dropdownContent.classList.contains(
          CLASSES.HIDE
        );
        if (isDropdownHidden && [KEYS.ARROW_UP, KEYS.ARROW_DOWN, KEYS.SPACE, KEYS.ENTER].includes(e.key)) {
          e.preventDefault();
          e.stopPropagation();
          this._openDropdown();
        }
        if (e.key === KEYS.TAB) {
          this._closeDropdown();
        }
      };
      this.ui.countryContainer.addEventListener(
        "keydown",
        handleCountryContainerKeydown,
        { signal }
      );
    }
    //* Init many requests: utils script / geo ip lookup.
    _initRequests() {
      const { loadUtils, initialCountry, geoIpLookup } = this.options;
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
            signal: this.abortController.signal
          });
        }
      } else {
        this.resolveUtilsScriptPromise();
      }
      const isAutoCountry = initialCountry === INITIAL_COUNTRY.AUTO && geoIpLookup;
      if (isAutoCountry && !this.selectedCountryData.iso2) {
        this._loadAutoCountry();
      } else {
        this.resolveAutoCountryPromise();
      }
    }
    //* Perform the geo ip lookup.
    _loadAutoCountry() {
      if (intlTelInput.autoCountry) {
        this.handleAutoCountry();
      } else if (!intlTelInput.startedLoadingAutoCountry) {
        intlTelInput.startedLoadingAutoCountry = true;
        if (typeof this.options.geoIpLookup === "function") {
          this.options.geoIpLookup(
            (iso2 = "") => {
              const iso2Lower = iso2.toLowerCase();
              if (isIso2(iso2Lower)) {
                intlTelInput.autoCountry = iso2Lower;
                setTimeout(() => forEachInstance("handleAutoCountry"));
              } else {
                this._setInitialState(true);
                forEachInstance("rejectAutoCountryPromise");
              }
            },
            () => {
              this._setInitialState(true);
              forEachInstance("rejectAutoCountryPromise");
            }
          );
        }
      }
    }
    _openDropdownWithPlus() {
      this._openDropdown();
      this.ui.searchInput.value = "+";
      this._filterCountriesByQuery("");
    }
    //* Initialize the tel input listeners.
    _initTelInputListeners() {
      this._bindInputListener();
      this._maybeBindKeydownListener();
      this._maybeBindPasteListener();
    }
    _bindInputListener() {
      const {
        strictMode,
        formatAsYouType,
        separateDialCode,
        allowDropdown,
        countrySearch
      } = this.options;
      let userOverrideFormatting = false;
      if (REGEX.ALPHA_UNICODE.test(this._getTelInputValue())) {
        userOverrideFormatting = true;
      }
      const handleInputEvent = (e) => {
        const inputValue = this._getTelInputValue();
        if (this.isAndroid && e?.data === "+" && separateDialCode && allowDropdown && countrySearch) {
          const currentCaretPos = this.ui.telInput.selectionStart || 0;
          const valueBeforeCaret = inputValue.substring(0, currentCaretPos - 1);
          const valueAfterCaret = inputValue.substring(currentCaretPos);
          this._setTelInputValue(valueBeforeCaret + valueAfterCaret);
          this._openDropdownWithPlus();
          return;
        }
        if (this._updateCountryFromNumber(inputValue)) {
          this._triggerCountryChange();
        }
        const isFormattingChar = e?.data && REGEX.NON_PLUS_NUMERIC.test(e.data);
        const isPaste = e?.inputType === INPUT_TYPES.PASTE && inputValue;
        if (isFormattingChar || isPaste && !strictMode) {
          userOverrideFormatting = true;
        } else if (!REGEX.NON_PLUS_NUMERIC.test(inputValue)) {
          userOverrideFormatting = false;
        }
        const isSetNumber = e?.detail && e.detail["isSetNumber"];
        const isAscii = this.userNumeralSet === "ascii";
        if (formatAsYouType && !userOverrideFormatting && !isSetNumber && isAscii) {
          const currentCaretPos = this.ui.telInput.selectionStart || 0;
          const valueBeforeCaret = inputValue.substring(
            0,
            currentCaretPos
          );
          const relevantCharsBeforeCaret = valueBeforeCaret.replace(
            REGEX.NON_PLUS_NUMERIC_GLOBAL,
            ""
          ).length;
          const isDeleteForwards = e?.inputType === INPUT_TYPES.DELETE_FWD;
          const fullNumber = this._getFullNumber();
          const formattedValue = formatNumberAsYouType(
            fullNumber,
            inputValue,
            intlTelInput.utils,
            this.selectedCountryData,
            this.options.separateDialCode
          );
          const newCaretPos = translateCursorPosition(
            relevantCharsBeforeCaret,
            formattedValue,
            currentCaretPos,
            isDeleteForwards
          );
          this._setTelInputValue(formattedValue);
          this.ui.telInput.setSelectionRange(newCaretPos, newCaretPos);
        }
      };
      this.ui.telInput.addEventListener(
        "input",
        handleInputEvent,
        {
          signal: this.abortController.signal
        }
      );
    }
    _maybeBindKeydownListener() {
      const { strictMode, separateDialCode, allowDropdown, countrySearch } = this.options;
      if (strictMode || separateDialCode) {
        const handleKeydownEvent = (e) => {
          if (e.key && e.key.length === 1 && !e.altKey && !e.ctrlKey && !e.metaKey) {
            if (separateDialCode && allowDropdown && countrySearch && e.key === "+") {
              e.preventDefault();
              this._openDropdownWithPlus();
              return;
            }
            if (strictMode) {
              const inputValue = this._getTelInputValue();
              const alreadyHasPlus = inputValue.startsWith("+");
              const isInitialPlus = !alreadyHasPlus && this.ui.telInput.selectionStart === 0 && e.key === "+";
              const normalisedKey = this._normaliseNumerals(e.key);
              const isNumeric = /^[0-9]$/.test(normalisedKey);
              const isAllowedChar = separateDialCode ? isNumeric : isInitialPlus || isNumeric;
              const input = this.ui.telInput;
              const selStart = input.selectionStart;
              const selEnd = input.selectionEnd;
              const before = inputValue.slice(0, selStart);
              const after = inputValue.slice(selEnd);
              const newValue = before + e.key + after;
              const newFullNumber = this._getFullNumber(newValue);
              const coreNumber = intlTelInput.utils.getCoreNumber(
                newFullNumber,
                this.selectedCountryData.iso2
              );
              const hasExceededMaxLength = this.maxCoreNumberLength && coreNumber.length > this.maxCoreNumberLength;
              const newCountry = this._getNewCountryFromNumber(newFullNumber);
              const isChangingDialCode = newCountry !== null;
              if (!isAllowedChar || hasExceededMaxLength && !isChangingDialCode && !isInitialPlus) {
                e.preventDefault();
              }
            }
          }
        };
        this.ui.telInput.addEventListener("keydown", handleKeydownEvent, {
          signal: this.abortController.signal
        });
      }
    }
    _maybeBindPasteListener() {
      if (this.options.strictMode) {
        const handlePasteEvent = (e) => {
          e.preventDefault();
          const input = this.ui.telInput;
          const selStart = input.selectionStart;
          const selEnd = input.selectionEnd;
          const inputValue = this._getTelInputValue();
          const before = inputValue.slice(0, selStart);
          const after = inputValue.slice(selEnd);
          const iso2 = this.selectedCountryData.iso2;
          const pastedRaw = e.clipboardData.getData("text");
          const pasted = this._normaliseNumerals(pastedRaw);
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
            if (this.maxCoreNumberLength && coreNumber.length > this.maxCoreNumberLength) {
              if (input.selectionEnd === inputValue.length) {
                const trimLength = coreNumber.length - this.maxCoreNumberLength;
                newVal = newVal.slice(0, newVal.length - trimLength);
              } else {
                return;
              }
            }
          }
          this._setTelInputValue(newVal);
          const caretPos = selStart + sanitised.length;
          input.setSelectionRange(caretPos, caretPos);
          input.dispatchEvent(new InputEvent("input", { bubbles: true }));
        };
        this.ui.telInput.addEventListener("paste", handlePasteEvent, {
          signal: this.abortController.signal
        });
      }
    }
    //* Adhere to the input's maxlength attr.
    _cap(number) {
      const max = Number(this.ui.telInput.getAttribute("maxlength"));
      return max && number.length > max ? number.substring(0, max) : number;
    }
    //* Trigger a custom event on the input (typed via ItiEventMap).
    _trigger(name, detailProps = {}) {
      const e = new CustomEvent(name, {
        bubbles: true,
        cancelable: true,
        detail: detailProps
      });
      this.ui.telInput.dispatchEvent(e);
    }
    //* Open the dropdown.
    _openDropdown() {
      const { fixDropdownWidth, countrySearch } = this.options;
      this.dropdownAbortController = new AbortController();
      if (fixDropdownWidth) {
        this.ui.dropdownContent.style.width = `${this.ui.telInput.offsetWidth}px`;
      }
      this.ui.dropdownContent.classList.remove(CLASSES.HIDE);
      this.ui.selectedCountry.setAttribute(ARIA.EXPANDED, "true");
      this._setDropdownPosition();
      if (countrySearch) {
        const firstCountryItem = this.ui.countryList.firstElementChild;
        if (firstCountryItem) {
          this.ui.highlightListItem(firstCountryItem, false);
          this.ui.countryList.scrollTop = 0;
        }
        this.ui.searchInput.focus();
      }
      this._bindDropdownListeners();
      this.ui.dropdownArrow.classList.add(CLASSES.ARROW_UP);
      this._trigger(EVENTS.OPEN_COUNTRY_DROPDOWN);
    }
    //* Set the dropdown position
    _setDropdownPosition() {
      if (this.options.dropdownContainer) {
        this.options.dropdownContainer.appendChild(this.ui.dropdown);
      }
      if (!this.options.useFullscreenPopup) {
        const inputPosRelativeToVP = this.ui.telInput.getBoundingClientRect();
        const inputHeight = this.ui.telInput.offsetHeight;
        if (this.options.dropdownContainer) {
          this.ui.dropdown.style.top = `${inputPosRelativeToVP.top + inputHeight}px`;
          this.ui.dropdown.style.left = `${inputPosRelativeToVP.left}px`;
          const handleWindowScroll = () => this._closeDropdown();
          window.addEventListener("scroll", handleWindowScroll, {
            signal: this.dropdownAbortController.signal
          });
        }
      }
    }
    //* We only bind dropdown listeners when the dropdown is open.
    _bindDropdownListeners() {
      const signal = this.dropdownAbortController.signal;
      this._bindDropdownMouseoverListener(signal);
      this._bindDropdownCountryClickListener(signal);
      this._bindDropdownClickOffListener(signal);
      this._bindDropdownKeydownListener(signal);
      if (this.options.countrySearch) {
        this._bindDropdownSearchListeners(signal);
      }
    }
    //* When mouse over a list item, just highlight that one
    //* we add the class "highlight", so if they hit "enter" we know which one to select.
    _bindDropdownMouseoverListener(signal) {
      const handleMouseoverCountryList = (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          this.ui.highlightListItem(listItem, false);
        }
      };
      this.ui.countryList.addEventListener(
        "mouseover",
        handleMouseoverCountryList,
        {
          signal
        }
      );
    }
    //* Listen for country selection.
    _bindDropdownCountryClickListener(signal) {
      const handleClickCountryList = (e) => {
        const listItem = e.target?.closest(
          `.${CLASSES.COUNTRY_ITEM}`
        );
        if (listItem) {
          this._selectListItem(listItem);
        }
      };
      this.ui.countryList.addEventListener("click", handleClickCountryList, {
        signal
      });
    }
    //* Click off to close (except when this initial opening click is bubbling up).
    //* We cannot just stopPropagation as it may be needed to close another instance.
    _bindDropdownClickOffListener(signal) {
      const handleClickOffToClose = (e) => {
        const target = e.target;
        const clickedInsideDropdown = !!target.closest(
          `#iti-${this.id}__dropdown-content`
        );
        if (!clickedInsideDropdown) {
          this._closeDropdown();
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
    _bindDropdownKeydownListener(signal) {
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
            this._handleUpDownKey(e.key);
          } else if (e.key === KEYS.ENTER) {
            this._handleEnterKey();
          } else if (e.key === KEYS.ESC) {
            this._closeDropdown();
            this.ui.selectedCountry.focus();
          }
        }
        if (!this.options.countrySearch && REGEX.HIDDEN_SEARCH_CHAR.test(e.key)) {
          e.stopPropagation();
          if (queryTimer) {
            clearTimeout(queryTimer);
          }
          query += e.key.toLowerCase();
          this._searchForCountry(query);
          queryTimer = setTimeout(() => {
            query = "";
          }, TIMINGS.HIDDEN_SEARCH_RESET_MS);
        }
      };
      document.addEventListener("keydown", handleKeydownOnDropdown, { signal });
    }
    //* Search input listeners when countrySearch enabled.
    _bindDropdownSearchListeners(signal) {
      const doFilter = () => {
        const inputQuery = this.ui.searchInput.value.trim();
        this._filterCountriesByQuery(inputQuery);
        if (this.ui.searchInput.value) {
          this.ui.searchClearButton.classList.remove(CLASSES.HIDE);
        } else {
          this.ui.searchClearButton.classList.add(CLASSES.HIDE);
        }
      };
      let keyupTimer = null;
      const handleSearchChange = () => {
        if (keyupTimer) {
          clearTimeout(keyupTimer);
        }
        keyupTimer = setTimeout(() => {
          doFilter();
          keyupTimer = null;
        }, 100);
      };
      this.ui.searchInput.addEventListener("input", handleSearchChange, {
        signal
      });
      const handleSearchClear = () => {
        this.ui.searchInput.value = "";
        this.ui.searchInput.focus();
        doFilter();
      };
      this.ui.searchClearButton.addEventListener("click", handleSearchClear, {
        signal
      });
    }
    //* Hidden search (countrySearch disabled): Find the first list item whose name starts with the query string.
    _searchForCountry(query) {
      const match = findFirstCountryStartingWith(this.countries, query);
      if (match) {
        const listItem = match.nodeById[this.id];
        this.ui.highlightListItem(listItem, false);
        this.ui.scrollTo(listItem);
      }
    }
    //* Country search: Filter the countries according to the search query.
    _filterCountriesByQuery(query) {
      let matchedCountries;
      if (query === "") {
        matchedCountries = this.countries;
      } else {
        matchedCountries = getMatchedCountries(this.countries, query);
      }
      this.ui.filterCountries(matchedCountries);
    }
    //* Highlight the next/prev item in the list (and ensure it is visible).
    _handleUpDownKey(key) {
      let next = key === KEYS.ARROW_UP ? this.ui.highlightedItem?.previousElementSibling : this.ui.highlightedItem?.nextElementSibling;
      if (!next && this.ui.countryList.childElementCount > 1) {
        next = key === KEYS.ARROW_UP ? this.ui.countryList.lastElementChild : this.ui.countryList.firstElementChild;
      }
      if (next) {
        this.ui.scrollTo(next);
        this.ui.highlightListItem(next, false);
      }
    }
    //* Select the currently highlighted item.
    _handleEnterKey() {
      if (this.ui.highlightedItem) {
        this._selectListItem(this.ui.highlightedItem);
      }
    }
    //* Update the input's value to the given val (format first if possible)
    //* NOTE: this is called from _setInitialState, handleUtils and setNumber.
    _updateValFromNumber(fullNumber) {
      let number = fullNumber;
      if (this.options.formatOnDisplay && intlTelInput.utils && this.selectedCountryData) {
        const useNational = this.options.nationalMode || !number.startsWith("+") && !this.options.separateDialCode;
        const { NATIONAL, INTERNATIONAL } = intlTelInput.utils.numberFormat;
        const format = useNational ? NATIONAL : INTERNATIONAL;
        number = intlTelInput.utils.formatNumber(
          number,
          this.selectedCountryData.iso2,
          format
        );
      }
      number = this._beforeSetNumber(number);
      this._setTelInputValue(number);
    }
    //* Check if need to select a new country based on the given number
    //* Note: called from _setInitialState, keyup handler, setNumber.
    _updateCountryFromNumber(fullNumber) {
      const iso2 = this._getNewCountryFromNumber(fullNumber);
      if (iso2 !== null) {
        return this._setCountry(iso2);
      }
      return false;
    }
    // if there is a selected country, and the number doesn't start with a dial code, then add it
    _ensureHasDialCode(number) {
      const { dialCode, nationalPrefix } = this.selectedCountryData;
      const alreadyHasPlus = number.startsWith("+");
      if (alreadyHasPlus || !dialCode) {
        return number;
      }
      const hasPrefix = nationalPrefix && number.startsWith(nationalPrefix) && !this.options.separateDialCode;
      const cleanNumber = hasPrefix ? number.substring(1) : number;
      return `+${dialCode}${cleanNumber}`;
    }
    // Get the country ISO2 code from the given number
    // BUT ONLY IF ITS CHANGED FROM THE CURRENTLY SELECTED COUNTRY
    // NOTE: consider refactoring this to be more clear
    _getNewCountryFromNumber(fullNumber) {
      const plusIndex = fullNumber.indexOf("+");
      let number = plusIndex ? fullNumber.substring(plusIndex) : fullNumber;
      const selectedIso2 = this.selectedCountryData.iso2;
      const selectedDialCode = this.selectedCountryData.dialCode;
      number = this._ensureHasDialCode(number);
      const dialCodeMatch = this._getDialCode(number, true);
      const numeric = getNumeric(number);
      if (dialCodeMatch) {
        const dialCodeMatchNumeric = getNumeric(dialCodeMatch);
        const iso2Codes = this.dialCodeToIso2Map[dialCodeMatchNumeric];
        if (iso2Codes.length === 1) {
          if (iso2Codes[0] === selectedIso2) {
            return null;
          }
          return iso2Codes[0];
        }
        if (!selectedIso2 && this.defaultCountry && iso2Codes.includes(this.defaultCountry)) {
          return this.defaultCountry;
        }
        const isRegionlessNanpNumber = selectedDialCode === DIAL.NANP && isRegionlessNanp(numeric);
        if (isRegionlessNanpNumber) {
          return null;
        }
        const { areaCodes, priority } = this.selectedCountryData;
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
        const currentDial = this.selectedCountryData.dialCode || "";
        if (currentDial && currentDial.startsWith(numeric)) {
          return null;
        }
        return "";
      } else if ((!number || number === "+") && !selectedIso2) {
        return this.defaultCountry;
      }
      return null;
    }
    //* Update the selected country, dial code (if separateDialCode), placeholder, title, and selected list item.
    //* Note: called from _setInitialState, _updateCountryFromNumber, _selectListItem, setCountry.
    _setCountry(iso2) {
      const { separateDialCode, showFlags, i18n, allowDropdown } = this.options;
      const prevIso2 = this.selectedCountryData.iso2 || "";
      if (allowDropdown) {
        this.ui.updateSelectedItem(iso2);
      }
      this.selectedCountryData = iso2 ? this.countryByIso2.get(iso2) : {};
      if (this.selectedCountryData.iso2) {
        this.defaultCountry = this.selectedCountryData.iso2;
      }
      if (this.ui.selectedCountry) {
        const flagClass = iso2 && showFlags ? `${CLASSES.FLAG} iti__${iso2}` : `${CLASSES.FLAG} ${CLASSES.GLOBE}`;
        let ariaLabel, title;
        if (iso2) {
          const { name, dialCode } = this.selectedCountryData;
          title = name;
          ariaLabel = i18n.selectedCountryAriaLabel.replace("${countryName}", name).replace("${dialCode}", `+${dialCode}`);
        } else {
          title = i18n.noCountrySelected;
          ariaLabel = i18n.noCountrySelected;
        }
        this.ui.selectedCountryInner.className = flagClass;
        this.ui.selectedCountry.setAttribute("title", title);
        this.ui.selectedCountry.setAttribute(ARIA.LABEL, ariaLabel);
      }
      if (separateDialCode) {
        const dialCode = this.selectedCountryData.dialCode ? `+${this.selectedCountryData.dialCode}` : "";
        this.ui.selectedDialCode.textContent = dialCode;
        this.ui.updateInputPadding();
      }
      this._updatePlaceholder();
      this._updateMaxLength();
      return prevIso2 !== iso2;
    }
    //* Update the maximum valid number length for the currently selected country.
    _updateMaxLength() {
      const { strictMode, placeholderNumberType, validationNumberTypes } = this.options;
      const { iso2 } = this.selectedCountryData;
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
            validationNumberTypes
          )) {
            validNumber = exampleNumber;
            exampleNumber += "0";
          }
          const coreNumber = intlTelInput.utils.getCoreNumber(validNumber, iso2);
          this.maxCoreNumberLength = coreNumber.length;
          if (iso2 === "by") {
            this.maxCoreNumberLength = coreNumber.length + 1;
          }
        } else {
          this.maxCoreNumberLength = null;
        }
      }
    }
    //* Update the input placeholder to an example number from the currently selected country.
    _updatePlaceholder() {
      const {
        autoPlaceholder,
        placeholderNumberType,
        nationalMode,
        customPlaceholder
      } = this.options;
      const shouldSetPlaceholder = autoPlaceholder === PLACEHOLDER_MODES.AGGRESSIVE || !this.ui.hadInitialPlaceholder && autoPlaceholder === PLACEHOLDER_MODES.POLITE;
      if (intlTelInput.utils && shouldSetPlaceholder) {
        const numberType = intlTelInput.utils.numberType[placeholderNumberType];
        let placeholder = this.selectedCountryData.iso2 ? intlTelInput.utils.getExampleNumber(
          this.selectedCountryData.iso2,
          nationalMode,
          numberType
        ) : "";
        placeholder = this._beforeSetNumber(placeholder);
        if (typeof customPlaceholder === "function") {
          placeholder = customPlaceholder(placeholder, this.selectedCountryData);
        }
        this.ui.telInput.setAttribute("placeholder", placeholder);
      }
    }
    //* Called when the user selects a list item from the dropdown.
    _selectListItem(listItem) {
      const iso2 = listItem.dataset[DATA_KEYS.COUNTRY_CODE];
      const countryChanged = this._setCountry(iso2);
      this._closeDropdown();
      const dialCode = listItem.dataset[DATA_KEYS.DIAL_CODE];
      this._updateDialCode(dialCode);
      if (this.options.formatOnDisplay) {
        const inputValue = this._getTelInputValue();
        this._updateValFromNumber(inputValue);
      }
      this.ui.telInput.focus();
      if (countryChanged) {
        this._triggerCountryChange();
      }
    }
    //* Close the dropdown and unbind any listeners.
    _closeDropdown() {
      if (this.ui.dropdownContent.classList.contains(CLASSES.HIDE)) {
        return;
      }
      this.ui.dropdownContent.classList.add(CLASSES.HIDE);
      this.ui.selectedCountry.setAttribute(ARIA.EXPANDED, "false");
      if (this.options.countrySearch) {
        this.ui.searchInput.removeAttribute(ARIA.ACTIVE_DESCENDANT);
        if (this.ui.highlightedItem) {
          this.ui.highlightedItem.classList.remove(CLASSES.HIGHLIGHT);
          this.ui.highlightedItem = null;
        }
      }
      this.ui.dropdownArrow.classList.remove(CLASSES.ARROW_UP);
      this.dropdownAbortController.abort();
      this.dropdownAbortController = null;
      if (this.options.dropdownContainer) {
        this.ui.dropdown.remove();
      }
      this._trigger(EVENTS.CLOSE_COUNTRY_DROPDOWN);
    }
    //* Replace any existing dial code with the new one
    //* Note: called from _selectListItem and setCountry
    _updateDialCode(newDialCodeBare) {
      const inputVal = this._getTelInputValue();
      const newDialCode = `+${newDialCodeBare}`;
      let newNumber;
      if (inputVal.startsWith("+")) {
        const prevDialCode = this._getDialCode(inputVal);
        if (prevDialCode) {
          newNumber = inputVal.replace(prevDialCode, newDialCode);
        } else {
          newNumber = newDialCode;
        }
        this._setTelInputValue(newNumber);
      }
    }
    //* Try and extract a valid international dial code from a full telephone number.
    //* Note: returns the raw string inc plus character and any whitespace/dots etc.
    _getDialCode(number, includeAreaCode) {
      let dialCode = "";
      if (number.startsWith("+")) {
        let numericChars = "";
        let foundBaseDialCode = false;
        for (let i = 0; i < number.length; i++) {
          const c = number.charAt(i);
          if (/[0-9]/.test(c)) {
            numericChars += c;
            const hasMapEntry = Boolean(this.dialCodeToIso2Map[numericChars]);
            if (!hasMapEntry) {
              break;
            }
            if (this.dialCodes.has(numericChars)) {
              dialCode = number.substring(0, i + 1);
              foundBaseDialCode = true;
              if (!includeAreaCode) {
                break;
              }
            } else if (includeAreaCode && foundBaseDialCode) {
              dialCode = number.substring(0, i + 1);
            }
            if (numericChars.length === this.dialCodeMaxLen) {
              break;
            }
          }
        }
      }
      return dialCode;
    }
    //* Get the input val, adding the dial code if separateDialCode is enabled.
    _getFullNumber(overrideVal) {
      const val = overrideVal ? this._normaliseNumerals(overrideVal) : this._getTelInputValue();
      const { dialCode } = this.selectedCountryData;
      let prefix;
      const numericVal = getNumeric(val);
      if (this.options.separateDialCode && !val.startsWith("+") && dialCode && numericVal) {
        prefix = `+${dialCode}`;
      } else {
        prefix = "";
      }
      return prefix + val;
    }
    //* Remove the dial code if separateDialCode is enabled also cap the length if the input has a maxlength attribute
    _beforeSetNumber(fullNumber) {
      const dialCode = this._getDialCode(fullNumber);
      const number = beforeSetNumber(
        fullNumber,
        dialCode,
        this.options.separateDialCode,
        this.selectedCountryData
      );
      return this._cap(number);
    }
    //* Trigger the 'countrychange' event.
    _triggerCountryChange() {
      this._trigger(EVENTS.COUNTRY_CHANGE);
    }
    //**************************
    //*  SECRET PUBLIC METHODS
    //**************************
    //* This is called when the geoip call returns.
    handleAutoCountry() {
      if (this.options.initialCountry === INITIAL_COUNTRY.AUTO && intlTelInput.autoCountry) {
        this.defaultCountry = intlTelInput.autoCountry;
        const hasSelectedCountryOrGlobe = this.selectedCountryData.iso2 || this.ui.selectedCountryInner.classList.contains(CLASSES.GLOBE);
        if (!hasSelectedCountryOrGlobe) {
          this.setCountry(this.defaultCountry);
        }
        this.resolveAutoCountryPromise();
      }
    }
    //* This is called when the utils request completes.
    handleUtils() {
      if (intlTelInput.utils) {
        const inputValue = this._getTelInputValue();
        if (inputValue) {
          this._updateValFromNumber(inputValue);
        }
        if (this.selectedCountryData.iso2) {
          this._updatePlaceholder();
          this._updateMaxLength();
        }
      }
      this.resolveUtilsScriptPromise();
    }
    //********************
    //*  PUBLIC METHODS
    //********************
    //* Remove plugin.
    destroy() {
      if (!this.ui.telInput) {
        return;
      }
      if (this.options.allowDropdown) {
        this._closeDropdown();
      }
      this.abortController.abort();
      this.abortController = null;
      this.ui.destroy();
      if (intlTelInput.instances instanceof Map) {
        intlTelInput.instances.delete(this.id);
      } else {
        delete intlTelInput.instances[this.id];
      }
    }
    //* Get the extension from the current number.
    getExtension() {
      if (intlTelInput.utils) {
        return intlTelInput.utils.getExtension(
          this._getFullNumber(),
          this.selectedCountryData.iso2
        );
      }
      return "";
    }
    //* Format the number to the given format.
    getNumber(format) {
      if (intlTelInput.utils) {
        const { iso2 } = this.selectedCountryData;
        const fullNumber = this._getFullNumber();
        const formattedNumber = intlTelInput.utils.formatNumber(
          fullNumber,
          iso2,
          format
        );
        return this._mapAsciiToUserNumerals(formattedNumber);
      }
      return "";
    }
    //* Get the type of the entered number e.g. landline/mobile.
    getNumberType() {
      if (intlTelInput.utils) {
        return intlTelInput.utils.getNumberType(
          this._getFullNumber(),
          this.selectedCountryData.iso2
        );
      }
      return SENTINELS.UNKNOWN_NUMBER_TYPE;
    }
    //* Get the country data for the currently selected country.
    getSelectedCountryData() {
      return this.selectedCountryData;
    }
    //* Get the validation error.
    getValidationError() {
      if (intlTelInput.utils) {
        const { iso2 } = this.selectedCountryData;
        return intlTelInput.utils.getValidationError(this._getFullNumber(), iso2);
      }
      return SENTINELS.UNKNOWN_VALIDATION_ERROR;
    }
    //* Validate the input val using number length only
    isValidNumber() {
      const { dialCode, iso2 } = this.selectedCountryData;
      if (dialCode === UK.DIAL_CODE && intlTelInput.utils) {
        const number = this._getFullNumber();
        const coreNumber = intlTelInput.utils.getCoreNumber(number, iso2);
        if (coreNumber[0] === UK.MOBILE_PREFIX && coreNumber.length !== UK.MOBILE_CORE_LENGTH) {
          return false;
        }
      }
      return this._validateNumber(false);
    }
    //* Validate the input val with precise validation
    isValidNumberPrecise() {
      return this._validateNumber(true);
    }
    _utilsIsPossibleNumber(val) {
      return intlTelInput.utils ? intlTelInput.utils.isPossibleNumber(
        val,
        this.selectedCountryData.iso2,
        this.options.validationNumberTypes
      ) : null;
    }
    //* Shared internal validation logic to handle alpha character extension rules.
    _validateNumber(precise) {
      if (!intlTelInput.utils) {
        return null;
      }
      if (!this.selectedCountryData.iso2) {
        return false;
      }
      const testValidity = (s) => precise ? this._utilsIsValidNumber(s) : this._utilsIsPossibleNumber(s);
      const val = this._getFullNumber();
      const alphaCharPosition = val.search(REGEX.ALPHA_UNICODE);
      const hasAlphaChar = alphaCharPosition > -1;
      if (hasAlphaChar && !this.options.allowPhonewords) {
        const beforeAlphaChar = val.substring(0, alphaCharPosition);
        const beforeAlphaIsValid = testValidity(beforeAlphaChar);
        const isValid = testValidity(val);
        return beforeAlphaIsValid && isValid;
      }
      return testValidity(val);
    }
    _utilsIsValidNumber(val) {
      return intlTelInput.utils ? intlTelInput.utils.isValidNumber(
        val,
        this.selectedCountryData.iso2,
        this.options.validationNumberTypes
      ) : null;
    }
    //* Update the selected country, and update the input val accordingly.
    setCountry(iso2) {
      const iso2Lower = iso2?.toLowerCase();
      if (!isIso2(iso2Lower)) {
        throw new Error(`Invalid country code: '${iso2Lower}'`);
      }
      const currentCountry = this.selectedCountryData.iso2;
      const isCountryChange = iso2 && iso2Lower !== currentCountry || !iso2 && currentCountry;
      if (isCountryChange) {
        this._setCountry(iso2Lower);
        this._updateDialCode(this.selectedCountryData.dialCode);
        if (this.options.formatOnDisplay) {
          const inputValue = this._getTelInputValue();
          this._updateValFromNumber(inputValue);
        }
        this._triggerCountryChange();
      }
    }
    //* Set the input value and update the country.
    setNumber(number) {
      const normalisedNumber = this._normaliseNumerals(number);
      const countryChanged = this._updateCountryFromNumber(normalisedNumber);
      this._updateValFromNumber(normalisedNumber);
      if (countryChanged) {
        this._triggerCountryChange();
      }
      this._trigger(EVENTS.INPUT, { isSetNumber: true });
    }
    //* Set the placeholder number typ
    setPlaceholderNumberType(type) {
      this.options.placeholderNumberType = type;
      this._updatePlaceholder();
    }
    setDisabled(disabled) {
      this.ui.telInput.disabled = disabled;
      if (disabled) {
        this.ui.selectedCountry.setAttribute("disabled", "true");
      } else {
        this.ui.selectedCountry.removeAttribute("disabled");
      }
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
        forEachInstance("handleUtils");
        return true;
      }).catch((error) => {
        forEachInstance("rejectUtilsScriptPromise", error);
        throw error;
      });
    }
    return null;
  };
  var forEachInstance = (method, ...args) => {
    Object.values(intlTelInput.instances).forEach((instance) => {
      const fn = instance[method];
      if (typeof fn === "function") {
        fn.apply(instance, args);
      }
    });
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
      version: "25.15.1"
    }
  );
  var intl_tel_input_default = intlTelInput;
  return __toCommonJS(intl_tel_input_exports);
})();

// UMD
  return factoryOutput.default;
}));
