### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
###

###
# Controller class for Bika Listing Table view
###

window.BikaListingTableView = ->
    that = this
    # To keep track if a transitions loading is taking place atm
    loading_transitions = false
    # Entry-point method for AnalysisServiceEditView

    show_more_clicked = ->
        $('a.bika_listing_show_more').click (e) ->
            e.preventDefault()
            formid = $(this).attr('data-form-id')
            pagesize = parseInt($(this).attr('data-pagesize'))
            url = $(this).attr('data-ajax-url')
            limit_from = parseInt($(this).attr('data-limitfrom'))
            url = url.replace('_limit_from=', '_olf=')
            url += '&' + formid + '_limit_from=' + limit_from
            $('#' + formid + ' a.bika_listing_show_more').fadeOut()
            tbody = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody')
            # The results must be filtered?
            filter_options = []
            filters1 = $('.bika_listing_filter_bar input[name][value!=""]')
            filters2 = $('.bika_listing_filter_bar select option:selected[value!=""]')
            filters = $.merge(filters1, filters2)
            $(filters).each (e) ->
                opt = [
                    $(this).attr('name')
                    $(this).val()
                ]
                filter_options.push opt
                return
            filterbar = {}
            if filter_options.length > 0
                filterbar.bika_listing_filter_bar = $.toJSON(filter_options)
            $.post(url, filterbar).done((data) ->
                try
                    # We must surround <tr> inside valid TABLE tags before extracting
                    rows = $('<html><table>' + data + '</table></html>').find('tr')
                    # Then we can simply append the rows to existing TBODY.
                    $(tbody).append rows
                    # Increase limit_from so that next iteration uses correct start point
                    $('#' + formid + ' a.bika_listing_show_more').attr 'data-limitfrom', limit_from + pagesize
                    loadNewRemarksEventHandlers()
                catch e
                    $('#' + formid + ' a.bika_listing_show_more').hide()
                    console.log e
                load_transitions()
                return
            ).fail(->
                $('#' + formid + ' a.bika_listing_show_more').hide()
                console.log 'bika_listing_show_more failed'
                return
            ).always ->
                numitems = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody tr').length
                $('#' + formid + ' span.number-items').html numitems
                if numitems % pagesize == 0
                    $('#' + formid + ' a.bika_listing_show_more').fadeIn()
                return
            return
        return

    loadNewRemarksEventHandlers = ->
        # Add a baloon icon before Analyses' name when you'd add a remark. If you click on, it'll display remarks textarea.
        $('a.add-remark').remove()
        txt1 = '<a href="#" class="add-remark"><img src="' + window.portal_url + '/++resource++bika.lims.images/comment_ico.png" title="' + _('Add Remark') + '")"></a>'
        pointer = $('.listing_remarks:contains(\'\')').closest('tr').prev().find('td.service_title span.before')
        $(pointer).append txt1
        $('a.add-remark').click (e) ->
            e.preventDefault()
            rmks = $(this).closest('tr').next('tr').find('td.remarks')
            if rmks.length > 0
                rmks.toggle()
            return
        $('td.remarks').hide()
        return

    column_header_clicked = ->
        # Click column header - set or modify sort order.
        $('th.sortable').live 'click', ->
            form = $(this).parents('form')
            form_id = $(form).attr('id')
            column_id = @id.split('-')[1]
            column_index = $(this).parent().children('th').index(this)
            sort_on_selector = '[name=' + form_id + '_sort_on]'
            sort_on = $(sort_on_selector).val()
            sort_order_selector = '[name=' + form_id + '_sort_order]'
            sort_order = $(sort_order_selector).val()
            # if this column_id is the current sort
            if sort_on == column_id
                # then we reverse sort order
                if sort_order == 'descending'
                    sort_order = 'ascending'
                else
                    sort_order = 'descending'
            else
                sort_on = column_id
                sort_order = 'ascending'
            # reset these values in the form (ajax sort uses them)
            $(sort_on_selector).val sort_on
            $(sort_order_selector).val sort_order
            # request new table content
            stored_form_action = $(form).attr('action')
            $(form).attr 'action', window.location.href
            $(form).append '<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>'
            options = 
                target: $(this).parents('table')
                replaceTarget: true
                data: form.formToArray()
            form.ajaxSubmit options
            $('[name=\'table_only\']').remove()
            $(form).attr 'action', stored_form_action
            return
        return

    ###
    * Fetch allowed transitions for all the objects listed in bika_listing and
    * sets the value for the attribute 'data-valid_transitions' for each check
    * box next to each row.
    * The process requires an ajax call, so the function keeps checkboxes
    * disabled until the allowed transitions for the associated object are set.
    ###

    load_transitions = (blisting) ->
        'use strict'
        if blisting == '' or typeof blisting == 'undefined'
            blistings = $('table.bika-listing-table')
            $(blistings).each (i) ->
                load_transitions $(this)
                return
            return
        buttonspane = $(blisting).find('span.workflow_action_buttons')
        if loading_transitions or $(buttonspane).length == 0
            # If show_workflow_action_buttons param is set to False in the
            # view, or transitions are being loaded already, do nothing
            return
        loading_transitions = true
        uids = []
        checkall = $("input[id*='select_all']")
        $(checkall).hide()
        # Update valid transitions for elements which have not yet been updated:
        wo_trans = $("input[data-valid_transitions='{}']")
        $(wo_trans).prop 'disabled', true
        $(wo_trans).each (e) ->
            uids.push $(this).val()
            return
        if uids.length > 0
            request_data = 
                _authenticator: $('input[name=\'_authenticator\']').val()
                uid: $.toJSON(uids)
            window.jsonapi_cache = window.jsonapi_cache or {}
            $.ajax
                type: 'POST'
                dataType: 'json'
                url: window.portal_url + '/@@API/allowedTransitionsFor_many'
                data: request_data
                success: (data) ->
                    if 'transitions' of data
                        i = 0
                        while i < data.transitions.length
                            uid = data.transitions[i].uid
                            trans = data.transitions[i].transitions
                            el = $("input[id*='_cb_'][value='#{uid}']")
                            el.attr 'data-valid_transitions', $.toJSON(trans)
                            $(el).prop 'disabled', false
                            i++
                        $("input[id*='select_all']").fadeIn()
                    return
        loading_transitions = false
        return

    ###
    * Controls the behavior when a checkbox of row selection is clicked.
    * Updates the status of the 'select all' checkbox accordingly and also
    * re-renders the workflow action buttons from the bottom of the list
    * based on the allowed transitions of the currently selected items
    ###

    select_one_clicked = ->
        'use strict'
        $('input[type=\'checkbox\'][id*=\'_cb_\']').live 'click', ->
            blst = $(this).parents('table.bika-listing-table')
            render_transition_buttons blst
            # Modify all checkbox statuses
            checked = $('input[type=\'checkbox\'][id*=\'_cb_\']:checked')
            all = $('input[type=\'checkbox\'][id*=\'_cb_\']')
            checkall = $(blst).find('input[id*=\'select_all\']')
            checkall.prop 'checked', checked.length == all.length
            return
        return

    ###
    * Controls the behavior when the 'select all' checkbox is clicked.
    * Checks/Unchecks all the row selection checkboxes and once done,
    * re-renders the workflow action buttons from the bottom of the list,
    * based on the allowed transitions for the currently selected items
    ###

    select_all_clicked = ->
        'use strict'
        # select all (on this page at least)
        $('input[id*=\'select_all\']').live 'click', ->
            blst = $(this).parents('table.bika-listing-table')
            checkboxes = $(blst).find('[id*=\'_cb_\']')
            $(checkboxes).prop 'checked', $(this).prop('checked')
            render_transition_buttons blst
            return
        return

    ###
    * Re-generates the workflow action buttons from the bottom of the list in
    * accordance with the allowed transitions for the currently selected items.
    * This is, makes the intersection within all allowed transitions and adds
    * the corresponding buttons to the workflow action bar.
    ###

    render_transition_buttons = (blst) ->
        'use strict'
        buttonspane = $(blst).find('span.workflow_action_buttons')
        if $(buttonspane).length == 0
            # If show_workflow_action_buttons param is set to False in the
            # view, do nothing
            return
        allowed_transitions = []
        # hidden_transitions and restricted are hidden fields
        # containing comma separated list of transition IDs.
        hidden_transitions = $(blst).find('input[id="hide_transitions"]')
        hidden_transitions = if $(hidden_transitions).length == 1 then $(hidden_transitions).val() else ''
        hidden_transitions = if hidden_transitions == '' then [] else hidden_transitions.split(',')
        restricted_transitions = $(blst).find('input[id="restricted_transitions"]')
        restricted_transitions = if $(restricted_transitions).length == 1 then $(restricted_transitions).val() else ''
        restricted_transitions = if restricted_transitions == '' then [] else restricted_transitions.split(',')
        checked = $(blst).find("input[id*='_cb_']:checked")

        $(checked).each (e) ->
            transitions = $.parseJSON($(this).attr('data-valid_transitions'))
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
            return

        # Generate the action buttons
        $(buttonspane).html ''
        i = 0
        while i < allowed_transitions.length
            trans = allowed_transitions[i]
            _button = "<input id='#{trans['id']}_transition'
                       class='context workflow_action_button action_button allowMultiSubmit'
                       type='submit'
                       value='#{PMF(trans['title'])}'
                       transition='#{trans['id']}'
                       name='workflow_action_button'/>&nbsp;"
            $(buttonspane).append _button
            i++
        # Add now custom actions
        if $(checked).length > 0
            custom_transitions = $(blst).find('input[type="hidden"].custom_transition')
            $(custom_transitions).each (i, e) ->
                _trans = $(e).val()
                _url = $(e).attr('url')
                _title = $(e).attr('title')
                _button = "<input id='#{_trans}_transition'
                           class='context workflow_action_button action_button allowMultiSubmit'
                           type='submit'
                           url='#{_url}'
                           value='#{_title}'
                           transition='#{_trans}'
                           name='workflow_action_button'/>&nbsp;"
                $(buttonspane).append _button
                return
        return

    listing_string_input_keypress = ->
        'use strict'
        $('.listing_string_entry,.listing_select_entry').live 'keypress', (event) ->
            # Prevent automatic submissions of manage_results forms when enter is pressed
            enter = 13
            if event.which == enter
                event.preventDefault()
            # check the item's checkbox
            uid = $(this).attr('uid')
            tr = $(this).parents('tr#folder-contents-item-' + uid)
            checkbox = tr.find('input[id$="_cb_' + uid + '"]')
            if $(checkbox).length == 1
                blst = $(checkbox).parents('table.bika-listing-table')
                $(checkbox).prop 'checked', true
                render_transition_buttons blst
            return
        return

    listing_string_select_changed = ->
        # always select checkbox when selectable listing item is changed
        $('.listing_select_entry').live 'change', ->
            uid = $(this).attr('uid')
            tr = $(this).parents('tr#folder-contents-item-' + uid)
            checkbox = tr.find('input[id$="_cb_' + uid + '"]')
            if $(checkbox).length == 1
                blst = $(checkbox).parents('table.bika-listing-table')
                $(checkbox).prop 'checked', true
                render_transition_buttons blst
            return
        return

    pagesize_change = ->
        # pagesize
        $('select.pagesize').live 'change', ->
            form = $(this).parents('form')
            form_id = $(form).attr('id')
            pagesize = $(this).val()
            new_query = $.query.set(form_id + '_pagesize', pagesize).set(form_id + '_pagenumber', 1).toString()
            window.location = window.location.href.split('?')[0] + new_query
            return
        return

    category_header_clicked = ->
        # expand/collapse categorised rows
        $('.bika-listing-table th.collapsed').live 'click', ->
            if !$(this).hasClass('ignore_bikalisting_default_handler')
                that.category_header_expand_handler this
            return
        $('.bika-listing-table th.expanded').live 'click', ->
            if !$(this).hasClass('ignore_bikalisting_default_handler')
                # After ajax_category expansion, collapse and expand work as they would normally.
                $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle()
                if $(this).hasClass('expanded')
                    # Set collapsed class on TR
                    $(this).removeClass('expanded').addClass 'collapsed'
                else if $(this).hasClass('collapsed')
                    # Set expanded class on TR
                    $(this).removeClass('collapsed').addClass 'expanded'
            return
        return

    filter_search_keypress = ->
        # pressing enter on filter search will trigger
        # a click on the search link.
        $('.filter-search-input').live 'keypress', (event) ->
            enter = 13
            if event.which == enter
                $('.filter-search-button').click()
                return false
            return
        return

    filter_search_button_click = ->
        # trap the Clear search / Search buttons
        $('.filter-search-button').live 'click', (event) ->
            form = $(this).parents('form')
            form_id = $(form).attr('id')
            stored_form_action = $(form).attr('action')
            $(form).attr 'action', window.location.href
            $(form).append '<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>'
            table = $(this).parents('table')
            url = window.location.href
            $.post(url, form.formToArray()).done((data) ->
                $(table).html(data)
                load_transitions()
                show_more_clicked()
                return
            )
            $('[name="table_only"]').remove()
            $(form).attr 'action', stored_form_action
            false
        return

    workflow_action_button_click = ->
        # Workflow Action button was clicked.
        $('.workflow_action_button').live 'click', (event) ->
            # The submit buttons would like to put the translated action title
            # into the request. Insert the real action name here to prevent the
            # WorkflowAction handler from having to look it up (painful/slow).
            form = $(this).parents('form')
            form_id = $(form).attr('id')
            $(form).append '<input type=\'hidden\' name=\'workflow_action_id\' value=\'' + $(this).attr('transition') + '\'>'
            # This submit_transition cheat fixes a bug where hitting submit caused
            # form to be posted before ajax calculation is returned
            if @id == 'submit_transition'
                focus = $('.ajax_calculate_focus')
                if focus.length > 0
                    e = $(focus[0])
                    if $(e).attr('focus_value') == $(e).val()
                        # value did not change - transparent blur handler.
                        $(e).removeAttr 'focus_value'
                        $(e).removeClass 'ajax_calculate_focus'
                    else
                        # The calcs.js code is now responsible for submitting
                        # this form when the calculation ajax is complete
                        $(e).parents('form').attr 'submit_after_calculation', 1
                        event.preventDefault()
            # If a custom_transitions action with a URL is clicked
            # the form will be submitted there
            if $(this).attr('url') != ''
                form = $(this).parents('form')
                $(form).attr 'action', $(this).attr('url')
                $(form).submit()
            return
        return

    column_toggle_context_menu = ->
        # show / hide columns - the right-click pop-up
        $('th[id^="foldercontents-"]').live 'contextmenu', (event) ->
            event.preventDefault()
            form_id = $(this).parents('form').attr('id')
            portal_url = window.portal_url
            toggle_cols = $('#' + form_id + '_toggle_cols').val()
            if toggle_cols == '' or toggle_cols == undefined or toggle_cols == null
                return false
            sorted_toggle_cols = []
            $.each $.parseJSON(toggle_cols), (col_id, v) ->
                v['id'] = col_id
                sorted_toggle_cols.push v
                return
            sorted_toggle_cols.sort (a, b) ->
                titleA = a['title'].toLowerCase()
                titleB = b['title'].toLowerCase()
                if titleA < titleB
                    return -1
                if titleA > titleB
                    return 1
                0
            txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">'
            txt = txt + '<tr><th colspan=\'2\'>' + _('Display columns') + '</th></tr>'
            i = 0
            while i < sorted_toggle_cols.length
                col = sorted_toggle_cols[i]
                col_id = col['id']
                col_title = _(col['title'])
                enabled = $('#foldercontents-' + col_id + '-column')
                if enabled.length > 0
                    txt = txt + '<tr class=\'enabled\' col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>'
                    txt = txt + '<td>'
                    txt = txt + '<img style=\'height:1em;\' src=\'' + portal_url + '/++resource++bika.lims.images/ok.png\'/>'
                    txt = txt + '</td>'
                    txt = txt + '<td>' + col_title + '</td></tr>'
                else
                    txt = txt + '<tr col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>'
                    txt = txt + '<td>&nbsp;</td>'
                    txt = txt + '<td>' + col_title + '</td></tr>'
                i++
            txt = txt + '<tr col_id=\'' + _('All') + '\' form_id=\'' + form_id + '\'>'
            txt = txt + '<td style=\'border-top:1px solid #ddd\'>&nbsp;</td>'
            txt = txt + '<td style=\'border-top:1px solid #ddd\'>' + _('All') + '</td></tr>'
            txt = txt + '<tr col_id=\'' + _('Default') + '\' form_id=\'' + form_id + '\'>'
            txt = txt + '<td>&nbsp;</td>'
            txt = txt + '<td>' + _('Default') + '</td></tr>'
            txt = txt + '</table></div>'
            $(txt).appendTo 'body'
            positionTooltip event
            false
        return

    column_toggle_context_menu_selection = ->
        # show / hide columns - the action when a column is clicked in the menu
        $('.contextmenu tr').live 'click', (event) ->
            form_id = $(this).attr('form_id')
            form = $('form#' + form_id)
            col_id = $(this).attr('col_id')
            col_title = $(this).text()
            enabled = $(this).hasClass('enabled')
            cookie = readCookie('toggle_cols')
            cookie = $.parseJSON(cookie)
            cookie_key = $(form[0].portal_type).val() + form_id
            if cookie == null or cookie == undefined
                cookie = {}
            if col_id == _('Default')
                # Remove entry from existing cookie if there is one
                delete cookie[cookie_key]
                createCookie 'toggle_cols', $.toJSON(cookie), 365
            else if col_id == _('All')
                # add all possible columns
                toggle_cols = []
                $.each $.parseJSON($('#' + form_id + '_toggle_cols').val()), (i, v) ->
                    toggle_cols.push i
                    return
                cookie[cookie_key] = toggle_cols
                createCookie 'toggle_cols', $.toJSON(cookie), 365
            else
                toggle_cols = cookie[cookie_key]
                if toggle_cols == null or toggle_cols == undefined
                    # this cookie key not yet defined
                    toggle_cols = []
                    $.each $.parseJSON($('#' + form_id + '_toggle_cols').val()), (i, v) ->
                        if !(col_id == i and enabled) and v['toggle']
                            toggle_cols.push i
                        return
                else
                    # modify existing cookie
                    if enabled
                        toggle_cols.splice toggle_cols.indexOf(col_id), 1
                    else
                        toggle_cols.push col_id
                cookie[cookie_key] = toggle_cols
                createCookie 'toggle_cols', $.toJSON(cookie), 365
            $(form).attr 'action', window.location.href
            $('.tooltip').remove()
            form.submit()
            false
        return

    positionTooltip = (event) ->
        tPosX = event.pageX - 5
        tPosY = event.pageY - 5
        $('div.tooltip').css
            'border': '1px solid #fff'
            'border-radius': '.25em'
            'background-color': '#fff'
            'position': 'absolute'
            'top': tPosY
            'left': tPosX
        return

    autosave = ->

        ###
        This function looks for the column defined as 'autosave' and if
        its value is true, the result of this input will be saved after each
        change via ajax.
        ###

        $('select.autosave, input.autosave').not('[type="hidden"]').each (i) ->
            # Save select fields
            $(this).change ->
                pointer = this
                build_typical_save_request pointer
                return
            return
        return

    build_typical_save_request = (pointer) ->

        ###
        # Build an array with the data to be saved for the typical data fields.
        # @pointer is the object which has been modified and we want to save its new data.
        ###

        fieldvalue = undefined
        fieldname = undefined
        requestdata = {}
        uid = undefined
        tr = undefined
        fieldvalue = $(pointer).val()
        if $(pointer).is(':checkbox')
            fieldvalue = $(pointer).is(':checked')
        fieldname = $(pointer).attr('field')
        tr = $(pointer).closest('tr')
        uid = $(pointer).attr('uid')
        requestdata[fieldname] = fieldvalue
        requestdata['obj_uid'] = uid
        save_elements requestdata, tr
        return

    save_elements = (requestdata, tr) ->

        ###
        # Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
        # @requestdata should has the format {fieldname=fieldvalue, uid=xxxx} -> { ReportDryMatter=false, uid=xxx}.
        ###

        url = window.location.href.replace('/base_view', '')
        # Staff for the notification
        name = $(tr).attr('title')
        $.ajax(
            type: 'POST'
            url: window.portal_url + '/@@API/update'
            data: requestdata).done((data) ->
            #success alert
            if data != null and data['success'] == true
                bika.lims.SiteView.notificationPanel name + ' updated successfully', 'succeed'
            else
                bika.lims.SiteView.notificationPanel 'Error while updating ' + name, 'error'
                msg = 'Error while updating ' + name
                console.warn msg
                window.bika.lims.error msg
            return
        ).fail ->
            #error
            bika.lims.SiteView.notificationPanel 'Error while updating ' + name, 'error'
            msg = 'Error while updating ' + name
            console.warn msg
            window.bika.lims.error msg
            return
        return

    that.load = ->
        column_header_clicked()
        load_transitions()
        select_one_clicked()
        select_all_clicked()
        listing_string_input_keypress()
        listing_string_select_changed()
        pagesize_change()
        category_header_clicked()
        filter_search_keypress()
        filter_search_button_click()
        workflow_action_button_click()
        column_toggle_context_menu()
        column_toggle_context_menu_selection()
        show_more_clicked()
        autosave()
        $('*').click ->
            if $('.tooltip').length > 0
                $('.tooltip').remove()
            return
        return

    that.category_header_expand_handler = (element) ->
        # element is the category header TH.
        # duplicated in bika.lims.analysisrequest.add_by_col.js
        def = $.Deferred()
        # with form_id allow multiple ajax-categorised tables in a page
        form_id = $(element).parents('[form_id]').attr('form_id')
        cat_title = $(element).attr('cat')
        # URL can be provided by bika_listing classes, with ajax_category_url attribute.
        url = if $('input[name=\'ajax_categories_url\']').length > 0 then $('input[name=\'ajax_categories_url\']').val() else window.location.href.split('?')[0]
        # We will replace this element with downloaded items:
        placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']')
        # If it's already been expanded, ignore
        if $(element).hasClass('expanded')
            def.resolve()
            return def.promise()
        # If ajax_categories are enabled, we need to go request items now.
        ajax_categories_enabled = $('input[name=\'ajax_categories\']')
        if ajax_categories_enabled.length > 0 and placeholder.length > 0
            options = {}
            options['ajax_category_expand'] = 1
            options['cat'] = cat_title
            options['form_id'] = form_id
            url = if $('input[name=\'ajax_categories_url\']').length > 0 then $('input[name=\'ajax_categories_url\']').val() else url
            if $('.review_state_selector a.selected').length > 0
                # review_state must be kept the same after items are loaded
                # (TODO does this work?)
                options['review_state'] = $('.review_state_selector a.selected')[0].id
            $.ajax(
                url: url
                data: options).done (data) ->
                # The same as: LIMS-1970 Analyses from AR Add form not displayed properly
                rows = $('<table>' + data + '</table>').find('tr')
                $('[form_id=\'' + form_id + '\'] tr[data-ajax_category=\'' + cat_title + '\']').replaceWith rows
                $(element).removeClass('collapsed').addClass 'expanded'
                def.resolve()
                load_transitions()
                return
        else
            # When ajax_categories are disabled, all cat items exist as TR elements:
            $(element).parent().nextAll('tr[cat=\'' + $(element).attr('cat') + '\']').toggle true
            $(element).removeClass('collapsed').addClass 'expanded'
            def.resolve()
        # Set expanded class on TR
        def.promise()

    return
