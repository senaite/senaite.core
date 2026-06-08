const interfaceTranslations = {
  selectedCountryAriaLabel: "Odabrana zemlja",
  noCountrySelected: "Zemlja nije odabrana",
  countryListAriaLabel: "Lista zemalja",
  searchPlaceholder: "Pretraži",
  zeroSearchResults: "Nema pronađenih rezultata",
  searchResultsText(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `Pronađen ${count} rezultat`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    return `${isFew ? "Pronađena" : "Pronađeno"} ${count} rezultata`;
  },
  // additional countries (not supported by country-list library)
  ac: "Ascension",
  xk: "Kosovo"
};
export default interfaceTranslations;
