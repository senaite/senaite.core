const interfaceTranslations = {
  selectedCountryAriaLabel: "Выбранная страна",
  noCountrySelected: "Страна не выбрана",
  countryListAriaLabel: "Список стран",
  searchPlaceholder: "Поиск",
  zeroSearchResults: "результатов не найдено",
  searchResultsText(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `найден ${count} результат`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    return `Найдено ${count} ${isFew ? "результата" : "результатов"}`;
  },
  // additional countries (not supported by country-list library)
  ac: "Остров Вознесения",
  xk: "Косово"
};
export default interfaceTranslations;
