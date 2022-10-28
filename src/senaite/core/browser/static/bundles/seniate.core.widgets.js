/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 51:
/***/ ((module) => {

/*
 * International Telephone Input v17.0.19
 * https://github.com/jackocnr/intl-tel-input.git
 * Licensed under the MIT license
 */

// wrap in UMD
(function(factory) {
    if ( true && module.exports) module.exports = factory(); else window.intlTelInput = factory();
})(function(undefined) {
    "use strict";
    return function() {
        // Array of country objects for the flag dropdown.
        // Here is the criteria for the plugin to support a given country/territory
        // - It has an iso2 code: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        // - It has it's own country calling code (it is not a sub-region of another country): https://en.wikipedia.org/wiki/List_of_country_calling_codes
        // - It has a flag in the region-flags project: https://github.com/behdad/region-flags/tree/gh-pages/png
        // - It is supported by libphonenumber (it must be listed on this page): https://github.com/googlei18n/libphonenumber/blob/master/resources/ShortNumberMetadata.xml
        // Each country array has the following information:
        // [
        //    Country name,
        //    iso2 code,
        //    International dial code,
        //    Order (if >1 country with same dial code),
        //    Area codes
        // ]
        var allCountries = [ [ "Afghanistan (‫افغانستان‬‎)", "af", "93" ], [ "Albania (Shqipëri)", "al", "355" ], [ "Algeria (‫الجزائر‬‎)", "dz", "213" ], [ "American Samoa", "as", "1", 5, [ "684" ] ], [ "Andorra", "ad", "376" ], [ "Angola", "ao", "244" ], [ "Anguilla", "ai", "1", 6, [ "264" ] ], [ "Antigua and Barbuda", "ag", "1", 7, [ "268" ] ], [ "Argentina", "ar", "54" ], [ "Armenia (Հայաստան)", "am", "374" ], [ "Aruba", "aw", "297" ], [ "Ascension Island", "ac", "247" ], [ "Australia", "au", "61", 0 ], [ "Austria (Österreich)", "at", "43" ], [ "Azerbaijan (Azərbaycan)", "az", "994" ], [ "Bahamas", "bs", "1", 8, [ "242" ] ], [ "Bahrain (‫البحرين‬‎)", "bh", "973" ], [ "Bangladesh (বাংলাদেশ)", "bd", "880" ], [ "Barbados", "bb", "1", 9, [ "246" ] ], [ "Belarus (Беларусь)", "by", "375" ], [ "Belgium (België)", "be", "32" ], [ "Belize", "bz", "501" ], [ "Benin (Bénin)", "bj", "229" ], [ "Bermuda", "bm", "1", 10, [ "441" ] ], [ "Bhutan (འབྲུག)", "bt", "975" ], [ "Bolivia", "bo", "591" ], [ "Bosnia and Herzegovina (Босна и Херцеговина)", "ba", "387" ], [ "Botswana", "bw", "267" ], [ "Brazil (Brasil)", "br", "55" ], [ "British Indian Ocean Territory", "io", "246" ], [ "British Virgin Islands", "vg", "1", 11, [ "284" ] ], [ "Brunei", "bn", "673" ], [ "Bulgaria (България)", "bg", "359" ], [ "Burkina Faso", "bf", "226" ], [ "Burundi (Uburundi)", "bi", "257" ], [ "Cambodia (កម្ពុជា)", "kh", "855" ], [ "Cameroon (Cameroun)", "cm", "237" ], [ "Canada", "ca", "1", 1, [ "204", "226", "236", "249", "250", "289", "306", "343", "365", "387", "403", "416", "418", "431", "437", "438", "450", "506", "514", "519", "548", "579", "581", "587", "604", "613", "639", "647", "672", "705", "709", "742", "778", "780", "782", "807", "819", "825", "867", "873", "902", "905" ] ], [ "Cape Verde (Kabu Verdi)", "cv", "238" ], [ "Caribbean Netherlands", "bq", "599", 1, [ "3", "4", "7" ] ], [ "Cayman Islands", "ky", "1", 12, [ "345" ] ], [ "Central African Republic (République centrafricaine)", "cf", "236" ], [ "Chad (Tchad)", "td", "235" ], [ "Chile", "cl", "56" ], [ "China (中国)", "cn", "86" ], [ "Christmas Island", "cx", "61", 2, [ "89164" ] ], [ "Cocos (Keeling) Islands", "cc", "61", 1, [ "89162" ] ], [ "Colombia", "co", "57" ], [ "Comoros (‫جزر القمر‬‎)", "km", "269" ], [ "Congo (DRC) (Jamhuri ya Kidemokrasia ya Kongo)", "cd", "243" ], [ "Congo (Republic) (Congo-Brazzaville)", "cg", "242" ], [ "Cook Islands", "ck", "682" ], [ "Costa Rica", "cr", "506" ], [ "Côte d’Ivoire", "ci", "225" ], [ "Croatia (Hrvatska)", "hr", "385" ], [ "Cuba", "cu", "53" ], [ "Curaçao", "cw", "599", 0 ], [ "Cyprus (Κύπρος)", "cy", "357" ], [ "Czech Republic (Česká republika)", "cz", "420" ], [ "Denmark (Danmark)", "dk", "45" ], [ "Djibouti", "dj", "253" ], [ "Dominica", "dm", "1", 13, [ "767" ] ], [ "Dominican Republic (República Dominicana)", "do", "1", 2, [ "809", "829", "849" ] ], [ "Ecuador", "ec", "593" ], [ "Egypt (‫مصر‬‎)", "eg", "20" ], [ "El Salvador", "sv", "503" ], [ "Equatorial Guinea (Guinea Ecuatorial)", "gq", "240" ], [ "Eritrea", "er", "291" ], [ "Estonia (Eesti)", "ee", "372" ], [ "Eswatini", "sz", "268" ], [ "Ethiopia", "et", "251" ], [ "Falkland Islands (Islas Malvinas)", "fk", "500" ], [ "Faroe Islands (Føroyar)", "fo", "298" ], [ "Fiji", "fj", "679" ], [ "Finland (Suomi)", "fi", "358", 0 ], [ "France", "fr", "33" ], [ "French Guiana (Guyane française)", "gf", "594" ], [ "French Polynesia (Polynésie française)", "pf", "689" ], [ "Gabon", "ga", "241" ], [ "Gambia", "gm", "220" ], [ "Georgia (საქართველო)", "ge", "995" ], [ "Germany (Deutschland)", "de", "49" ], [ "Ghana (Gaana)", "gh", "233" ], [ "Gibraltar", "gi", "350" ], [ "Greece (Ελλάδα)", "gr", "30" ], [ "Greenland (Kalaallit Nunaat)", "gl", "299" ], [ "Grenada", "gd", "1", 14, [ "473" ] ], [ "Guadeloupe", "gp", "590", 0 ], [ "Guam", "gu", "1", 15, [ "671" ] ], [ "Guatemala", "gt", "502" ], [ "Guernsey", "gg", "44", 1, [ "1481", "7781", "7839", "7911" ] ], [ "Guinea (Guinée)", "gn", "224" ], [ "Guinea-Bissau (Guiné Bissau)", "gw", "245" ], [ "Guyana", "gy", "592" ], [ "Haiti", "ht", "509" ], [ "Honduras", "hn", "504" ], [ "Hong Kong (香港)", "hk", "852" ], [ "Hungary (Magyarország)", "hu", "36" ], [ "Iceland (Ísland)", "is", "354" ], [ "India (भारत)", "in", "91" ], [ "Indonesia", "id", "62" ], [ "Iran (‫ایران‬‎)", "ir", "98" ], [ "Iraq (‫العراق‬‎)", "iq", "964" ], [ "Ireland", "ie", "353" ], [ "Isle of Man", "im", "44", 2, [ "1624", "74576", "7524", "7924", "7624" ] ], [ "Israel (‫ישראל‬‎)", "il", "972" ], [ "Italy (Italia)", "it", "39", 0 ], [ "Jamaica", "jm", "1", 4, [ "876", "658" ] ], [ "Japan (日本)", "jp", "81" ], [ "Jersey", "je", "44", 3, [ "1534", "7509", "7700", "7797", "7829", "7937" ] ], [ "Jordan (‫الأردن‬‎)", "jo", "962" ], [ "Kazakhstan (Казахстан)", "kz", "7", 1, [ "33", "7" ] ], [ "Kenya", "ke", "254" ], [ "Kiribati", "ki", "686" ], [ "Kosovo", "xk", "383" ], [ "Kuwait (‫الكويت‬‎)", "kw", "965" ], [ "Kyrgyzstan (Кыргызстан)", "kg", "996" ], [ "Laos (ລາວ)", "la", "856" ], [ "Latvia (Latvija)", "lv", "371" ], [ "Lebanon (‫لبنان‬‎)", "lb", "961" ], [ "Lesotho", "ls", "266" ], [ "Liberia", "lr", "231" ], [ "Libya (‫ليبيا‬‎)", "ly", "218" ], [ "Liechtenstein", "li", "423" ], [ "Lithuania (Lietuva)", "lt", "370" ], [ "Luxembourg", "lu", "352" ], [ "Macau (澳門)", "mo", "853" ], [ "North Macedonia (Македонија)", "mk", "389" ], [ "Madagascar (Madagasikara)", "mg", "261" ], [ "Malawi", "mw", "265" ], [ "Malaysia", "my", "60" ], [ "Maldives", "mv", "960" ], [ "Mali", "ml", "223" ], [ "Malta", "mt", "356" ], [ "Marshall Islands", "mh", "692" ], [ "Martinique", "mq", "596" ], [ "Mauritania (‫موريتانيا‬‎)", "mr", "222" ], [ "Mauritius (Moris)", "mu", "230" ], [ "Mayotte", "yt", "262", 1, [ "269", "639" ] ], [ "Mexico (México)", "mx", "52" ], [ "Micronesia", "fm", "691" ], [ "Moldova (Republica Moldova)", "md", "373" ], [ "Monaco", "mc", "377" ], [ "Mongolia (Монгол)", "mn", "976" ], [ "Montenegro (Crna Gora)", "me", "382" ], [ "Montserrat", "ms", "1", 16, [ "664" ] ], [ "Morocco (‫المغرب‬‎)", "ma", "212", 0 ], [ "Mozambique (Moçambique)", "mz", "258" ], [ "Myanmar (Burma) (မြန်မာ)", "mm", "95" ], [ "Namibia (Namibië)", "na", "264" ], [ "Nauru", "nr", "674" ], [ "Nepal (नेपाल)", "np", "977" ], [ "Netherlands (Nederland)", "nl", "31" ], [ "New Caledonia (Nouvelle-Calédonie)", "nc", "687" ], [ "New Zealand", "nz", "64" ], [ "Nicaragua", "ni", "505" ], [ "Niger (Nijar)", "ne", "227" ], [ "Nigeria", "ng", "234" ], [ "Niue", "nu", "683" ], [ "Norfolk Island", "nf", "672" ], [ "North Korea (조선 민주주의 인민 공화국)", "kp", "850" ], [ "Northern Mariana Islands", "mp", "1", 17, [ "670" ] ], [ "Norway (Norge)", "no", "47", 0 ], [ "Oman (‫عُمان‬‎)", "om", "968" ], [ "Pakistan (‫پاکستان‬‎)", "pk", "92" ], [ "Palau", "pw", "680" ], [ "Palestine (‫فلسطين‬‎)", "ps", "970" ], [ "Panama (Panamá)", "pa", "507" ], [ "Papua New Guinea", "pg", "675" ], [ "Paraguay", "py", "595" ], [ "Peru (Perú)", "pe", "51" ], [ "Philippines", "ph", "63" ], [ "Poland (Polska)", "pl", "48" ], [ "Portugal", "pt", "351" ], [ "Puerto Rico", "pr", "1", 3, [ "787", "939" ] ], [ "Qatar (‫قطر‬‎)", "qa", "974" ], [ "Réunion (La Réunion)", "re", "262", 0 ], [ "Romania (România)", "ro", "40" ], [ "Russia (Россия)", "ru", "7", 0 ], [ "Rwanda", "rw", "250" ], [ "Saint Barthélemy", "bl", "590", 1 ], [ "Saint Helena", "sh", "290" ], [ "Saint Kitts and Nevis", "kn", "1", 18, [ "869" ] ], [ "Saint Lucia", "lc", "1", 19, [ "758" ] ], [ "Saint Martin (Saint-Martin (partie française))", "mf", "590", 2 ], [ "Saint Pierre and Miquelon (Saint-Pierre-et-Miquelon)", "pm", "508" ], [ "Saint Vincent and the Grenadines", "vc", "1", 20, [ "784" ] ], [ "Samoa", "ws", "685" ], [ "San Marino", "sm", "378" ], [ "São Tomé and Príncipe (São Tomé e Príncipe)", "st", "239" ], [ "Saudi Arabia (‫المملكة العربية السعودية‬‎)", "sa", "966" ], [ "Senegal (Sénégal)", "sn", "221" ], [ "Serbia (Србија)", "rs", "381" ], [ "Seychelles", "sc", "248" ], [ "Sierra Leone", "sl", "232" ], [ "Singapore", "sg", "65" ], [ "Sint Maarten", "sx", "1", 21, [ "721" ] ], [ "Slovakia (Slovensko)", "sk", "421" ], [ "Slovenia (Slovenija)", "si", "386" ], [ "Solomon Islands", "sb", "677" ], [ "Somalia (Soomaaliya)", "so", "252" ], [ "South Africa", "za", "27" ], [ "South Korea (대한민국)", "kr", "82" ], [ "South Sudan (‫جنوب السودان‬‎)", "ss", "211" ], [ "Spain (España)", "es", "34" ], [ "Sri Lanka (ශ්‍රී ලංකාව)", "lk", "94" ], [ "Sudan (‫السودان‬‎)", "sd", "249" ], [ "Suriname", "sr", "597" ], [ "Svalbard and Jan Mayen", "sj", "47", 1, [ "79" ] ], [ "Sweden (Sverige)", "se", "46" ], [ "Switzerland (Schweiz)", "ch", "41" ], [ "Syria (‫سوريا‬‎)", "sy", "963" ], [ "Taiwan (台灣)", "tw", "886" ], [ "Tajikistan", "tj", "992" ], [ "Tanzania", "tz", "255" ], [ "Thailand (ไทย)", "th", "66" ], [ "Timor-Leste", "tl", "670" ], [ "Togo", "tg", "228" ], [ "Tokelau", "tk", "690" ], [ "Tonga", "to", "676" ], [ "Trinidad and Tobago", "tt", "1", 22, [ "868" ] ], [ "Tunisia (‫تونس‬‎)", "tn", "216" ], [ "Turkey (Türkiye)", "tr", "90" ], [ "Turkmenistan", "tm", "993" ], [ "Turks and Caicos Islands", "tc", "1", 23, [ "649" ] ], [ "Tuvalu", "tv", "688" ], [ "U.S. Virgin Islands", "vi", "1", 24, [ "340" ] ], [ "Uganda", "ug", "256" ], [ "Ukraine (Україна)", "ua", "380" ], [ "United Arab Emirates (‫الإمارات العربية المتحدة‬‎)", "ae", "971" ], [ "United Kingdom", "gb", "44", 0 ], [ "United States", "us", "1", 0 ], [ "Uruguay", "uy", "598" ], [ "Uzbekistan (Oʻzbekiston)", "uz", "998" ], [ "Vanuatu", "vu", "678" ], [ "Vatican City (Città del Vaticano)", "va", "39", 1, [ "06698" ] ], [ "Venezuela", "ve", "58" ], [ "Vietnam (Việt Nam)", "vn", "84" ], [ "Wallis and Futuna (Wallis-et-Futuna)", "wf", "681" ], [ "Western Sahara (‫الصحراء الغربية‬‎)", "eh", "212", 1, [ "5288", "5289" ] ], [ "Yemen (‫اليمن‬‎)", "ye", "967" ], [ "Zambia", "zm", "260" ], [ "Zimbabwe", "zw", "263" ], [ "Åland Islands", "ax", "358", 1, [ "18" ] ] ];
        // loop over all of the countries above, restructuring the data to be objects with named keys
        for (var i = 0; i < allCountries.length; i++) {
            var c = allCountries[i];
            allCountries[i] = {
                name: c[0],
                iso2: c[1],
                dialCode: c[2],
                priority: c[3] || 0,
                areaCodes: c[4] || null
            };
        }
        "use strict";
        function _classCallCheck(instance, Constructor) {
            if (!(instance instanceof Constructor)) {
                throw new TypeError("Cannot call a class as a function");
            }
        }
        function _defineProperties(target, props) {
            for (var i = 0; i < props.length; i++) {
                var descriptor = props[i];
                descriptor.enumerable = descriptor.enumerable || false;
                descriptor.configurable = true;
                if ("value" in descriptor) descriptor.writable = true;
                Object.defineProperty(target, descriptor.key, descriptor);
            }
        }
        function _createClass(Constructor, protoProps, staticProps) {
            if (protoProps) _defineProperties(Constructor.prototype, protoProps);
            if (staticProps) _defineProperties(Constructor, staticProps);
            return Constructor;
        }
        var intlTelInputGlobals = {
            getInstance: function getInstance(input) {
                var id = input.getAttribute("data-intl-tel-input-id");
                return window.intlTelInputGlobals.instances[id];
            },
            instances: {},
            // using a global like this allows us to mock it in the tests
            documentReady: function documentReady() {
                return document.readyState === "complete";
            }
        };
        if (typeof window === "object") window.intlTelInputGlobals = intlTelInputGlobals;
        // these vars persist through all instances of the plugin
        var id = 0;
        var defaults = {
            // whether or not to allow the dropdown
            allowDropdown: true,
            // if there is just a dial code in the input: remove it on blur
            autoHideDialCode: true,
            // add a placeholder in the input with an example number for the selected country
            autoPlaceholder: "polite",
            // modify the parentClass
            customContainer: "",
            // modify the auto placeholder
            customPlaceholder: null,
            // append menu to specified element
            dropdownContainer: null,
            // don't display these countries
            excludeCountries: [],
            // format the input value during initialisation and on setNumber
            formatOnDisplay: true,
            // geoIp lookup function
            geoIpLookup: null,
            // inject a hidden input with this name, and on submit, populate it with the result of getNumber
            hiddenInput: "",
            // initial country
            initialCountry: "",
            // localized country names e.g. { 'de': 'Deutschland' }
            localizedCountries: null,
            // don't insert international dial codes
            nationalMode: true,
            // display only these countries
            onlyCountries: [],
            // number type to use for placeholders
            placeholderNumberType: "MOBILE",
            // the countries at the top of the list. defaults to united states and united kingdom
            preferredCountries: [ "us", "gb" ],
            // display the country dial code next to the selected flag so it's not part of the typed number
            separateDialCode: false,
            // specify the path to the libphonenumber script to enable validation/formatting
            utilsScript: ""
        };
        // https://en.wikipedia.org/wiki/List_of_North_American_Numbering_Plan_area_codes#Non-geographic_area_codes
        var regionlessNanpNumbers = [ "800", "822", "833", "844", "855", "866", "877", "880", "881", "882", "883", "884", "885", "886", "887", "888", "889" ];
        // utility function to iterate over an object. can't use Object.entries or native forEach because
        // of IE11
        var forEachProp = function forEachProp(obj, callback) {
            var keys = Object.keys(obj);
            for (var i = 0; i < keys.length; i++) {
                callback(keys[i], obj[keys[i]]);
            }
        };
        // run a method on each instance of the plugin
        var forEachInstance = function forEachInstance(method) {
            forEachProp(window.intlTelInputGlobals.instances, function(key) {
                window.intlTelInputGlobals.instances[key][method]();
            });
        };
        // this is our plugin class that we will create an instance of
        // eslint-disable-next-line no-unused-vars
        var Iti = /*#__PURE__*/
        function() {
            function Iti(input, options) {
                var _this = this;
                _classCallCheck(this, Iti);
                this.id = id++;
                this.telInput = input;
                this.activeItem = null;
                this.highlightedItem = null;
                // process specified options / defaults
                // alternative to Object.assign, which isn't supported by IE11
                var customOptions = options || {};
                this.options = {};
                forEachProp(defaults, function(key, value) {
                    _this.options[key] = customOptions.hasOwnProperty(key) ? customOptions[key] : value;
                });
                this.hadInitialPlaceholder = Boolean(input.getAttribute("placeholder"));
            }
            _createClass(Iti, [ {
                key: "_init",
                value: function _init() {
                    var _this2 = this;
                    // if in nationalMode, disable options relating to dial codes
                    if (this.options.nationalMode) this.options.autoHideDialCode = false;
                    // if separateDialCode then doesn't make sense to A) insert dial code into input
                    // (autoHideDialCode), and B) display national numbers (because we're displaying the country
                    // dial code next to them)
                    if (this.options.separateDialCode) {
                        this.options.autoHideDialCode = this.options.nationalMode = false;
                    }
                    // we cannot just test screen size as some smartphones/website meta tags will report desktop
                    // resolutions
                    // Note: for some reason jasmine breaks if you put this in the main Plugin function with the
                    // rest of these declarations
                    // Note: to target Android Mobiles (and not Tablets), we must find 'Android' and 'Mobile'
                    this.isMobile = /Android.+Mobile|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                    if (this.isMobile) {
                        // trigger the mobile dropdown css
                        document.body.classList.add("iti-mobile");
                        // on mobile, we want a full screen dropdown, so we must append it to the body
                        if (!this.options.dropdownContainer) this.options.dropdownContainer = document.body;
                    }
                    // these promises get resolved when their individual requests complete
                    // this way the dev can do something like iti.promise.then(...) to know when all requests are
                    // complete
                    if (typeof Promise !== "undefined") {
                        var autoCountryPromise = new Promise(function(resolve, reject) {
                            _this2.resolveAutoCountryPromise = resolve;
                            _this2.rejectAutoCountryPromise = reject;
                        });
                        var utilsScriptPromise = new Promise(function(resolve, reject) {
                            _this2.resolveUtilsScriptPromise = resolve;
                            _this2.rejectUtilsScriptPromise = reject;
                        });
                        this.promise = Promise.all([ autoCountryPromise, utilsScriptPromise ]);
                    } else {
                        // prevent errors when Promise doesn't exist
                        this.resolveAutoCountryPromise = this.rejectAutoCountryPromise = function() {};
                        this.resolveUtilsScriptPromise = this.rejectUtilsScriptPromise = function() {};
                    }
                    // in various situations there could be no country selected initially, but we need to be able
                    // to assume this variable exists
                    this.selectedCountryData = {};
                    // process all the data: onlyCountries, excludeCountries, preferredCountries etc
                    this._processCountryData();
                    // generate the markup
                    this._generateMarkup();
                    // set the initial state of the input value and the selected flag
                    this._setInitialState();
                    // start all of the event listeners: autoHideDialCode, input keydown, selectedFlag click
                    this._initListeners();
                    // utils script, and auto country
                    this._initRequests();
                }
            }, {
                key: "_processCountryData",
                value: function _processCountryData() {
                    // process onlyCountries or excludeCountries array if present
                    this._processAllCountries();
                    // process the countryCodes map
                    this._processCountryCodes();
                    // process the preferredCountries
                    this._processPreferredCountries();
                    // translate countries according to localizedCountries option
                    if (this.options.localizedCountries) this._translateCountriesByLocale();
                    // sort countries by name
                    if (this.options.onlyCountries.length || this.options.localizedCountries) {
                        this.countries.sort(this._countryNameSort);
                    }
                }
            }, {
                key: "_addCountryCode",
                value: function _addCountryCode(iso2, countryCode, priority) {
                    if (countryCode.length > this.countryCodeMaxLen) {
                        this.countryCodeMaxLen = countryCode.length;
                    }
                    if (!this.countryCodes.hasOwnProperty(countryCode)) {
                        this.countryCodes[countryCode] = [];
                    }
                    // bail if we already have this country for this countryCode
                    for (var i = 0; i < this.countryCodes[countryCode].length; i++) {
                        if (this.countryCodes[countryCode][i] === iso2) return;
                    }
                    // check for undefined as 0 is falsy
                    var index = priority !== undefined ? priority : this.countryCodes[countryCode].length;
                    this.countryCodes[countryCode][index] = iso2;
                }
            }, {
                key: "_processAllCountries",
                value: function _processAllCountries() {
                    if (this.options.onlyCountries.length) {
                        var lowerCaseOnlyCountries = this.options.onlyCountries.map(function(country) {
                            return country.toLowerCase();
                        });
                        this.countries = allCountries.filter(function(country) {
                            return lowerCaseOnlyCountries.indexOf(country.iso2) > -1;
                        });
                    } else if (this.options.excludeCountries.length) {
                        var lowerCaseExcludeCountries = this.options.excludeCountries.map(function(country) {
                            return country.toLowerCase();
                        });
                        this.countries = allCountries.filter(function(country) {
                            return lowerCaseExcludeCountries.indexOf(country.iso2) === -1;
                        });
                    } else {
                        this.countries = allCountries;
                    }
                }
            }, {
                key: "_translateCountriesByLocale",
                value: function _translateCountriesByLocale() {
                    for (var i = 0; i < this.countries.length; i++) {
                        var iso = this.countries[i].iso2.toLowerCase();
                        if (this.options.localizedCountries.hasOwnProperty(iso)) {
                            this.countries[i].name = this.options.localizedCountries[iso];
                        }
                    }
                }
            }, {
                key: "_countryNameSort",
                value: function _countryNameSort(a, b) {
                    return a.name.localeCompare(b.name);
                }
            }, {
                key: "_processCountryCodes",
                value: function _processCountryCodes() {
                    this.countryCodeMaxLen = 0;
                    // here we store just dial codes
                    this.dialCodes = {};
                    // here we store "country codes" (both dial codes and their area codes)
                    this.countryCodes = {};
                    // first: add dial codes
                    for (var i = 0; i < this.countries.length; i++) {
                        var c = this.countries[i];
                        if (!this.dialCodes[c.dialCode]) this.dialCodes[c.dialCode] = true;
                        this._addCountryCode(c.iso2, c.dialCode, c.priority);
                    }
                    // next: add area codes
                    // this is a second loop over countries, to make sure we have all of the "root" countries
                    // already in the map, so that we can access them, as each time we add an area code substring
                    // to the map, we also need to include the "root" country's code, as that also matches
                    for (var _i = 0; _i < this.countries.length; _i++) {
                        var _c = this.countries[_i];
                        // area codes
                        if (_c.areaCodes) {
                            var rootCountryCode = this.countryCodes[_c.dialCode][0];
                            // for each area code
                            for (var j = 0; j < _c.areaCodes.length; j++) {
                                var areaCode = _c.areaCodes[j];
                                // for each digit in the area code to add all partial matches as well
                                for (var k = 1; k < areaCode.length; k++) {
                                    var partialDialCode = _c.dialCode + areaCode.substr(0, k);
                                    // start with the root country, as that also matches this dial code
                                    this._addCountryCode(rootCountryCode, partialDialCode);
                                    this._addCountryCode(_c.iso2, partialDialCode);
                                }
                                // add the full area code
                                this._addCountryCode(_c.iso2, _c.dialCode + areaCode);
                            }
                        }
                    }
                }
            }, {
                key: "_processPreferredCountries",
                value: function _processPreferredCountries() {
                    this.preferredCountries = [];
                    for (var i = 0; i < this.options.preferredCountries.length; i++) {
                        var countryCode = this.options.preferredCountries[i].toLowerCase();
                        var countryData = this._getCountryData(countryCode, false, true);
                        if (countryData) this.preferredCountries.push(countryData);
                    }
                }
            }, {
                key: "_createEl",
                value: function _createEl(name, attrs, container) {
                    var el = document.createElement(name);
                    if (attrs) forEachProp(attrs, function(key, value) {
                        return el.setAttribute(key, value);
                    });
                    if (container) container.appendChild(el);
                    return el;
                }
            }, {
                key: "_generateMarkup",
                value: function _generateMarkup() {
                    // if autocomplete does not exist on the element and its form, then
                    // prevent autocomplete as there's no safe, cross-browser event we can react to, so it can
                    // easily put the plugin in an inconsistent state e.g. the wrong flag selected for the
                    // autocompleted number, which on submit could mean wrong number is saved (esp in nationalMode)
                    if (!this.telInput.hasAttribute("autocomplete") && !(this.telInput.form && this.telInput.form.hasAttribute("autocomplete"))) {
                        this.telInput.setAttribute("autocomplete", "off");
                    }
                    // containers (mostly for positioning)
                    var parentClass = "iti";
                    if (this.options.allowDropdown) parentClass += " iti--allow-dropdown";
                    if (this.options.separateDialCode) parentClass += " iti--separate-dial-code";
                    if (this.options.customContainer) {
                        parentClass += " ";
                        parentClass += this.options.customContainer;
                    }
                    var wrapper = this._createEl("div", {
                        "class": parentClass
                    });
                    this.telInput.parentNode.insertBefore(wrapper, this.telInput);
                    this.flagsContainer = this._createEl("div", {
                        "class": "iti__flag-container"
                    }, wrapper);
                    wrapper.appendChild(this.telInput);
                    // selected flag (displayed to left of input)
                    this.selectedFlag = this._createEl("div", {
                        "class": "iti__selected-flag",
                        role: "combobox",
                        "aria-controls": "iti-".concat(this.id, "__country-listbox"),
                        "aria-owns": "iti-".concat(this.id, "__country-listbox"),
                        "aria-expanded": "false"
                    }, this.flagsContainer);
                    this.selectedFlagInner = this._createEl("div", {
                        "class": "iti__flag"
                    }, this.selectedFlag);
                    if (this.options.separateDialCode) {
                        this.selectedDialCode = this._createEl("div", {
                            "class": "iti__selected-dial-code"
                        }, this.selectedFlag);
                    }
                    if (this.options.allowDropdown) {
                        // make element focusable and tab navigable
                        this.selectedFlag.setAttribute("tabindex", "0");
                        this.dropdownArrow = this._createEl("div", {
                            "class": "iti__arrow"
                        }, this.selectedFlag);
                        // country dropdown: preferred countries, then divider, then all countries
                        this.countryList = this._createEl("ul", {
                            "class": "iti__country-list iti__hide",
                            id: "iti-".concat(this.id, "__country-listbox"),
                            role: "listbox",
                            "aria-label": "List of countries"
                        });
                        if (this.preferredCountries.length) {
                            this._appendListItems(this.preferredCountries, "iti__preferred", true);
                            this._createEl("li", {
                                "class": "iti__divider",
                                role: "separator",
                                "aria-disabled": "true"
                            }, this.countryList);
                        }
                        this._appendListItems(this.countries, "iti__standard");
                        // create dropdownContainer markup
                        if (this.options.dropdownContainer) {
                            this.dropdown = this._createEl("div", {
                                "class": "iti iti--container"
                            });
                            this.dropdown.appendChild(this.countryList);
                        } else {
                            this.flagsContainer.appendChild(this.countryList);
                        }
                    }
                    if (this.options.hiddenInput) {
                        var hiddenInputName = this.options.hiddenInput;
                        var name = this.telInput.getAttribute("name");
                        if (name) {
                            var i = name.lastIndexOf("[");
                            // if input name contains square brackets, then give the hidden input the same name,
                            // replacing the contents of the last set of brackets with the given hiddenInput name
                            if (i !== -1) hiddenInputName = "".concat(name.substr(0, i), "[").concat(hiddenInputName, "]");
                        }
                        this.hiddenInput = this._createEl("input", {
                            type: "hidden",
                            name: hiddenInputName
                        });
                        wrapper.appendChild(this.hiddenInput);
                    }
                }
            }, {
                key: "_appendListItems",
                value: function _appendListItems(countries, className, preferred) {
                    // we create so many DOM elements, it is faster to build a temp string
                    // and then add everything to the DOM in one go at the end
                    var tmp = "";
                    // for each country
                    for (var i = 0; i < countries.length; i++) {
                        var c = countries[i];
                        var idSuffix = preferred ? "-preferred" : "";
                        // open the list item
                        tmp += "<li class='iti__country ".concat(className, "' tabIndex='-1' id='iti-").concat(this.id, "__item-").concat(c.iso2).concat(idSuffix, "' role='option' data-dial-code='").concat(c.dialCode, "' data-country-code='").concat(c.iso2, "' aria-selected='false'>");
                        // add the flag
                        tmp += "<div class='iti__flag-box'><div class='iti__flag iti__".concat(c.iso2, "'></div></div>");
                        // and the country name and dial code
                        tmp += "<span class='iti__country-name'>".concat(c.name, "</span>");
                        tmp += "<span class='iti__dial-code'>+".concat(c.dialCode, "</span>");
                        // close the list item
                        tmp += "</li>";
                    }
                    this.countryList.insertAdjacentHTML("beforeend", tmp);
                }
            }, {
                key: "_setInitialState",
                value: function _setInitialState() {
                    // fix firefox bug: when first load page (with input with value set to number with intl dial
                    // code) and initialising plugin removes the dial code from the input, then refresh page,
                    // and we try to init plugin again but this time on number without dial code so get grey flag
                    var attributeValue = this.telInput.getAttribute("value");
                    var inputValue = this.telInput.value;
                    var useAttribute = attributeValue && attributeValue.charAt(0) === "+" && (!inputValue || inputValue.charAt(0) !== "+");
                    var val = useAttribute ? attributeValue : inputValue;
                    var dialCode = this._getDialCode(val);
                    var isRegionlessNanp = this._isRegionlessNanp(val);
                    var _this$options = this.options, initialCountry = _this$options.initialCountry, nationalMode = _this$options.nationalMode, autoHideDialCode = _this$options.autoHideDialCode, separateDialCode = _this$options.separateDialCode;
                    // if we already have a dial code, and it's not a regionlessNanp, we can go ahead and set the
                    // flag, else fall back to the default country
                    if (dialCode && !isRegionlessNanp) {
                        this._updateFlagFromNumber(val);
                    } else if (initialCountry !== "auto") {
                        // see if we should select a flag
                        if (initialCountry) {
                            this._setFlag(initialCountry.toLowerCase());
                        } else {
                            if (dialCode && isRegionlessNanp) {
                                // has intl dial code, is regionless nanp, and no initialCountry, so default to US
                                this._setFlag("us");
                            } else {
                                // no dial code and no initialCountry, so default to first in list
                                this.defaultCountry = this.preferredCountries.length ? this.preferredCountries[0].iso2 : this.countries[0].iso2;
                                if (!val) {
                                    this._setFlag(this.defaultCountry);
                                }
                            }
                        }
                        // if empty and no nationalMode and no autoHideDialCode then insert the default dial code
                        if (!val && !nationalMode && !autoHideDialCode && !separateDialCode) {
                            this.telInput.value = "+".concat(this.selectedCountryData.dialCode);
                        }
                    }
                    // NOTE: if initialCountry is set to auto, that will be handled separately
                    // format - note this wont be run after _updateDialCode as that's only called if no val
                    if (val) this._updateValFromNumber(val);
                }
            }, {
                key: "_initListeners",
                value: function _initListeners() {
                    this._initKeyListeners();
                    if (this.options.autoHideDialCode) this._initBlurListeners();
                    if (this.options.allowDropdown) this._initDropdownListeners();
                    if (this.hiddenInput) this._initHiddenInputListener();
                }
            }, {
                key: "_initHiddenInputListener",
                value: function _initHiddenInputListener() {
                    var _this3 = this;
                    this._handleHiddenInputSubmit = function() {
                        _this3.hiddenInput.value = _this3.getNumber();
                    };
                    if (this.telInput.form) this.telInput.form.addEventListener("submit", this._handleHiddenInputSubmit);
                }
            }, {
                key: "_getClosestLabel",
                value: function _getClosestLabel() {
                    var el = this.telInput;
                    while (el && el.tagName !== "LABEL") {
                        el = el.parentNode;
                    }
                    return el;
                }
            }, {
                key: "_initDropdownListeners",
                value: function _initDropdownListeners() {
                    var _this4 = this;
                    // hack for input nested inside label (which is valid markup): clicking the selected-flag to
                    // open the dropdown would then automatically trigger a 2nd click on the input which would
                    // close it again
                    this._handleLabelClick = function(e) {
                        // if the dropdown is closed, then focus the input, else ignore the click
                        if (_this4.countryList.classList.contains("iti__hide")) _this4.telInput.focus(); else e.preventDefault();
                    };
                    var label = this._getClosestLabel();
                    if (label) label.addEventListener("click", this._handleLabelClick);
                    // toggle country dropdown on click
                    this._handleClickSelectedFlag = function() {
                        // only intercept this event if we're opening the dropdown
                        // else let it bubble up to the top ("click-off-to-close" listener)
                        // we cannot just stopPropagation as it may be needed to close another instance
                        if (_this4.countryList.classList.contains("iti__hide") && !_this4.telInput.disabled && !_this4.telInput.readOnly) {
                            _this4._showDropdown();
                        }
                    };
                    this.selectedFlag.addEventListener("click", this._handleClickSelectedFlag);
                    // open dropdown list if currently focused
                    this._handleFlagsContainerKeydown = function(e) {
                        var isDropdownHidden = _this4.countryList.classList.contains("iti__hide");
                        if (isDropdownHidden && [ "ArrowUp", "Up", "ArrowDown", "Down", " ", "Enter" ].indexOf(e.key) !== -1) {
                            // prevent form from being submitted if "ENTER" was pressed
                            e.preventDefault();
                            // prevent event from being handled again by document
                            e.stopPropagation();
                            _this4._showDropdown();
                        }
                        // allow navigation from dropdown to input on TAB
                        if (e.key === "Tab") _this4._closeDropdown();
                    };
                    this.flagsContainer.addEventListener("keydown", this._handleFlagsContainerKeydown);
                }
            }, {
                key: "_initRequests",
                value: function _initRequests() {
                    var _this5 = this;
                    // if the user has specified the path to the utils script, fetch it on window.load, else resolve
                    if (this.options.utilsScript && !window.intlTelInputUtils) {
                        // if the plugin is being initialised after the window.load event has already been fired
                        if (window.intlTelInputGlobals.documentReady()) {
                            window.intlTelInputGlobals.loadUtils(this.options.utilsScript);
                        } else {
                            // wait until the load event so we don't block any other requests e.g. the flags image
                            window.addEventListener("load", function() {
                                window.intlTelInputGlobals.loadUtils(_this5.options.utilsScript);
                            });
                        }
                    } else this.resolveUtilsScriptPromise();
                    if (this.options.initialCountry === "auto") this._loadAutoCountry(); else this.resolveAutoCountryPromise();
                }
            }, {
                key: "_loadAutoCountry",
                value: function _loadAutoCountry() {
                    // 3 options:
                    // 1) already loaded (we're done)
                    // 2) not already started loading (start)
                    // 3) already started loading (do nothing - just wait for loading callback to fire)
                    if (window.intlTelInputGlobals.autoCountry) {
                        this.handleAutoCountry();
                    } else if (!window.intlTelInputGlobals.startedLoadingAutoCountry) {
                        // don't do this twice!
                        window.intlTelInputGlobals.startedLoadingAutoCountry = true;
                        if (typeof this.options.geoIpLookup === "function") {
                            this.options.geoIpLookup(function(countryCode) {
                                window.intlTelInputGlobals.autoCountry = countryCode.toLowerCase();
                                // tell all instances the auto country is ready
                                // TODO: this should just be the current instances
                                // UPDATE: use setTimeout in case their geoIpLookup function calls this callback straight
                                // away (e.g. if they have already done the geo ip lookup somewhere else). Using
                                // setTimeout means that the current thread of execution will finish before executing
                                // this, which allows the plugin to finish initialising.
                                setTimeout(function() {
                                    return forEachInstance("handleAutoCountry");
                                });
                            }, function() {
                                return forEachInstance("rejectAutoCountryPromise");
                            });
                        }
                    }
                }
            }, {
                key: "_initKeyListeners",
                value: function _initKeyListeners() {
                    var _this6 = this;
                    // update flag on keyup
                    this._handleKeyupEvent = function() {
                        if (_this6._updateFlagFromNumber(_this6.telInput.value)) {
                            _this6._triggerCountryChange();
                        }
                    };
                    this.telInput.addEventListener("keyup", this._handleKeyupEvent);
                    // update flag on cut/paste events (now supported in all major browsers)
                    this._handleClipboardEvent = function() {
                        // hack because "paste" event is fired before input is updated
                        setTimeout(_this6._handleKeyupEvent);
                    };
                    this.telInput.addEventListener("cut", this._handleClipboardEvent);
                    this.telInput.addEventListener("paste", this._handleClipboardEvent);
                }
            }, {
                key: "_cap",
                value: function _cap(number) {
                    var max = this.telInput.getAttribute("maxlength");
                    return max && number.length > max ? number.substr(0, max) : number;
                }
            }, {
                key: "_initBlurListeners",
                value: function _initBlurListeners() {
                    var _this7 = this;
                    // on blur or form submit: if just a dial code then remove it
                    this._handleSubmitOrBlurEvent = function() {
                        _this7._removeEmptyDialCode();
                    };
                    if (this.telInput.form) this.telInput.form.addEventListener("submit", this._handleSubmitOrBlurEvent);
                    this.telInput.addEventListener("blur", this._handleSubmitOrBlurEvent);
                }
            }, {
                key: "_removeEmptyDialCode",
                value: function _removeEmptyDialCode() {
                    if (this.telInput.value.charAt(0) === "+") {
                        var numeric = this._getNumeric(this.telInput.value);
                        // if just a plus, or if just a dial code
                        if (!numeric || this.selectedCountryData.dialCode === numeric) {
                            this.telInput.value = "";
                        }
                    }
                }
            }, {
                key: "_getNumeric",
                value: function _getNumeric(s) {
                    return s.replace(/\D/g, "");
                }
            }, {
                key: "_trigger",
                value: function _trigger(name) {
                    // have to use old school document.createEvent as IE11 doesn't support `new Event()` syntax
                    var e = document.createEvent("Event");
                    e.initEvent(name, true, true);
                    // can bubble, and is cancellable
                    this.telInput.dispatchEvent(e);
                }
            }, {
                key: "_showDropdown",
                value: function _showDropdown() {
                    this.countryList.classList.remove("iti__hide");
                    this.selectedFlag.setAttribute("aria-expanded", "true");
                    this._setDropdownPosition();
                    // update highlighting and scroll to active list item
                    if (this.activeItem) {
                        this._highlightListItem(this.activeItem, false);
                        this._scrollTo(this.activeItem, true);
                    }
                    // bind all the dropdown-related listeners: mouseover, click, click-off, keydown
                    this._bindDropdownListeners();
                    // update the arrow
                    this.dropdownArrow.classList.add("iti__arrow--up");
                    this._trigger("open:countrydropdown");
                }
            }, {
                key: "_toggleClass",
                value: function _toggleClass(el, className, shouldHaveClass) {
                    if (shouldHaveClass && !el.classList.contains(className)) el.classList.add(className); else if (!shouldHaveClass && el.classList.contains(className)) el.classList.remove(className);
                }
            }, {
                key: "_setDropdownPosition",
                value: function _setDropdownPosition() {
                    var _this8 = this;
                    if (this.options.dropdownContainer) {
                        this.options.dropdownContainer.appendChild(this.dropdown);
                    }
                    if (!this.isMobile) {
                        var pos = this.telInput.getBoundingClientRect();
                        // windowTop from https://stackoverflow.com/a/14384091/217866
                        var windowTop = window.pageYOffset || document.documentElement.scrollTop;
                        var inputTop = pos.top + windowTop;
                        var dropdownHeight = this.countryList.offsetHeight;
                        // dropdownFitsBelow = (dropdownBottom < windowBottom)
                        var dropdownFitsBelow = inputTop + this.telInput.offsetHeight + dropdownHeight < windowTop + window.innerHeight;
                        var dropdownFitsAbove = inputTop - dropdownHeight > windowTop;
                        // by default, the dropdown will be below the input. If we want to position it above the
                        // input, we add the dropup class.
                        this._toggleClass(this.countryList, "iti__country-list--dropup", !dropdownFitsBelow && dropdownFitsAbove);
                        // if dropdownContainer is enabled, calculate postion
                        if (this.options.dropdownContainer) {
                            // by default the dropdown will be directly over the input because it's not in the flow.
                            // If we want to position it below, we need to add some extra top value.
                            var extraTop = !dropdownFitsBelow && dropdownFitsAbove ? 0 : this.telInput.offsetHeight;
                            // calculate placement
                            this.dropdown.style.top = "".concat(inputTop + extraTop, "px");
                            this.dropdown.style.left = "".concat(pos.left + document.body.scrollLeft, "px");
                            // close menu on window scroll
                            this._handleWindowScroll = function() {
                                return _this8._closeDropdown();
                            };
                            window.addEventListener("scroll", this._handleWindowScroll);
                        }
                    }
                }
            }, {
                key: "_getClosestListItem",
                value: function _getClosestListItem(target) {
                    var el = target;
                    while (el && el !== this.countryList && !el.classList.contains("iti__country")) {
                        el = el.parentNode;
                    }
                    // if we reached the countryList element, then return null
                    return el === this.countryList ? null : el;
                }
            }, {
                key: "_bindDropdownListeners",
                value: function _bindDropdownListeners() {
                    var _this9 = this;
                    // when mouse over a list item, just highlight that one
                    // we add the class "highlight", so if they hit "enter" we know which one to select
                    this._handleMouseoverCountryList = function(e) {
                        // handle event delegation, as we're listening for this event on the countryList
                        var listItem = _this9._getClosestListItem(e.target);
                        if (listItem) _this9._highlightListItem(listItem, false);
                    };
                    this.countryList.addEventListener("mouseover", this._handleMouseoverCountryList);
                    // listen for country selection
                    this._handleClickCountryList = function(e) {
                        var listItem = _this9._getClosestListItem(e.target);
                        if (listItem) _this9._selectListItem(listItem);
                    };
                    this.countryList.addEventListener("click", this._handleClickCountryList);
                    // click off to close
                    // (except when this initial opening click is bubbling up)
                    // we cannot just stopPropagation as it may be needed to close another instance
                    var isOpening = true;
                    this._handleClickOffToClose = function() {
                        if (!isOpening) _this9._closeDropdown();
                        isOpening = false;
                    };
                    document.documentElement.addEventListener("click", this._handleClickOffToClose);
                    // listen for up/down scrolling, enter to select, or letters to jump to country name.
                    // use keydown as keypress doesn't fire for non-char keys and we want to catch if they
                    // just hit down and hold it to scroll down (no keyup event).
                    // listen on the document because that's where key events are triggered if no input has focus
                    var query = "";
                    var queryTimer = null;
                    this._handleKeydownOnDropdown = function(e) {
                        // prevent down key from scrolling the whole page,
                        // and enter key from submitting a form etc
                        e.preventDefault();
                        // up and down to navigate
                        if (e.key === "ArrowUp" || e.key === "Up" || e.key === "ArrowDown" || e.key === "Down") _this9._handleUpDownKey(e.key); else if (e.key === "Enter") _this9._handleEnterKey(); else if (e.key === "Escape") _this9._closeDropdown(); else if (/^[a-zA-ZÀ-ÿа-яА-Я ]$/.test(e.key)) {
                            // jump to countries that start with the query string
                            if (queryTimer) clearTimeout(queryTimer);
                            query += e.key.toLowerCase();
                            _this9._searchForCountry(query);
                            // if the timer hits 1 second, reset the query
                            queryTimer = setTimeout(function() {
                                query = "";
                            }, 1e3);
                        }
                    };
                    document.addEventListener("keydown", this._handleKeydownOnDropdown);
                }
            }, {
                key: "_handleUpDownKey",
                value: function _handleUpDownKey(key) {
                    var next = key === "ArrowUp" || key === "Up" ? this.highlightedItem.previousElementSibling : this.highlightedItem.nextElementSibling;
                    if (next) {
                        // skip the divider
                        if (next.classList.contains("iti__divider")) {
                            next = key === "ArrowUp" || key === "Up" ? next.previousElementSibling : next.nextElementSibling;
                        }
                        this._highlightListItem(next, true);
                    }
                }
            }, {
                key: "_handleEnterKey",
                value: function _handleEnterKey() {
                    if (this.highlightedItem) this._selectListItem(this.highlightedItem);
                }
            }, {
                key: "_searchForCountry",
                value: function _searchForCountry(query) {
                    for (var i = 0; i < this.countries.length; i++) {
                        if (this._startsWith(this.countries[i].name, query)) {
                            var listItem = this.countryList.querySelector("#iti-".concat(this.id, "__item-").concat(this.countries[i].iso2));
                            // update highlighting and scroll
                            this._highlightListItem(listItem, false);
                            this._scrollTo(listItem, true);
                            break;
                        }
                    }
                }
            }, {
                key: "_startsWith",
                value: function _startsWith(a, b) {
                    return a.substr(0, b.length).toLowerCase() === b;
                }
            }, {
                key: "_updateValFromNumber",
                value: function _updateValFromNumber(originalNumber) {
                    var number = originalNumber;
                    if (this.options.formatOnDisplay && window.intlTelInputUtils && this.selectedCountryData) {
                        var useNational = !this.options.separateDialCode && (this.options.nationalMode || number.charAt(0) !== "+");
                        var _intlTelInputUtils$nu = intlTelInputUtils.numberFormat, NATIONAL = _intlTelInputUtils$nu.NATIONAL, INTERNATIONAL = _intlTelInputUtils$nu.INTERNATIONAL;
                        var format = useNational ? NATIONAL : INTERNATIONAL;
                        number = intlTelInputUtils.formatNumber(number, this.selectedCountryData.iso2, format);
                    }
                    number = this._beforeSetNumber(number);
                    this.telInput.value = number;
                }
            }, {
                key: "_updateFlagFromNumber",
                value: function _updateFlagFromNumber(originalNumber) {
                    // if we're in nationalMode and we already have US/Canada selected, make sure the number starts
                    // with a +1 so _getDialCode will be able to extract the area code
                    // update: if we dont yet have selectedCountryData, but we're here (trying to update the flag
                    // from the number), that means we're initialising the plugin with a number that already has a
                    // dial code, so fine to ignore this bit
                    var number = originalNumber;
                    var selectedDialCode = this.selectedCountryData.dialCode;
                    var isNanp = selectedDialCode === "1";
                    if (number && this.options.nationalMode && isNanp && number.charAt(0) !== "+") {
                        if (number.charAt(0) !== "1") number = "1".concat(number);
                        number = "+".concat(number);
                    }
                    // update flag if user types area code for another country
                    if (this.options.separateDialCode && selectedDialCode && number.charAt(0) !== "+") {
                        number = "+".concat(selectedDialCode).concat(number);
                    }
                    // try and extract valid dial code from input
                    var dialCode = this._getDialCode(number, true);
                    var numeric = this._getNumeric(number);
                    var countryCode = null;
                    if (dialCode) {
                        var countryCodes = this.countryCodes[this._getNumeric(dialCode)];
                        // check if the right country is already selected. this should be false if the number is
                        // longer than the matched dial code because in this case we need to make sure that if
                        // there are multiple country matches, that the first one is selected (note: we could
                        // just check that here, but it requires the same loop that we already have later)
                        var alreadySelected = countryCodes.indexOf(this.selectedCountryData.iso2) !== -1 && numeric.length <= dialCode.length - 1;
                        var isRegionlessNanpNumber = selectedDialCode === "1" && this._isRegionlessNanp(numeric);
                        // only update the flag if:
                        // A) NOT (we currently have a NANP flag selected, and the number is a regionlessNanp)
                        // AND
                        // B) the right country is not already selected
                        if (!isRegionlessNanpNumber && !alreadySelected) {
                            // if using onlyCountries option, countryCodes[0] may be empty, so we must find the first
                            // non-empty index
                            for (var j = 0; j < countryCodes.length; j++) {
                                if (countryCodes[j]) {
                                    countryCode = countryCodes[j];
                                    break;
                                }
                            }
                        }
                    } else if (number.charAt(0) === "+" && numeric.length) {
                        // invalid dial code, so empty
                        // Note: use getNumeric here because the number has not been formatted yet, so could contain
                        // bad chars
                        countryCode = "";
                    } else if (!number || number === "+") {
                        // empty, or just a plus, so default
                        countryCode = this.defaultCountry;
                    }
                    if (countryCode !== null) {
                        return this._setFlag(countryCode);
                    }
                    return false;
                }
            }, {
                key: "_isRegionlessNanp",
                value: function _isRegionlessNanp(number) {
                    var numeric = this._getNumeric(number);
                    if (numeric.charAt(0) === "1") {
                        var areaCode = numeric.substr(1, 3);
                        return regionlessNanpNumbers.indexOf(areaCode) !== -1;
                    }
                    return false;
                }
            }, {
                key: "_highlightListItem",
                value: function _highlightListItem(listItem, shouldFocus) {
                    var prevItem = this.highlightedItem;
                    if (prevItem) prevItem.classList.remove("iti__highlight");
                    this.highlightedItem = listItem;
                    this.highlightedItem.classList.add("iti__highlight");
                    if (shouldFocus) this.highlightedItem.focus();
                }
            }, {
                key: "_getCountryData",
                value: function _getCountryData(countryCode, ignoreOnlyCountriesOption, allowFail) {
                    var countryList = ignoreOnlyCountriesOption ? allCountries : this.countries;
                    for (var i = 0; i < countryList.length; i++) {
                        if (countryList[i].iso2 === countryCode) {
                            return countryList[i];
                        }
                    }
                    if (allowFail) {
                        return null;
                    }
                    throw new Error("No country data for '".concat(countryCode, "'"));
                }
            }, {
                key: "_setFlag",
                value: function _setFlag(countryCode) {
                    var prevCountry = this.selectedCountryData.iso2 ? this.selectedCountryData : {};
                    // do this first as it will throw an error and stop if countryCode is invalid
                    this.selectedCountryData = countryCode ? this._getCountryData(countryCode, false, false) : {};
                    // update the defaultCountry - we only need the iso2 from now on, so just store that
                    if (this.selectedCountryData.iso2) {
                        this.defaultCountry = this.selectedCountryData.iso2;
                    }
                    this.selectedFlagInner.setAttribute("class", "iti__flag iti__".concat(countryCode));
                    // update the selected country's title attribute
                    var title = countryCode ? "".concat(this.selectedCountryData.name, ": +").concat(this.selectedCountryData.dialCode) : "Unknown";
                    this.selectedFlag.setAttribute("title", title);
                    if (this.options.separateDialCode) {
                        var dialCode = this.selectedCountryData.dialCode ? "+".concat(this.selectedCountryData.dialCode) : "";
                        this.selectedDialCode.innerHTML = dialCode;
                        // offsetWidth is zero if input is in a hidden container during initialisation
                        var selectedFlagWidth = this.selectedFlag.offsetWidth || this._getHiddenSelectedFlagWidth();
                        // add 6px of padding after the grey selected-dial-code box, as this is what we use in the css
                        this.telInput.style.paddingLeft = "".concat(selectedFlagWidth + 6, "px");
                    }
                    // and the input's placeholder
                    this._updatePlaceholder();
                    // update the active list item
                    if (this.options.allowDropdown) {
                        var prevItem = this.activeItem;
                        if (prevItem) {
                            prevItem.classList.remove("iti__active");
                            prevItem.setAttribute("aria-selected", "false");
                        }
                        if (countryCode) {
                            // check if there is a preferred item first, else fall back to standard
                            var nextItem = this.countryList.querySelector("#iti-".concat(this.id, "__item-").concat(countryCode, "-preferred")) || this.countryList.querySelector("#iti-".concat(this.id, "__item-").concat(countryCode));
                            nextItem.setAttribute("aria-selected", "true");
                            nextItem.classList.add("iti__active");
                            this.activeItem = nextItem;
                            this.selectedFlag.setAttribute("aria-activedescendant", nextItem.getAttribute("id"));
                        }
                    }
                    // return if the flag has changed or not
                    return prevCountry.iso2 !== countryCode;
                }
            }, {
                key: "_getHiddenSelectedFlagWidth",
                value: function _getHiddenSelectedFlagWidth() {
                    // to get the right styling to apply, all we need is a shallow clone of the container,
                    // and then to inject a deep clone of the selectedFlag element
                    var containerClone = this.telInput.parentNode.cloneNode();
                    containerClone.style.visibility = "hidden";
                    document.body.appendChild(containerClone);
                    var flagsContainerClone = this.flagsContainer.cloneNode();
                    containerClone.appendChild(flagsContainerClone);
                    var selectedFlagClone = this.selectedFlag.cloneNode(true);
                    flagsContainerClone.appendChild(selectedFlagClone);
                    var width = selectedFlagClone.offsetWidth;
                    containerClone.parentNode.removeChild(containerClone);
                    return width;
                }
            }, {
                key: "_updatePlaceholder",
                value: function _updatePlaceholder() {
                    var shouldSetPlaceholder = this.options.autoPlaceholder === "aggressive" || !this.hadInitialPlaceholder && this.options.autoPlaceholder === "polite";
                    if (window.intlTelInputUtils && shouldSetPlaceholder) {
                        var numberType = intlTelInputUtils.numberType[this.options.placeholderNumberType];
                        var placeholder = this.selectedCountryData.iso2 ? intlTelInputUtils.getExampleNumber(this.selectedCountryData.iso2, this.options.nationalMode, numberType) : "";
                        placeholder = this._beforeSetNumber(placeholder);
                        if (typeof this.options.customPlaceholder === "function") {
                            placeholder = this.options.customPlaceholder(placeholder, this.selectedCountryData);
                        }
                        this.telInput.setAttribute("placeholder", placeholder);
                    }
                }
            }, {
                key: "_selectListItem",
                value: function _selectListItem(listItem) {
                    // update selected flag and active list item
                    var flagChanged = this._setFlag(listItem.getAttribute("data-country-code"));
                    this._closeDropdown();
                    this._updateDialCode(listItem.getAttribute("data-dial-code"), true);
                    // focus the input
                    this.telInput.focus();
                    // put cursor at end - this fix is required for FF and IE11 (with nationalMode=false i.e. auto
                    // inserting dial code), who try to put the cursor at the beginning the first time
                    var len = this.telInput.value.length;
                    this.telInput.setSelectionRange(len, len);
                    if (flagChanged) {
                        this._triggerCountryChange();
                    }
                }
            }, {
                key: "_closeDropdown",
                value: function _closeDropdown() {
                    this.countryList.classList.add("iti__hide");
                    this.selectedFlag.setAttribute("aria-expanded", "false");
                    // update the arrow
                    this.dropdownArrow.classList.remove("iti__arrow--up");
                    // unbind key events
                    document.removeEventListener("keydown", this._handleKeydownOnDropdown);
                    document.documentElement.removeEventListener("click", this._handleClickOffToClose);
                    this.countryList.removeEventListener("mouseover", this._handleMouseoverCountryList);
                    this.countryList.removeEventListener("click", this._handleClickCountryList);
                    // remove menu from container
                    if (this.options.dropdownContainer) {
                        if (!this.isMobile) window.removeEventListener("scroll", this._handleWindowScroll);
                        if (this.dropdown.parentNode) this.dropdown.parentNode.removeChild(this.dropdown);
                    }
                    this._trigger("close:countrydropdown");
                }
            }, {
                key: "_scrollTo",
                value: function _scrollTo(element, middle) {
                    var container = this.countryList;
                    // windowTop from https://stackoverflow.com/a/14384091/217866
                    var windowTop = window.pageYOffset || document.documentElement.scrollTop;
                    var containerHeight = container.offsetHeight;
                    var containerTop = container.getBoundingClientRect().top + windowTop;
                    var containerBottom = containerTop + containerHeight;
                    var elementHeight = element.offsetHeight;
                    var elementTop = element.getBoundingClientRect().top + windowTop;
                    var elementBottom = elementTop + elementHeight;
                    var newScrollTop = elementTop - containerTop + container.scrollTop;
                    var middleOffset = containerHeight / 2 - elementHeight / 2;
                    if (elementTop < containerTop) {
                        // scroll up
                        if (middle) newScrollTop -= middleOffset;
                        container.scrollTop = newScrollTop;
                    } else if (elementBottom > containerBottom) {
                        // scroll down
                        if (middle) newScrollTop += middleOffset;
                        var heightDifference = containerHeight - elementHeight;
                        container.scrollTop = newScrollTop - heightDifference;
                    }
                }
            }, {
                key: "_updateDialCode",
                value: function _updateDialCode(newDialCodeBare, hasSelectedListItem) {
                    var inputVal = this.telInput.value;
                    // save having to pass this every time
                    var newDialCode = "+".concat(newDialCodeBare);
                    var newNumber;
                    if (inputVal.charAt(0) === "+") {
                        // there's a plus so we're dealing with a replacement (doesn't matter if nationalMode or not)
                        var prevDialCode = this._getDialCode(inputVal);
                        if (prevDialCode) {
                            // current number contains a valid dial code, so replace it
                            newNumber = inputVal.replace(prevDialCode, newDialCode);
                        } else {
                            // current number contains an invalid dial code, so ditch it
                            // (no way to determine where the invalid dial code ends and the rest of the number begins)
                            newNumber = newDialCode;
                        }
                    } else if (this.options.nationalMode || this.options.separateDialCode) {
                        // don't do anything
                        return;
                    } else {
                        // nationalMode is disabled
                        if (inputVal) {
                            // there is an existing value with no dial code: prefix the new dial code
                            newNumber = newDialCode + inputVal;
                        } else if (hasSelectedListItem || !this.options.autoHideDialCode) {
                            // no existing value and either they've just selected a list item, or autoHideDialCode is
                            // disabled: insert new dial code
                            newNumber = newDialCode;
                        } else {
                            return;
                        }
                    }
                    this.telInput.value = newNumber;
                }
            }, {
                key: "_getDialCode",
                value: function _getDialCode(number, includeAreaCode) {
                    var dialCode = "";
                    // only interested in international numbers (starting with a plus)
                    if (number.charAt(0) === "+") {
                        var numericChars = "";
                        // iterate over chars
                        for (var i = 0; i < number.length; i++) {
                            var c = number.charAt(i);
                            // if char is number (https://stackoverflow.com/a/8935649/217866)
                            if (!isNaN(parseInt(c, 10))) {
                                numericChars += c;
                                // if current numericChars make a valid dial code
                                if (includeAreaCode) {
                                    if (this.countryCodes[numericChars]) {
                                        // store the actual raw string (useful for matching later)
                                        dialCode = number.substr(0, i + 1);
                                    }
                                } else {
                                    if (this.dialCodes[numericChars]) {
                                        dialCode = number.substr(0, i + 1);
                                        // if we're just looking for a dial code, we can break as soon as we find one
                                        break;
                                    }
                                }
                                // stop searching as soon as we can - in this case when we hit max len
                                if (numericChars.length === this.countryCodeMaxLen) {
                                    break;
                                }
                            }
                        }
                    }
                    return dialCode;
                }
            }, {
                key: "_getFullNumber",
                value: function _getFullNumber() {
                    var val = this.telInput.value.trim();
                    var dialCode = this.selectedCountryData.dialCode;
                    var prefix;
                    var numericVal = this._getNumeric(val);
                    if (this.options.separateDialCode && val.charAt(0) !== "+" && dialCode && numericVal) {
                        // when using separateDialCode, it is visible so is effectively part of the typed number
                        prefix = "+".concat(dialCode);
                    } else {
                        prefix = "";
                    }
                    return prefix + val;
                }
            }, {
                key: "_beforeSetNumber",
                value: function _beforeSetNumber(originalNumber) {
                    var number = originalNumber;
                    if (this.options.separateDialCode) {
                        var dialCode = this._getDialCode(number);
                        // if there is a valid dial code
                        if (dialCode) {
                            // in case _getDialCode returned an area code as well
                            dialCode = "+".concat(this.selectedCountryData.dialCode);
                            // a lot of numbers will have a space separating the dial code and the main number, and
                            // some NANP numbers will have a hyphen e.g. +1 684-733-1234 - in both cases we want to get
                            // rid of it
                            // NOTE: don't just trim all non-numerics as may want to preserve an open parenthesis etc
                            var start = number[dialCode.length] === " " || number[dialCode.length] === "-" ? dialCode.length + 1 : dialCode.length;
                            number = number.substr(start);
                        }
                    }
                    return this._cap(number);
                }
            }, {
                key: "_triggerCountryChange",
                value: function _triggerCountryChange() {
                    this._trigger("countrychange");
                }
            }, {
                key: "handleAutoCountry",
                value: function handleAutoCountry() {
                    if (this.options.initialCountry === "auto") {
                        // we must set this even if there is an initial val in the input: in case the initial val is
                        // invalid and they delete it - they should see their auto country
                        this.defaultCountry = window.intlTelInputGlobals.autoCountry;
                        // if there's no initial value in the input, then update the flag
                        if (!this.telInput.value) {
                            this.setCountry(this.defaultCountry);
                        }
                        this.resolveAutoCountryPromise();
                    }
                }
            }, {
                key: "handleUtils",
                value: function handleUtils() {
                    // if the request was successful
                    if (window.intlTelInputUtils) {
                        // if there's an initial value in the input, then format it
                        if (this.telInput.value) {
                            this._updateValFromNumber(this.telInput.value);
                        }
                        this._updatePlaceholder();
                    }
                    this.resolveUtilsScriptPromise();
                }
            }, {
                key: "destroy",
                value: function destroy() {
                    var form = this.telInput.form;
                    if (this.options.allowDropdown) {
                        // make sure the dropdown is closed (and unbind listeners)
                        this._closeDropdown();
                        this.selectedFlag.removeEventListener("click", this._handleClickSelectedFlag);
                        this.flagsContainer.removeEventListener("keydown", this._handleFlagsContainerKeydown);
                        // label click hack
                        var label = this._getClosestLabel();
                        if (label) label.removeEventListener("click", this._handleLabelClick);
                    }
                    // unbind hiddenInput listeners
                    if (this.hiddenInput && form) form.removeEventListener("submit", this._handleHiddenInputSubmit);
                    // unbind autoHideDialCode listeners
                    if (this.options.autoHideDialCode) {
                        if (form) form.removeEventListener("submit", this._handleSubmitOrBlurEvent);
                        this.telInput.removeEventListener("blur", this._handleSubmitOrBlurEvent);
                    }
                    // unbind key events, and cut/paste events
                    this.telInput.removeEventListener("keyup", this._handleKeyupEvent);
                    this.telInput.removeEventListener("cut", this._handleClipboardEvent);
                    this.telInput.removeEventListener("paste", this._handleClipboardEvent);
                    // remove attribute of id instance: data-intl-tel-input-id
                    this.telInput.removeAttribute("data-intl-tel-input-id");
                    // remove markup (but leave the original input)
                    var wrapper = this.telInput.parentNode;
                    wrapper.parentNode.insertBefore(this.telInput, wrapper);
                    wrapper.parentNode.removeChild(wrapper);
                    delete window.intlTelInputGlobals.instances[this.id];
                }
            }, {
                key: "getExtension",
                value: function getExtension() {
                    if (window.intlTelInputUtils) {
                        return intlTelInputUtils.getExtension(this._getFullNumber(), this.selectedCountryData.iso2);
                    }
                    return "";
                }
            }, {
                key: "getNumber",
                value: function getNumber(format) {
                    if (window.intlTelInputUtils) {
                        var iso2 = this.selectedCountryData.iso2;
                        return intlTelInputUtils.formatNumber(this._getFullNumber(), iso2, format);
                    }
                    return "";
                }
            }, {
                key: "getNumberType",
                value: function getNumberType() {
                    if (window.intlTelInputUtils) {
                        return intlTelInputUtils.getNumberType(this._getFullNumber(), this.selectedCountryData.iso2);
                    }
                    return -99;
                }
            }, {
                key: "getSelectedCountryData",
                value: function getSelectedCountryData() {
                    return this.selectedCountryData;
                }
            }, {
                key: "getValidationError",
                value: function getValidationError() {
                    if (window.intlTelInputUtils) {
                        var iso2 = this.selectedCountryData.iso2;
                        return intlTelInputUtils.getValidationError(this._getFullNumber(), iso2);
                    }
                    return -99;
                }
            }, {
                key: "isValidNumber",
                value: function isValidNumber() {
                    var val = this._getFullNumber().trim();
                    var countryCode = this.options.nationalMode ? this.selectedCountryData.iso2 : "";
                    return window.intlTelInputUtils ? intlTelInputUtils.isValidNumber(val, countryCode) : null;
                }
            }, {
                key: "setCountry",
                value: function setCountry(originalCountryCode) {
                    var countryCode = originalCountryCode.toLowerCase();
                    // check if already selected
                    if (!this.selectedFlagInner.classList.contains("iti__".concat(countryCode))) {
                        this._setFlag(countryCode);
                        this._updateDialCode(this.selectedCountryData.dialCode, false);
                        this._triggerCountryChange();
                    }
                }
            }, {
                key: "setNumber",
                value: function setNumber(number) {
                    // we must update the flag first, which updates this.selectedCountryData, which is used for
                    // formatting the number before displaying it
                    var flagChanged = this._updateFlagFromNumber(number);
                    this._updateValFromNumber(number);
                    if (flagChanged) {
                        this._triggerCountryChange();
                    }
                }
            }, {
                key: "setPlaceholderNumberType",
                value: function setPlaceholderNumberType(type) {
                    this.options.placeholderNumberType = type;
                    this._updatePlaceholder();
                }
            } ]);
            return Iti;
        }();
        /********************
 *  STATIC METHODS
 ********************/
        // get the country data object
        intlTelInputGlobals.getCountryData = function() {
            return allCountries;
        };
        // inject a <script> element to load utils.js
        var injectScript = function injectScript(path, handleSuccess, handleFailure) {
            // inject a new script element into the page
            var script = document.createElement("script");
            script.onload = function() {
                forEachInstance("handleUtils");
                if (handleSuccess) handleSuccess();
            };
            script.onerror = function() {
                forEachInstance("rejectUtilsScriptPromise");
                if (handleFailure) handleFailure();
            };
            script.className = "iti-load-utils";
            script.async = true;
            script.src = path;
            document.body.appendChild(script);
        };
        // load the utils script
        intlTelInputGlobals.loadUtils = function(path) {
            // 2 options:
            // 1) not already started loading (start)
            // 2) already started loading (do nothing - just wait for the onload callback to fire, which will
            // trigger handleUtils on all instances, invoking their resolveUtilsScriptPromise functions)
            if (!window.intlTelInputUtils && !window.intlTelInputGlobals.startedLoadingUtilsScript) {
                // only do this once
                window.intlTelInputGlobals.startedLoadingUtilsScript = true;
                // if we have promises, then return a promise
                if (typeof Promise !== "undefined") {
                    return new Promise(function(resolve, reject) {
                        return injectScript(path, resolve, reject);
                    });
                }
                injectScript(path);
            }
            return null;
        };
        // default options
        intlTelInputGlobals.defaults = defaults;
        // version
        intlTelInputGlobals.version = "17.0.19";
        // convenience wrapper
        return function(input, options) {
            var iti = new Iti(input, options);
            iti._init();
            input.setAttribute("data-intl-tel-input-id", iti.id);
            window.intlTelInputGlobals.instances[iti.id] = iti;
            return iti;
        };
    }();
});

/***/ }),

