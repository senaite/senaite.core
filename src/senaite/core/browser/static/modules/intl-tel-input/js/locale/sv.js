"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Byt land för telefonnummer, valt ${countryName} (${dialCode})",
  noCountrySelected: "Välj land för telefonnummer",
  countryListAriaLabel: "Lista över länder",
  searchPlaceholder: "Sök",
  clearSearchAriaLabel: "Rensa sökning",
  searchEmptyState: "Inga resultat hittades",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Inga resultat hittades";
    }
    return `${count} resultat hittades`;
  }
};
export default interfaceTranslations;
