### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
###


class window.BikaListingTableView
  ###
  * Controller class for Bika Listing Table view
  ###

  load: =>
    console.debug "ListingTableView::load"

    # bind the event handler to the elements
    @bind_eventhandler()

    # flag to signal async wf button loading
    @loading_transitions = no

    # toggle columns cookie name
    @toggle_cols_cookie = "toggle_cols"

    # Initially load the transitions
    @load_transitions()

    # dev only
    window.tv = @


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "ListingTableView::bind_eventhandler"

    # Table header clicked for sorting
    $("form").on "click", "th.sortable", @on_column_header_click

    # Show More clickd
    $("form").on "click", "a.bika_listing_show_more", @on_show_more_click

    # Single checkbox clicked
    $("form").on "click", "input[type='checkbox'][id*='_cb_']", @on_checkbox_click

    # Check all checkbox clicked
    $("form").on "click", "input[id*='select_all']", @on_select_all_click

    # Enter keypress in search field
    $("form").on "keypress", ".filter-search-input", @on_search_field_keypress

    # Search button clicked (magnifier in search field)
    $("form").on "click", ".filter-search-button", @on_search_button_click

    # Context menu
    $("form").on 'contextmenu', "th[id^='foldercontents-']", @on_contextmenu

    # Workflow Button
    $("form").on "click", "input.workflow_action_button", @on_workflow_button_click

    # Autosave – seems to be used by sample and analysis views
    $("form").on "change", "input.autosave, select.autsave", @on_autosave_field_change

    # Category headers
    $("form").on "click", "th.collapsed, th.expanded", @on_category_header_click

    # Results entry
    $("form").on "change", ".listing_string_entry, .listing_select_entry", @on_listing_entry_change
    $("form").on "keypress", ".listing_string_entry, .listing_select_entry", @on_listing_entry_keypress

    # Review state filter buttons
    $("form").on "click", "td.review_state_selector a", @on_review_state_filter_click

    # Document click
    $(document).on "click", @on_click

    # bind event handler for contextmenu clicks
    $(document).on "click", ".contextmenu tr", @on_contextmenu_item_click

    # Ajax form submit events
    $(this).on "ajax:submit:start", @on_ajax_submit_start
    $(this).on "ajax:submit:end", @on_ajax_submit_end


  ### METHODS ###

  ajax_submit: (options={}) =>
    ###
     * Ajax Submit with automatic event triggering and some sane defaults
    ###
    console.debug "°°° ajax_submit °°°"

    # some sane option defaults
    options.type ?= "POST"
    options.url ?= window.location.href
    options.context ?= this

    console.debug ">>> ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = =>
        $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done


  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url or window.portal_url


  get_base_url: =>
    ###
     * Return the current base url
    ###
    url = window.location.href
    return url.split('?')[0]


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_cookie: (name) =>
    ###
     * read the value of the cookie
    ###
    name = "#{name}="
    cookies = document.cookie.split ";"

    i = 0
    while i < cookies.length
      c = cookies[i]
      while c.charAt(0) == " "
        c = c.substring(1, c.length)
      if c.indexOf(name) == 0
        return unescape(c.substring(name.length, c.length))
      i = i + 1
    return null


  set_cookie: (name, value, days) =>
    ###
     * set the value of the cookie
    ###
    if days
      date = new Date
      date.setTime date.getTime() + days * 24 * 60 * 60 * 1000
      expires = date.toGMTString()
    else
      expires = ""
    cookie = "#{name}=#{escape(value)}; expires=#{expires}; path=/;"
    document.cookie = cookie
    return true


  get_toggle_cookie_key: (form_id) =>
    ###
     * Make a unique toggle cookie key for the current listing site
    ###
    portal_type = $("##{form_id} input[name=portal_type]").val()
    return "#{portal_type}#{form_id}"


  toggle_sort_order: (sort_order) =>
    ###
     * Toggle the sort_order value
    ###
    if sort_order == "ascending"
      return "descending"
    return "ascending"


  get_toggle_cols: (form_id) =>
    ###
     * Get the value of the toggle cols input field
    ###
    toggle_cols = $("##{form_id}_toggle_cols")
    if toggle_cols.length == 0
      return {}
    return $.parseJSON toggle_cols.val()


  toggle_column: (form_id, col_id) =>
    ###
     * Toggle column by form and column id
    ###

    # get the form object
    form = $("form##{form_id}")
    # get the listing table within the form
    table = $("table.bika-listing-table", form)
    # get the toggle column settings of this page
    toggle_cols = @get_toggle_cols form_id
    # read the current value of the toggle cookie
    cookie = $.parseJSON(@get_cookie(@toggle_cols_cookie) or "{}")
    # get the right key for this page
    cookie_key = @get_toggle_cookie_key form_id
    # current set columns
    columns = cookie[cookie_key]

    # initialize columns if not yet set
    if !columns
      columns = []
      $.each toggle_cols, (name, record) ->
        # only append current visible columns
        if $("#foldercontents-#{name}-column").length > 0
          columns.push name

    # Set default toggle columns
    if col_id == _('Default')
      console.debug "*** Set DEFAULT toggle columns ***"
      # delete the settings for this page
      delete cookie[cookie_key]

    # Set all toggle columns
    else if col_id == _('All')
      console.debug "*** Set ALL toggle columns ***"
      # add all possible columns which have the toggle state
      all_cols = []
      $.each toggle_cols, (name, record) ->
        all_cols.push name
      # set the cookie with the updated value
      cookie[cookie_key] = all_cols

    # Toggle individual columns
    else
      if col_id not of toggle_cols
        console.warn "Invalid column name: '#{col_id}'"
        return
      if columns.indexOf(col_id) > -1
        # toggle off
        console.debug "*** Toggle #{col_id} OFF ***"
        columns.splice columns.indexOf(col_id), 1
      else
        # toggle on
        console.debug "*** Toggle #{col_id} ON ***"
        columns.push col_id
      # set the cookie with the updated value
      cookie[cookie_key] = columns

    # set the toggle config cookie
    @set_cookie @toggle_cols_cookie, $.toJSON(cookie), 365

    # prepare the form data
    form_data = new FormData form[0]
    form_data.set "table_only", form_id

    # send the new data to the server
    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      $(table).replaceWith data
      table = $("table.bika-listing-table", form)
      tooltip = $(".tooltip")
      # re-render the tooltip
      if tooltip.length > 0
        style = tooltip.attr "style"
        menu = @make_context_menu table
        menu = $(menu).appendTo "body"
        menu.attr "style", style


  sort_column: (form_id, sort_index) =>
    ###
     * Sort column by form and sort index
    ###

    # get the form object
    form = $("form##{form_id}")
    # get the listing table within the form
    table = $("table.bika-listing-table", form)

    # hidden input fields which holds the current sort_on value
    sort_on = $("[name=#{form_id}_sort_on]")
    # hidden input field which holds the current sort_order value
    sort_order = $("[name=#{form_id}_sort_order]")
    # current sort_on value
    sort_on_value = sort_on.val()
    # current sort_order value
    sort_order_value = sort_order.val()

    # update sort_on value
    sort_on.val sort_index
    # update sort_order value
    sort_order.val @toggle_sort_order sort_order_value

    # prepare the form data
    form_data = new FormData form[0]
    form_data.set "table_only", form_id

    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      $(table).replaceWith data
      @load_transitions()


  toggle_category: (form_id, cat_id) =>
    ###
     * Toggle category by form and category id
    ###

    # get the form object
    form = $("form##{form_id}")

    cat = $("th.cat_header[cat=#{cat_id}]")
    placeholder = $("tr[data-ajax_category=#{cat_id}")
    expanded = cat.hasClass "expanded"
    cat_items = $("tr[cat=#{cat_id}]")

    # Toggle expand/collapsed class
    cat.toggleClass "expanded collapsed"

    # Just hide/show if the items are already loaded
    if cat_items.length > 0
      console.debug "ListingTableView::toggle_category: Category #{cat_id} is already expanded -> Toggle only"
      cat_items.toggle()
      return

    # load the items asynchronous
    cat_url = $("input[name=ajax_categories_url]").val()
    base_url = @get_base_url()
    url = cat_url or base_url

    # prepare a new form data
    form_data = new FormData()
    form_data.set "cat", cat_id
    form_data.set "form_id", form_id
    form_data.set "ajax_category_expand", 1

    # send the new data to the server
    @ajax_submit
      url: url
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      # replace the placeholder with the loaded rows
      placeholder.replaceWith data
      @load_transitions()


  filter_state: (form_id, state_id) =>
    ###
     * Filter listing by review_state
    ###

    # get the form object
    form = $("form##{form_id}")
    table = $("table.bika-listing-table", form)

    input_name = "#{form_id}_review_state"
    input = $("input[name=#{input_name}]", form)
    if input.length == 0
      input = form.append "<input name='#{input_name}' value='#{state_id}' type='hidden'/>"
    input.val state_id

    # prepare the form data
    form_data = new FormData form[0]
    form_data.set "table_only", form_id
    form_data.set "#{form_id}_review_state", state_id

    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      $(table).replaceWith data
      @load_transitions()


  show_more: (form_id, pagesize, limit_from) =>
    ###
     * Show more
    ###

    # get the form object
    form = $("form##{form_id}")
    table = $("table.bika-listing-table", form)
    tbody = $("tbody.item-listing-tbody", table)
    show_more = $("##{form_id} a.bika_listing_show_more")

    # sane defaults
    pagesize ?= 30
    limit_from ?= 0

    # prepare the form data
    form_data = new FormData form[0]
    form_data.set "rows_only", form_id
    form_data.set "#{form_id}_pagesize", pagesize
    form_data.set "#{form_id}_limit_from", limit_from

    # Advanced filter bar options
    filter_options = []
    filters1 = $(".bika_listing_filter_bar input[name][value!='']")
    filters2 = $(".bika_listing_filter_bar select option:selected[value!='']")
    filters = $.merge(filters1, filters2)
    $(filters).each (e) ->
      filter_options.push [
        $(this).attr('name')
        $(this).val()
      ]
    if filter_options.length > 0
      form_data.set "bika_listing_filter_bar", $.toJSON(filter_options)

    show_more.fadeOut()
    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      # filter out all <tr> elements
      rows = $(data).filter "tr"
      # probably further pages exist when this returns 0
      if rows.length % pagesize == 0
        show_more.fadeIn()
      # flush the whole table when there is no limit from
      if limit_from == 0
        $(tbody).empty()
      $(tbody).append rows
      # update the counter with the number of rendered rows
      numitems = $("table.bika-listing-table[form_id=#{form_id}] tbody.item-listing-tbody tr").length
      $("##{form_id} span.number-items").html numitems
      # update the show more control
      show_more.attr "data-limitfrom", numitems
      show_more.attr "data-pagesize", pagesize
      # reload the transitions
      @load_transitions()


  parse_int: (thing, fallback=0) =>
    ###
     * Safely parse to an integer
    ###
    number = parseInt thing
    return number or fallback


  load_transitions: (table) ->
    ###
     * Fetch allowed transitions for all the objects listed in bika_listing and
     * sets the value for the attribute 'data-valid_transitions' for each check
     * box next to each row.
     * The process requires an ajax call, so the function keeps checkboxes
     * disabled until the allowed transitions for the associated object are set.
    ###

    self = this

    # Recursively call for all listing tables of the current page
    if !table
      $("table.bika-listing-table").each (index) ->
        self.load_transitions this

    # The listing table object
    $table = $(table)

    wf_buttons = $(table).find("span.workflow_action_buttons")
    if @loading_transitions or $(wf_buttons).length == 0
        # If show_workflow_action_buttons param is set to False in the
        # view, or transitions are being loaded already, do nothing
        return

    uids = []
    checkall = $("input[id*='select_all']", $table)

    $(checkall).hide()

    # Update valid transitions for elements which have not yet been updated:
    wo_trans = $("input[id*='_cb_'][data-valid_transitions='{}']")

    $(wo_trans).prop "disabled", yes
    $(wo_trans).each (e) ->
      uids.push $(this).val()

    if uids.length == 0
      return

    # load possible transitions
    @loading_transitions = yes
    @ajax_submit
      url: "#{@get_portal_url()}/@@API/allowedTransitionsFor_many"
      data:
        _authenticator: @get_authenticator()
        uid: $.toJSON(uids)
    .done (data) ->
      @loading_transitions = no
      $("input[id*='select_all']").fadeIn()

      # setting a data attribute on each checkbox
      if "transitions" of data
        $.each data.transitions, (index, record) ->
          uid = record.uid
          trans = record.transitions
          checkbox = $("input[id*='_cb_'][value='#{uid}']")
          checkbox.attr "data-valid_transitions", $.toJSON(trans)
          $(checkbox).prop "disabled", false

      # re-render the transition buttons in case the user clicked the back
      # button of the browser
      @render_transition_buttons table


  render_transition_buttons: (table) ->
    ### Render workflow transition buttons to the table
     *
     * Re-generates the workflow action buttons from the bottom of the list in
     * accordance with the allowed transitions for the currently selected items.
     * This is, makes the intersection within all allowed transitions and adds
     * the corresponding buttons to the workflow action bar.
    ###

    # reference to this instance
    self = this

    wf_buttons = $(table).find("span.workflow_action_buttons")
    if $(wf_buttons).length == 0
        # If `show_workflow_action_buttons` param is set to False in the view,
        # do nothing
        return

    allowed_transitions = []

    # hidden_transitions and restricted are hidden fields containing comma
    # separated list of transition IDs.
    hidden_transitions = $(table).find("input[id='hide_transitions']")
    hidden_transitions = if $(hidden_transitions).length == 1 then $(hidden_transitions).val() else ''
    hidden_transitions = if hidden_transitions == '' then [] else hidden_transitions.split(',')

    restricted_transitions = $(table).find("input[id='restricted_transitions']")
    restricted_transitions = if $(restricted_transitions).length == 1 then $(restricted_transitions).val() else ''
    restricted_transitions = if restricted_transitions == '' then [] else restricted_transitions.split(',')

    checked = $(table).find("input[id*='_cb_']:checked")

    $(checked).each (index) ->
      transitions = $.parseJSON($(this).attr("data-valid_transitions"))
      if ! transitions.length
        return

      # Do not want transitions other than those defined in bikalisting
      if restricted_transitions.length > 0
        transitions = transitions.filter (el) ->
          return restricted_transitions.indexOf(el.id) > -1

      # Do not show hidden transitions
      if hidden_transitions.length > 0
        transitions = transitions.filter (el) ->
          return hidden_transitions.indexOf(el.id) < 0

      # We only want the intersection within all selected items
      if allowed_transitions.length > 0
        transitions = transitions.filter (el) ->
          return allowed_transitions.indexOf(el) > -1
      else
        allowed_transitions = transitions
        # and the inverse of the intersection
        if transitions.length > 0
          allowed_transitions = allowed_transitions.filter (el) ->
            return transitions.indexOf(el) > -1

    # Flush existing Workflow buttons
    $(wf_buttons).html ""

    # Generate the action buttons
    $.each allowed_transitions, (index, record) ->
      transition = record.id
      url = ""
      value = PMF(record.title)
      button = self.make_wf_button transition, url, value
      $(wf_buttons).append button

    # Add now custom actions
    if $(checked).length > 0
      custom_transitions = $(table).find("input[type='hidden'].custom_transition")

      $.each custom_transitions, (index, element) ->
        transition = $(element).val()
        url = $(element).attr "url"
        value = $(element).attr "title"
        button = self.make_wf_button transition, url, value
        $(wf_buttons).append button


  make_wf_button: (transition, url, value) ->
    ###
     * Make a workflow button
    ###
    button = "<input id='#{transition}_transition'
                     class='context workflow_action_button action_button allowMultiSubmit'
                     type='submit'
                     url='#{url}'
                     value='#{value}'
                     transition='#{transition}'
                     name='workflow_action_button'/>&nbsp;"
    return button


  search: (form_id, searchterm) ->
    ###
     * Search in table and expand the rows
    ###

    # get the form object
    form = $("form##{form_id}")
    form_id = form.attr "id"
    table = $("table.bika-listing-table", form)

    form_data = new FormData form[0]
    form_data.set "table_only", form_id
    form_data.set "#{form_id}_filter", searchterm

    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      # replace table with server data
      table = $(table).replaceWith data
      # focus on the search field
      $(".filter-search-input", form).select()
      @load_transitions()


  make_context_menu: (table) ->
    ###
     * Build context menu HTML
    ###
    console.debug "°°° ListingTableView::make_context_menu °°°"

    # remove any existing tooltip
    $(".tooltip").remove()

    form = $(table).parents "form"
    form_id = form.attr "id"
    portal_url = @get_portal_url()

    # toggle'able columns are stored in a hidden input field, e.g.
    # {"getStorageLocation": {"index": "getStorageLocationTitle",
    #  "toggle": false, "sortable": true, "title": "Storage Location"}, ...}
    toggle_cols = $("##{form_id}_toggle_cols")

    # return if the data was not found
    if !toggle_cols.val()
      console.warn "Could not get toggle column info from input field #{toggle_cols}"
      return false

    sorted_toggle_cols = []

    $.each $.parseJSON(toggle_cols.val()), (column, record) ->
      record.id = column
      record.title = _(record.title) or _(record.id)
      sorted_toggle_cols.push record
      return

    sorted_toggle_cols.sort (a, b) ->
        titleA = a.title.toLowerCase()
        titleB = b.title.toLowerCase()
        if titleA < titleB
            return -1
        if titleA > titleB
            return 1
        return 0

    toggleable_columns = ""
    $.each sorted_toggle_cols, (index, record) ->
      column_exists = $("#foldercontents-#{record.id}-column")
      if column_exists.length > 0
        col = """<tr class="enabled" col_id="#{record.id}" form_id="#{form_id}">
          <td>&#10003;</td>
          <td>#{record.title or record.id}</td>
        </tr>
        """
      else
        col = """<tr col_id=#{record.id} form_id="#{form_id}">
          <td>&nbsp;</td>
          <td>#{record.title or record.id}</td>
        </tr>
        """
      # append row to list
      toggleable_columns += col

    # Note: This markup is bootstrap ready:
    #       http://getbootstrap.com/docs/3.3/javascript/#tooltips
    menu = """<div class="tooltip bottom">
      <div class="tooltip-inner">
        <table class="contextmenu" cellpadding="0" cellspacing="0">
          <tr>
            <th colspan="2">#{_("Display columns")}</th>
          </tr>
          #{toggleable_columns}
          <tr col_id="#{_("All")}" form_id="#{form_id}">
            <td style="border-top:1px solid #ddd;">&nbsp;</td>
            <td style="border-top:1px solid #ddd;">#{_("All")}</td>
          </tr>
          <tr col_id="#{_("Default")}" form_id="#{form_id}">
            <td>&nbsp;</td>
            <td>#{_("Default")}</td>
          </tr>
        </table>
      </div>
      <div class="tooltip-arrow"></div>
    </div>
    """

    return menu


  ### EVENT HANDLER ###

  on_click: (event) =>
    ###
     * Eventhandler for all clicks
    ###
    el = $(event.target)

    # dismiss the tooltip
    if el.parents(".tooltip").length == 0
      $(".tooltip").remove()


  on_review_state_filter_click: (event) =>
    ###
     * Eventhandler for review state filter buttons
    ###
    console.debug "°°° ListingTableView::on_review_state_filter_click °°°"

    # prevent full page reload
    event.preventDefault()

    el = event.currentTarget
    $el = $(el)

    form = $el.parents "form"
    form_id = form.attr "id"
    state_id = $el.attr "value"

    @filter_state form_id, state_id


  on_listing_entry_change: (event) =>
    ###
     * Eventhandler for listing entries (results capturing)
    ###
    console.debug "°°° ListingTableView::on_listing_entry_change °°°"

    el = event.currentTarget
    $el = $(el)

    uid = $el.attr "uid"
    tr = $el.parents "tr#folder-contents-item-#{uid}"
    checkbox = tr.find "input[id$=_cb_#{uid}]"

    if $(checkbox).length == 1
      table = $(checkbox).parents "table.bika-listing-table"
      $(checkbox).prop 'checked', true
      @render_transition_buttons table


  on_listing_entry_keypress: (event) =>
    ###
     * Eventhandler for listing entries (results capturing)
    ###
    console.debug "°°° ListingTableView::on_listing_entry_keypress °°°"

    # Prevent automatic submissions of manage_results forms when enter is pressed
    if event.which == 13
      console.debug "ListingTableView::on_listing_entry_keypress: capture Enter key"
      event.preventDefault()


  on_category_header_click: (event) =>
    ###
     * Eventhandler for collapsed/expanded categories
    ###
    console.debug "°°° ListingTableView::on_category_header_click °°°"

    el = event.currentTarget
    $el = $(el)

    # disable category collapse
    if $el.hasClass "ignore_bikalisting_default_handler"
      console.debug "Category toggling disabled by CSS class"
      return

    form = $el.parents "form"
    form_id = form.attr "id"
    cat_id = $el.attr "cat"

    @toggle_category form_id, cat_id


  on_autosave_field_change: (event) =>
    ###
     * Eventhandler for input fields with `autosave` css class
     *
     * This function looks for the column defined as 'autosave' and if its value
     * is true, the result of this input will be saved after each change via
     * ajax.
    ###
    console.warn "BBB: Autosave is deprecated and not supported anymore"
    return false


  on_workflow_button_click: (event) =>
    ###
     * Eventhandler for the workflow buttons
    ###
    console.debug "°°° ListingTableView::on_workflow_button_click °°°"

    el = event.currentTarget
    $el = $(el)

    form = $el.parents "form"
    form_id = $(form).attr "id"

    # The submit buttons would like to put the translated action title into the
    # request. Insert the real action name here to prevent the WorkflowAction
    # handler from having to look it up (painful/slow).
    transition = $el.attr "transition"
    $(form).append "<input type='hidden' name='workflow_action_id' value='#{transition}' />"

    # This submit_transition cheat fixes a bug where hitting submit caused form
    # to be posted before ajax calculation is returned
    if $el.id == "submit_transition"
      focus = $(".ajax_calculate_focus")
      if focus.length > 0
        e = $(focus[0])
        if $(e).attr("focus_value") == $(e).val()
          # value did not change - transparent blur handler.
          $(e).removeAttr "focus_value"
          $(e).removeClass "ajax_calculate_focus"
        else
          # The calcs.js code is now responsible for submitting
          # this form when the calculation ajax is complete
          $(e).parents("form").attr "submit_after_calculation", 1
          event.preventDefault()

    # If a custom_transitions action with a URL is clicked the form will be
    # submitted there
    if $el.attr("url") != ""
      form = $el.parents("form")
      $(form).attr "action", $(this).attr("url")
      $(form).submit()


  on_contextmenu: (event) =>
    ###
     * Eventhandler for the table contextmenu
    ###
    console.debug "°°° ListingTableView::on_contextmenu °°°"

    # prevent the system context menu
    event.preventDefault()

    el = event.currentTarget
    $el = $(el)
    table = $el.parents "table.bika-listing-table"

    # create the context menu HTML
    menu = @make_context_menu table

    # append to the body
    menu = $(menu).appendTo "body"

    # position the contextmenu where the mouse clicked
    $(menu).css
      "border": "1px solid #fff"
      "border-radius": ".25em"
      "background-color": "#fff"
      "position": "absolute"
      "top": event.pageY - 5
      "left": event.pageX - 5


  on_contextmenu_item_click: (event) =>
    ###
     * Eventhandler when an item was clicked in the contextmenu
    ###
    console.debug "°°° ListingTableView::on_contextmenu_item_click °°°"

    # current event target (table header)
    el = event.currentTarget
    # We're getting here the <tr> element from the context menu
    $el = $(el)

    # get the form and column id from the contextmenu <tr> element
    form_id = $el.attr "form_id"
    col_id = $el.attr "col_id"

    # toggle the column
    @toggle_column form_id, col_id


  on_search_field_keypress: (event) =>
    ###
     * Eventhandler for the search field
    ###
    console.debug "°°° ListingTableView::on_search_field_keypress °°°"

    # current event target (table header)
    el = event.currentTarget
    $el = $(el)

    # only trigger search on enter
    if event.which == 13
      # prevent form submit on enter
      event.preventDefault()
      # get the form and column id from the contextmenu <tr> element
      form = $el.parents "form"
      form_id = form.attr "id"
      searchfield = $(".filter-search-input", form)
      searchterm = searchfield.val()
      @search form_id, searchterm


  on_search_button_click: (event) =>
    ###
     * Eventhandler for the search field button
    ###
    console.debug "°°° ListingTableView::on_search_button_click °°°"

    # current event target (table header)
    el = event.currentTarget
    $el = $(el)

    @on_search_field_keypress event


  on_select_all_click: (event) =>
    ###
     * Eventhandler when the select all checkbox was clicked
     *
     * Controls the behavior when the 'select all' checkbox is clicked.
     * Checks/Unchecks all the row selection checkboxes and once done,
     * re-renders the workflow action buttons from the bottom of the list,
     * based on the allowed transitions for the currently selected items
    ###
    console.debug "°°° ListingTableView::on_select_all_click °°°"

    # current event target (table header)
    el = event.currentTarget
    $el = $(el)

    table = $el.parents("table.bika-listing-table")
    checkboxes = $(table).find("[id*='_cb_']")
    $(checkboxes).prop "checked", $el.prop("checked")

    # render transition buttons
    @render_transition_buttons table


  on_checkbox_click: (event) =>
    ###
     * Eventhandler when a Checkbox was clicked
     *
     * Controls the behavior when a checkbox of row selection is clicked.
     * Updates the status of the 'select all' checkbox accordingly and also
     * re-renders the workflow action buttons from the bottom of the list
     * based on the allowed transitions of the currently selected items
    ###
    console.debug "°°° ListingTableView::on_checkbox_click °°°"

    # current event target (table header)
    el = event.currentTarget
    $el = $(el)

    table = $el.parents("table.bika-listing-table")

    # Toggle select all checkbox
    checked = $("input[type='checkbox'][id*='_cb_']:checked")
    all = $("input[type='checkbox'][id*='_cb_']")
    checkall = $(table).find("input[id*='select_all']")
    checkall.prop "checked", checked.length == all.length

    # render transition buttons
    @render_transition_buttons table


  on_ajax_submit_start: (event) =>
    ###
     * Eventhandler for Ajax form submit
    ###
    console.debug "°°° ListingTableView::on_ajax_submit_start °°°"


  on_ajax_submit_end: (event) =>
    ###
     * Eventhandler for Ajax form submit
    ###
    console.debug "°°° ListingTableView::on_ajax_submit_end °°°"


  on_column_header_click: (event) =>
    ###
     * Eventhandler for Table Column Header
    ###
    console.debug "°°° ListingTableView::on_column_header_click °°°"

    # current event target (table header)
    el = event.currentTarget
    $el = $(el)

    form = $el.parents "form"
    form_id = form.attr "id"

    # extract the sort on index
    # XXX add the index directly to the table header
    # foldercontents-getClientReference-column -> getClientReference
    sort_index = $el.attr("id").split("-")[1]

    # sort the table
    @sort_column form_id, sort_index


  on_show_more_click: (event) =>
    ###
     * Eventhandler for the Table "Show More" Button
    ###
    console.debug "°°° ListingTableView::on_show_more_click °°°"

    # current event target (Show More button)
    el = event.currentTarget
    $el = $(el)

    # prevent form submit on button click
    event.preventDefault()

    form_id = $el.attr "data-form-id"
    pagesize = @parse_int $el.attr "data-pagesize"
    limit_from = @parse_int $el.attr "data-limitfrom"

    @show_more form_id, pagesize, limit_from