/***/ 583:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

/**
 * Exposing intl-tel-input as a component
 */
module.exports = __webpack_require__(51);


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be in strict mode.
(() => {
"use strict";

;// CONCATENATED MODULE: external "React"
const external_React_namespaceObject = React;
var external_React_default = /*#__PURE__*/__webpack_require__.n(external_React_namespaceObject);
;// CONCATENATED MODULE: external "ReactDOM"
const external_ReactDOM_namespaceObject = ReactDOM;
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/api.js
function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var ReferenceWidgetAPI = /*#__PURE__*/function () {
  function ReferenceWidgetAPI(props) {
    _classCallCheck(this, ReferenceWidgetAPI);

    console.debug("ReferenceWidgetAPI::constructor");
    this.api_url = props.api_url;

    this.on_api_error = props.on_api_error || function (response) {};

    return this;
  }

  _createClass(ReferenceWidgetAPI, [{
    key: "get_api_url",
    value: function get_api_url(endpoint) {
      return "".concat(this.api_url, "/").concat(endpoint, "#").concat(location.search);
    }
    /*
     * Fetch Ajax API resource from the server
     *
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
     */

  }, {
    key: "get_json",
    value: function get_json(endpoint, options) {
      var data, init, method, on_api_error, request, url;

      if (options == null) {
        options = {};
      }

      method = options.method || "POST";
      data = JSON.stringify(options.data) || "{}";
      on_api_error = this.on_api_error;
      url = this.get_api_url(endpoint);
      init = {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": this.get_csrf_token()
        },
        body: method === "POST" ? data : null,
        credentials: "include"
      };
      console.info("ReferenceWidgetAPI::fetch:endpoint=" + endpoint + " init=", init);
      request = new Request(url, init);
      return fetch(request).then(function (response) {
        if (!response.ok) {
          return Promise.reject(response);
        }

        return response;
      }).then(function (response) {
        return response.json();
      })["catch"](function (response) {
        on_api_error(response);
        return response;
      });
    }
  }, {
    key: "search",
    value: function search(catalog, query, params) {
      params = params || {};
      var url = "search?catalog=".concat(catalog);

      var _loop = function _loop() {
        var _Object$entries$_i = _slicedToArray(_Object$entries[_i], 2),
            key = _Object$entries$_i[0],
            value = _Object$entries$_i[1];

        // handle arrays as repeating parameters
        if (Array.isArray(value)) {
          value.forEach(function (item) {
            url += "&".concat(key, "=").concat(item);
          });
          return "continue";
        } // workaround for path queries


        if (key == "path") {
          value = value.query || null;

          if (value.depth !== null) {
            url += "&depth=".concat(value.depth);
          }
        }

        if (value) {
          url += "&".concat(key, "=").concat(value);
        }
      };

      for (var _i = 0, _Object$entries = Object.entries(query); _i < _Object$entries.length; _i++) {
        var _ret = _loop();

        if (_ret === "continue") continue;
      }

      for (var _i2 = 0, _Object$entries2 = Object.entries(params); _i2 < _Object$entries2.length; _i2++) {
        var _Object$entries2$_i = _slicedToArray(_Object$entries2[_i2], 2),
            key = _Object$entries2$_i[0],
            value = _Object$entries2$_i[1];

        url += "&".concat(key, "=").concat(value);
      }

      console.debug("ReferenceWidgetAPI::search:url=", url);
      return this.get_json(url, {
        method: "GET"
      });
    }
    /*
     * Get the plone.protect CSRF token
     * Note: The fields won't save w/o that token set
     */

  }, {
    key: "get_csrf_token",
    value: function get_csrf_token() {
      return document.querySelector("#protect-script").dataset.token;
    }
  }]);

  return ReferenceWidgetAPI;
}();

/* harmony default export */ const api = (ReferenceWidgetAPI);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/ReferenceField.js
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function ReferenceField_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ReferenceField_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function ReferenceField_createClass(Constructor, protoProps, staticProps) { if (protoProps) ReferenceField_defineProperties(Constructor.prototype, protoProps); if (staticProps) ReferenceField_defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { var hasNativeReflectConstruct = _isNativeReflectConstruct(); return function _createSuperInternal() { var Super = _getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }




var ReferenceField = /*#__PURE__*/function (_React$Component) {
  _inherits(ReferenceField, _React$Component);

  var _super = _createSuper(ReferenceField);

  function ReferenceField(props) {
    var _this;

    ReferenceField_classCallCheck(this, ReferenceField);

    _this = _super.call(this, props);
    _this.state = {}; // React reference to the input field
    // https://reactjs.org/docs/react-api.html#reactcreateref

    _this.input_field_ref = /*#__PURE__*/external_React_default().createRef(); // bind event handlers

    _this.on_focus = _this.on_focus.bind(_assertThisInitialized(_this));
    _this.on_blur = _this.on_blur.bind(_assertThisInitialized(_this));
    _this.on_change = _this.on_change.bind(_assertThisInitialized(_this));
    _this.on_keydown = _this.on_keydown.bind(_assertThisInitialized(_this));
    _this.on_keypress = _this.on_keypress.bind(_assertThisInitialized(_this));
    _this.on_clear_click = _this.on_clear_click.bind(_assertThisInitialized(_this));
    _this.on_search_click = _this.on_search_click.bind(_assertThisInitialized(_this));
    return _this;
  }
  /*
   * Returns the search value from the input field
   */


  ReferenceField_createClass(ReferenceField, [{
    key: "get_search_value",
    value: function get_search_value() {
      return this.input_field_ref.current.value;
    }
    /*
     * Handler when the search field get focused
     */

  }, {
    key: "on_focus",
    value: function on_focus(event) {
      console.debug("ReferenceField::on_focus");

      if (this.props.on_focus) {
        var value = this.get_search_value() || null;
        this.props.on_focus(value);
      }
    }
    /*
     * Handler when the search field lost focus
     */

  }, {
    key: "on_blur",
    value: function on_blur(event) {
      console.debug("ReferenceField::on_blur");

      if (this.props.on_blur) {
        var value = this.get_search_value();
        this.props.on_blur(value);
      }
    }
    /*
     * Handler when the search value changed
     */

  }, {
    key: "on_change",
    value: function on_change(event) {
      event.preventDefault();
      var value = this.get_search_value();
      console.debug("ReferenceField::on_change:value: ", value);

      if (this.props.on_search) {
        this.props.on_search(value);
      }
    }
    /*
     * Handler for keydown events in the search field
     *
     */

  }, {
    key: "on_keydown",
    value: function on_keydown(event) {
      // backspace
      if (event.which == 8) {
        if (this.get_search_value() == "") {
          this.props.on_clear();
        }
      } // down arrow


      if (event.which == 40) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("down");
        }
      } // up arrow


      if (event.which == 38) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("up");
        }
      } // left arrow


      if (event.which == 37) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("left");
        }
      } // right arrow


      if (event.which == 39) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("right");
        }
      }
    }
    /*
     * Handler for keypress events in the search field
     *
     */

  }, {
    key: "on_keypress",
    value: function on_keypress(event) {
      if (event.which == 13) {
        console.debug("ReferenceField::on_keypress:ENTER"); // prevent form submission when clicking ENTER

        event.preventDefault();

        if (this.props.on_enter) {
          this.props.on_enter();
        }
      }
    }
  }, {
    key: "on_clear_click",
    value: function on_clear_click(event) {
      event.preventDefault();

      if (this.props.on_clear) {
        var value = this.get_search_value();
        this.props.on_clear(value); // clear the input field

        this.input_field_ref.current.value = "";
      }
    }
  }, {
    key: "on_search_click",
    value: function on_search_click(event) {
      event.preventDefault();

      if (this.props.on_search) {
        var value = this.get_search_value();
        this.props.on_search(value);
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget-search-field"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        className: "input-group"
      }, /*#__PURE__*/external_React_default().createElement("input", _defineProperty({
        type: "text",
        name: this.props.name,
        className: this.props.className,
        ref: this.input_field_ref,
        disabled: this.props.disabled,
        onKeyDown: this.on_keydown,
        onKeyPress: this.on_keypress,
        onChange: this.on_change,
        onFocus: this.on_focus,
        onBlur: this.on_blur,
        placeholder: this.props.placeholder,
        style: {
          maxWidth: "160px"
        }
      }, "disabled", this.props.disabled)), /*#__PURE__*/external_React_default().createElement("div", {
        "class": "input-group-append"
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-outline-secondary",
        disabled: this.props.disabled,
        onClick: this.on_clear_click
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-times"
      })), /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-outline-primary",
        disabled: this.props.disabled,
        onClick: this.on_search_click
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-search"
      })))));
    }
  }]);

  return ReferenceField;
}((external_React_default()).Component);

