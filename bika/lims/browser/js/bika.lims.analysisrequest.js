/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.coffee
 */
/**
 * Controller class for Analysis Request View/s
 */
(function() {
  window.AnalysisRequestView = function() {
    /**
     * Entry-point method for AnalysisRequestView
     */
    var that, transition_schedule_sampling, transition_with_publication_spec, workflow_transition_sample;
    that = this;
    transition_with_publication_spec = function(event) {
      var element, href;
      // Pass the Publication Spec UID (if present) into the WorkflowAction handler
      // Force the transition to use the "workflow_action" url instead of content_status_modify.
      // TODO This should be using content_status_modify!  modifying the href is silly.
      event.preventDefault();
      href = event.currentTarget.href.replace('content_status_modify', 'workflow_action');
      element = $('#PublicationSpecification_uid');
      if (element.length > 0) {
        href = href + '&PublicationSpecification=' + $(element).val();
      }
      window.location.href = href;
    };
    transition_schedule_sampling = function() {
      /* Force the transition to use the "workflow_action" url instead of content_status_modify. workflow_action triggers a class from
      analysisrequest/workflow/AnalysisRequestWorkflowAction which manage
      workflow_actions from analysisrequest/sample/samplepartition objects.
      It is not possible to abort a transition using "workflow_script_*".
      The recommended way is to set a guard instead.

      The guard expression should be able to look up a view to facilitate more complex guard code, but when a guard returns False the transition isn't even listed as available. It is listed after saving the fields.

      TODO This should be using content_status_modify!  modifying the href
      is silly.
      */
      var new_url, url;
      url = $('#workflow-transition-schedule_sampling').attr('href');
      if (url) {
        new_url = url.replace('content_status_modify', 'workflow_action');
        $('#workflow-transition-schedule_sampling').attr('href', new_url);
        // When user clicks on the transition
        $('#workflow-transition-schedule_sampling').click(function() {
          var date, message, sampler;
          date = $('#SamplingDate').val();
          sampler = $('#ScheduledSamplingSampler').val();
          if (date !== '' && date !== void 0 && date !== null && sampler !== '' && sampler !== void 0 && sampler !== null) {
            window.location.href = new_url;
          } else {
            message = '';
            if (date === '' || date === void 0 || date === null) {
              message = message + PMF('${name} is required for this action, please correct.', {
                'name': _('Sampling Date')
              });
            }
            if (sampler === '' || sampler === void 0 || sampler === null) {
              if (message !== '') {
                message = message + '<br/>';
              }
              message = message + PMF('${name} is required, please correct.', {
                'name': _('\'Define the Sampler for the shceduled\'')
              });
            }
            if (message !== '') {
              window.bika.lims.portalMessage(message);
            }
          }
        });
      }
    };
    workflow_transition_sample = function() {
      $('#workflow-transition-sample').click(function(event) {
        var date, form, message, sampler;
        event.preventDefault();
        date = $('#DateSampled').val();
        sampler = $('#Sampler').val();
        if (date && sampler) {
          form = $('form[name=\'header_form\']');
          // this 'transition' key is scanned for in header_table.py/__call__
          form.append('<input type=\'hidden\' name=\'transition\' value=\'sample\'/>');
          form.submit();
        } else {
          message = '';
          if (date === '' || date === void 0 || date === null) {
            message = message + PMF('${name} is required, please correct.', {
              'name': _('Date Sampled')
            });
          }
          if (sampler === '' || sampler === void 0 || sampler === null) {
            if (message !== '') {
              message = message + '<br/>';
            }
            message = message + PMF('${name} is required, please correct.', {
              'name': _('Sampler')
            });
          }
          if (message !== '') {
            window.bika.lims.portalMessage(message);
          }
        }
      });
    };
    that.load = function() {
      // fires for all AR workflow transitions fired using the plone contentmenu workflow actions
      $('a[id^=\'workflow-transition\']').not('#workflow-transition-schedule_sampling').not('#workflow-transition-sample').click(transition_with_publication_spec);
      // fires AR workflow transitions when using the schedule samplign transition
      transition_schedule_sampling();
    };
  };

  /**
   * Controller class for Analysis Request View View
   */
  window.AnalysisRequestViewView = function() {
    /**
     * Entry-point method for AnalysisRequestView
     */
    var build_typical_save_request, filter_CCContacts, filter_by_client, getClientUID, parse_CCClist, resultsinterpretation_move_below, save_elements, set_autosave_input, that;
    that = this;
    resultsinterpretation_move_below = function() {
      // By default show only the Results Interpretation for the whole AR, not Dept specific
      $('a.department-tab').click(function(e) {
        var uid;
        e.preventDefault();
        uid = $(this).attr('data-uid');
        $('.department-area').not('[id="' + uid + '"]').hide();
        $('.department-area[id="' + uid + '"]').show();
        $('a.department-tab.selected').removeClass('selected');
        $(this).addClass('selected');
      });
      $('a.department-tab[data-uid="ResultsInterpretationDepts-general"]').click();
      //Remove buttons from TinyMCE
      setTimeout((function() {
        $('div.arresultsinterpretation-container .fieldTextFormat').remove();
        $('table.mceToolbar a.mce_image').remove();
        $('table.mceToolbar a.mce_code').remove();
        $('table.mceToolbar a.mce_save').hide();
      }), 1500);
    };
    filter_CCContacts = function() {
      var clientUID, element;
      /**
       * Filter the CCContacts dropdown list by the current client.
       */
      if ($('#CCContact').length > 0) {
        element = $('#CCContact');
        clientUID = getClientUID();
        filter_by_client(element, 'getParentUID', clientUID);
      }
    };
    getClientUID = function() {
      /**
       * Return the AR client's UID.
       */
      var clientid, clientuid;
      clientid = window.location.href.split('clients')[1].split('/')[1];
      // ajax petition to obtain the current client info
      clientuid = '';
      $.ajax({
        url: window.portal_url + '/clients/' + clientid + '/getClientInfo',
        type: 'POST',
        async: false,
        data: {
          '_authenticator': $('input[name="_authenticator"]').val()
        },
        dataType: 'json',
        success: function(data, textStatus, $XHR) {
          if (data['ClientUID'] !== '') {
            clientuid = data['ClientUID'] !== '' ? data['ClientUID'] : null;
          }
        }
      });
      return clientuid;
    };
    filter_by_client = function(element, filterkey, filtervalue) {
      var base_query, options;
      /**
       * Filter the dropdown's results (called element) by current client contacts.
       */
      // Get the base_query data in array format
      base_query = $.parseJSON($(element).attr('base_query'));
      base_query[filterkey] = filtervalue;
      $(element).attr('base_query', $.toJSON(base_query));
      options = $.parseJSON($(element).attr('combogrid_options'));
      $(element).attr('base_query', $.toJSON(base_query));
      $(element).attr('combogrid_options', $.toJSON(options));
      referencewidget_lookups($(element));
    };
    set_autosave_input = function() {
      /**
       * Set an event for each input field in the AR header. After write something in the input field and
       * focus out it, the event automatically saves the change.
       */
      $('table.header_table input').not('[attr="referencewidget"]').not('[type="hidden"]').not('.rejectionwidget-field').each(function(i) {
        // Save input fields
        $(this).change(function() {
          var pointer;
          pointer = this;
          build_typical_save_request(pointer);
        });
      });
      $('table.header_table select').not('[type="hidden"]').not('.rejectionwidget-field').each(function(i) {
        // Save select fields
        $(this).change(function() {
          var pointer;
          pointer = this;
          build_typical_save_request(pointer);
        });
      });
      $('table.header_table input.referencewidget').not('[type="hidden"]').not('[id="CCContact"]').each(function(i) {
        // Save referencewidget inputs.
        $(this).bind('selected', function() {
          var fieldname, fieldvalue, pointer, requestdata;
          requestdata = {};
          pointer = this;
          fieldvalue = void 0;
          fieldname = void 0;
          setTimeout((function() {
            fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
            fieldvalue = $(pointer).attr('uid');
            // To search by uid, we should follow this array template:
            // { SamplePoint = "uid:TheValueOfuid1|uid:TheValueOfuid2..." }
            // This is the way how jsonapi/__init__.py/resolve_request_lookup() works.
            requestdata[fieldname] = 'uid:' + fieldvalue;
            save_elements(requestdata);
          }), 500);
        });
      });
      $('table.header_table input#CCContact.referencewidget').not('[type="hidden"]').each(function(i) {
        // CCContact works different.
        $(this).bind('selected', function() {
          var fieldname, fieldvalue, pointer, requestdata;
          pointer = this;
          fieldvalue = void 0;
          fieldname = void 0;
          requestdata = {};
          setTimeout((function() {
            // To search by uid, we should follow this array template:
            // { SamplePoint = "uid:TheValueOfuid1|uid:TheValueOfuid2..." }
            // This is the way how jsonapi/__init__.py/resolve_request_lookup() works.
            fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
            fieldvalue = parse_CCClist();
            requestdata[fieldname] = fieldvalue;
            save_elements(requestdata);
          }), 500);
        });
      });
      $('img[fieldname="CCContact"]').each(function() {
        var fieldname, fieldvalue, requestdata;
        // If a delete cross is clicked on CCContact-listing, we should update the saved list.
        fieldvalue = void 0;
        requestdata = {};
        fieldname = void 0;
        $(this).click(function() {
          fieldname = $(this).attr('fieldname');
          setTimeout(function() {
            fieldvalue = parse_CCClist();
            requestdata[fieldname] = fieldvalue;
            save_elements(requestdata);
          });
        });
      });
    };
    build_typical_save_request = function(pointer) {
      /**
       * Build an array with the data to be saved for the typical data fields.
       * @pointer is the object which has been modified and we want to save its new data.
       */
      var fieldname, fieldvalue, requestdata;
      fieldvalue = void 0;
      fieldname = void 0;
      requestdata = {};
      // Checkbox
      if ($(pointer).attr('type') === 'checkbox') {
        // Checkboxes name is located in its parent div, but its value is located inside the input.
        fieldvalue = $(pointer).prop('checked');
        fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
      } else {
        fieldvalue = $(pointer).val();
        fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
      }
      requestdata[fieldname] = fieldvalue;
      save_elements(requestdata);
    };
    save_elements = function(requestdata) {
      /**
       * Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
       * @requestdata should has the format  {fieldname=fieldvalue}
       */
      var anch, ar, element, name, obj_path, url;
      url = window.location.href.replace('/base_view', '');
      obj_path = url.replace(window.portal_url, '');
      // Staff for the notification
      element = void 0;
      name = $.map(requestdata, function(element, index) {
        element;
        return index;
      });
      name = $.trim($('[data-fieldname="' + name + '"]').closest('td').prev().text());
      ar = $.trim($('.documentFirstHeading').text());
      anch = '<a href=\'' + url + '\'>' + ar + '</a>';
      // Needed fot the ajax petition
      requestdata['obj_path'] = obj_path;
      $.ajax({
        type: 'POST',
        url: window.portal_url + '/@@API/update',
        data: requestdata
      }).done(function(data) {
        var msg;
        var msg;
        //success alert
        if (data !== null && data['success'] === true) {
          bika.lims.SiteView.notificationPanel(anch + ': ' + name + ' updated successfully', 'succeed');
        } else if (data === null) {
          bika.lims.SiteView.notificationPanel('Field ' + name + ' for ' + anch + ' could not be updated.' + ' Wrong value?', 'error');
          msg = '[bika.lims.analysisrequest.js] No data returned ' + 'while updating ' + name + ' for ' + ar;
          console.warn(msg);
          window.bika.lims.warning(msg);
        } else {
          bika.lims.SiteView.notificationPanel('Field ' + name + ' for ' + anch + ' could not be updated.' + ' Wrong value?', 'error');
          msg = '[bika.lims.analysisrequest.js] No success ' + 'while updating ' + name + ' for ' + ar;
          console.warn(msg);
          window.bika.lims.warning(msg);
        }
      }).fail(function(xhr, textStatus, errorThrown) {
        var msg;
        //error
        bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for ' + anch, 'error');
        msg = '[bika.lims.analysisrequest.js] Error in AJAX call' + 'while updating ' + name + ' for ' + ar + '. Error: ' + xhr.responseText;
        console.warn(msg);
        window.bika.lims.error(msg);
      });
    };
    parse_CCClist = function() {
      /**
       * It parses the CCContact-listing, where are located the CCContacts, and build the fieldvalue list.
       * @return: the builed field value -> "uid:TheValueOfuid1|uid:TheValueOfuid2..."
       */
      var fieldvalue;
      fieldvalue = '';
      $('#CCContact-listing').children('.reference_multi_item').each(function(ii) {
        if (fieldvalue.length < 1) {
          fieldvalue = 'uid:' + $(this).attr('uid');
        } else {
          fieldvalue = fieldvalue + '|uid:' + $(this).attr('uid');
        }
      });
      return fieldvalue;
    };
    that.load = function() {
      var cid;
      resultsinterpretation_move_below();
      filter_CCContacts();
      set_autosave_input();
      if (document.location.href.search('/clients/') >= 0 && $('#archetypes-fieldname-SamplePoint #SamplePoint').length > 0) {
        cid = document.location.href.split('clients')[1].split('/')[1];
        $.ajax({
          url: window.portal_url + '/clients/' + cid + '/getClientInfo',
          type: 'POST',
          data: {
            '_authenticator': $('input[name="_authenticator"]').val()
          },
          dataType: 'json',
          success: function(data, textStatus, $XHR) {
            var base_query, options, setup_uid, simple_url, spelement;
            if (data['ClientUID'] !== '') {
              spelement = $('#archetypes-fieldname-SamplePoint #SamplePoint');
              base_query = $.parseJSON($(spelement).attr('base_query'));
              setup_uid = $('#bika_setup').attr('bika_samplepoints');
              base_query['getClientUID'] = [data['ClientUID'], setup_uid];
              $(spelement).attr('base_query', $.toJSON(base_query));
              options = $.parseJSON($(spelement).attr('combogrid_options'));
              // Getting the url like that will return the query
              // part of it:
              // http://localhost:8080/Plone/clients/client17-14/..
              //    ..OA17-0030-R01
              // In order to create a correct ajax call
              // we only need until the pathname of that url:
              // http://localhost:8080/Plone/clients/client17-14/..
              //    ..OA17-0030-R01
              simple_url = window.location.href.split('/ar')[0];
              simple_url = simple_url.split('?')[0];
              options.url = simple_url + '/' + options.url;
              options.url = options.url + '?_authenticator=' + $('input[name=\'_authenticator\']').val();
              options.url = options.url + '&catalog_name=' + $(spelement).attr('catalog_name');
              options.url = options.url + '&base_query=' + $.toJSON(base_query);
              options.url = options.url + '&search_query=' + $(spelement).attr('search_query');
              options.url = options.url + '&colModel=' + $.toJSON($.parseJSON($(spelement).attr('combogrid_options')).colModel);
              options.url = options.url + '&search_fields=' + $.toJSON($.parseJSON($(spelement).attr('combogrid_options')).search_fields);
              options.url = options.url + '&discard_empty=' + $.toJSON($.parseJSON($(spelement).attr('combogrid_options')).discard_empty);
              options.force_all = 'false';
              $(spelement).combogrid(options);
              $(spelement).addClass('has_combogrid_widget');
              $(spelement).attr('search_query', '{}');
            }
          }
        });
      }
    };
  };

  /**
   * Controller class for Analysis Request Manage Results view
   */
  window.AnalysisRequestManageResultsView = function() {
    var that;
    that = this;
    /**
     * Entry-point method for AnalysisRequestManageResultsView
     */
    that.load = function() {
      // Set the analyst automatically when selected in the picklist
      $('.portaltype-analysisrequest .bika-listing-table td.Analyst select').change(function() {
        var analyst, key, obj_path, obj_path_split;
        analyst = $(this).val();
        key = $(this).closest('tr').attr('keyword');
        obj_path = window.location.href.replace(window.portal_url, '');
        obj_path_split = obj_path.split('/');
        if (obj_path_split.length > 4) {
          obj_path_split[obj_path_split.length - 1] = key;
        } else {
          obj_path_split.push(key);
        }
        obj_path = obj_path_split.join('/');
        $.ajax({
          type: 'POST',
          url: window.portal_url + '/@@API/update',
          data: {
            'obj_path': obj_path,
            'Analyst': analyst
          }
        });
      });
    };
  };

  /**
   * Controller class for Analysis Request Analyses view
   */
  window.AnalysisRequestAnalysesView = function() {
    /**
    * Given a selected service, this function selects the dependencies for
    * the selected service.
    * @param {String} dlg: The dialog to display (Not working!)
    * @param {DOM object} element: The checkbox object.
    * @param {Object} dep_services: A list of UIDs.
    * @return {None} nothing.
     */
    /**
    * Once a checkbox has been selected, this functions finds out which are
    * the dependencies and dependants related to it.
    * @param {elements} The selected element, a checkbox.
    * @param {auto_yes} A boolean. If 'true', the dependants and dependencies
    * will be automatically selected/unselected.
     */
    /**
    * This functions runs the logic needed after setting the checkbox of a
    * service.
    * @param {service_uid} the service uid checked.
     */
    /**
    * Given an analysis service UID, this function expands the category for
    * that service and selects it.
    * @param {String} serv_uid: uid of the analysis service.
    * @return {None} nothing.
     */
    /**
    * This functions runs the logic needed after unsetting the checkbox of a
    * service.
    * @param {service_uid} the service uid unchecked.
     */
    /**
     * Entry-point method for AnalysisRequestAnalysesView
     */
    /**
    * This function validates specification inputs
    * @param {element} The input field from specifications (min, max, err)
     */
    var add_No, add_Yes, calcdependencies, check_service, expand_category_for_service, that, uncheck_service, validate_spec_field_entry;
    that = this;
    validate_spec_field_entry = function(element) {
      var error, error_element, max, max_element, min, min_element, uid;
      uid = $(element).attr('uid');
      min_element = $('[name=\'min\\.' + uid + '\\:records\']');
      max_element = $('[name=\'max\\.' + uid + '\\:records\']');
      error_element = $('[name=\'error\\.' + uid + '\\:records\']');
      min = parseFloat($(min_element).val(), 10);
      max = parseFloat($(max_element).val(), 10);
      error = parseFloat($(error_element).val(), 10);
      if ($(element).attr('name') === $(min_element).attr('name')) {
        if (isNaN(min)) {
          $(min_element).val('');
        } else if (!isNaN(max) && min > max) {
          $(max_element).val('');
        }
      } else if ($(element).attr('name') === $(max_element).attr('name')) {
        if (isNaN(max)) {
          $(max_element).val('');
        } else if (!isNaN(min) && max < min) {
          $(min_element).val('');
        }
      } else if ($(element).attr('name') === $(error_element).attr('name')) {
        if (isNaN(error) || error < 0 || error > 100) {
          $(error_element).val('');
        }
      }
    };
    check_service = function(service_uid) {
      /* Check if this row is disabled. row_data has the attribute "disabled"
      as true if the analysis service has been submitted. So, in this case
      no further action will take place.

      "allow_edit" attribute in bika_listing displays the editable fields.
      Since the object keeps this attr even if the row is disabled; price,
      partition, min,max and error will be displayed (but disabled).
      */
      var element, i, logged_in_client, new_element, row_data, specfields;
      new_element = void 0;
      element = void 0;
      row_data = $.parseJSON($('#' + service_uid + '_row_data').val());
      if (row_data !== '' && row_data !== void 0 && row_data !== null) {
        if ('disabled' in row_data && row_data.disabled === true) {
          return;
        }
      }
      // Add partition dropdown
      element = $('[name=\'Partition.' + service_uid + ':records\']');
      new_element = '' + '<select class=\'listing_select_entry\' ' + 'name=\'Partition.' + service_uid + ':records\' ' + 'field=\'Partition\' uid=\'' + service_uid + '\' ' + 'style=\'font-size: 100%\'>';
      $.each($('td.PartTitle'), function(i, v) {
        var partid;
        partid = $($(v).children()[1]).text();
        new_element = new_element + '<option value=\'' + partid + '\'>' + partid + '</option>';
      });
      new_element = new_element + '</select>';
      $(element).replaceWith(new_element);
      // Add price field
      logged_in_client = $('input[name=\'logged_in_client\']').val();
      if (logged_in_client !== '1') {
        element = $('[name=\'Price.' + service_uid + ':records\']');
        new_element = '' + '<input class=\'listing_string_entry numeric\' ' + 'name=\'Price.' + service_uid + ':records\' ' + 'field=\'Price\' type=\'text\' uid=\'' + service_uid + '\' ' + 'autocomplete=\'off\' style=\'font-size: 100%\' size=\'5\' ' + 'value=\'' + $(element).val() + '\'>';
        $($(element).siblings()[1]).remove();
        $(element).replaceWith(new_element);
      }
      // spec fields
      specfields = ['min', 'max', 'error'];
      for (i in specfields) {
        element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']');
        new_element = '' + '<input class=\'listing_string_entry numeric\' type=\'text\' size=\'5\' ' + 'field=\'' + specfields[i] + '\' value=\'' + $(element).val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' ' + 'uid=\'' + service_uid + '\' autocomplete=\'off\' style=\'font-size: 100%\'>';
        $(element).replaceWith(new_element);
      }
    };
    uncheck_service = function(service_uid) {
      var element, i, logged_in_client, new_element, specfields;
      new_element = void 0;
      element = void 0;
      element = $('[name=\'Partition.' + service_uid + ':records\']');
      new_element = '' + '<input type=\'hidden\' name=\'Partition.' + service_uid + ':records\' value=\'\'/>';
      $(element).replaceWith(new_element);
      logged_in_client = $('input[name=\'logged_in_client\']').val();
      if (logged_in_client !== '1') {
        element = $('[name=\'Price.' + service_uid + ':records\']');
        $($(element).siblings()[0]).after('<span class=\'state-active state-active \'>' + $(element).val() + '</span>');
        new_element = '' + '<input type=\'hidden\' name=\'Price.' + service_uid + ':records\' value=\'' + $(element).val() + '\'/>';
        $(element).replaceWith(new_element);
      }
      specfields = ['min', 'max', 'error'];
      for (i in specfields) {
        element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']');
        new_element = '' + '<input type=\'hidden\' field=\'' + specfields[i] + '\' value=\'' + element.val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' uid=\'' + service_uid + '\'>';
        $(element).replaceWith(new_element);
      }
    };
    add_Yes = function(dlg, element, dep_services) {
      var dep_cb, i, service_uid;
      service_uid = void 0;
      dep_cb = void 0;
      i = 0;
      while (i < dep_services.length) {
        service_uid = dep_services[i];
        dep_cb = $('#list_cb_' + service_uid);
        if (dep_cb.length > 0) {
          if (!$(dep_cb).prop('checked')) {
            check_service(service_uid);
            $('#list_cb_' + service_uid).prop('checked', true);
          }
        } else {
          expand_category_for_service(service_uid);
        }
        i++;
      }
      if (dlg !== false) {
        $(dlg).dialog('close');
        $('#messagebox').remove();
      }
    };
    add_No = function(dlg, element) {
      if ($(element).prop('checked')) {
        uncheck_service($(element).attr('value'));
        $(element).prop('checked', false);
      }
      if (dlg !== false) {
        $(dlg).dialog('close');
        $('#messagebox').remove();
      }
    };
    calcdependencies = function(elements, auto_yes) {
      var Dependants, Dependencies, _, cb, dep, dep_services, dep_titles, element, elements_i, html, i, lims, service_uid;
      auto_yes = auto_yes || false;
      jarn.i18n.loadCatalog('bika');
      _ = window.jarn.i18n.MessageFactory('bika');
      dep = void 0;
      i = void 0;
      cb = void 0;
      lims = window.bika.lims;
      elements_i = 0;
      while (elements_i < elements.length) {
        dep_services = [];
        // actionable services
        dep_titles = [];
        element = elements[elements_i];
        service_uid = $(element).attr('value');
        // selecting a service; discover dependencies
        if ($(element).prop('checked')) {
          Dependencies = lims.AnalysisService.Dependencies(service_uid);
          i = 0;
          while (i < Dependencies.length) {
            dep = Dependencies[i];
            if ($('#list_cb_' + dep.Service_uid).prop('checked')) {
              i++;
              continue;
            }
            // skip if checked already
            dep_services.push(dep);
            dep_titles.push(dep.Service);
            i++;
          }
          if (dep_services.length > 0) {
            if (auto_yes) {
              add_Yes(false, element, dep_services);
            } else {
              html = '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>';
              html = html + _('<p>${service} requires the following services to be selected:</p>' + '<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>', {
                service: $(element).attr('title'),
                deps: dep_titles.join('<br/>')
              });
              html = html + '</div>';
              $('body').append(html);
              $('#messagebox').dialog({
                width: 450,
                resizable: false,
                closeOnEscape: false,
                buttons: {
                  yes: function() {
                    add_Yes(this, element, dep_services);
                  },
                  no: function() {
                    add_No(this, element);
                  }
                }
              });
            }
          }
        } else {
          Dependants = lims.AnalysisService.Dependants(service_uid);
          i = 0;
          while (i < Dependants.length) {
            dep = Dependants[i];
            cb = $('#list_cb_' + dep);
            if (cb.prop('checked')) {
              dep_titles.push(dep.Service);
              dep_services.push(dep);
            }
            i++;
          }
          if (dep_services.length > 0) {
            if (auto_yes) {
              i = 0;
              while (i < dep_services.length) {
                dep = dep_services[i];
                service_uid = dep;
                cb = $('#list_cb_' + service_uid);
                uncheck_service(service_uid);
                $(cb).prop('checked', false);
                i += 1;
              }
            } else {
              $('body').append('<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>' + _('<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>', {
                service: $(element).attr('title'),
                deps: dep_titles.join('<br/>')
              }) + '</div>');
              $('#messagebox').dialog({
                width: 450,
                resizable: false,
                closeOnEscape: false,
                buttons: {
                  yes: function() {
                    i = 0;
                    while (i < dep_services.length) {
                      dep = dep_services[i];
                      service_uid = dep;
                      cb = $('#list_cb_' + dep);
                      $(cb).prop('checked', false);
                      uncheck_service(dep);
                      i += 1;
                    }
                    $(this).dialog('close');
                    $('#messagebox').remove();
                  },
                  no: function() {
                    service_uid = $(element).attr('value');
                    check_service(service_uid);
                    $(element).prop('checked', true);
                    $('#messagebox').remove();
                    $(this).dialog('close');
                  }
                }
              });
            }
          }
        }
        elements_i++;
      }
    };
    expand_category_for_service = function(serv_uid) {
      var request_data;
      // Ajax getting the category from uid
      request_data = {
        catalog_name: 'uid_catalog',
        UID: serv_uid,
        include_methods: 'getCategoryTitle'
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var cat_title, element, msg;
        if (data.objects.length < 1) {
          msg = '[bika.lims.analysisrequest.add_by_col.js] No data returned ' + 'while running "expand_category_for_service" for ' + serv_uid;
          console.warn(msg);
          window.bika.lims.warning(msg);
        } else {
          cat_title = data.objects[0].getCategoryTitle;
          // Expand category by uid and select the service
          element = $('th[cat=\'' + cat_title + '\']');
          //category_header_expand_handler(element, arnum, serv_uid);
          window.bika.lims.BikaListingTableView.category_header_expand_handler(element).done(function() {
            check_service(serv_uid);
            $('#list_cb_' + serv_uid).prop('checked', true);
          });
        }
      });
    };
    that.load = function() {
      $('[name^=\'min\\.\'], [name^=\'max\\.\'], [name^=\'error\\.\']').live('change', function() {
        validate_spec_field_entry(this);
      });
      ////////////////////////////////////////
      // disable checkboxes for eg verified analyses.
      $.each($('[name=\'uids:list\']'), function(x, cb) {
        var cbid, cbname, el, element, elname, elval, i, new_element, row_data, service_uid, specfields;
        service_uid = $(cb).val();
        row_data = $.parseJSON($('#' + service_uid + '_row_data').val());
        if (row_data.disabled === true) {
          // disabled fields must be shadowed by hidden fields,
          // or they don't appear in the submitted form.
          $(cb).prop('disabled', true);
          cbname = $(cb).attr('name');
          cbid = $(cb).attr('id');
          $(cb).removeAttr('name').removeAttr('id');
          $(cb).after('<input type=\'hidden\' name=\'' + cbname + '\' value=\'' + service_uid + '\' id=\'' + cbid + '\'/>');
          el = $('[name=\'Price.' + service_uid + ':records\']');
          elname = $(el).attr('name');
          elval = $(el).val();
          $(el).after('<input type=\'hidden\' name=\'' + elname + '\' value=\'' + elval + '\'/>');
          $(el).prop('disabled', true);
          el = $('[name=\'Partition.' + service_uid + ':records\']');
          elname = $(el).attr('name');
          elval = $(el).val();
          $(el).after('<input type=\'hidden\' name=\'' + elname + '\' value=\'' + elval + '\'/>');
          $(el).prop('disabled', true);
          specfields = ['min', 'max', 'error'];
          for (i in specfields) {
            element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']');
            new_element = '' + '<input type=\'hidden\' field=\'' + specfields[i] + '\' value=\'' + element.val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' uid=\'' + service_uid + '\'>';
            $(element).replaceWith(new_element);
          }
        }
      });
      ////////////////////////////////////////
      // checkboxes in services list
      $('[name=\'uids:list\']').live('click', function() {
        var service_uid;
        calcdependencies([this], true);
        service_uid = $(this).val();
        if ($(this).prop('checked')) {
          check_service(service_uid);
        } else {
          uncheck_service(service_uid);
        }
      });
    };
  };

}).call(this);
