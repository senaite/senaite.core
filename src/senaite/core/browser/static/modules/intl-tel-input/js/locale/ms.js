"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Tukar negara untuk nombor telefon, dipilih ${countryName} (${dialCode})",
  noCountrySelected: "Pilih negara untuk nombor telefon",
  countryListAriaLabel: "Senarai negara",
  searchPlaceholder: "Cari",
  clearSearchAriaLabel: "Kosongkan carian",
  searchEmptyState: "Tiada hasil ditemui",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Tiada hasil ditemui";
    }
    return `${count} hasil ditemui`;
  }
};
export default interfaceTranslations;