/* harmony default export */ const components_ReferenceField = (ReferenceField);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/ReferenceResults.js
function ReferenceResults_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ReferenceResults_typeof = function _typeof(obj) { return typeof obj; }; } else { ReferenceResults_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ReferenceResults_typeof(obj); }

function _createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = ReferenceResults_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function ReferenceResults_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ReferenceResults_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ReferenceResults_arrayLikeToArray(o, minLen); }

function ReferenceResults_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ReferenceResults_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ReferenceResults_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function ReferenceResults_createClass(Constructor, protoProps, staticProps) { if (protoProps) ReferenceResults_defineProperties(Constructor.prototype, protoProps); if (staticProps) ReferenceResults_defineProperties(Constructor, staticProps); return Constructor; }

function ReferenceResults_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ReferenceResults_setPrototypeOf(subClass, superClass); }

function ReferenceResults_setPrototypeOf(o, p) { ReferenceResults_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ReferenceResults_setPrototypeOf(o, p); }

function ReferenceResults_createSuper(Derived) { var hasNativeReflectConstruct = ReferenceResults_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = ReferenceResults_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = ReferenceResults_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ReferenceResults_possibleConstructorReturn(this, result); }; }

function ReferenceResults_possibleConstructorReturn(self, call) { if (call && (ReferenceResults_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return ReferenceResults_assertThisInitialized(self); }

function ReferenceResults_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ReferenceResults_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function ReferenceResults_getPrototypeOf(o) { ReferenceResults_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ReferenceResults_getPrototypeOf(o); }




var ReferenceResults = /*#__PURE__*/function (_React$Component) {
  ReferenceResults_inherits(ReferenceResults, _React$Component);

  var _super = ReferenceResults_createSuper(ReferenceResults);

  function ReferenceResults(props) {
    var _this;

    ReferenceResults_classCallCheck(this, ReferenceResults);

    _this = _super.call(this, props); // bind event handlers

    _this.on_select = _this.on_select.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_page = _this.on_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_prev_page = _this.on_prev_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_next_page = _this.on_next_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_close = _this.on_close.bind(ReferenceResults_assertThisInitialized(_this));
    return _this;
  }
  /*
   * Return the header columns config
   *
   * @returns {Array} of column config objects
   */


  ReferenceResults_createClass(ReferenceResults, [{
    key: "get_columns",
    value: function get_columns() {
      return this.props.columns || [];
    }
    /*
     * Return only the (field-)names of the columns config
     *
     * @returns {Array} of column names
     */

  }, {
    key: "get_column_names",
    value: function get_column_names() {
      var columns = this.get_columns();
      return columns.map(function (column) {
        return column.name;
      });
    }
    /*
     * Return only the labels of the columns config
     *
     * @returns {Array} of column labels
     */

  }, {
    key: "get_column_labels",
    value: function get_column_labels() {
      var columns = this.get_columns();
      return columns.map(function (column) {
        return column.label;
      });
    }
    /*
     * Return the search results
     *
     * @returns {Array} of result objects (items of `senaite.jsonapi` response)
     */

  }, {
    key: "get_results",
    value: function get_results() {
      return this.props.results || [];
    }
    /*
     * Checks if results are available
     *
     * @returns {Boolean} true if there are results, false otherwise
     */

  }, {
    key: "has_results",
    value: function has_results() {
      return this.get_results().length > 0;
    }
    /*
     * Returns the style object for the dropdown table
     *
     * @returns {Object} of ReactJS CSS styles
     */

  }, {
    key: "get_style",
    value: function get_style() {
      return {
        minWidth: this.props.width || "400px",
        backgroundColor: "white",
        zIndex: 999999
      };
    }
    /*
     * Returns the UID of a result object
     *
     * @returns {String} UID of the result
     */

  }, {
    key: "get_result_uid",
    value: function get_result_uid(result) {
      return result.uid || "NO UID FOUND!";
    }
    /*
     * Checks wehter the UID is already in the list of selected UIDs
     *
     * @returns {Boolean} true if the UID is already selected, false otherwise
     */

  }, {
    key: "is_uid_selected",
    value: function is_uid_selected(uid) {
      return this.props.uids.indexOf(uid) > -1;
    }
    /*
     * Build Header <th></th> columns
     *
     * @returns {Array} of <th>...</th> columns
     */

  }, {
    key: "build_header_columns",
    value: function build_header_columns() {
      var columns = [];

      var _iterator = _createForOfIteratorHelper(this.get_columns()),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var column = _step.value;
          var label = column.label || column.title;
          var width = column.width || "auto";
          var align = column.align || "left";
          columns.push( /*#__PURE__*/external_React_default().createElement("th", {
            className: "border-top-0",
            width: width,
            align: align
          }, _t(label)));
        } // Append additional column for usage state

      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      columns.push( /*#__PURE__*/external_React_default().createElement("th", {
        className: "border-top-0",
        width: "1"
      }));
      return columns;
    }
    /*
     * Build table <tr></tr> rows
     *
     * @returns {Array} of <tr>...</tr> rows
     */

  }, {
    key: "build_rows",
    value: function build_rows() {
      var _this2 = this;

      var rows = [];
      var results = this.get_results();
      results.forEach(function (result, index) {
        var uid = _this2.get_result_uid(result);

        rows.push( /*#__PURE__*/external_React_default().createElement("tr", {
          uid: uid,
          className: _this2.props.focused == index ? "table-active" : "",
          onClick: _this2.on_select
        }, _this2.build_columns(result)));
      });
      return rows;
    }
    /*
     * Build Header <td></td> columns
     *
     * @returns {Array} of <td>...</td> columns
     */

  }, {
    key: "build_columns",
    value: function build_columns(result) {
      var columns = [];
      var searchterm = this.props.searchterm || "";

      var _iterator2 = _createForOfIteratorHelper(this.get_column_names()),
          _step2;

      try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
          var name = _step2.value;
          var value = result[name];
          var highlighted = this.highlight(value, searchterm);
          columns.push( /*#__PURE__*/external_React_default().createElement("td", {
            dangerouslySetInnerHTML: {
              __html: highlighted
            }
          }));
        }
      } catch (err) {
        _iterator2.e(err);
      } finally {
        _iterator2.f();
      }

      var uid = result.uid;
      var used = this.props.uids.indexOf(uid) > -1;
      columns.push( /*#__PURE__*/external_React_default().createElement("td", null, used && /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-link text-success"
      })));
      return columns;
    }
    /*
     * Highlight any found match of the searchterm in the text
     *
     * @returns {String} highlighted text
     */

  }, {
    key: "highlight",
    value: function highlight(text, searchterm) {
      if (searchterm.length == 0) return text;

      try {
        var rx = new RegExp(searchterm, "gi");
        text = text.replaceAll(rx, function (m) {
          return "<span class='font-weight-bold text-info'>" + m + "</span>";
        });
      } catch (error) {// pass
      }

      return text;
    }
    /*
     * Build pagination <li>...</li> items
     *
     * @returns {Array} Pagination JSX
     */

  }, {
    key: "build_pages",
    value: function build_pages() {
      var pages = [];
      var total = this.props.pages;
      var current = this.props.page;
      var padding = this.props.padding;
      var first_page = current - padding > 0 ? current - padding : 1;
      var last_page = current + padding < total ? current + padding : total;
      var crop_before = first_page === 1 ? false : true;
      var crop_after = last_page < total ? true : false;

      for (var page = first_page; page <= last_page; page++) {
        var cls = ["page-item"];
        if (current === page) cls.push("active"); // crop before the current page

        if (page == first_page && crop_before) {
          // link to first page
          pages.push( /*#__PURE__*/external_React_default().createElement("li", null, /*#__PURE__*/external_React_default().createElement("button", {
            className: "page-link",
            page: 1,
            onClick: this.on_page
          }, "1"))); // placeholder

          pages.push( /*#__PURE__*/external_React_default().createElement("li", null, /*#__PURE__*/external_React_default().createElement("div", {
            className: "page-link"
          }, "...")));
          crop_before = false;
        }

        pages.push( /*#__PURE__*/external_React_default().createElement("li", {
          className: cls.join(" ")
        }, /*#__PURE__*/external_React_default().createElement("button", {
          className: "page-link",
          page: page,
          onClick: this.on_page
        }, page))); // crop after the current page

        if (page === last_page && crop_after) {
          // placeholder
          pages.push( /*#__PURE__*/external_React_default().createElement("li", null, /*#__PURE__*/external_React_default().createElement("div", {
            className: "page-link"
          }, "..."))); // link to last page

          pages.push( /*#__PURE__*/external_React_default().createElement("li", null, /*#__PURE__*/external_React_default().createElement("button", {
            className: "page-link",
            page: total,
            onClick: this.on_page
          }, total)));
          crop_after = false;
        }
      }

      return pages;
    }
    /*
     * Build pagination next button
     *
     * @returns {Array} Next button JSX
     */

  }, {
    key: "build_next_button",
    value: function build_next_button() {
      var cls = ["page-item"];
      if (!this.props.next_url) cls.push("disabled");
      return /*#__PURE__*/external_React_default().createElement("li", {
        className: cls.join(" ")
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "page-link",
        onClick: this.on_next_page
      }, "Next"));
    }
    /*
     * Build pagination previous button
     *
     * @returns {Array} Previous button JSX
     */

  }, {
    key: "build_prev_button",
    value: function build_prev_button() {
      var cls = ["page-item"];
      if (!this.props.prev_url) cls.push("disabled");
      return /*#__PURE__*/external_React_default().createElement("li", {
        className: cls.join(" ")
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "page-link",
        onClick: this.on_prev_page
      }, "Previous"));
    }
    /*
     * Build results dropdown close button
     *
     * @returns {Array} Close button JSX
     */

  }, {
    key: "build_close_button",
    value: function build_close_button() {
      return /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-link",
        onClick: this.on_close
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-window-close"
      }));
    }
    /*
     * Event handler when a result was selected
     */

  }, {
    key: "on_select",
    value: function on_select(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var uid = target.getAttribute("uid");
      console.debug("ReferenceResults::on_select:event=", event);

      if (this.props.on_select) {
        this.props.on_select(uid);
      }
    }
    /*
     * Event handler when a page was clicked
     */

  }, {
    key: "on_page",
    value: function on_page(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var page = target.getAttribute("page");
      console.debug("ReferenceResults::on_page:event=", event);

      if (page == this.props.page) {
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page);
      }
    }
    /*
     * Event handler when the pagination previous button was clicked
     */

  }, {
    key: "on_prev_page",
    value: function on_prev_page(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_prev_page:event=", event);
      var page = this.props.page;

      if (page < 2) {
        console.warn("No previous pages available!");
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page - 1);
      }
    }
    /*
     * Event handler when the pagination next button was clicked
     */

  }, {
    key: "on_next_page",
    value: function on_next_page(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_next_page:event=", event);
      var page = this.props.page;

      if (page + 1 > this.props.pages) {
        console.warn("No next pages available!");
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page + 1);
      }
    }
    /*
     * Event handler when the dropdown close button was clicked
     */

  }, {
    key: "on_close",
    value: function on_close(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_close:event=", event);

      if (this.props.on_clear) {
        this.props.on_clear();
      }
    }
    /*
     * Render the reference results selection
     */

  }, {
    key: "render",
    value: function render() {
      if (!this.has_results()) {
        return null;
      }

      return /*#__PURE__*/external_React_default().createElement("div", {
        className: this.props.className,
        style: this.get_style()
      }, /*#__PURE__*/external_React_default().createElement("div", {
        style: {
          position: "absolute",
          top: 0,
          right: 0
        }
      }, this.build_close_button()), /*#__PURE__*/external_React_default().createElement("table", {
        className: "table table-sm table-hover small"
      }, /*#__PURE__*/external_React_default().createElement("thead", null, /*#__PURE__*/external_React_default().createElement("tr", null, this.build_header_columns())), /*#__PURE__*/external_React_default().createElement("tbody", null, this.build_rows())), this.props.pages > 1 && /*#__PURE__*/external_React_default().createElement("nav", null, /*#__PURE__*/external_React_default().createElement("ul", {
        className: "pagination pagination-sm justify-content-center"
      }, this.build_prev_button(), this.build_pages(), this.build_next_button())));
    }
  }]);

  return ReferenceResults;
}((external_React_default()).Component);

