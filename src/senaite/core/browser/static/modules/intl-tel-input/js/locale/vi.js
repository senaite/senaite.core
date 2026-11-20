"use strict";
const interfaceTranslations = {
  selectedCountryAriaLabel: "Thay đổi quốc gia cho số điện thoại, đã chọn ${countryName} (${dialCode})",
  noCountrySelected: "Chọn quốc gia cho số điện thoại",
  countryListAriaLabel: "Danh sách các quốc gia",
  searchPlaceholder: "Khám xét",
  clearSearchAriaLabel: "Xóa tìm kiếm",
  searchEmptyState: "Không tìm thấy kết quả nào",
  searchSummaryAria(count) {
    if (count === 0) {
      return "Không tìm thấy kết quả nào";
    }
    return `Đã tìm thấy ${count} kết quả`;
  }
};
export default interfaceTranslations;
