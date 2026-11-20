"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Cambia il paese del numero di telefono, selezionato ${countryName} (${dialCode})",
  noCountrySelected: "Seleziona il paese del numero di telefono",
  countryListAriaLabel: "Elenco dei paesi",
  searchPlaceholder: "Ricerca",
  clearSearchAriaLabel: "Cancella ricerca",
  searchEmptyState: "Nessun risultato trovato",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Nessun risultato trovato";
    }
    if (count === 1) {
      return "1 risultato trovato";
    }
    return `${count} risultati trovati`;
  }
};
export default interfaceTranslations;
