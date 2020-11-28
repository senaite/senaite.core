document.addEventListener("DOMContentLoaded", () => {

  try {
    var lang = i18n.currentLanguage;
  } catch(err) {
    lang = "en";
  }

  var dt_config = $.datepicker.regional[lang] || $.datepicker.regional[''];
  var tp_config = $.timepicker.regional[lang] || $.timepicker.regional[''];

  var date_format = "yy-mm-dd";
  var dt_fmt_string = "date_format_short_datepicker";
  var dt_fmt = _t(dt_fmt_string);

  if (dt_fmt != dt_fmt_string) {
    dt_fmt = dt_fmt.replaceAll(/[${}]/gi, "");
  }

  var config = Object.assign(dt_config, tp_config);

  $('[datepicker="1"]').datepicker(
    Object.assign(config, {
      dateFormat: "yy-mm-dd",
      changeMonth: true,
      changeYear: true,
      yearRange: "-150:+150",
      dateFormat: date_format
    }));

  $('[datetimepicker="1"]').datetimepicker(
    Object.assign(config, {
      hourGrid: 4,
      minuteGrid: 10,
      dateFormat: date_format,
      timeFormat: "HH:mm",
      changeMonth: true,
      changeYear: true,
      yearRange: "-150:+150"
    }));

  $('[datepicker_nofuture="1"]').on("click", function() {
    $(this).datepicker("option", {
      maxDate: "0",
      changeMonth: true,
      changeYear: true,
      yearRange: "-150:+0",
      dateFormat: date_format
    })
    .click(function() { $(this).attr("value", ""); })
    .focus();
  });

  $('[datepicker_nopast="1"]').on("click", function() {
    $(this).datepicker("option", {
      minDate: "0",
      changeMonth: true,
      changeYear: true,
      yearRange: "-0:+150",
      dateFormat: date_format
    })
    .click(function() { $(this).attr("value", ""); })
    .focus();
  });

});