/* harmony default export */ const components_ReferenceResults = (ReferenceResults);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/References.js
function References_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { References_typeof = function _typeof(obj) { return typeof obj; }; } else { References_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return References_typeof(obj); }

function References_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = References_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function References_slicedToArray(arr, i) { return References_arrayWithHoles(arr) || References_iterableToArrayLimit(arr, i) || References_unsupportedIterableToArray(arr, i) || References_nonIterableRest(); }

function References_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function References_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return References_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return References_arrayLikeToArray(o, minLen); }

function References_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function References_iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function References_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function References_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function References_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function References_createClass(Constructor, protoProps, staticProps) { if (protoProps) References_defineProperties(Constructor.prototype, protoProps); if (staticProps) References_defineProperties(Constructor, staticProps); return Constructor; }

function References_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) References_setPrototypeOf(subClass, superClass); }

function References_setPrototypeOf(o, p) { References_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return References_setPrototypeOf(o, p); }

function References_createSuper(Derived) { var hasNativeReflectConstruct = References_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = References_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = References_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return References_possibleConstructorReturn(this, result); }; }

function References_possibleConstructorReturn(self, call) { if (call && (References_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return References_assertThisInitialized(self); }

function References_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function References_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function References_getPrototypeOf(o) { References_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return References_getPrototypeOf(o); }




var References = /*#__PURE__*/function (_React$Component) {
  References_inherits(References, _React$Component);

  var _super = References_createSuper(References);

  function References(props) {
    var _this;

    References_classCallCheck(this, References);

    _this = _super.call(this, props);
    _this.on_deselect = _this.on_deselect.bind(References_assertThisInitialized(_this));
    return _this;
  }

  References_createClass(References, [{
    key: "get_selected_uids",
    value: function get_selected_uids() {
      return this.props.uids || [];
    }
    /*
     * Simple template interpolation that replaces ${...} placeholders
     * with any found value from the context object.
     *
     * https://stackoverflow.com/questions/29182244/convert-a-string-to-a-template-string
     */

  }, {
    key: "interpolate",
    value: function interpolate(template, context) {
      for (var _i = 0, _Object$entries = Object.entries(context); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = References_slicedToArray(_Object$entries[_i], 2),
            key = _Object$entries$_i[0],
            value = _Object$entries$_i[1];

        template = template.replace(new RegExp('\\$\\{' + key + '\\}', 'g'), value);
      }

      return template;
    }
  }, {
    key: "render_display_template",
    value: function render_display_template(uid) {
      var template = this.props.display_template;
      var context = this.props.records[uid];
      if (!context) return uid;
      return this.interpolate(template, context);
    }
  }, {
    key: "build_selected_items",
    value: function build_selected_items() {
      var items = [];
      var selected_uids = this.get_selected_uids();

      var _iterator = References_createForOfIteratorHelper(selected_uids),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var uid = _step.value;
          items.push( /*#__PURE__*/external_React_default().createElement("li", {
            uid: uid
          }, /*#__PURE__*/external_React_default().createElement("div", {
            className: "p-1 mb-1 mr-1 bg-light border rounded d-inline-block"
          }, /*#__PURE__*/external_React_default().createElement("span", {
            dangerouslySetInnerHTML: {
              __html: this.render_display_template(uid)
            }
          }), /*#__PURE__*/external_React_default().createElement("button", {
            uid: uid,
            className: "btn btn-sm btn-link-danger",
            onClick: this.on_deselect
          }, /*#__PURE__*/external_React_default().createElement("i", {
            className: "fas fa-times-circle"
          })))));
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      return items;
    }
  }, {
    key: "on_deselect",
    value: function on_deselect(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var uid = target.getAttribute("uid");
      console.debug("References::on_deselect: Remove UID", uid);

      if (this.props.on_deselect) {
        this.props.on_deselect(uid);
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget-references"
      }, /*#__PURE__*/external_React_default().createElement("ul", {
        className: "list-unstyled list-group list-group-horizontal"
      }, this.build_selected_items()), /*#__PURE__*/external_React_default().createElement("textarea", {
        className: "d-none",
        name: this.props.name,
        value: this.props.uids.join("\n")
      }));
    }
  }]);

  return References;
}((external_React_default()).Component);

/* harmony default export */ const components_References = (References);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/widget.js
function widget_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { widget_typeof = function _typeof(obj) { return typeof obj; }; } else { widget_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return widget_typeof(obj); }

function widget_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = widget_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function widget_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return widget_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return widget_arrayLikeToArray(o, minLen); }

