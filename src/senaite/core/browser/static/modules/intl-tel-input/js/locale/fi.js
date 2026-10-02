"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Vaihda maa puhelinnumeroa varten, valittu ${countryName} (${dialCode})",
  noCountrySelected: "Valitse maa puhelinnumeroa varten",
  countryListAriaLabel: "Luettelo maista",
  searchPlaceholder: "Haku",
  clearSearchAriaLabel: "Tyhjennä haku",
  searchEmptyState: "Ei tuloksia",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Ei tuloksia";
    }
    if (count === 1) {
      return "1 tulos löytyi";
    }
    return `${count} tulosta löytyi`;
  }
};
export default interfaceTranslations;
