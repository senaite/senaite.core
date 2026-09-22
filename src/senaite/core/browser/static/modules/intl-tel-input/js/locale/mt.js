"use strict";
import countryNames from "./country-names/mt.js";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Biddel il-pajjiż għan-numru tat-telefon, attwalment magħżul ${countryName} (${dialCode})",
  noCountrySelected: "Agħżel il-pajjiż għan-numru tat-telefon",
  countryListAriaLabel: "Lista tal-pajjiżi",
  searchPlaceholder: "Fittex",
  clearSearchAriaLabel: "Ħassar it-tfittxija",
  searchEmptyState: "Ma nstabux riżultati",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Ma nstabux riżultati";
    }
    if (count === 1) {
      return "Instab riżultat 1";
    }
    const mod100 = count % 100;
    if (mod100 >= 2 && mod100 <= 10) {
      return `Instabu ${count} riżultati`;
    }
    if (mod100 >= 11 && mod100 <= 19) {
      return `Instabu ${count}-il riżultat`;
    }
    return `Instabu ${count} riżultat`;
  }
};
export default { ...interfaceTranslations, countryNames };