function widget_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function widget_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function widget_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function widget_createClass(Constructor, protoProps, staticProps) { if (protoProps) widget_defineProperties(Constructor.prototype, protoProps); if (staticProps) widget_defineProperties(Constructor, staticProps); return Constructor; }

function widget_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) widget_setPrototypeOf(subClass, superClass); }

function widget_setPrototypeOf(o, p) { widget_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return widget_setPrototypeOf(o, p); }

function widget_createSuper(Derived) { var hasNativeReflectConstruct = widget_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = widget_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = widget_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return widget_possibleConstructorReturn(this, result); }; }

function widget_possibleConstructorReturn(self, call) { if (call && (widget_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return widget_assertThisInitialized(self); }

function widget_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function widget_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function widget_getPrototypeOf(o) { widget_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return widget_getPrototypeOf(o); }








var UIDReferenceWidgetController = /*#__PURE__*/function (_React$Component) {
  widget_inherits(UIDReferenceWidgetController, _React$Component);

  var _super = widget_createSuper(UIDReferenceWidgetController);

  function UIDReferenceWidgetController(props) {
    var _this;

    widget_classCallCheck(this, UIDReferenceWidgetController);

    _this = _super.call(this, props); // Internal state

    _this.state = {
      results: [],
      // `items` list of search results coming from `senaite.jsonapi`
      searchterm: "",
      // the search term that was entered by the user
      loading: false,
      // loading flag when searching for results
      count: 0,
      // count of results (coming from `senaite.jsonapi`)
      page: 1,
      // current page (coming from `senaite.jsonapi`)
      pages: 1,
      // number of pages (coming from `senaite.jsonapi`)
      next_url: null,
      // next page API URL (coming from `senaite.jsonapi`)
      prev_url: null,
      // previous page API URL (coming from `senaite.jsonapi`)
      b_start: 1,
      // batch start for pagination (see `senaite.jsonapi.batch`)
      focused: 0,
      // current result that has the focus
      padding: 3 // page padding

    }; // Root input HTML element

    var el = props.root_el; // Data keys located at the root element
    // -> initial values are set from the widget class

    var data_keys = ["id", "name", "uids", "api_url", "records", "catalog", "query", "columns", "display_template", "limit", "multi_valued", "disabled", "readonly", "padding"]; // Query data keys and set state with parsed JSON value

    for (var _i = 0, _data_keys = data_keys; _i < _data_keys.length; _i++) {
      var key = _data_keys[_i];
      var value = el.dataset[key];

      if (value === undefined) {
        continue;
      }

      _this.state[key] = _this.parse_json(value);
    } // Initialize communication API with the API URL


    _this.api = new api({
      api_url: _this.state.api_url
    }); // Bind callbacks to current context

    _this.search = _this.search.bind(widget_assertThisInitialized(_this));
    _this.goto_page = _this.goto_page.bind(widget_assertThisInitialized(_this));
    _this.clear_results = _this.clear_results.bind(widget_assertThisInitialized(_this));
    _this.select = _this.select.bind(widget_assertThisInitialized(_this));
    _this.select_focused = _this.select_focused.bind(widget_assertThisInitialized(_this));
    _this.deselect = _this.deselect.bind(widget_assertThisInitialized(_this));
    _this.navigate_results = _this.navigate_results.bind(widget_assertThisInitialized(_this));
    _this.on_keydown = _this.on_keydown.bind(widget_assertThisInitialized(_this));
    _this.on_click = _this.on_click.bind(widget_assertThisInitialized(_this)); // dev only

    window.widget = widget_assertThisInitialized(_this);
    return widget_possibleConstructorReturn(_this, widget_assertThisInitialized(_this));
  }

  widget_createClass(UIDReferenceWidgetController, [{
    key: "componentDidMount",
    value: function componentDidMount() {
      // Bind event listeners of the document
      document.addEventListener("keydown", this.on_keydown, false);
      document.addEventListener("click", this.on_click, false);
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      // Remove event listeners of the document
      document.removeEventListener("keydown", this.on_keydown, false);
      document.removeEventListener("click", this.on_click, false);
    }
    /*
     * JSON parse the given value
     *
     * @param {String} value: The JSON value to parse
     */

  }, {
    key: "parse_json",
    value: function parse_json(value) {
      try {
        return JSON.parse(value);
      } catch (error) {
        console.error("Could not parse \"".concat(value, "\" to JSON"));
      }
    }
  }, {
    key: "is_disabled",
    value: function is_disabled() {
      if (this.state.disabled) {
        return true;
      }

      if (this.state.readonly) {
        return true;
      }

      if (!this.state.multi_valued && this.state.uids.length > 0) {
        return true;
      }

      return false;
    }
    /*
     * Create a query object for the API
     *
     * This method prepares a query from the current state variables,
     * which can be used to call the `api.search` method.
     *
     * @param {Object} options: Additional options to add to the query
     * @returns {Object} The query object
     */

  }, {
    key: "make_query",
    value: function make_query(options) {
      options = options || {};
      return Object.assign({
        q: this.state.searchterm,
        limit: this.state.limit,
        complete: 1
      }, options, this.state.query);
    }
    /*
     * Execute a search query and set the results to the state
     *
     * @param {Object} url_params: Additional search params for the API search URL
     * @returns {Promise}
     */

  }, {
    key: "fetch_results",
    value: function fetch_results(url_params) {
      url_params = url_params || {}; // prepare the server request

      var self = this;
      var query = this.make_query();
      this.toggle_loading(true);
      var promise = this.api.search(this.state.catalog, query, url_params);
      promise.then(function (data) {
        console.debug("ReferenceWidgetController::fetch_results:GOT DATA: ", data);
        self.set_results_data(data);
        self.toggle_loading(false);
      });
      return promise;
    }
    /*
     * Execute a search for the given searchterm
     *
     * @param {String} searchterm: The value entered into the search field
     * @returns {Promise}
     */

  }, {
    key: "search",
    value: function search(searchterm) {
      if (!searchterm && this.state.results.length > 0) {
        this.state.searchterm = "";
        return;
      }

      console.debug("ReferenceWidgetController::search:searchterm:", searchterm); // set the searchterm directly to avoid re-rendering

      this.state.searchterm = searchterm || "";
      return this.fetch_results();
    }
    /*
     * Fetch results of a page
     *
     * @param {Integer} page: The page to fetch
     * @returns {Promise}
     */

  }, {
    key: "goto_page",
    value: function goto_page(page) {
      page = parseInt(page);
      var limit = parseInt(this.state.limit); // calculate the beginning of the page
      // Note: this is the count of previous items that are excluded

      var b_start = page * limit - limit;
      return this.fetch_results({
        b_start: b_start
      });
    }
    /*
     * Add the UID of a search result to the state
     *
     * @param {String} uid: The selected UID
     * @returns {Array} uids: current selected UIDs
     */

  }, {
    key: "select",
    value: function select(uid) {
      console.debug("ReferenceWidgetController::select:uid:", uid); // create a copy of the selected UIDs

      var uids = [].concat(this.state.uids); // Add the new UID if it is not selected yet

      if (uids.indexOf(uid) == -1) {
        uids.push(uid);
      }

      this.setState({
        uids: uids
      });

      if (uids.length > 0 && !this.state.multi_valued) {
        this.clear_results();
      }

      return uids;
    }
    /*
     * Add/remove the focused result
     *
     */

  }, {
    key: "select_focused",
    value: function select_focused() {
      console.debug("ReferenceWidgetController::select_focused");
      var focused = this.state.focused;
      var result = this.state.results.at(focused);

      if (result) {
        var uid = result.uid;

        if (this.state.uids.indexOf(uid) == -1) {
          this.select(uid);
        } else {
          this.deselect(uid);
        }
      }
    }
    /*
     * Remove the UID of a reference from the state
     *
     * @param {String} uid: The selected UID
     * @returns {Array} uids: current selected UIDs
     */

  }, {
    key: "deselect",
    value: function deselect(uid) {
      console.debug("ReferenceWidgetController::deselect:uid:", uid);
      var uids = [].concat(this.state.uids);
      var pos = uids.indexOf(uid);

      if (pos > -1) {
        uids.splice(pos, 1);
      }

      this.setState({
        uids: uids
      });
      return uids;
    }
    /*
     * Navigate the results either up or down
     *
     * @param {String} direction: either up or down
     */

  }, {
    key: "navigate_results",
    value: function navigate_results(direction) {
      var page = this.state.page;
      var pages = this.state.pages;
      var results = this.state.results;
      var focused = this.state.focused;
      var searchterm = this.state.searchterm;
      console.debug("ReferenceWidgetController::navigate_results:focused:", focused);

      if (direction == "up") {
        if (focused > 0) {
          this.setState({
            focused: focused - 1
          });
        } else {
          this.setState({
            focused: 0
          });

          if (page > 1) {
            this.goto_page(page - 1);
          }
        }
      } else if (direction == "down") {
        if (this.state.results.length == 0) {
          this.search(searchterm);
        }

        if (focused < results.length - 1) {
          this.setState({
            focused: focused + 1
          });
        } else {
          this.setState({
            focused: 0
          });

          if (page < pages) {
            this.goto_page(page + 1);
          }
        }
      } else if (direction == "left") {
        this.setState({
          focused: 0
        });

        if (page > 0) {
          this.goto_page(page - 1);
        }
      } else if (direction == "right") {
        this.setState({
          focused: 0
        });

        if (page < pages) {
          this.goto_page(page + 1);
        }
      }
    }
    /*
     * Toggle loading state
     *
     * @param {Boolean} toggle: The loading state to set
     * @returns {Boolean} toggle: The current loading state
     */

  }, {
    key: "toggle_loading",
    value: function toggle_loading(toggle) {
      if (toggle == null) {
        toggle = false;
      }

      this.setState({
        loading: toggle
      });
      return toggle;
    }
    /*
     * Set results data coming from `senaite.jsonapi`
     *
     * @param {Object} data: JSON search result object returned from `senaite.jsonapi`
     */

  }, {
    key: "set_results_data",
    value: function set_results_data(data) {
      data = data || {};
      var items = data.items || [];
      var records = Object.assign(this.state.records, {}); // update state records

      var _iterator = widget_createForOfIteratorHelper(items),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var item = _step.value;
          var uid = item.uid;
          records[uid] = item;
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      this.setState({
        records: records,
        results: items,
        count: data.count || 0,
        page: data.page || 1,
        pages: data.pages || 1,
        next_url: data.next || null,
        prev_url: data.previous || null
      });
    }
    /*
     * Clear results from the state
     */

  }, {
    key: "clear_results",
    value: function clear_results() {
      this.setState({
        results: [],
        count: 0,
        page: 1,
        pages: 1,
        next_url: null,
        prev_url: null
      });
    }
    /*
     * ReactJS event handler for keydown event
     */

  }, {
    key: "on_keydown",
    value: function on_keydown(event) {
      // clear results when ESC key is pressed
      if (event.keyCode === 27) {
        this.clear_results();
      }
    }
    /*
     * ReactJS event handler for click events
     */

  }, {
    key: "on_click",
    value: function on_click(event) {
      // clear results when clicked outside of the widget
      var widget = this.props.root_el;
      var target = event.target;

      if (!widget.contains(target)) {
        this.clear_results();
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget"
      }, /*#__PURE__*/external_React_default().createElement(components_References, {
        uids: this.state.uids,
        records: this.state.records,
        display_template: this.state.display_template,
        name: this.state.name,
        on_deselect: this.deselect
      }), /*#__PURE__*/external_React_default().createElement(components_ReferenceField, {
        className: "form-control",
        name: "uidreference-search",
        disabled: this.is_disabled(),
        on_search: this.search,
        on_clear: this.clear_results,
        on_focus: this.search,
        on_arrow_key: this.navigate_results,
        on_enter: this.select_focused
      }), /*#__PURE__*/external_React_default().createElement(components_ReferenceResults, {
        className: "position-absolute shadow border rounded bg-white mt-1 p-1",
        columns: this.state.columns,
        uids: this.state.uids,
        searchterm: this.state.searchterm,
        results: this.state.results,
        focused: this.state.focused,
        count: this.state.count,
        page: this.state.page,
        pages: this.state.pages,
        padding: this.state.padding,
        next_url: this.state.next_url,
        prev_url: this.state.prev_url,
        on_select: this.select,
        on_page: this.goto_page,
        on_clear: this.clear_results
      }));
    }
  }]);

  return UIDReferenceWidgetController;
}((external_React_default()).Component);

/* harmony default export */ const uidreferencewidget_widget = (UIDReferenceWidgetController);
;// CONCATENATED MODULE: ./widgets/addresswidget/api.js
function api_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function api_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function api_createClass(Constructor, protoProps, staticProps) { if (protoProps) api_defineProperties(Constructor.prototype, protoProps); if (staticProps) api_defineProperties(Constructor, staticProps); return Constructor; }

var AddressWidgetAPI = /*#__PURE__*/function () {
  function AddressWidgetAPI(props) {
    api_classCallCheck(this, AddressWidgetAPI);

    console.debug("AddressWidgetAPI::constructor");
    this.portal_url = props.portal_url;

    this.on_api_error = props.on_api_error || function (response) {};

    return this;
  }

  api_createClass(AddressWidgetAPI, [{
    key: "get_url",
    value: function get_url(endpoint) {
      return "".concat(this.portal_url, "/").concat(endpoint);
    }
    /*
     * Fetch JSON resource from the server
     *
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
     */

  }, {
    key: "get_json",
    value: function get_json(endpoint, options) {
      var data, init, method, on_api_error, request, url;

      if (options == null) {
        options = {};
      }

      method = options.method || "POST";
      data = JSON.stringify(options.data) || "{}";
      on_api_error = this.on_api_error;
      url = this.get_url(endpoint);
      init = {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": this.get_csrf_token()
        },
        body: method === "POST" ? data : null,
        credentials: "include"
      };
      console.info("AddressWidgetAPI::fetch:endpoint=" + endpoint + " init=", init);
      request = new Request(url, init);
      return fetch(request).then(function (response) {
        if (!response.ok) {
          return Promise.reject(response);
        }

        return response;
      }).then(function (response) {
        return response.json();
      })["catch"](function (response) {
        on_api_error(response);
        return response;
      });
    }
  }, {
    key: "fetch_subdivisions",
    value: function fetch_subdivisions(parent) {
      var url = "geo_subdivisions";
      console.debug("AddressWidgetAPI::fetch_subdivisions:url=", url);
      var options = {
        method: "POST",
        data: {
          "parent": parent
        }
      };
      return this.get_json(url, options);
    }
    /*
     * Get the plone.protect CSRF token
     */

  }, {
    key: "get_csrf_token",
    value: function get_csrf_token() {
      return document.querySelector("#protect-script").dataset.token;
    }
  }]);

  return AddressWidgetAPI;
}();

