const interfaceTranslations = {
  selectedCountryAriaLabel: "Выбранная страна",
  noCountrySelected: "Страна не выбрана",
  countryListAriaLabel: "Список стран",
  searchPlaceholder: "Поиск",
  clearSearchAriaLabel: "Очистить поиск",
  searchEmptyState: "результатов не найдено",
  searchSummaryAria(count) {
    if (count === 0) {
      return "результатов не найдено";
    }
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `найден ${count} результат`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    if (isFew) {
      return `Найдено ${count} результата`;
    }
    return `Найдено ${count} результатов`;
  }
};
export default interfaceTranslations;
