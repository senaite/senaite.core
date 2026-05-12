const interfaceTranslations = {
  selectedCountryAriaLabel: "Vybraná krajina",
  noCountrySelected: "Nie je vybratá žiadna krajina",
  countryListAriaLabel: "Zoznam krajín",
  searchPlaceholder: "Vyhľadať",
  clearSearchAriaLabel: "Vymazať vyhľadávanie",
  searchEmptyState: "Neboli nájdené žiadne výsledky",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Neboli nájdené žiadne výsledky";
    }
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `${count} výsledok nájdený`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    if (isFew) {
      return `${count} výsledky nájdené`;
    }
    return `${count} výsledkov nájdených`;
  }
};
export default interfaceTranslations;
