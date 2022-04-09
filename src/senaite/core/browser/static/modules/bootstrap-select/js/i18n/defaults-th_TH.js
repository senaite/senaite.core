/*!
 * Bootstrap-select v1.13.18 (https://developer.snapappointments.com/bootstrap-select)
 *
 * Copyright 2012-2020 SnapAppointments, LLC
 * Licensed under MIT (https://github.com/snapappointments/bootstrap-select/blob/master/LICENSE)
 */

(function (root, factory) {
  if (root === undefined && window !== undefined) root = window;
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module unless amdModuleId is set
    define(["jquery"], function (a0) {
      return (factory(a0));
    });
  } else if (typeof module === 'object' && module.exports) {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like environments that support module.exports,
    // like Node.
    module.exports = factory(require("jquery"));
  } else {
    factory(root["jQuery"]);
  }
}(this, function (jQuery) {

(function ($) {
  $.fn.selectpicker.defaults = {
    noneSelectedText: 'ไม่ได้เลือกอะไรเลย',
    noneResultsText: 'ไม่มีผลลัพธ์ที่ตรงกัน {0}',
    countSelectedText: '{0} รายการที่เลือก',
    maxOptionsText: ['เกินจำนวนที่กำหนด (สูงสุด {n} รายการ)', 'เกินจำนวนที่กำหนด (สูงสุด {n} กลุ่ม)'],
    selectAllText: 'เลือกทั้งหมด',
    deselectAllText: 'ไม่เลือกทั้งหมด',
    multipleSeparator: ', '
  };
})(jQuery);


}));
//# sourceMappingURL=defaults-th_TH.js.map