/* harmony default export */ const addresswidget_api = (AddressWidgetAPI);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/LocationSelector.js
function LocationSelector_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { LocationSelector_typeof = function _typeof(obj) { return typeof obj; }; } else { LocationSelector_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return LocationSelector_typeof(obj); }

function LocationSelector_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = LocationSelector_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function LocationSelector_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return LocationSelector_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return LocationSelector_arrayLikeToArray(o, minLen); }

function LocationSelector_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function LocationSelector_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function LocationSelector_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function LocationSelector_createClass(Constructor, protoProps, staticProps) { if (protoProps) LocationSelector_defineProperties(Constructor.prototype, protoProps); if (staticProps) LocationSelector_defineProperties(Constructor, staticProps); return Constructor; }

function LocationSelector_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) LocationSelector_setPrototypeOf(subClass, superClass); }

function LocationSelector_setPrototypeOf(o, p) { LocationSelector_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return LocationSelector_setPrototypeOf(o, p); }

function LocationSelector_createSuper(Derived) { var hasNativeReflectConstruct = LocationSelector_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = LocationSelector_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = LocationSelector_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return LocationSelector_possibleConstructorReturn(this, result); }; }

function LocationSelector_possibleConstructorReturn(self, call) { if (call && (LocationSelector_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return LocationSelector_assertThisInitialized(self); }

function LocationSelector_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function LocationSelector_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function LocationSelector_getPrototypeOf(o) { LocationSelector_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return LocationSelector_getPrototypeOf(o); }




var LocationSelector = /*#__PURE__*/function (_React$Component) {
  LocationSelector_inherits(LocationSelector, _React$Component);

  var _super = LocationSelector_createSuper(LocationSelector);

  function LocationSelector(props) {
    LocationSelector_classCallCheck(this, LocationSelector);

    return _super.call(this, props);
  }

  LocationSelector_createClass(LocationSelector, [{
    key: "render_options",
    value: function render_options() {
      var options = [];
      var locations = this.props.locations;
      options.push( /*#__PURE__*/external_React_default().createElement("option", {
        value: ""
      }));

      if (Array.isArray(locations)) {
        var _iterator = LocationSelector_createForOfIteratorHelper(locations),
            _step;

        try {
          for (_iterator.s(); !(_step = _iterator.n()).done;) {
            var location = _step.value;
            options.push( /*#__PURE__*/external_React_default().createElement("option", {
              value: location
            }, location));
          }
        } catch (err) {
          _iterator.e(err);
        } finally {
          _iterator.f();
        }
      }

      return options;
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("select", {
        id: this.props.id,
        name: this.props.name,
        value: this.props.value,
        onChange: this.props.onChange
      }, this.render_options());
    }
  }]);

  return LocationSelector;
}((external_React_default()).Component);

/* harmony default export */ const components_LocationSelector = (LocationSelector);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/AddressField.js
function AddressField_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { AddressField_typeof = function _typeof(obj) { return typeof obj; }; } else { AddressField_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return AddressField_typeof(obj); }

function AddressField_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function AddressField_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function AddressField_createClass(Constructor, protoProps, staticProps) { if (protoProps) AddressField_defineProperties(Constructor.prototype, protoProps); if (staticProps) AddressField_defineProperties(Constructor, staticProps); return Constructor; }

function AddressField_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) AddressField_setPrototypeOf(subClass, superClass); }

