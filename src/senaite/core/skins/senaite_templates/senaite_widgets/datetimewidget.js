document.addEventListener("DOMContentLoaded", () => {

  try {
    var lang = i18n.currentLanguage;
  } catch(err) {
    lang = "en";
  }

  var dt_config = $.datepicker.regional[lang] || $.datepicker.regional[''];
  var tp_config = $.timepicker.regional[lang] || $.timepicker.regional[''];
  var config = Object.assign(dt_config, tp_config);

  $('[datepicker="1"]').datepicker(
    Object.assign(config, {
      dateFormat: "yy-mm-dd",
      changeMonth: true,
      changeYear: true,
      yearRange: "-50:+20"
    }));

  $('[datetimepicker="1"]').datetimepicker(
    Object.assign(config, {
      hourGrid: 4,
      minuteGrid: 10,
      dateFormat: "yy-mm-dd",
      timeFormat: "HH:mm",
      changeMonth: true,
      changeYear: true,
      yearRange: "-100:+2"
    }));

  $('[datepicker_nofuture="1"]').on("click", function() {
    $(this).datepicker("option", "maxDate", "0")
      .click(function() { $(this).attr("value", ""); })
      .focus();
  });

  $('[datepicker_nopast="1"]').on("click", function() {
    $(this).datepicker("option", "minDate", "0")
      .click(function() { $(this).attr("value", ""); })
      .focus();
  });

});
