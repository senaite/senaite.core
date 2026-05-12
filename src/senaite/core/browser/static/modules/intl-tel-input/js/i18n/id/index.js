const interfaceTranslations = {
  selectedCountryAriaLabel: "Negara yang dipilih",
  noCountrySelected: "Tidak ada negara yang dipilih",
  countryListAriaLabel: "Daftar negara",
  searchPlaceholder: "Mencari",
  clearSearchAriaLabel: "Hapus pencarian",
  searchEmptyState: "Tidak ada hasil yang ditemukan",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Tidak ada hasil yang ditemukan";
    }
    if (count === 1) {
      return "1 hasil ditemukan";
    }
    return `${count} hasil ditemukan`;
  }
};
export default interfaceTranslations;
