### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.reports.coffee
###


class window.ReportFolderView

  load: =>
    console.debug "ReportFolderView::load"

    # initialize toggle anchors
    @bind_eventhandler()


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
    ###
    console.debug "ReportFolderView::bind_eventhandler"

    # When the anchor for a given report is selected, display the report form
    $("body").on "click", "a[id$='_selector']", @on_toggle_change


  on_toggle_change: (event) =>
    ###*
     * Event handler when the toggle anchor is clicked
    ###
    console.debug "°°° ReportFolderView::on_toggle_change °°°"

    event.preventDefault()
    $(".criteria").toggle false
    div_id = event.currentTarget.id.split("_selector")[0]
    $("[id='"+div_id+"']").toggle true
