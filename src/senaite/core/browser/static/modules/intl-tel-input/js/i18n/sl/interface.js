const interfaceTranslations = {
  selectedCountryAriaLabel: "Spremeni državo, izbrano ${countryName} (${dialCode})",
  noCountrySelected: "Izberi državo",
  countryListAriaLabel: "Seznam držav",
  searchPlaceholder: "Išči",
  clearSearchAriaLabel: "Počisti iskanje",
  zeroSearchResults: "Ni rezultatov",
  searchResultsText(count) {
    const mod100 = count % 100;
    if (mod100 === 1) {
      return `Najden ${count} rezultat`;
    }
    if (mod100 === 2) {
      return `Najdena ${count} rezultata`;
    }
    if (mod100 === 3 || mod100 === 4) {
      return `Najdeni ${count} rezultati`;
    }
    return `Najdenih ${count} rezultatov`;
  },
  // additional countries (not supported by country-list library)
  ac: "Otok Ascension",
  xk: "Kosovo"
};
export default interfaceTranslations;
