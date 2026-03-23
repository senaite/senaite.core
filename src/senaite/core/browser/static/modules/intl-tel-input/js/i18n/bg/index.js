const interfaceTranslations = {
  selectedCountryAriaLabel: "Избрана държава",
  noCountrySelected: "Няма избрана държава",
  countryListAriaLabel: "Списък на страните",
  searchPlaceholder: "Търсене",
  clearSearchAriaLabel: "Изчистване на търсенето",
  searchEmptyState: "Няма намерени резултати",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Няма намерени резултати";
    }
    if (count === 1) {
      return "Намерен е 1 резултат";
    }
    return `${count} намерени резултата`;
  }
};
export default interfaceTranslations;
