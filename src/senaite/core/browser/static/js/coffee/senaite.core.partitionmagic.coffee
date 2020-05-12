### Please use this command to compile this file into the parent directory:
    coffee --no-header -w -o ../ -c senaite.core.partitionmagic.coffee
###

# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** DOMContentLoaded: --> Loading Partition Controller"
  window.partition_controller = new PartitionController()


class PartitionController
  ###
   * Partition Controller
  ###

  constructor: ->
    # bind the event handler to the elements
    @bind_eventhandler()
    return @

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the body and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "PartitionController::bind_eventhandler"

    # Categories header clicked
    $("body").on "click", "tr.analysis", @on_analysis_click

  on_analysis_click: (event) =>
    ###
     * Eventhandler for Analysis Click
    ###

    me = this
    el = event.currentTarget
    $el = $(el)

    # click the checkbox
    if event.target.type isnt "checkbox"
      $("input[type=checkbox]", $el).click()
