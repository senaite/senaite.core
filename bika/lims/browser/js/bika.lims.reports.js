
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.reports.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.ReportFolderView = (function() {
    function ReportFolderView() {
      this.on_toggle_change = bind(this.on_toggle_change, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    ReportFolderView.prototype.load = function() {
      console.debug("ReportFolderView::load");
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
