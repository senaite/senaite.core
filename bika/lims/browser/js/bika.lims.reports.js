
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.reports.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.ReportFolderView = (function() {
    function ReportFolderView() {
      this.on_toggle_change = bind(this.on_toggle_change, this);
      this.init_datepickers = bind(this.init_datepickers, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    ReportFolderView.prototype.load = function() {
      console.debug("ReportFolderView::load");
      jarn.i18n.loadCatalog('senaite.core');
      this._ = window.jarn.i18n.MessageFactory("senaite.core");
      this.init_datepickers();
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    ReportFolderView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       */
      console.debug("ReportFolderView::bind_eventhandler");
      return $("body").on("click", "a[id$='_selector']", this.on_toggle_change);
    };

    ReportFolderView.prototype.init_datepickers = function() {

      /*
       * Initialize date pickers
       */
      var config, curDate, dateFormat, lang, limitString, y;
      console.debug("ReportFolderView::init_datepickers");
      curDate = new Date;
      lang = jarn.i18n.currentLanguage;
      y = curDate.getFullYear();
      limitString = '1900:' + y;
      dateFormat = this._('date_format_short_datepicker');
      if (dateFormat === 'date_format_short_datepicker') {
        dateFormat = 'yy-mm-dd';
      }
      config = $.datepicker.regional[lang] || $.datepicker.regional[''];
      $("input[class*='datepicker']").datepicker(Object.assign(config, {
        showOn: 'focus',
        showAnim: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: dateFormat,
        maxDate: '+0d',
        numberOfMonths: 1,
        yearRange: limitString
      }));
      return $('input.datepicker_2months').datepicker("option", "numberOfMonths", 2);
    };

    ReportFolderView.prototype.on_toggle_change = function(event) {

      /**
       * Event handler when the toggle anchor is clicked
       */
      var div_id;
      console.debug("°°° ReportFolderView::on_toggle_change °°°");
      event.preventDefault();
      $(".criteria").toggle(false);
      div_id = event.currentTarget.id.split("_selector")[0];
      return $("[id='" + div_id + "']").toggle(true);
    };

    return ReportFolderView;

  })();

}).call(this);
