const interfaceTranslations = {
  selectedCountryAriaLabel: "País seleccionat",
  noCountrySelected: "No s'ha seleccionat cap país",
  countryListAriaLabel: "Llista de països",
  searchPlaceholder: "Cerca",
  clearSearchAriaLabel: "Esborra la cerca",
  searchEmptyState: "Sense resultats",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Sense resultats";
    }
    if (count === 1) {
      return "1 resultat trobat";
    }
    return `${count} resultats trobats`;
  }
};
export default interfaceTranslations;
