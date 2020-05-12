
/* Please use this command to compile this file into the parent directory:
    coffee --no-header -w -o ../ -c senaite.core.partitionmagic.coffee
 */

(function() {
  var PartitionController,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  document.addEventListener("DOMContentLoaded", function() {
    console.debug("*** DOMContentLoaded: --> Loading Partition Controller");
    return window.partition_controller = new PartitionController();
  });

  PartitionController = (function() {

    /*
     * Partition Controller
     */
    function PartitionController() {
      this.on_analysis_click = bind(this.on_analysis_click, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.bind_eventhandler();
      return this;
    }

    PartitionController.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the body and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("PartitionController::bind_eventhandler");
      return $("body").on("click", "tr.analysis", this.on_analysis_click);
    };

    PartitionController.prototype.on_analysis_click = function(event) {

      /*
       * Eventhandler for Analysis Click
       */
      var $el, el, me;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      if (event.target.type !== "checkbox") {
        return $("input[type=checkbox]", $el).click();
      }
    };

    return PartitionController;

  })();

}).call(this);
