"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Змінити країну для номера телефону, обрана ${countryName} (${dialCode})",
  noCountrySelected: "Виберіть країну для номера телефону",
  countryListAriaLabel: "Список країн",
  searchPlaceholder: "Шукати",
  clearSearchAriaLabel: "Очистити пошук",
  searchEmptyState: "Результатів не знайдено",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Результатів не знайдено";
    }
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) {
      return `Знайдено ${count} результат`;
    }
    const isFew = mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14);
    if (isFew) {
      return `Знайдено ${count} результати`;
    }
    return `Знайдено ${count} результатів`;
  }
};
export default interfaceTranslations;
