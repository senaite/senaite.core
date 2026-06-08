const interfaceTranslations = {
  selectedCountryAriaLabel: "Επιλεγμένη χώρα",
  noCountrySelected: "Δεν έχει επιλεγεί χώρα",
  countryListAriaLabel: "Κατάλογος χωρών",
  searchPlaceholder: "Αναζήτηση",
  clearSearchAriaLabel: "Εκκαθάριση αναζήτησης",
  searchEmptyState: "Δεν βρέθηκαν αποτελέσματα",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Δεν βρέθηκαν αποτελέσματα";
    }
    if (count === 1) {
      return "Βρέθηκε 1 αποτέλεσμα";
    }
    return `Βρέθηκαν ${count} αποτελέσματα`;
  }
};
export default interfaceTranslations;
