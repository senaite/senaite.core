const interfaceTranslations = {
  selectedCountryAriaLabel: "Change country, selected ${countryName} (${dialCode})",
  noCountrySelected: "Select country",
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
export default interfaceTranslations;
