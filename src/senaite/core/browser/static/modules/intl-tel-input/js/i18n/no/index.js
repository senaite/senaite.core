const interfaceTranslations = {
  selectedCountryAriaLabel: "Valgt land",
  noCountrySelected: "Ingen land er valgt",
  countryListAriaLabel: "Liste over land",
  searchPlaceholder: "Søk",
  clearSearchAriaLabel: "Tøm søk",
  searchEmptyState: "Ingen resultater funnet",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Ingen resultater funnet";
    }
    if (count === 1) {
      return "1 resultat funnet";
    }
    return `${count} resultater funnet`;
  }
};
export default interfaceTranslations;