function AddressField_setPrototypeOf(o, p) { AddressField_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return AddressField_setPrototypeOf(o, p); }

function AddressField_createSuper(Derived) { var hasNativeReflectConstruct = AddressField_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = AddressField_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = AddressField_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return AddressField_possibleConstructorReturn(this, result); }; }

function AddressField_possibleConstructorReturn(self, call) { if (call && (AddressField_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return AddressField_assertThisInitialized(self); }

function AddressField_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function AddressField_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function AddressField_getPrototypeOf(o) { AddressField_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return AddressField_getPrototypeOf(o); }





var AddressField = /*#__PURE__*/function (_React$Component) {
  AddressField_inherits(AddressField, _React$Component);

  var _super = AddressField_createSuper(AddressField);

  function AddressField(props) {
    AddressField_classCallCheck(this, AddressField);

    return _super.call(this, props);
  }

  AddressField_createClass(AddressField, [{
    key: "is_location_selector",
    value: function is_location_selector() {
      return Array.isArray(this.props.locations);
    }
  }, {
    key: "is_visible",
    value: function is_visible() {
      var visible = true;

      if (this.is_location_selector()) {
        visible = this.props.locations.length > 0;
      }

      return visible;
    }
  }, {
    key: "render_element",
    value: function render_element() {
      if (this.is_location_selector()) {
        return /*#__PURE__*/external_React_default().createElement(components_LocationSelector, {
          id: this.props.id,
          name: this.props.name,
          value: this.props.value,
          locations: this.props.locations,
          onChange: this.props.onChange
        });
      } else {
        return /*#__PURE__*/external_React_default().createElement("input", {
          type: "text",
          id: this.props.id,
          name: this.props.name,
          value: this.props.value,
          onChange: this.props.onChange
        });
      }
    }
  }, {
    key: "render",
    value: function render() {
      if (!this.is_visible()) {
        return /*#__PURE__*/external_React_default().createElement("input", {
          type: "hidden",
          id: this.props.id,
          name: this.props.name,
          value: this.props.value
        });
      }

      return /*#__PURE__*/external_React_default().createElement("div", {
        "class": "form-group form-row mb-2"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        "class": "col input-group input-group-sm"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        "class": "input-group-prepend"
      }, /*#__PURE__*/external_React_default().createElement("label", {
        "class": "input-group-text",
        "for": this.props.id
      }, this.props.label)), this.render_element()));
    }
  }]);

  return AddressField;
}((external_React_default()).Component);

/* harmony default export */ const components_AddressField = (AddressField);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/Address.js
function Address_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { Address_typeof = function _typeof(obj) { return typeof obj; }; } else { Address_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return Address_typeof(obj); }

function Address_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function Address_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function Address_createClass(Constructor, protoProps, staticProps) { if (protoProps) Address_defineProperties(Constructor.prototype, protoProps); if (staticProps) Address_defineProperties(Constructor, staticProps); return Constructor; }

function Address_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) Address_setPrototypeOf(subClass, superClass); }

function Address_setPrototypeOf(o, p) { Address_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return Address_setPrototypeOf(o, p); }

function Address_createSuper(Derived) { var hasNativeReflectConstruct = Address_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = Address_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = Address_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return Address_possibleConstructorReturn(this, result); }; }

