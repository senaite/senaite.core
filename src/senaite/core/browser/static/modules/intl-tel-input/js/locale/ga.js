"use strict";
import countryNames from "./country-names/ga.js";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Athraigh tír don uimhir theileafóin, roghnaithe faoi láthair ${countryName} (${dialCode})",
  noCountrySelected: "Roghnaigh tír don uimhir theileafóin",
  countryListAriaLabel: "Liosta tíortha",
  searchPlaceholder: "Cuardaigh",
  clearSearchAriaLabel: "Glan an cuardach",
  searchEmptyState: "Níor aimsíodh aon torthaí",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Níor aimsíodh aon torthaí";
    }
    if (count === 1) {
      return "1 toradh aimsithe";
    }
    if (count >= 2 && count <= 6) {
      return `${count} thoradh aimsithe`;
    }
    if (count >= 7 && count <= 10) {
      return `${count} dtoradh aimsithe`;
    }
    return `${count} toradh aimsithe`;
  }
};
export default { ...interfaceTranslations, countryNames };
