const interfaceTranslations = {
  selectedCountryAriaLabel: "Vybraná krajina",
  noCountrySelected: "Nie je vybratá žiadna krajina",
  countryListAriaLabel: "Zoznam krajín",
  searchPlaceholder: "Vyhľadať",
  zeroSearchResults: "Neboli nájdené žiadne výsledky",
  searchResultsText(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `${count} výsledok nájdený`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    return `${count} ${isFew ? "výsledky nájdené" : "výsledkov nájdených"}`;
  },
  // additional countries (not supported by country-list library)
  ac: "Ascension",
  xk: "Kosovo"
};
export default interfaceTranslations;
