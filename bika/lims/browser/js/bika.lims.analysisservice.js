(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
  */
  window.AnalysisServiceEditView = class AnalysisServiceEditView {
    constructor() {
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* EVENT HANDLER */
      this.on_default_method_change = this.on_default_method_change.bind(this);
      this.on_methods_change = this.on_methods_change.bind(this);
      this.on_instruments_change = this.on_instruments_change.bind(this);
      this.on_default_instrument_change = this.on_default_instrument_change.bind(this);
      this.on_instrument_assignment_allowed_change = this.on_instrument_assignment_allowed_change.bind(this);
      this.on_manual_entry_of_results_change = this.on_manual_entry_of_results_change.bind(this);
      this.on_use_default_calculation_change = this.on_use_default_calculation_change.bind(this);
      this.on_calculation_change = this.on_calculation_change.bind(this);
      this.on_display_detection_limit_selector_change = this.on_display_detection_limit_selector_change.bind(this);
    }

    load() {
      console.debug("AnalysisServiceEditView::load");
      // bind the event handler to the elements
      return this.bind_eventhandler();
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("AnalysisServiceEditView::bind_eventhandler");
      /* METHODS TAB */
      // The "Default Method" select changed
      $("body").on("change", "#archetypes-fieldname-Method #Method", this.on_default_method_change);
      // The "Methods" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Methods #Methods", this.on_methods_change);
      // The "Default Instrument" selector changed
      $("body").on("change", "#archetypes-fieldname-Instrument #Instrument", this.on_default_instrument_change);
      // The "Instruments" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Instruments #Instruments", this.on_instruments_change);
      // The "Instrument assignment is allowed" checkbox changed
      $("body").on("change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", this.on_instrument_assignment_allowed_change);
      // The "Instrument assignment is not required" checkbox changed
      $("body").on("change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", this.on_manual_entry_of_results_change);
      // The "Use the Default Calculation of Method" checkbox changed
      $("body").on("change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", this.on_use_default_calculation_change);
      // The "Calculation" selector changed
      $("body").on("change", "#archetypes-fieldname-Calculation #Calculation", this.on_calculation_change);
      /* ANALYSIS TAB */
      // The "Display a Detection Limit selector" checkbox changed
      return $("body").on("change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", this.on_display_detection_limit_selector_change);
    }

    on_default_method_change(event) {
      /*
       * Eventhandler when the "Default Method" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
    }

    on_methods_change(event) {
      /*
       * Eventhandler when the "Methods" multiselect changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_methods_change °°°");
    }

    on_instruments_change(event) {
      /*
       * Eventhandler when the "Instruments" multiselect changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
    }

    on_default_instrument_change(event) {
      /*
       * Eventhandler when the "Default Instrument" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_instrument_change °°°");
    }

    on_instrument_assignment_allowed_change(event) {
      /*
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
    }

    on_manual_entry_of_results_change(event) {
      /*
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
    }

    on_use_default_calculation_change(event) {
      /*
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
    }

    on_calculation_change(event) {
      /*
       * Eventhandler when the "Calculation" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
    }

    on_display_detection_limit_selector_change(event) {
      /*
       * Eventhandler when the "Display a Detection Limit selector" checkbox changed
       *
       * This checkbox is located on the "Analysis" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°");
    }

  };

}).call(this);
