/*
 * International Telephone Input v29.4.0
 * git+https://github.com/jackocnr/intl-tel-input.git
 * Licensed under the MIT license
 */
"use strict";
var _factory = (() => {
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

  // packages/core/src/js/intlTelInput.ts
  var intlTelInput_exports = {};
  __export(intlTelInput_exports, {
    COUNTRY_SELECTOR_MODE: () => COUNTRY_SELECTOR_MODE,
    Iti: () => Iti,
    NUMBER_FORMAT: () => NUMBER_FORMAT,
    NUMBER_TYPE: () => NUMBER_TYPE,
    PLACEHOLDER_POLICY: () => PLACEHOLDER_POLICY,
    VALIDATION_ERROR: () => VALIDATION_ERROR,
    default: () => intlTelInput_default
  });

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
  return __toCommonJS(intlTelInput_exports);
})();
var intlTelInput = _factory.default;
