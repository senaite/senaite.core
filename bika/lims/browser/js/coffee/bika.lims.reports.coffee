### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.reports.coffee
###


class window.ReportFolderView

  load: =>
    console.debug "ReportFolderView::load"

    # load translations
    jarn.i18n.loadCatalog 'senaite.core'
    @_ = window.jarn.i18n.MessageFactory("senaite.core")

    # initialize datepickers
    @init_datepickers()

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


  init_datepickers: =>
    ###
     * Initialize date pickers
    ###
    console.debug "ReportFolderView::init_datepickers"

    curDate = new Date
    lang = jarn.i18n.currentLanguage
    y = curDate.getFullYear()
    limitString = '1900:' + y
    dateFormat = @_('date_format_short_datepicker')

    if dateFormat == 'date_format_short_datepicker'
      dateFormat = 'yy-mm-dd'

    # Initialize default settings for datepicker
    # See https://github.com/senaite/senaite.core/pull/1634
    config = $.datepicker.regional[lang] or $.datepicker.regional['']
    $("input[class*='datepicker']").datepicker(
      Object.assign(config, {
        showOn: 'focus',
        showAnim: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: dateFormat,
        maxDate: '+0d',
        numberOfMonths: 1,
        yearRange: limitString
        }
      )
    )

    $('input.datepicker_2months').datepicker("option", "numberOfMonths", 2)


  on_toggle_change: (event) =>
    ###*
     * Event handler when the toggle anchor is clicked
    ###
    console.debug "°°° ReportFolderView::on_toggle_change °°°"

    event.preventDefault()
    $(".criteria").toggle false
    div_id = event.currentTarget.id.split("_selector")[0]
    $("[id='"+div_id+"']").toggle true
