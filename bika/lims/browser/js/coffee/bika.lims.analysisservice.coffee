### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
###


class window.AnalysisServiceEditView

  load: =>
    console.debug "AnalysisServiceEditView::load"


    # bind the event handler to the elements
    @bind_eventhandler()


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
    ###
    console.debug "AnalysisServiceEditView::bind_eventhandler"


    ### METHODS TAB ###

    # The "Default Method" select changed
    $("body").on "change", "#archetypes-fieldname-Method #Method", @on_default_method_change

    # The "Methods" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Methods #Methods", @on_methods_change

    # The "Default Instrument" selector changed
    $("body").on "change", "#archetypes-fieldname-Instrument #Instrument", @on_default_instrument_change

    # The "Instruments" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Instruments #Instruments", @on_instruments_change

    # The "Instrument assignment is allowed" checkbox changed
    $("body").on "change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", @on_instrument_assignment_allowed_change

    # The "Instrument assignment is not required" checkbox changed
    $("body").on "change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", @on_manual_entry_of_results_change

    # The "Use the Default Calculation of Method" checkbox changed
    $("body").on "change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", @on_use_default_calculation_change

    # The "Calculation" selector changed
    $("body").on "change", "#archetypes-fieldname-Calculation #Calculation", @on_calculation_change


    ### ANALYSIS TAB ###

    # The "Display a Detection Limit selector" checkbox changed
    $("body").on "change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", @on_display_detection_limit_selector_change



  ### EVENT HANDLER ###


  on_default_method_change: (event) =>
    ###
     * Eventhandler when the "Default Method" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_method_change °°°"


  on_methods_change: (event) =>
    ###
     * Eventhandler when the "Methods" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_methods_change °°°"


  on_instruments_change: (event) =>
    ###
     * Eventhandler when the "Instruments" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instruments_change °°°"


  on_default_instrument_change: (event) =>
    ###
     * Eventhandler when the "Default Instrument" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_instrument_change °°°"


  on_instrument_assignment_allowed_change: (event) =>
    ###
     * Eventhandler when the "Instrument assignment is allowed" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°"


  on_manual_entry_of_results_change: (event) =>
    ###
     * Eventhandler when the "Instrument assignment is not required" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°"


  on_use_default_calculation_change: (event) =>
    ###
     * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_use_default_calculation_change °°°"


  on_calculation_change: (event) =>
    ###
     * Eventhandler when the "Calculation" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_calculation_change °°°"


  on_display_detection_limit_selector_change: (event) =>
    ###
     * Eventhandler when the "Display a Detection Limit selector" checkbox changed
     *
     * This checkbox is located on the "Analysis" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°"
