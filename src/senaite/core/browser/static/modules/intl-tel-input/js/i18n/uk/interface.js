const interfaceTranslations = {
  selectedCountryAriaLabel: "Обрана країна",
  noCountrySelected: "Країну не обрано",
  countryListAriaLabel: "Список країн",
  searchPlaceholder: "Шукати",
  zeroSearchResults: "Результатів не знайдено",
  searchResultsText(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `Знайдено ${count} результат`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    return `Знайдено ${count} ${isFew ? "результати" : "результатів"}`;
  },
  // additional countries (not supported by country-list library)
  ac: "Острів Вознесіння",
  xk: "Косово"
};
export default interfaceTranslations;
