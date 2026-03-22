const interfaceTranslations = {
  selectedCountryAriaLabel: "Spremeni državo, izbrano ${countryName} (${dialCode})",
  noCountrySelected: "Izberi državo",
  countryListAriaLabel: "Seznam držav",
  searchPlaceholder: "Išči",
  clearSearchAriaLabel: "Počisti iskanje",
  searchEmptyState: "Ni rezultatov",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Ni rezultatov";
    }
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
  }
};
export default interfaceTranslations;