function Address_possibleConstructorReturn(self, call) { if (call && (Address_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return Address_assertThisInitialized(self); }

function Address_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function Address_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function Address_getPrototypeOf(o) { Address_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return Address_getPrototypeOf(o); }





var Address = /*#__PURE__*/function (_React$Component) {
  Address_inherits(Address, _React$Component);

  var _super = Address_createSuper(Address);

  function Address(props) {
    var _this;

    Address_classCallCheck(this, Address);

    _this = _super.call(this, props);
    _this.state = {
      country: props.country,
      subdivision1: props.subdivision1,
      subdivision2: props.subdivision2,
      city: props.city,
      zip: props.zip,
      address: props.address,
      address_type: props.address_type
    }; // Event handlers

    _this.on_country_change = _this.on_country_change.bind(Address_assertThisInitialized(_this));
    _this.on_subdivision1_change = _this.on_subdivision1_change.bind(Address_assertThisInitialized(_this));
    _this.on_subdivision2_change = _this.on_subdivision2_change.bind(Address_assertThisInitialized(_this));
    _this.on_city_change = _this.on_city_change.bind(Address_assertThisInitialized(_this));
    _this.on_zip_change = _this.on_zip_change.bind(Address_assertThisInitialized(_this));
    _this.on_address_change = _this.on_address_change.bind(Address_assertThisInitialized(_this));
    return _this;
  }

  Address_createClass(Address, [{
    key: "force_array",
    value: function force_array(value) {
      if (!Array.isArray(value)) {
        value = [];
      }

      return value;
    }
    /**
     * Returns the list of first-level subdivisions of the current country,
     * sorted alphabetically
     */

  }, {
    key: "get_subdivisions1",
    value: function get_subdivisions1() {
      var country = this.state.country;
      return this.force_array(this.props.subdivisions1[country]);
    }
    /**
     * Returns the list of subdivisions of the current first-level subdivision,
     * sorted sorted alphabetically
     */

  }, {
    key: "get_subdivisions2",
    value: function get_subdivisions2() {
      var subdivision1 = this.state.subdivision1;
      return this.force_array(this.props.subdivisions2[subdivision1]);
    }
  }, {
    key: "get_label",
    value: function get_label(key) {
      var country = this.state.country;
      var label = this.props.labels[country];

      if (label != null && label.constructor == Object && key in label) {
        label = label[key];
      } else {
        label = this.props.labels[key];
      }

      return label;
    }
    /** Event triggered when the value for Country selector changes. Updates the
     * selector of subdivisions (e.g. states) with the list of top-level
     * subdivisions for the selected country
     */

  }, {
    key: "on_country_change",
    value: function on_country_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_country_change: ".concat(value));

      if (this.props.on_country_change) {
        this.props.on_country_change(value);
      }

      this.setState({
        country: value,
        subdivision1: "",
        subdivision2: ""
      });
    }
    /** Event triggered when the value for the Country first-level subdivision
     * (e.g. state) selector changes. Updates the selector of subdivisions (e.g.
     * districts) for the selected subdivision and country
     */

  }, {
    key: "on_subdivision1_change",
    value: function on_subdivision1_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_subdivision1_change: ".concat(value));

      if (this.props.on_subdivision1_change) {
        var country = this.state.country;
        this.props.on_subdivision1_change(country, value);
      }

      this.setState({
        subdivision1: value,
        subdivision2: ""
      });
    }
    /** Event triggered when the value for the second-level subdivision (e.g.
     * district) selector changes
     */

  }, {
    key: "on_subdivision2_change",
    value: function on_subdivision2_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_subdivision2_change: ".concat(value));

      if (this.props.on_subdivision2_change) {
        this.props.on_subdivision2_change(value);
      }

      this.setState({
        subdivision2: value
      });
    }
    /** Event triggered when the value for the address field changes
     */

  }, {
    key: "on_address_change",
    value: function on_address_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        address: value
      });
    }
    /** Event triggered when the value for the zip field changes
     */

  }, {
    key: "on_zip_change",
    value: function on_zip_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        zip: value
      });
    }
    /** Event triggered when the value for the city field changes
     */

  }, {
    key: "on_city_change",
    value: function on_city_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        city: value
      });
    }
  }, {
    key: "get_input_id",
    value: function get_input_id(subfield) {
      var id = this.props.id;
      var index = this.props.index;
      return "".concat(id, "-").concat(index, "-").concat(subfield);
    }
  }, {
    key: "get_input_name",
    value: function get_input_name(subfield) {
      var name = this.props.name;
      var index = this.props.index;
      return "".concat(name, ".").concat(index, ".").concat(subfield);
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", null, /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("country"),
        name: this.get_input_name("country"),
        label: this.props.labels.country,
        value: this.state.country,
        locations: this.props.countries,
        onChange: this.on_country_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("subdivision1"),
        name: this.get_input_name("subdivision1"),
        label: this.get_label("subdivision1"),
        value: this.state.subdivision1,
        locations: this.get_subdivisions1(),
        onChange: this.on_subdivision1_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("subdivision2"),
        name: this.get_input_name("subdivision2"),
        label: this.get_label("subdivision2"),
        value: this.state.subdivision2,
        locations: this.get_subdivisions2(),
        onChange: this.on_subdivision2_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("city"),
        name: this.get_input_name("city"),
        label: this.props.labels.city,
        value: this.state.city,
        onChange: this.on_city_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("zip"),
        name: this.get_input_name("zip"),
        label: this.props.labels.zip,
        value: this.state.zip,
        onChange: this.on_zip_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("address"),
        name: this.get_input_name("address"),
        label: this.props.labels.address,
        value: this.state.address,
        onChange: this.on_address_change
      }), /*#__PURE__*/external_React_default().createElement("input", {
        type: "hidden",
        id: this.get_input_id("type"),
        name: this.get_input_name("type"),
        value: this.state.address_type
      }));
    }
  }]);

  return Address;
}((external_React_default()).Component);

/* harmony default export */ const components_Address = (Address);
;// CONCATENATED MODULE: ./widgets/addresswidget/widget.js
function addresswidget_widget_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { addresswidget_widget_typeof = function _typeof(obj) { return typeof obj; }; } else { addresswidget_widget_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return addresswidget_widget_typeof(obj); }

function widget_slicedToArray(arr, i) { return widget_arrayWithHoles(arr) || widget_iterableToArrayLimit(arr, i) || addresswidget_widget_unsupportedIterableToArray(arr, i) || widget_nonIterableRest(); }

function widget_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function widget_iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function widget_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function addresswidget_widget_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = addresswidget_widget_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function addresswidget_widget_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return addresswidget_widget_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return addresswidget_widget_arrayLikeToArray(o, minLen); }

function addresswidget_widget_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) { symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); } keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { widget_defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function widget_defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function addresswidget_widget_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function addresswidget_widget_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function addresswidget_widget_createClass(Constructor, protoProps, staticProps) { if (protoProps) addresswidget_widget_defineProperties(Constructor.prototype, protoProps); if (staticProps) addresswidget_widget_defineProperties(Constructor, staticProps); return Constructor; }

function addresswidget_widget_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) addresswidget_widget_setPrototypeOf(subClass, superClass); }

function addresswidget_widget_setPrototypeOf(o, p) { addresswidget_widget_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return addresswidget_widget_setPrototypeOf(o, p); }

function addresswidget_widget_createSuper(Derived) { var hasNativeReflectConstruct = addresswidget_widget_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = addresswidget_widget_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = addresswidget_widget_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return addresswidget_widget_possibleConstructorReturn(this, result); }; }

function addresswidget_widget_possibleConstructorReturn(self, call) { if (call && (addresswidget_widget_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return addresswidget_widget_assertThisInitialized(self); }

function addresswidget_widget_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function addresswidget_widget_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function addresswidget_widget_getPrototypeOf(o) { addresswidget_widget_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return addresswidget_widget_getPrototypeOf(o); }






var AddressWidgetController = /*#__PURE__*/function (_React$Component) {
  addresswidget_widget_inherits(AddressWidgetController, _React$Component);

  var _super = addresswidget_widget_createSuper(AddressWidgetController);

  function AddressWidgetController(props) {
    var _this;

    addresswidget_widget_classCallCheck(this, AddressWidgetController);

    _this = _super.call(this, props); // Root input HTML element

    var el = props.root_el;
    _this.state = {}; // Data keys located at the root element
    // -> initial values are set from the widget class

    var data_keys = ["id", "name", "items", "portal_url", "labels", "countries", "subdivisions1", "subdivisions2"]; // Query data keys and set state with parsed JSON value

    for (var _i = 0, _data_keys = data_keys; _i < _data_keys.length; _i++) {
      var key = _data_keys[_i];
      var value = el.dataset[key];
      _this.state[key] = _this.parse_json(value);
    } // Initialize communication API with the API URL


    _this.api = new addresswidget_api({
      portal_url: _this.state.portal_url
    }); // Bind callbacks to current context

    _this.on_country_change = _this.on_country_change.bind(addresswidget_widget_assertThisInitialized(_this));
    _this.on_subdivision1_change = _this.on_subdivision1_change.bind(addresswidget_widget_assertThisInitialized(_this));
    return addresswidget_widget_possibleConstructorReturn(_this, addresswidget_widget_assertThisInitialized(_this));
  }

  addresswidget_widget_createClass(AddressWidgetController, [{
    key: "parse_json",
    value: function parse_json(value) {
      try {
        return JSON.parse(value);
      } catch (error) {
        console.error("Could not parse \"".concat(value, "\" to JSON"));
      }
    }
    /**
     * Event triggered when the user selects a country. Function fetches and
     * updates the geo mapping with the first level subdivisions for the selected
     * country if are not up-to-date yet. It also updates the label for the first
     * level subdivision in accordance.
     */

  }, {
    key: "on_country_change",
    value: function on_country_change(country) {
      console.debug("widget::on_country_change: ".concat(country));
      var self = this;
      var promise = this.api.fetch_subdivisions(country);
      promise.then(function (data) {
        // Update the label with the type of 1st-level subdivisions
        var labels = _objectSpread({}, self.state.labels);

        if (data.length > 0) {
          labels[country]["subdivision1"] = data[0].type;
        } // Create a copy instead of modifying the existing dict from state var


        var subdivisions = _objectSpread({}, self.state.subdivisions1); // Only interested in names, sorted alphabetically


        subdivisions[country] = data.map(function (x) {
          return x.name;
        }).sort(); // Update current state with the changes

        self.setState({
          subdivisions1: subdivisions,
          labels: labels
        });
      });
      return promise;
    }
    /**
     * Event triggered when the user selects a first-level subdivision of a
     * country. Function fetches and updates the geo mapping with the second level
     * subdivisions for the selected subdivision if are not up-to-date. It also
     * updates the label for the second level subdivision in accordance.
     */

  }, {
    key: "on_subdivision1_change",
    value: function on_subdivision1_change(country, subdivision) {
      console.debug("widget::on_subdivision1_change: ".concat(country, ", ").concat(subdivision));
      var self = this;
      var promise = this.api.fetch_subdivisions(subdivision);
      promise.then(function (data) {
        // Update the label with the type of 1st-level subdivisions
        var labels = _objectSpread({}, self.state.labels);

        if (data.length > 0) {
          labels[country]["subdivision2"] = data[0].type;
        } // Create a copy instead of modifying the existing dict from state var


        var subdivisions = _objectSpread({}, self.state.subdivisions2); // Only interested in names, sorted alphabetically


        subdivisions[subdivision] = data.map(function (x) {
          return x.name;
        }).sort(); // Update current state with the changes

        self.setState({
          subdivisions2: subdivisions,
          labels: labels
        });
      });
      return promise;
    }
  }, {
    key: "render_items",
    value: function render_items() {
      var html_items = [];
      var items = this.state.items;

      var _iterator = addresswidget_widget_createForOfIteratorHelper(items.entries()),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var _step$value = widget_slicedToArray(_step.value, 2),
              index = _step$value[0],
              item = _step$value[1];

          var section_title = "";

          if (items.length > 1) {
            // Only render the title if more than one address
            section_title = /*#__PURE__*/external_React_default().createElement("strong", null, this.state.labels[item.type]);
          }

          html_items.push( /*#__PURE__*/external_React_default().createElement("div", {
            "class": "mb-2 pt-2"
          }, section_title, /*#__PURE__*/external_React_default().createElement(components_Address, {
            id: this.state.id,
            name: this.state.name,
            index: index,
            address_type: item.type,
            country: item.country,
            subdivision1: item.subdivision1,
            subdivision2: item.subdivision2,
            city: item.city,
            zip: item.zip,
            address: item.address,
            labels: this.state.labels,
            countries: this.state.countries,
            subdivisions1: this.state.subdivisions1,
            subdivisions2: this.state.subdivisions2,
            on_country_change: this.on_country_change,
            on_subdivision1_change: this.on_subdivision1_change
          })));
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      return html_items;
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "addresswidget"
      }, this.render_items());
    }
  }]);

  return AddressWidgetController;
}((external_React_default()).Component);

/* harmony default export */ const addresswidget_widget = (AddressWidgetController);
// EXTERNAL MODULE: ../node_modules/intl-tel-input/index.js
var intl_tel_input = __webpack_require__(583);
var intl_tel_input_default = /*#__PURE__*/__webpack_require__.n(intl_tel_input);
;// CONCATENATED MODULE: ./senaite.core.widgets.js
function senaite_core_widgets_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = senaite_core_widgets_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function senaite_core_widgets_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return senaite_core_widgets_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return senaite_core_widgets_arrayLikeToArray(o, minLen); }

function senaite_core_widgets_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }





document.addEventListener("DOMContentLoaded", function () {
  console.info("*** SENAITE CORE WIDGETS JS LOADED ***"); // Widgets

  window.widgets = {}; // TinyMCE

  var wysiwig_elements = ["textarea.mce_editable", "div.ArchetypesRichWidget textarea", "textarea[name='form.widgets.IRichTextBehavior.text']", "textarea.richTextWidget"];
  tinymce.init({
    height: 300,
    paste_data_images: true,
    selector: wysiwig_elements.join(","),
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    // NOTE: CSS file must match configuration of entry point in webpack.config.js
    content_css: "/++plone++senaite.core.static/bundles/senaite.core.css"
  }); // Referencewidget

  var ref_widgets = document.getElementsByClassName("senaite-uidreference-widget-input");

  var _iterator = senaite_core_widgets_createForOfIteratorHelper(ref_widgets),
      _step;

  try {
    for (_iterator.s(); !(_step = _iterator.n()).done;) {
      var widget = _step.value;
      var id = widget.dataset.id;
      var controller = ReactDOM.render( /*#__PURE__*/React.createElement(uidreferencewidget_widget, {
        root_el: widget
      }), widget);
      window.widgets[id] = controller;
    } // AddressWidget

  } catch (err) {
    _iterator.e(err);
  } finally {
    _iterator.f();
  }

  var address_widgets = document.getElementsByClassName("senaite-address-widget-input");

  var _iterator2 = senaite_core_widgets_createForOfIteratorHelper(address_widgets),
      _step2;

  try {
    for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
      var _widget = _step2.value;
      var _id = _widget.dataset.id;

      var _controller = ReactDOM.render( /*#__PURE__*/React.createElement(addresswidget_widget, {
        root_el: _widget
      }), _widget);

      window.widgets[_id] = _controller;
    } // PhoneWidget
    // https://github.com/jackocnr/intl-tel-input#readme

  } catch (err) {
    _iterator2.e(err);
  } finally {
    _iterator2.f();
  }

  var phone_widgets = document.getElementsByClassName("senaite-phone-widget-input");
  var error_codes = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

  var init_phone_input = function init_phone_input(el) {
    var id = el.dataset.intlTelInputId;
    var initial_country = el.dataset.initial_country;
    var preferred_countries = JSON.parse(el.dataset.preferred_countries);
    var iti = intl_tel_input_default()(el, {
      initialCountry: initial_country,
      preferredCountries: preferred_countries,
      // avoid that the dropdown is cropped in records widget
      dropdownContainer: document.body,
      // https://github.com/jackocnr/intl-tel-input#utilities-script
      utilsScript: "++plone++senaite.core.static/modules/intl-tel-input/js/utils.js"
    }); // add event handler only once

    if (id === undefined) {
      el.addEventListener("blur", function () {
        // validation
        var valid = iti.isValidNumber();
        var number = iti.getNumber();
        var field = el.closest(".field");

        if (valid) {
          field.classList.remove("error");
          field.title = "";
        } else {
          field.classList.add("error");
          var error_code = iti.getValidationError();
          var error_msg = error_codes[error_code];
          field.title = error_msg;
        } // always set the number (even if validation failed!)


        var name = el.dataset.name;
        var hidden = document.querySelector("input[name='" + name + "']");
        hidden.value = number;
      });
    }
  }; // initialize all phone widgets


  var _iterator3 = senaite_core_widgets_createForOfIteratorHelper(phone_widgets),
      _step3;

  try {
    for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
      var _widget2 = _step3.value;
      init_phone_input(_widget2);
    } // dynamically initialize new phone widgets when used in datagrid fields

  } catch (err) {
    _iterator3.e(err);
  } finally {
    _iterator3.f();
  }

  document.body.addEventListener("datagrid:row_added", function (event) {
    var row = event.detail.row;
    var input = row.querySelector(".senaite-phone-widget-input");

    if (input) {
      init_phone_input(input);
    }
  });
});
})();

/******/ })()
;
//# sourceMappingURL=seniate.core.widgets.js.map