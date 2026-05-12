const interfaceTranslations = {
  selectedCountryAriaLabel: "ประเทศที่เลือก",
  noCountrySelected: "ไม่ได้เลือกประเทศ",
  countryListAriaLabel: "รายชื่อประเทศ",
  searchPlaceholder: "ค้นหา",
  clearSearchAriaLabel: "ล้างการค้นหา",
  searchEmptyState: "ไม่พบผลลัพธ์",
  searchSummaryAria(count) {
    if (count === 0) {
      return "ไม่พบผลลัพธ์";
    }
    if (count === 1) {
      return "พบผลลัพธ์ 1 รายการ";
    }
    return `พบผลลัพธ์ ${count} รายการ`;
  }
};
export default interfaceTranslations;
