
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.coffee
 */


/**
 * Controller class for Analysis Request View/s
 */

(function() {
  window.AnalysisRequestView = function() {
    var that, transition_schedule_sampling, transition_with_publication_spec, workflow_transition_sample;
    that = this;

    /**
     * Entry-point method for AnalysisRequestView
     */
    transition_with_publication_spec = function(event) {
      var element, href;
      event.preventDefault();
      href = event.currentTarget.href.replace('content_status_modify', 'workflow_action');
      element = $('#PublicationSpecification_uid');
      if (element.length > 0) {
        href = href + '&PublicationSpecification=' + $(element).val();
      }
      window.location.href = href;
    };
    transition_schedule_sampling = function() {

      /* Force the transition to use the "workflow_action" url instead of
      content_status_modify.
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
      $('a[id^=\'workflow-transition\']').not('#workflow-transition-schedule_sampling').not('#workflow-transition-sample').click(transition_with_publication_spec);
      transition_schedule_sampling();
    };
  };


  /**
   * Controller class for Analysis Request View View
   */

  window.AnalysisRequestViewView = function() {
    var parse_CCClist, resultsinterpretation_move_below, that;
    that = this;

    /**
     * Entry-point method for AnalysisRequestView
     */
    resultsinterpretation_move_below = function() {
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
      setTimeout((function() {
        $('div.arresultsinterpretation-container .fieldTextFormat').remove();
        $('table.mceToolbar a.mce_image').remove();
        $('table.mceToolbar a.mce_code').remove();
        $('table.mceToolbar a.mce_save').hide();
      }), 1500);
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
      resultsinterpretation_move_below();
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
    var add_No, add_Yes, calcdependencies, check_service, expand_category_for_service, that, uncheck_service, validate_spec_field_entry;
    that = this;

    /**
     * Entry-point method for AnalysisRequestAnalysesView
     */

    /**
    * This function validates specification inputs
    * @param {element} The input field from specifications (min, max, err)
     */
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

    /**
    * This functions runs the logic needed after setting the checkbox of a
    * service.
    * @param {service_uid} the service uid checked.
     */
    check_service = function(service_uid) {
      var element, i, logged_in_client, new_element, row_data, specfields;
      new_element = void 0;
      element = void 0;

      /* Check if this row is disabled. row_data has the attribute "disabled"
      as true if the analysis service has been submitted. So, in this case
      no further action will take place.
      
      "allow_edit" attribute in bika_listing displays the editable fields.
      Since the object keeps this attr even if the row is disabled; price,
      partition, min,max and error will be displayed (but disabled).
       */
      row_data = $.parseJSON($('#' + service_uid + '_row_data').val());
      if (row_data !== '' && row_data !== void 0 && row_data !== null) {
        if ('disabled' in row_data && row_data.disabled === true) {
          return;
        }
      }
      element = $('[name=\'Partition.' + service_uid + ':records\']');
      new_element = '' + '<select class=\'listing_select_entry\' ' + 'name=\'Partition.' + service_uid + ':records\' ' + 'field=\'Partition\' uid=\'' + service_uid + '\' ' + 'style=\'font-size: 100%\'>';
      $.each($('td.PartTitle'), function(i, v) {
        var partid;
        partid = $($(v).children()[1]).text();
        new_element = new_element + '<option value=\'' + partid + '\'>' + partid + '</option>';
      });
      new_element = new_element + '</select>';
      $(element).replaceWith(new_element);
      logged_in_client = $('input[name=\'logged_in_client\']').val();
      if (logged_in_client !== '1') {
        element = $('[name=\'Price.' + service_uid + ':records\']');
        new_element = '' + '<input class=\'listing_string_entry numeric\' ' + 'name=\'Price.' + service_uid + ':records\' ' + 'field=\'Price\' type=\'text\' uid=\'' + service_uid + '\' ' + 'autocomplete=\'off\' style=\'font-size: 100%\' size=\'5\' ' + 'value=\'' + $(element).val() + '\'>';
        $($(element).siblings()[1]).remove();
        $(element).replaceWith(new_element);
      }
      specfields = ['min', 'max', 'error'];
      for (i in specfields) {
        element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']');
        new_element = '' + '<input class=\'listing_string_entry numeric\' type=\'text\' size=\'5\' ' + 'field=\'' + specfields[i] + '\' value=\'' + $(element).val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' ' + 'uid=\'' + service_uid + '\' autocomplete=\'off\' style=\'font-size: 100%\'>';
        $(element).replaceWith(new_element);
      }
    };

    /**
    * This functions runs the logic needed after unsetting the checkbox of a
    * service.
    * @param {service_uid} the service uid unchecked.
     */
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

    /**
    * Given a selected service, this function selects the dependencies for
    * the selected service.
    * @param {String} dlg: The dialog to display (Not working!)
    * @param {DOM object} element: The checkbox object.
    * @param {Object} dep_services: A list of UIDs.
    * @return {None} nothing.
     */
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

    /**
    * Once a checkbox has been selected, this functions finds out which are
    * the dependencies and dependants related to it.
    * @param {elements} The selected element, a checkbox.
    * @param {auto_yes} A boolean. If 'true', the dependants and dependencies
    * will be automatically selected/unselected.
     */
    calcdependencies = function(elements, auto_yes) {

      /*jshint validthis:true */
      var Dependants, Dependencies, _, cb, dep, dep_services, dep_titles, element, elements_i, html, i, lims, service_uid;
      auto_yes = auto_yes || false;
      jarn.i18n.loadCatalog('senaite.core');
      _ = window.jarn.i18n.MessageFactory("senaite.core");
      dep = void 0;
      i = void 0;
      cb = void 0;
      lims = window.bika.lims;
      elements_i = 0;
      while (elements_i < elements.length) {
        dep_services = [];
        dep_titles = [];
        element = elements[elements_i];
        service_uid = $(element).attr('value');
        if ($(element).prop('checked')) {
          Dependencies = lims.AnalysisService.Dependencies(service_uid);
          i = 0;
          while (i < Dependencies.length) {
            dep = Dependencies[i];
            if ($('#list_cb_' + dep.Service_uid).prop('checked')) {
              i++;
              continue;
            }
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

    /**
    * Given an analysis service UID, this function expands the category for
    * that service and selects it.
    * @param {String} serv_uid: uid of the analysis service.
    * @return {None} nothing.
     */
    expand_category_for_service = function(serv_uid) {
      var request_data;
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
          element = $('th[cat=\'' + cat_title + '\']');
          window.bika.lims.BikaListingTableView.category_header_expand_handler(element).done(function() {
            check_service(serv_uid);
            $('#list_cb_' + serv_uid).prop('checked', true);
          });
        }
      });
    };
    that.load = function() {};
  };

}).call(this);
