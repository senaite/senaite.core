/**
 * Controller class for Analysis Profile Edit view
 */
function AnalysisProfileEditView() {

    var that = this;

    var price_fd = $('#archetypes-fieldname-AnalysisProfilePrice');
    var price_in = $('#archetypes-fieldname-AnalysisProfilePrice #AnalysisProfilePrice');
    var vat_fd = $('#archetypes-fieldname-AnalysisProfileVAT');
    var vat_in = $('#archetypes-fieldname-AnalysisProfileVAT #AnalysisProfileVAT');
    var useprice_chk = $('#archetypes-fieldname-UseAnalysisProfilePrice #UseAnalysisProfilePrice');

    /**
     * Entry-point method for AnalysisProfileEditView
     */
    that.load = function() {
        $(useprice_chk).change(function() {
            if ($(this).is(':checked')) {
                $(price_fd).show();
                $(vat_fd).show();
            } else {
                $(price_fd).hide();
                $(vat_fd).hide();
                $(price_in).val('0');
                $(vat_in).val('0');
            }
        });
        $(useprice_chk).change();
    }
}


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.coffee
 */


/**
 * Controller class for Analysis Request View/s
 */

(function() {
  window.AnalysisRequestView = function() {
    var insert_interpretation_template, that, transition_schedule_sampling, transition_with_publication_spec, workflow_transition_sample;
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
    insert_interpretation_template = function() {
      $('#interpretationtemplate-insert').click(function(event) {
        var container, container_id, request_data, template_uid;
        event.preventDefault();
        template_uid = $('#interpretationtemplate').val();
        if (!template_uid) {
          return;
        }
        container = $('div[id^="ResultsInterpretationDepts-"].active  textarea[id^="ResultsInterpretationDepts-richtext-"]');
        if (container.length !== 1) {
          return;
        }
        container_id = container.attr("id");
        request_data = {
          catalog_name: 'uid_catalog',
          UID: template_uid,
          include_fields: ['text']
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          var text;
          if (data.objects.length === 1) {
            text = data.objects[0].text;
            return tinymce.get(container_id).insertContent(text);
          }
        });
      });
    };
    that.load = function() {
      $('a[id^=\'workflow-transition\']').not('#workflow-transition-schedule_sampling').not('#workflow-transition-sample').click(transition_with_publication_spec);
      transition_schedule_sampling();
      insert_interpretation_template();
    };
  };


  /**
   * Controller class for Analysis Request View View
   */

  window.AnalysisRequestViewView = function() {
    var parse_CCClist, that;
    that = this;

    /**
     * Entry-point method for AnalysisRequestView
     */
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
    that.load = function() {};
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


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.AnalysisServiceEditView = (function() {
    function AnalysisServiceEditView() {
      this.on_partition_required_volume_change = bind(this.on_partition_required_volume_change, this);
      this.on_partition_container_change = bind(this.on_partition_container_change, this);
      this.on_partition_separate_container_change = bind(this.on_partition_separate_container_change, this);
      this.on_partition_sampletype_change = bind(this.on_partition_sampletype_change, this);
      this.on_default_container_change = bind(this.on_default_container_change, this);
      this.on_default_preservation_change = bind(this.on_default_preservation_change, this);
      this.on_separate_container_change = bind(this.on_separate_container_change, this);
      this.on_calculation_change = bind(this.on_calculation_change, this);
      this.on_use_default_calculation_change = bind(this.on_use_default_calculation_change, this);
      this.on_default_method_change = bind(this.on_default_method_change, this);
      this.on_default_instrument_change = bind(this.on_default_instrument_change, this);
      this.on_instruments_change = bind(this.on_instruments_change, this);
      this.on_instrument_assignment_allowed_change = bind(this.on_instrument_assignment_allowed_change, this);
      this.on_methods_change = bind(this.on_methods_change, this);
      this.on_manual_entry_of_results_change = bind(this.on_manual_entry_of_results_change, this);
      this.toggle_checkbox = bind(this.toggle_checkbox, this);
      this.select_options = bind(this.select_options, this);
      this.parse_select_option = bind(this.parse_select_option, this);
      this.parse_select_options = bind(this.parse_select_options, this);
      this.add_select_option = bind(this.add_select_option, this);
      this.is_uid = bind(this.is_uid, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.get_url = bind(this.get_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.load_object_by_uid = bind(this.load_object_by_uid, this);
      this.load_manual_interims = bind(this.load_manual_interims, this);
      this.load_calculation = bind(this.load_calculation, this);
      this.load_method_calculation = bind(this.load_method_calculation, this);
      this.load_instrument_methods = bind(this.load_instrument_methods, this);
      this.load_available_instruments = bind(this.load_available_instruments, this);
      this.show_alert = bind(this.show_alert, this);
      this.set_instrument_methods = bind(this.set_instrument_methods, this);
      this.set_method_calculation = bind(this.set_method_calculation, this);
      this.flush_interims = bind(this.flush_interims, this);
      this.set_interims = bind(this.set_interims, this);
      this.get_interims = bind(this.get_interims, this);
      this.select_calculation = bind(this.select_calculation, this);
      this.set_calculation = bind(this.set_calculation, this);
      this.get_calculation = bind(this.get_calculation, this);
      this.toggle_use_default_calculation_of_method = bind(this.toggle_use_default_calculation_of_method, this);
      this.use_default_calculation_of_method = bind(this.use_default_calculation_of_method, this);
      this.select_default_instrument = bind(this.select_default_instrument, this);
      this.set_default_instrument = bind(this.set_default_instrument, this);
      this.get_default_instrument = bind(this.get_default_instrument, this);
      this.select_default_method = bind(this.select_default_method, this);
      this.set_default_method = bind(this.set_default_method, this);
      this.get_default_method = bind(this.get_default_method, this);
      this.select_instruments = bind(this.select_instruments, this);
      this.set_instruments = bind(this.set_instruments, this);
      this.get_instruments = bind(this.get_instruments, this);
      this.toggle_instrument_assignment_allowed = bind(this.toggle_instrument_assignment_allowed, this);
      this.is_instrument_assignment_allowed = bind(this.is_instrument_assignment_allowed, this);
      this.select_methods = bind(this.select_methods, this);
      this.set_methods = bind(this.set_methods, this);
      this.get_methods = bind(this.get_methods, this);
      this.toggle_manual_entry_of_results_allowed = bind(this.toggle_manual_entry_of_results_allowed, this);
      this.is_manual_entry_of_results_allowed = bind(this.is_manual_entry_of_results_allowed, this);
      this.init = bind(this.init, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    AnalysisServiceEditView.prototype.load = function() {
      var d1, d2;
      console.debug("AnalysisServiceEditView::load");
      this.all_instruments = {};
      this.invalid_instruments = {};
      d1 = this.load_available_instruments().done(function(instruments) {
        var me;
        me = this;
        return $.each(instruments, function(index, instrument) {
          var uid;
          uid = instrument.UID;
          me.all_instruments[uid] = instrument;
          if (instrument.Valid !== "1") {
            return me.invalid_instruments[uid] = instrument;
          }
        });
      });
      this.manual_interims = [];
      d2 = this.load_manual_interims().done(function(manual_interims) {
        return this.manual_interims = manual_interims;
      });
      this.selected_methods = this.get_methods();
      this.selected_instruments = this.get_instruments();
      this.selected_calculation = this.get_calculation();
      this.selected_default_instrument = this.get_default_instrument();
      this.selected_default_method = this.get_default_method();
      this.methods = this.parse_select_options($("#archetypes-fieldname-Methods #Methods"));
      this.instruments = this.parse_select_options($("#archetypes-fieldname-Instruments #Instruments"));
      this.calculations = this.parse_select_options($("#archetypes-fieldname-Calculation #Calculation"));
      this.bind_eventhandler();
      $.when(d1, d2).then(this.init);
      return window.asv = this;
    };


    /* INITIALIZERS */

    AnalysisServiceEditView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("AnalysisServiceEditView::bind_eventhandler");

      /* METHODS TAB */
      $("body").on("change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", this.on_manual_entry_of_results_change);
      $("body").on("change", "#archetypes-fieldname-Methods #Methods", this.on_methods_change);
      $("body").on("change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", this.on_instrument_assignment_allowed_change);
      $("body").on("change", "#archetypes-fieldname-Instruments #Instruments", this.on_instruments_change);
      $("body").on("change", "#archetypes-fieldname-Instrument #Instrument", this.on_default_instrument_change);
      $("body").on("change", "#archetypes-fieldname-Method #Method", this.on_default_method_change);
      $("body").on("change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", this.on_use_default_calculation_change);
      $("body").on("change", "#archetypes-fieldname-Calculation #Calculation", this.on_calculation_change);

      /* CONTAINER AND PRESERVATION TAB */
      $("body").on("change", "#archetypes-fieldname-Separate #Separate", this.on_separate_container_change);
      $("body").on("change", "#archetypes-fieldname-Preservation #Preservation", this.on_default_preservation_change);
      $("body").on("selected", "#archetypes-fieldname-Container #Container", this.on_default_container_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.sampletype']", this.on_partition_sampletype_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.separate']", this.on_partition_separate_container_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.container']", this.on_partition_container_change);
      return $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.vol']", this.on_partition_required_volume_change);
    };

    AnalysisServiceEditView.prototype.init = function() {

      /**
       * Initialize Form
       */
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("--> Manual Entry of Results is allowed");
        this.set_methods(this.methods);
      } else {
        console.debug("--> Manual Entry of Results is **not** allowed");
        this.set_methods(null);
      }
      if (this.is_instrument_assignment_allowed()) {
        console.debug("--> Instrument assignment is allowed");
        this.set_instruments(this.instruments);
      } else {
        console.debug("--> Instrument assignment is **not** allowed");
        this.set_instruments(null);
      }
      if (this.use_default_calculation_of_method()) {
        return console.debug("--> Use default calculation of method");
      } else {
        return console.debug("--> Use default calculation of instrument");
      }
    };


    /* FIELD GETTERS/SETTERS/SELECTORS */

    AnalysisServiceEditView.prototype.is_manual_entry_of_results_allowed = function() {

      /**
       * Get the value of the checkbox "Instrument assignment is not required"
       *
       * @returns {boolean} True if results can be entered without instrument
       */
      var field;
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_manual_entry_of_results_allowed = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Instrument assignment is not required" checkbox
       */
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_methods = function() {

      /**
       * Get all selected method UIDs from the multiselect field
       *
       * @returns {array} of method objects
       */
      var field;
      field = $("#archetypes-fieldname-Methods #Methods");
      return $.extend([], field.val());
    };

    AnalysisServiceEditView.prototype.set_methods = function(methods, flush) {
      var field, me;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the methods multiselect field with the given methods
       *
       * @param {array} methods
       *    Array of method objects with at least `title` and `uid` keys set
       *
       * @param {boolean} flush
       *    True to empty all instruments first
       */
      field = $("#archetypes-fieldname-Methods #Methods");
      methods = $.extend([], methods);
      if (flush) {
        field.empty();
      }
      if (methods.length === 0) {
        this.add_select_option(field, null);
      } else {
        me = this;
        $.each(methods, function(index, method) {
          var title, uid;
          if (method.ManualEntryOfResults === false) {
            return;
          }
          title = method.title || method.Title;
          uid = method.uid || method.UID;
          return me.add_select_option(field, title, uid);
        });
      }
      return this.select_methods(this.selected_methods);
    };

    AnalysisServiceEditView.prototype.select_methods = function(uids) {

      /**
       * Select methods by UID
       *
       * @param {Array} uids
       *    UIDs of Methods to select
       */
      var field, me;
      if (!this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is not allowed");
        return;
      }
      field = $("#archetypes-fieldname-Methods #Methods");
      this.select_options(field, uids);
      me = this;
      $.each(uids, function(index, uid) {
        var flush, method, option;
        flush = index === 0 && true || false;
        option = field.find("option[value=" + uid + "]");
        method = {
          uid: option.val(),
          title: option.text()
        };
        return me.set_default_method(method, flush = flush);
      });
      this.select_default_method(this.selected_default_method);
      if (this.use_default_calculation_of_method()) {
        return this.set_method_calculation(this.get_default_method());
      }
    };

    AnalysisServiceEditView.prototype.is_instrument_assignment_allowed = function() {

      /**
       * Get the value of the checkbox "Instrument assignment is allowed"
       *
       * @returns {boolean} True if instrument assignment is allowed
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_instrument_assignment_allowed = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Instrument assignment is allowed" checkbox
       */
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_instruments = function() {

      /**
       * Get all selected instrument UIDs from the multiselect
       *
       * @returns {array} of instrument objects
       */
      var field;
      field = $("#archetypes-fieldname-Instruments #Instruments");
      return $.extend([], field.val());
    };

    AnalysisServiceEditView.prototype.set_instruments = function(instruments, flush) {
      var field, me;
      if (flush == null) {
        flush = true;
      }

      /*
       * Set the instruments to the field
       *
       * @param {array} instruments
       *    Array of instrument objects to set in the multi-select
       *
       * @param {boolean} flush
       *    True to empty all instruments first
       */
      field = $("#archetypes-fieldname-Instruments #Instruments");
      instruments = $.extend([], instruments);
      if (flush) {
        field.empty();
      }
      if (instruments.length === 0) {
        this.add_select_option(field, null);
      } else {
        me = this;
        $.each(instruments, function(index, instrument) {
          var title, uid;
          uid = instrument.uid || instrument.UID;
          title = instrument.title || instrument.Title;
          return me.add_select_option(field, title, uid);
        });
      }
      return this.select_instruments(this.selected_instruments);
    };

    AnalysisServiceEditView.prototype.select_instruments = function(uids) {

      /**
       * Select instruments by UID
       *
       * @param {Array} uids
       *    UIDs of Instruments to select
       */
      var field, invalid_instruments, me, notification, title;
      if (!this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment not allowed");
        this.set_default_instrument(null);
        return;
      }
      field = $("#archetypes-fieldname-Instruments #Instruments");
      this.select_options(field, uids);
      invalid_instruments = [];
      me = this;
      $.each(uids, function(index, uid) {
        var flush, instrument;
        flush = index === 0 && true || false;
        instrument = me.all_instruments[uid];
        if (uid in me.invalid_instruments) {
          console.warn("Instrument '" + instrument.Title + "' is invalid");
          invalid_instruments.push(instrument);
        }
        return me.set_default_instrument(instrument, flush = flush);
      });
      if (invalid_instruments.length > 0) {
        notification = $("<dl/>");
        $.each(invalid_instruments, function(index, instrument) {
          return notification.append("<dd>⚠ " + instrument.Title + "</dd>");
        });
        title = _t("Some of the selected instruments are out-of-date, with failed calibration tests or under maintenance");
        this.show_alert({
          title: title,
          message: notification[0].outerHTML
        });
      } else {
        this.show_alert({
          message: ""
        });
      }
      this.select_default_instrument(this.selected_default_instrument);
      return this.set_instrument_methods(this.get_default_instrument());
    };

    AnalysisServiceEditView.prototype.get_default_method = function() {

      /**
       * Get the UID of the selected default method
       *
       * @returns {string} UID of the default method
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_default_method = function(method, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set options for the default method select
       */
      field = $("#archetypes-fieldname-Method #Method");
      method = $.extend({}, method);
      if (flush) {
        field.empty();
      }
      title = method.title || method.Title;
      uid = method.uid || method.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_default_method = function(uid) {

      /**
       * Select method by UID
       *
       * @param {string} uid
       *    UID of Method to select
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return this.select_options(field, [uid]);
    };

    AnalysisServiceEditView.prototype.get_default_instrument = function() {

      /**
       * Get the UID of the selected default instrument
       *
       * @returns {string} UID of the default instrument
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_default_instrument = function(instrument, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /*
       * Set options for the default instrument select
       */
      field = $("#archetypes-fieldname-Instrument #Instrument");
      instrument = $.extend({}, instrument);
      if (flush) {
        field.empty();
      }
      title = instrument.title || instrument.Title;
      uid = instrument.uid || instrument.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_default_instrument = function(uid) {

      /**
       * Select instrument by UID
       *
       * @param {string} uid
       *    UID of Instrument to select
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return this.select_options(field, [uid]);
    };

    AnalysisServiceEditView.prototype.use_default_calculation_of_method = function() {

      /**
       * Get the value of the checkbox "Use the Default Calculation of Method"
       *
       * @returns {boolean} True if the calculation of the method should be used
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_use_default_calculation_of_method = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Use the Default Calculation of Method" checkbox
       */
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_calculation = function() {

      /**
       * Get the UID of the selected default calculation
       *
       * @returns {string} UID of the calculation
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_calculation = function(calculation, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the calculation field with the given calculation data
       */
      field = $("#archetypes-fieldname-Calculation #Calculation");
      calculation = $.extend({}, calculation);
      if (flush) {
        field.empty();
      }
      title = calculation.title || calculation.Title;
      uid = calculation.uid || calculation.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_calculation = function(uid) {

      /**
       * Select calculation by UID
       *
       * @param {string} uid
       *    UID of Calculation to select
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      this.select_options(field, [uid]);
      return this.load_calculation(uid).done(function(calculation) {
        return this.set_interims(calculation.InterimFields);
      });
    };

    AnalysisServiceEditView.prototype.get_interims = function() {

      /**
       * Extract the interim field values as a list of objects
       *
       * @returns {array} of interim record objects
       */
      var field, interims, rows;
      field = $("#archetypes-fieldname-InterimFields");
      rows = field.find("tr.records_row_InterimFields");
      interims = [];
      $.each(rows, function(index, row) {
        var inputs, values;
        values = {};
        inputs = row.querySelectorAll("td input");
        $.each(inputs, function(index, input) {
          var key, value;
          key = this.name.split(":")[0].split(".")[1];
          value = input.value;
          if (input.type === "checkbox") {
            value = input.checked;
          }
          values[key] = value;
          return true;
        });
        if (values.keyword !== "") {
          interims.push(values);
        }
        return true;
      });
      return interims;
    };

    AnalysisServiceEditView.prototype.set_interims = function(interims, flush) {
      var field, interim_keys, more_button;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the interim field values
       *
       * Note: This method takes the same input format as returned from get_interims
       */
      interims = $.extend([], interims);
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      if (flush) {
        this.flush_interims();
      }
      interim_keys = interims.map(function(v) {
        return v.keyword;
      });
      $.each(this.manual_interims, function(index, interim) {
        var i;
        i = interim_keys.indexOf(interim.keyword);
        if (i >= 0) {
          return interims[i] = interim;
        } else {
          return interims.push(interim);
        }
      });
      return $.each(interims, function(index, interim) {
        var inputs, last_row;
        last_row = field.find("tr.records_row_InterimFields").last();
        more_button.click();
        inputs = last_row.find("input");
        return $.each(inputs, function(index, input) {
          var key, value;
          key = this.name.split(":")[0].split(".")[1];
          value = interim[key];
          if (input.type === "checkbox") {
            input.checked = value;
            input.value = "on";
          } else {
            if (!value) {
              value = "";
            }
            input.value = value;
          }
          return true;
        });
      });
    };

    AnalysisServiceEditView.prototype.flush_interims = function() {

      /**
       * Flush interim field
       */
      var field, more_button, rows;
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      more_button.click();
      rows = field.find("tr.records_row_InterimFields");
      return rows.not(":last").remove();
    };

    AnalysisServiceEditView.prototype.set_method_calculation = function(method_uid) {

      /**
       * Loads the calculation of the method and set the interims of it
       *
       * @param {string} method_uid
       *    The UID of the method to set the calculations from
       */
      if (!this.is_uid(method_uid)) {
        this.set_interims(null);
        return this.set_calculation(null);
      } else {
        return this.load_method_calculation(method_uid).done(function(calculation) {
          this.set_calculation(calculation);
          return this.set_interims(calculation.InterimFields);
        });
      }
    };

    AnalysisServiceEditView.prototype.set_instrument_methods = function(instrument_uid, flush) {
      var me;
      if (flush == null) {
        flush = true;
      }

      /**
       * Loads the methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument to set the method from
       */
      me = this;
      if (!this.is_uid(instrument_uid)) {
        return;
      }
      return this.load_instrument_methods(instrument_uid).done(function(methods) {
        methods = $.extend([], methods);
        $.each(methods, function(index, method) {
          flush = index === 0 ? true : false;
          return me.set_default_method(method, flush = flush);
        });
        this.select_default_method(this.selected_default_method);
        if (this.use_default_calculation_of_method()) {
          return this.set_method_calculation(this.get_default_method());
        }
      });
    };

    AnalysisServiceEditView.prototype.show_alert = function(options) {

      /*
       * Display a notification box above the content
       */
      var alerts, flush, html, level, message, title;
      title = options.title || "";
      message = options.message || "";
      level = options.level || "warning";
      flush = options.flush || true;
      alerts = $("#viewlet-above-content #alerts");
      if (alerts.length === 0) {
        $("#viewlet-above-content").append("<div id='alerts'></div>");
      }
      alerts = $("#viewlet-above-content #alerts");
      if (flush) {
        alerts.empty();
      }
      if (message === "") {
        alerts.remove();
      }
      html = "<div class=\"alert alert-" + level + " errorbox\" role=\"alert\">\n  <h3>" + title + "</h3>\n  <div>" + message + "</div>\n</div>";
      return alerts.append(html);
    };


    /* ASYNC DATA LOADERS */

    AnalysisServiceEditView.prototype.load_available_instruments = function() {

      /**
       * Load all available and valid instruments
       *
       * @returns {Deferred} Array of all available Instrument objects
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "bika_setup_catalog",
          page_size: 0,
          portal_type: "Instrument"
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.objects) {
          return deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.objects]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_instrument_methods = function(instrument_uid) {

      /**
       * Load assigned methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument
       * @returns {Deferred} Array of Method objects
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(instrument_uid)) {
        deferred.resolveWith(this, [[]]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/get_instrument_methods",
        data: {
          uid: instrument_uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.methods) {
          deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.methods]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_method_calculation = function(method_uid) {

      /**
       * Load assigned calculation of the given method UID
       *
       * @param {string} method_uid
       *    The UID of the method
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(method_uid)) {
        deferred.resolveWith(this, [{}]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/get_method_calculation",
        data: {
          uid: method_uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!this.is_uid(data.uid)) {
          return deferred.resolveWith(this, [{}]);
        }
        return this.load_calculation(data.uid).done(function(calculation) {
          return deferred.resolveWith(this, [calculation]);
        });
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_calculation = function(calculation_uid) {

      /*
       * Load calculation object from the JSON API for the given UID
       *
       * @param {string} calculation_uid
       *    The UID of the calculation
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(calculation_uid)) {
        deferred.resolveWith(this, [{}]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "bika_setup_catalog",
          page_size: 0,
          UID: calculation_uid,
          is_active: true,
          sort_on: "sortable_title"
        }
      };
      this.ajax_submit(options).done(function(data) {
        var calculation;
        calculation = {};
        if (data.objects.length === 1) {
          calculation = data.objects[0];
        } else {
          console.warn("Invalid data returned for calculation UID " + calculation_uid + ": ", data);
        }
        return deferred.resolveWith(this, [calculation]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_manual_interims = function() {

      /**
       * 1. Load the default calculation
       * 2. Subtract calculation interims from the current active interims
       *
       * XXX: This should be better done by the server!
       *
       * @returns {Deferred} Array of manual interims
       */
      var deferred;
      deferred = $.Deferred();
      this.load_calculation(this.get_calculation()).done(function(calculation) {
        var calculation_interim_keys, calculation_interims, manual_interims;
        calculation_interims = $.extend([], calculation.InterimFields);
        calculation_interim_keys = calculation_interims.map(function(v) {
          return v.keyword;
        });
        manual_interims = [];
        $.each(this.get_interims(), function(index, value) {
          var calculation_interim, i, ref;
          if (ref = value.keyword, indexOf.call(calculation_interim_keys, ref) < 0) {
            return manual_interims.push(value);
          } else {
            i = calculation_interim_keys.indexOf(value.keyword);
            calculation_interim = calculation_interims[i];
            return $.each(calculation_interim, function(k, v) {
              if (v !== value[k]) {
                manual_interims.push(value);
                return false;
              }
            });
          }
        });
        return deferred.resolveWith(this, [manual_interims]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_object_by_uid = function(uid) {

      /*
       * Load object by UID
       *
       * @returns {Deferred}
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "uid_catalog",
          page_size: 0,
          UID: uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        var object;
        object = {};
        if (data.objects.length === 1) {
          object = data.objects[0];
        }
        return deferred.resolveWith(this, [object]);
      });
      return deferred.promise();
    };


    /* HELPERS */

    AnalysisServiceEditView.prototype.ajax_submit = function(options) {

      /**
       * Ajax Submit with automatic event triggering and some sane defaults
       *
       * @param {object} options
       *    jQuery ajax options
       * @returns {Deferred} XHR request
       */
      var base, done;
      console.debug("°°° ajax_submit °°°");
      if (options == null) {
        options = {};
      }
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_portal_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      if (options.dataType == null) {
        options.dataType = "json";
      }
      if (options.data == null) {
        options.data = {};
      }
      if ((base = options.data)._authenticator == null) {
        base._authenticator = $("input[name='_authenticator']").val();
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = function() {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    };

    AnalysisServiceEditView.prototype.get_url = function() {

      /**
       * Return the current absolute url
       *
       * @returns {string} current absolute url
       */
      var host, location, pathname, protocol;
      location = window.location;
      protocol = location.protocol;
      host = location.host;
      pathname = location.pathname;
      return protocol + "//" + host + pathname;
    };

    AnalysisServiceEditView.prototype.get_portal_url = function() {

      /**
       * Return the portal url
       *
       * @returns {string} portal url
       */
      return window.portal_url;
    };

    AnalysisServiceEditView.prototype.is_uid = function(str) {

      /**
       * Validate valid UID
       *
       * @returns {boolean} True if the argument is a UID
       */
      var match;
      if (typeof str !== "string") {
        return false;
      }
      match = str.match(/[a-z0-9]{32}/);
      return match !== null;
    };

    AnalysisServiceEditView.prototype.add_select_option = function(select, name, value) {

      /**
       * Adds an option to the select
       */
      var option;
      if (value) {
        option = "<option value='" + value + "'>" + (_t(name)) + "</option>";
      } else {
        option = "<option selected='selected' value=''>" + (_t("None")) + "</option>";
      }
      return $(select).append(option);
    };

    AnalysisServiceEditView.prototype.parse_select_options = function(select) {

      /**
       * Parse UID/Title from the select field
       *
       * @returns {Array} of UID/Title objects
       */
      var options;
      options = [];
      $.each($(select).children(), function(index, option) {
        var title, uid;
        uid = option.value;
        title = option.innerText;
        if (!uid) {
          return;
        }
        return options.push({
          uid: uid,
          title: title
        });
      });
      return options;
    };

    AnalysisServiceEditView.prototype.parse_select_option = function(select, value) {

      /**
       * Return the option by value
       */
      var data, option;
      option = field.find("option[value=" + uid + "]");
      data = {
        uid: option.val() || "",
        title: option.text() || ""
      };
      return data;
    };

    AnalysisServiceEditView.prototype.select_options = function(select, values) {

      /**
       * Select the options of the given select field where the value is in values
       */
      return $.each($(select).children(), function(index, option) {
        var value;
        value = option.value;
        if (indexOf.call(values, value) < 0) {
          return;
        }
        return option.selected = "selected";
      });
    };

    AnalysisServiceEditView.prototype.toggle_checkbox = function(checkbox, toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the checkbox
       *
       * @param {element} checkbox
       *    The checkbox to toggle
       *
       * @param {boolean} toggle
       *    True to check the checkbox
       *
       * @param {boolean} silent
       *    True to trigger a "change" event after set
       */
      field = $(checkbox);
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      if (!silent) {
        return field.trigger("change");
      }
    };


    /* EVENT HANDLER */

    AnalysisServiceEditView.prototype.on_manual_entry_of_results_change = function(event) {

      /**
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is allowed");
        return this.set_methods(this.methods);
      } else {
        console.debug("Manual entry of results is **not** allowed");
        return this.set_methods(null);
      }
    };

    AnalysisServiceEditView.prototype.on_methods_change = function(event) {

      /**
       * Eventhandler when the "Methods" multiselect changed
       */
      var method_uids;
      console.debug("°°° AnalysisServiceEditView::on_methods_change °°°");
      method_uids = this.get_methods();
      if (method_uids.length === 0) {
        console.warn("All methods deselected");
      }
      return this.select_methods(method_uids);
    };

    AnalysisServiceEditView.prototype.on_instrument_assignment_allowed_change = function(event) {

      /**
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
      if (this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment is allowed");
        return this.set_instruments(this.instruments);
      } else {
        console.debug("Instrument assignment is **not** allowed");
        return this.set_instruments(null);
      }
    };

    AnalysisServiceEditView.prototype.on_instruments_change = function(event) {

      /**
       * Eventhandler when the "Instruments" multiselect changed
       */
      var instrument_uids;
      console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
      instrument_uids = this.get_instruments();
      if (instrument_uids.length === 0) {
        console.warn("All instruments deselected");
      }
      return this.select_instruments(instrument_uids);
    };

    AnalysisServiceEditView.prototype.on_default_instrument_change = function(event) {

      /**
       * Eventhandler when the "Default Instrument" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_instrument_change °°°");
      return this.set_instrument_methods(this.get_default_instrument());
    };

    AnalysisServiceEditView.prototype.on_default_method_change = function(event) {

      /**
       * Eventhandler when the "Default Method" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
      if (this.use_default_calculation_of_method()) {
        return this.set_method_calculation(this.get_default_method());
      }
    };

    AnalysisServiceEditView.prototype.on_use_default_calculation_change = function(event) {

      /**
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      var me;
      console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
      if (this.use_default_calculation_of_method()) {
        console.debug("Use default calculation");
        return this.set_method_calculation(this.get_default_method());
      } else {
        me = this;
        $.each(this.calculations, function(index, calculation) {
          var flush;
          flush = index === 0 ? true : false;
          return me.set_calculation(calculation, flush = flush);
        });
        if (this.selected_calculation) {
          return this.select_calculation(this.selected_calculation);
        } else {
          return this.select_calculation(this.get_calculation());
        }
      }
    };

    AnalysisServiceEditView.prototype.on_calculation_change = function(event) {

      /**
       * Eventhandler when the "Calculation" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
      return this.select_calculation(this.get_calculation());
    };

    AnalysisServiceEditView.prototype.on_separate_container_change = function(event) {

      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      var value;
      console.debug("°°° AnalysisServiceEditView::on_separate_container_change °°°");
      return value = event.currentTarget.checked;
    };

    AnalysisServiceEditView.prototype.on_default_preservation_change = function(event) {

      /**
       * Eventhandler when the "Default Preservation" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_preservation_change °°°");
    };

    AnalysisServiceEditView.prototype.on_default_container_change = function(event) {

      /**
       * Eventhandler when the "Default Container" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      var el, field, uid;
      console.debug("°°° AnalysisServiceEditView::on_default_container_change °°°");
      el = event.currentTarget;
      uid = el.getAttribute("uid");
      field = $("#archetypes-fieldname-Preservation #Preservation");
      return this.load_object_by_uid(uid).done(function(data) {
        if (data) {
          field.val(data.Preservation);
          return field.prop("disabled", true);
        } else {
          field.val("");
          return field.prop("disabled", false);
        }
      });
    };

    AnalysisServiceEditView.prototype.on_partition_sampletype_change = function(event) {

      /**
       * Eventhandler when the "Sample Type" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      var el, uid;
      console.debug("°°° AnalysisServiceEditView::on_partition_sampletype_change °°°");
      el = event.currentTarget;
      uid = el.value;
      return this.load_object_by_uid(uid).done(function(sampletype) {
        var minvol;
        minvol = sampletype.MinimumVolume || "";
        return $(el).parents("tr").find("[name^='PartitionSetup.vol']").val(minvol);
      });
    };

    AnalysisServiceEditView.prototype.on_partition_separate_container_change = function(event) {

      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_separate_container_change °°°");
    };

    AnalysisServiceEditView.prototype.on_partition_container_change = function(event) {

      /**
       * Eventhandler when the "Container" multi-select changed
       *
       * This multi select is located on the "Container and Preservation" Tab
       */
      var el, field, uid;
      console.debug("°°° AnalysisServiceEditView::on_partition_container_change °°°");
      el = event.currentTarget;
      uid = el.value;
      field = $(el).parents("tr").find("[name^='PartitionSetup.preservation']");
      return this.load_object_by_uid(uid).done(function(data) {
        if (!$.isEmptyObject(data)) {
          $(el).val(data.UID);
          $(field).val(data.Preservation);
          return $(field).prop("disabled", true);
        } else {
          return $(field).prop("disabled", false);
        }
      });
    };

    AnalysisServiceEditView.prototype.on_partition_required_volume_change = function(event) {

      /**
       * Eventhandler when the "Required Volume" value changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_required_volume_change °°°");
    };

    return AnalysisServiceEditView;

  })();

}).call(this);

/**
 * Controller class for AR Template Edit view
 */
function ARTemplateEditView() {

    var that = this;
    var samplepoint = $('#archetypes-fieldname-SamplePoint #SamplePoint');
    var sampletype = $('#archetypes-fieldname-SampleType #SampleType');

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        $(".portaltype-artemplate input[name$='save']").addClass('allowMultiSubmit');
        $(".portaltype-artemplate input[name$='save']").click(clickSaveButton);

        // Display only the sample points contained by the same parent
        filterSamplePointsByClientCombo();
        filterSampleTypesBySamplePointsCombo();
	filterSamplePointsBySampleTypesCombo();
    }

    /***
     * Filters the Sample Points Combo.
     * Display only the Sample Points from the same parent (Client or
     * BikaSetup) as the current Template.
     */
    function filterSamplePointsByClientCombo() {
        var request_data = {};
        if (document.location.href.search('/clients/') > 0) {
            // The parent object for this template is a Client.
            // Need to retrieve the Client UID from the client ID
            var cid = document.location.href.split("clients")[1].split("/")[1];
            request_data = {
                portal_type: "Client",
                id: cid,
                include_fields: ["UID"]
            };
        } else {
            // The parent object is bika_setup
            request_data = {
                portal_type: "BikaSetup",
                include_fields: ["UID"]
            };
        }
        window.bika.lims.jsonapi_read(request_data, function(data){
            if(data.objects && data.objects.length < 1) {
                return;
            }
            var obj = data.objects[0];
            var puid = obj.UID;
            $(samplepoint).attr("search_query", JSON.stringify({"getClientUID": obj.UID}));
            referencewidget_lookups([$(samplepoint)]);
        });
    }

    //Filter the Sample Type by Sample Point
    function filterSampleTypesBySamplePointsCombo() {
        $(samplepoint).bind("selected blur change", function() {
            var samplepointuid = $(samplepoint).val() ? $(samplepoint).attr('uid'): '';
            $(sampletype).attr("search_query", JSON.stringify({"getRawSamplePoints": samplepointuid}));
            referencewidget_lookups([$(sampletype)]);
        });
    }

    //Filter the Sample Point by Sample Type
    function filterSamplePointsBySampleTypesCombo() {
        $(sampletype).bind("selected blur change", function() {
            var sampletypeid = $(sampletype).val() ? $(sampletype).attr('uid'): '';
            $(samplepoint).attr("search_query", JSON.stringify({"getRawSampleTypes": sampletypeid}));
            referencewidget_lookups([$(samplepoint)]);
        });
    }


    function clickSaveButton(event){
        var selected_analyses = $('[name^="uids\\:list"]').filter(':checked');
        if(selected_analyses.length < 1){
            window.bika.lims.portalMessage("No analyses have been selected");
            window.scroll(0, 0);
            return false;
        }
    }
}

/**
 * Controller class for Batch Folder View
 */
function BatchFolderView() {

    var that = this;

    that.load = function() {

        /**
         * Modal confirmation when user clicks on 'cancel' active button.
         * Used on batch folder views
         */
        $(".portaltype-batchfolder").append("" +
                "<div id='batch-cancel-dialog' title='"+_t("Cancel batch/es?")+"'>" +
                "    <p style='padding:10px'>" +
                "        <span class='ui-icon ui-icon-alert' style=''float: left; margin: 0 7px 30px 0;'><br/></span>" +
                "        "+_t("All linked Samples will be cancelled too.") +
                "    </p>" +
                "    <p style='padding:0px 10px'>" +
                "       "+_t("Are you sure?") +
                "    </p>" +
                "</div>" +
                "<input id='batch-cancel-resp' type='hidden' value='false'/>");

        $("#batch-cancel-dialog").dialog({
            autoOpen:false,
            resizable: false,
            height:200,
            width:400,
            modal: true,
            buttons: {
                "Cancel selected batches": function() {
                    $(this).dialog("close");
                    $("#batch-cancel-resp").val('true');
                    $(".portaltype-batchfolder #cancel_transition").click();
                },
                Cancel: function() {
                    $("#batch-cancel-resp").val('false');
                    $(this).dialog("close");
                }
            }
        });

        $("#cancel_transition").click(function(event){
           if ($(".bika-listing-table input[type='checkbox']:checked").length) {
               if ($("#batch-cancel-resp").val() == 'true') {
                   return true;
               } else {
                   event.preventDefault();
                   $("#batch-cancel-dialog").dialog("open");
                   return false;
               }
           } else {
               return false;
           }
        });
    }
}

/**
 * Controller class for BikaSetup Edit view
 */
function BikaSetupEditView() {

    var that = this;

    var restrict_useraccess = $('#archetypes-fieldname-RestrictWorksheetUsersAccess #RestrictWorksheetUsersAccess');
    var restrict_wsmanagement = $('#archetypes-fieldname-RestrictWorksheetManagement #RestrictWorksheetManagement');

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function () {
        // Controller to avoid introducing no accepted prefix separator.
        $('input[id^="Prefixes-separator-"]').each(function() {
            toSelectionList(this);
        });
        // After modify the selection list, the hidden input should update its own value with the
        // selected value on the list
        $('select[id^="Prefixes-separator-"]').bind('select change', function () {
            var selection = $(this).val();
            var id = $(this).attr('id');
            $('input#'+id).val(selection)
        });

        $(restrict_useraccess).change(function () {

            if ($(this).is(':checked')) {

                // If checked, the checkbox for restrict the management
                // of worksheets must be checked too and readonly
                $(restrict_wsmanagement).prop('checked', true);
                $(restrict_wsmanagement).click(function(e) {
                    e.preventDefault();
                });

            } else {

                // The user must be able to 'un-restrict' the worksheet
                // management
                $(restrict_wsmanagement).unbind("click");

            }
        });

        if ($("select[name=NumberOfRequiredVerifications] option:selected").val() == 1) {
            document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='none';
        }
        $('#NumberOfRequiredVerifications').change(function () {
            if ($(this).val()>1) {
              document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='block';
            } else {
              document.getElementById('archetypes-fieldname-TypeOfmultiVerification').style.display='none';
            }
        });

        $(restrict_useraccess).change();
    };

    function toSelectionList(pointer) {
        /*
        The function generates a selection list to choose the prefix separator. Doing that, we can be
        sure that the user will only be able to select a correct separator.
         */
        var def_value = pointer.value;
        var current_id = pointer.id;
        // Allowed separators
        var allowed_elements = ['','-','_'];
        var selectbox = '<select id="'+current_id+'">'+'</select>';
        $(pointer).after(selectbox);
        $(pointer).hide();
        for(var i = 0; i < allowed_elements.length; i++) {
            var selected = 'selected';
            if (allowed_elements[i] != def_value) {selected = ''}
            var option =  "<option "+selected+" value="+allowed_elements[i]+">"+allowed_elements[i]+"</option>";
            $('select#'+current_id).append(option)
        }
    }
}

/**
 * Controller class for calculation edit page.
 */
function CalculationEditView() {

    var that = this;

    that.load = function() {

        // Immediately hide the TestParameters_more button
        $("#TestParameters_more").hide();

        // When updating Formula, we must modify TestParameters
        $('#Formula').live('change', function(event){

            // Get existing param keywords
            var existing_params = [];
            $.each($("[id^=TestParameters-keyword]"), function(i, e){
                existing_params.push($(e).val());
            });

            // Find param keywords used in formula
            var formula = $("#Formula").val();
            var re = /\[[^\]]*\]/gi;
            var used = formula.match(re);

            // Add missing params to bottom of list
            $.each(used, function(i, e){
                e = e.replace('[', '').replace(']', '');
                if(existing_params.indexOf(e) == -1){
                    // get the last (empty) param row, for copying
                    var existing_rows = $(".records_row_TestParameters");
                    var lastrow = $(existing_rows[existing_rows.length-1]);
                    // row_count for renaming new row
                    var nr = existing_rows.length.toString();
                    // clone row
                    var newrow = $(lastrow).clone(true);
                    // insert the keyword into the new row
                    $(newrow).find('[id^=TestParameters-keyword]').val(e);
                    // rename IDs of inputs
                    $(newrow).find('[id^=TestParameters-keyword]').attr('id', 'TestParameters-keyword-' + nr);
                    $(newrow).find('[id^=TestParameters-value]').attr('id', 'TestParameters-value-' + nr);
                    $(newrow).insertBefore(lastrow);
                }
            });
        });
    }

}

/**
 * Controller class for Client's Edit view
 */
function ClientEditView() {

    var that = this;
    var acheck = "#archetypes-fieldname-DecimalMark";
    var check  = "#DefaultDecimalMark"

    /**
     * Entry-point method for ClientEditView
     */
    that.load = function() {

        loadDecimalMarkBehavior();

    }

    /**
     * When the Avoid Client's Decimal Mark Selection checkbox is set,
     * the function will disable Select Decimal Mark dropdown list.
     */
    function loadDecimalMarkBehavior() {

        loadDMVisibility($(check));

        $(check).click(function(){
            loadDMVisibility($(this));
        });

        function loadDMVisibility(dmcheck) {
            if (dmcheck.is(':checked')) {
                $(acheck).fadeOut().hide();
            } else {
                $(acheck).fadeIn();

            }
        }
    }
}
/**
* Client's overlay edit view Handler. Used by add buttons to
* manage the behaviour of the overlay.
*/
function ClientOverlayHandler() {
  var that = this;

  // Needed for bika.lims.loader to register the object at runtime
  that.load = function() {}

  /**
   * Event fired on overlay.onLoad()
   * Hides undesired contents from inside the overlay and also
   * loads additional javascripts still not managed by the bika.lims
   * loader
   */
  that.onLoad = function(event) {

      // Address widget
      $.ajax({
          url: 'bika_widgets/addresswidget.js',
          dataType: 'script',
          async: false
      });
  }
}

/**
 * Global vars
 */

function CommonUtils() {

    var that = this;

    /**
     * Entry-point method for CommonUtils
     */
    that.load = function() {

        window.bika = window.bika || {
            lims: {}
        };

        /**
         * Analysis Service dependants and dependencies retrieval
         */
        window.bika.lims.AnalysisService = window.bika.lims.AnalysisService || {
            Dependants: function(service_uid){
                var request_data = {
                    catalog_name: "bika_setup_catalog",
                    UID: service_uid,
                    include_methods: 'getServiceDependantsUIDs',
                };
                var deps = {};
                $.ajaxSetup({async:false});
                window.bika.lims.jsonapi_read(request_data, function(data){
                    if (data.objects != null && data.objects.length > 0) {
                        deps = data.objects[0].getServiceDependantsUIDs;
                    } else {
                        deps = [];
                    }
                });
                $.ajaxSetup({async:true});
                return deps;
            },
            Dependencies: function(service_uid){
                var request_data = {
                    catalog_name: "bika_setup_catalog",
                    UID: service_uid,
                    include_methods: 'getServiceDependenciesUIDs',
                };
                var deps = {};
                $.ajaxSetup({async:false});
                window.bika.lims.jsonapi_read(request_data, function(data){
                    if (data.objects != null && data.objects.length > 0) {
                        deps = data.objects[0].getServiceDependenciesUIDs;
                    } else {
                        deps = [];
                    }
                });
                $.ajaxSetup({async:true});
                return deps;
            }
        };

        window.bika.lims.portalMessage = function (message) {
            var str = "<dl class='portalMessage error alert alert-danger'>"+
                "<dt>"+_t("Error")+"</dt>"+
                "<dd><ul>" + message +
                "</ul></dd></dl>";
            $(".portalMessage").remove();
            $(str).appendTo("#viewlet-above-content");
        };

        window.bika.lims.log = function(e) {
            if (window.location.url == undefined || window.location.url == null) {
                return;
            }
            var message = "(" + window.location.url + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_log",
                data: {"message":message,
                        "_authenticator": $("input[name='_authenticator']").val()}
            });
        };
        window.bika.lims.warning = function(e) {
            var message = "(" + window.location.href + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_warn",
                data: {"message":message,
                        "_authenticator": $("input[name='_authenticator']").val()}
            });
        };
        window.bika.lims.error = function(e) {
            var message = "(" + window.location.href + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_err",
                data: {"message":message,
                        "_authenticator": $("input[name='_authenticator']").val()}
            });
        };

        window.bika.lims.jsonapi_cache = {};
        window.bika.lims.jsonapi_read = function(request_data, handler) {
            window.bika.lims.jsonapi_cache = window.bika.lims.jsonapi_cache || {};
            // if no page_size is specified, we need to explicitly add one here: 0=all.
            var page_size = request_data.page_size;
            if (page_size == undefined) {
                request_data.page_size = 0
            }
            var jsonapi_cacheKey = $.param(request_data);
            var jsonapi_read_handler = handler;
            if (window.bika.lims.jsonapi_cache[jsonapi_cacheKey] === undefined){
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: window.portal_url + "/@@API/read",
                    data: request_data,
                    success: function(data) {
                        window.bika.lims.jsonapi_cache[jsonapi_cacheKey] = data;
                        jsonapi_read_handler(data);
                    }
                });
            } else {
                jsonapi_read_handler(window.bika.lims.jsonapi_cache[jsonapi_cacheKey]);
            }
        };

        /**
         * Update or modify a query filter for a reference widget.
         * This will set the options, then re-create the combogrid widget
         * with the new filter key/value.
         * If filtervalue is empty, the function will delete the query element.
         *
         * @param {object} element - the input element as combogrid.
         * @param {string} filterkey - the new filter key to filter by.
         * @param {string} filtervalue - the value of the new filter.
         * @param {string} querytype - it can be 'base_query' or 'search_query'
         */
        window.bika.lims.update_combogrid_query = function(
                element, filterkey, filtervalue, querytype) {

            if (!$(element).is(':visible')) {
                return;
            };
            if (!querytype) {
                querytype = 'base_query';
            };
            var query =  jQuery.parseJSON($(element).attr(querytype));
            // Adding the new query filter
            if (filtervalue) {
                query[filterkey] = filtervalue;
                };
            // Deleting the query filter
            if (filtervalue === '' && query[filterkey]){
                delete query[filterkey];
            };
            $(element).attr(querytype, JSON.stringify(query));

            var options = jQuery.parseJSON(
                $(element).attr("combogrid_options"));

            // Building new ajax request
            options.url = window.portal_url + "/" + options.url;
            options.url = options.url + "?_authenticator=" +
                $("input[name='_authenticator']").val();
            options.url = options.url + "&catalog_name=" +
                $(element).attr("catalog_name");

            options.url = options.url + "&base_query=" +
                encodeURIComponent($(element).attr("base_query"));
            options.url = options.url + "&search_query=" +
                encodeURIComponent($.toJSON(query));

            var col_model = options.colModel;
            var search_fields = options.search_fields;
            var discard_empty = options.discard_empty;
            var min_length = options.minLength;

            options.url = options.url + "&colModel=" +
                $.toJSON(col_model);

            options.url = options.url + "&search_fields=" +
                $.toJSON(search_fields)

            options.url = options.url + "&discard_empty=" +
                $.toJSON(discard_empty);

            options.url = options.url + "&minLength=" +
                $.toJSON(min_length);

            options.force_all = "false";

            // Apply changes
            $(element).combogrid(options);
        };

        // Priority Selection Widget
        $('.ArchetypesPrioritySelectionWidget select').change(function(e){
            var val = $(this).find('option:selected').val();
            $(this).attr('value', val);
        });
        $('.ArchetypesPrioritySelectionWidget select').change();

    }
    that.svgToImage = function(svg) {
        var url = 'data:image/svg+xml;base64,' + btoa(svg);
        return '<img src="'+url+'"/>';
    };
}

/**
 * Controller class for Lab Contacts view of Department
 */
function DepartmentLabContactsView() {

    var that = this;

    /**
     * Entry-point method for DepartmentLabContactsViewView
     */
    that.load = function() {
        set_autosave();
    };

    function set_autosave() {
        /**
        Set an event for each checkbox in the view. After chenging the state of
        the checkbox, the event automatically saves the change.
        */
        $("table.bika-listing-table td input[type='checkbox']")
            .not('[type="hidden"]').each(function(i){
            // Save input fields
            $(this).change(function () {
                var pointer = this;
                save_change(pointer);
            });
        });
    }

    function save_change(pointer) {
        /**
         Build an array with the data to be saved.
         @pointer is the object which has been modified and we want to save
         its new state.
         */
        var check_value, contact_uid, department_uid, uid, department_path,
            requestdata={};
        // Getting the checkbox state
        check_value = $(pointer).prop('checked');
        // Getting the lab contact uid, url and name
        contact_uid = $(pointer).val();
        // Getting the department uid
        url = window.location.href.replace('/labcontacts', '');
        department_path = url.replace(window.portal_url, '');
        // Filling the requestdata
        requestdata.contact_uid = contact_uid;
        requestdata.checkbox_value = check_value;
        requestdata.department = department_path;
        save_element(requestdata);
    }

    function save_element(requestdata) {
        /**
        Given a dict with the uid and the checkbox value, update this state via
        ajax petition.
        @requestdata should has the format:
            {department=department_path,
            checkbox_value=check_value,
            contact_uid=contact_uid}
        */
        // Getting the name of the modified lab contact as an anchor
        var url =  $('tr[uid="' + requestdata.contact_uid + '"] td.Fullname a')
            .attr('href');
        var name =  $('tr[uid="' + requestdata.contact_uid + '"] td.Fullname a')
            .text();
        var anch =  "<a href='"+ url + "'>" + name + "</a>";
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location.href.replace('/labcontacts', '')+"/labcontactupdate",
            data: {'data': JSON.stringify(requestdata)}
        })
        .done(function(data) {
            //success alert
            if (data !== null && data.success === true) {
                bika.lims.SiteView.notificationPanel(
                    anch + ' updated successfully', "succeed");
            } else {
                bika.lims.SiteView.notificationPanel(
                    'Failure while updating ' + anch, "error");
                var msg =
                    '[bika.lims.department.js in DepartmentLabContactsView] ' +
                    'Failure while updating ' + name + 'in ' +
                    window.location.href;
                console.warn(msg);
                window.bika.lims.error(msg);
            }
        })
        .fail(function(){
            //error
            bika.lims.SiteView.notificationPanel(
                'Error while updating ' + anch, "error");
            var msg =
                '[bika.lims.department.js in DepartmentLabContactsView] ' +
                'Error while updating ' + name + 'in ' +
                window.location.href;
            console.warn(msg);
            window.bika.lims.error(msg);
        });
    }

}

/**
 * D3 Control chart
 */
function ControlChart() {

    var that = this;
    var datasource = [];
    var xcolumnkey = 'date';
    var ycolumnkey = 'value';
    var xlabel = "Date";
    var ylabel = "Value";
    var lowerlimit = 0;
    var upperlimit = 1;
    var centerlimit = 0.5;
    var lowerlimit_text = "Lower Limit";
    var upperlimit_text = "Upper Limit";
    var lowerlimit_text = "Center Limit";
    var interpolation = "basis";
    var pointid = "";

    /**
     * Sets the data to the chart
     *
     * Data format:
     *   [{ "date": "2014-03-12 13:01:00",
     *      "value": "2.13"},
     *    { "date": "2014-03-13 11:11:11",
     *      "value": "5.2"}]
     *
     * By default the column keys are 'date' and 'value', but can be
     * changed using the methods setXColumn and setYColumn. This allows
     * not to restrict the data source to only two columns.
     */
    this.setData = function(data) {
        that.datasource = data;
    }

    /**
     * Sets the X key from the datasource X-values.
     * By default, 'date'
     */
    this.setXColumn = function(xcolumnkey) {
        that.xcolumnkey = xcolumnkey;
    }

    /**
     * Sets the Y key from the datasource Y-values.
     * By default, 'value'
     */
    this.setYColumn = function(ycolumnkey) {
        that.ycolumnkey = ycolumnkey;
    }

    /**
     * Label to display on the Y-axis
     * By default, 'Date'
     */
    this.setYLabel = function(ylabel) {
        that.ylabel = ylabel;
    }

    /**
     * Label to display on the X-axis
     * By default, 'Value'
    */
    this.setXLabel = function(xlabel) {
        that.xlabel = xlabel;
    }

    /**
     * Sets the upper limit line value
     * Default: 1
     */
    this.setUpperLimit = function(upperLimit) {
        that.upperlimit = upperLimit;
    }

    /**
     * Sets the lower limit line value
     * Default: 0
     */
    this.setLowerLimit = function(lowerLimit) {
        that.lowerlimit = lowerLimit;
    }

    /**
     * Sets the center limit line value
     * Default: 0.5
     */
    this.setCenterLimit = function(centerLimit) {
        that.centerlimit = centerLimit;
    }

    /**
     * Sets the text to be displayed above upper limit line
     * By default: 'Upper Limit'
     */
    this.setUpperLimitText = function(upperLimitText) {
        that.upperlimit_text = upperLimitText;
    }

    /**
     * Sets the text to be displayed below lower limit line
     * By default: 'Lower Limit'
     */
    this.setLowerLimitText = function(lowerLimitText) {
        that.lowerlimit_text = lowerLimitText;
    }

    /**
     * Sets the text to be displayed above center limit line
     * By default: 'Center Limit'
     */
    this.setCenterLimitText = function(centerLimitText) {
        that.centerlimit_text = centerLimitText;
    }

    /**
     * Sets the interpolation to be used for drawing the line
     */
    this.setInterpolation = function(interpolation) {
        that.interpolation = interpolation;
    }

    /**
     * Sets the key to be used to set the identifier to each point
     */
    this.setPointId = function(pointId) {
        that.pointid = pointId;
    }

    /**
     * Draws the chart inside the container specified as 'canvas'
     * Accepts a jquery element identifier (i.e. '#chart')
     */
    this.draw = function(canvas) {
        var width = $(canvas).innerWidth() - 20;
        var height = $(canvas).innerHeight() - 20;
        var margin = {top: 20, right: 20, bottom: 30, left: 30},
        width = width - margin.left - margin.right,
        height = height - margin.top - margin.bottom;

        var x = d3.time.scale()
            .range([0, width]);

        var y = d3.scale.linear()
            .range([height,0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickSize(0);

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .tickSize(0);

        var line = d3.svg.line()
            .interpolate(that.interpolation)
            .x(function(d) { return x(d.x_axis); })
            .y(function(d) { return y(d.y_axis); });

        var svg = d3.select(canvas).append("svg")
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        function tonumber(val) {
            if (!val || typeof o !== 'string') {
              return val;
            }
            return +val;
        }

        // Let's go for fun
        // Convert values to floats
        // "2014-02-19 03:11 PM"
        x_data_parse = d3.time.format("%Y-%m-%d %I:%M %p").parse;
        that.datasource.forEach(function(d) {
            d.x_axis = x_data_parse(d[that.xcolumnkey]);
            d.y_axis = tonumber(d[that.ycolumnkey]);
            d.point_id = d[that.pointid];
        });

        function sortByDateAscending(a, b) {
            return a.x_axis - b.x_axis;
        }
        that.datasource.sort(sortByDateAscending);

        x.domain(d3.extent(that.datasource, function(d) { return d.x_axis; }));
        var min = d3.min(that.datasource, function(d) { return d.y_axis; });
        if (min > that.lowerlimit) {
            min = that.lowerlimit;
        }
        var max = d3.max(that.datasource, function(d) { return d.y_axis; });
        if (max < that.upperlimit) {
            max = that.upperlimit;
        }
        y.domain([min, max]);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
                .style("font-size", "11px")
                .append("text")
                    .attr("x", width)
                    .attr("dy", "-0.71em")
                    .attr("text-anchor", "end")
                    .text(that.xlabel);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .style("font-size", "11px")
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(that.ylabel);

        svg.append("path")
            .datum(that.datasource)
            .attr("stroke", "#4682b4")
            .attr("stroke-width", "1.5px")
            .attr("fill", "none")
            .attr("class", "line")
            .attr("d", line);

        // set points
        that.datasource.forEach(function(d) {
            svg.append("g")
                .attr("fill", "#2f2f2f")
                .append("circle")
                .attr("id", d.point_id)
                .attr("r", 3)
                .attr("cx", x(d.x_axis))
                .attr("cy", y(d.y_axis))
                .on("mouseout", function() {
                    d3.select(this)
                        .attr("fill", "#2f2f2f")
                        .attr("r", 3);
                    d3.select(this.parentNode.children[1])
                        .remove();
                })
                .on("mouseover",  function() {
                    d3.select(this)
                        .attr("fill", "#4682b4")
                        .attr("r", 6);
                    d3.select(this.parentNode)
                        .append("text")
                            .attr("fill", "#000000")
                            .style("font-size", "10px")
                            .attr("x", x(d.x_axis) - 10)
                            .attr("y", y(d.y_axis) - 10)
                            .text(d.y_axis+that.ylabel);
                }).on("click",  function() {
                    d3.select(this)
                        .attr("fill", "#4682b4")
                        .attr("r", 6);
                    d3.select(this.parentNode)
                        .append("text")
                            .attr("fill", "#000000")
                            .style("font-size", "10px")
                            .attr("x", x(d.x_axis) - 10)
                            .attr("y", y(d.y_axis) - 10)
                            .text(d.y_axis+that.ylabel);
                });
        });

        // upper limit line
        svg.append("line")
            .attr("stroke", "#8e0000")
            .attr("stroke-width", "1px")
            .attr("stroke-dasharray", "5, 5")
            .attr({ x1: 0, y1: y(that.upperlimit), x2: width, y2: y(that.upperlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.upperlimit) - 5})
            .style("font-size","11px")
            .text(that.upperlimit_text);

        // lower limit line
        svg.append("line")
            .attr("stroke", "#8e0000")
            .attr("stroke-width", "1px")
            .attr("stroke-dasharray", "5, 5")
            .attr({ x1: 0, y1: y(that.lowerlimit), x2: width, y2: y(that.lowerlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.lowerlimit) - 5})
            .style("font-size","11px")
            .text(that.lowerlimit_text);

        // center limit line
        svg.append("line")
            .attr("stroke", "#598859")
            .attr("stroke-width", "1px")
            .attr({ x1: 0, y1: y(that.centerlimit), x2: width, y2: y(that.centerlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.centerlimit) - 5})
            .style("font-size","11px")
            .text(that.centerlimit_text);
    }
}

/**
 * Controller class for Range graphics
 */
function RangeGraph() {

    var that = this;

    that.load = function() {
        $(".range-chart").each(function(e) {
          var width = Number($(this).css('width').replace(/[^\d\.\-]/g, ''));
          loadRangeChart($(this).get(0), width,
              $.parseJSON($(this).attr('data-range')),
              $.parseJSON($(this).attr('data-result')));
          $(this).removeClass('range-chart');
        });
    }

    function to_dict_of_floats(range, result) {
        if (!$.isNumeric(result)) {
            return null;
        }
        var result = parseFloat(result);
        if (!('min' in range) || !('max' in range)) {
            return null;
        }
        var range_min = $.isNumeric(range.min) ? parseFloat(range.min) : result;
        var range_max = $.isNumeric(range.max) ? parseFloat(range.max) : result;
        if (range_min == range_max) {
            return null;
        }
        var warn_min = range_min;
        var warn_max = range_max;
        if ('warn_min' in range && $.isNumeric(range.warn_min)) {
            warn_min = parseFloat(range.warn_min);
            warn_min = (warn_min < range_min) ? warn_min : range_min;
        }
        if ('warn_max' in range && $.isNumeric(range.warn_max)) {
            warn_max = parseFloat(range.warn_max);
            warn_max = (warn_max > range_max) ? warn_max : range_max;
        }
        return {'result': result,
                'min': range_min,
                'max': range_max,
                'warn_min': warn_min,
                'warn_max': warn_max}
    }

    function loadRangeChart(canvas, width, range, result) {
        var specs = to_dict_of_floats(range, result)
        if (!specs) {
            return
        }
        console.log($.toJSON(specs));

        var radius = width*0.03;
        var height = radius*2;
        width -= radius*2;
        var range_min = specs.min;
        var range_max = specs.max;
        var warn_min = specs.warn_min;
        var warn_max = specs.warn_max;
        var result = specs.result;
        var min_operator = 'min_operator' in range ? range.min_operator : 'geq';
        var max_operator = 'max_operator' in range ? range.max_operator : 'leq';

        // We want 1/3 of the whole scale length at left and right
        var extra = (warn_max - warn_min)/3;
        var x_min = result < warn_min ? result : warn_min - extra;
        var x_max = result > warn_max ? result : warn_max + extra;
        var inrange = (result >= range_min);
        if (min_operator == 'gt') {
            inrange = result > range_min;
        }
        if (max_operator == 'lt') {
            inrange = inrange && (result < range_max);
        } else {
            inrange = inrange && (result <= range_max);
        }
        var inshoulder = false;
        if (!inrange) {
            var in_warn_min = (result < range_min);
            if (min_operator == 'gt') {
                in_warn_min = (result <= range_min);
            }
            in_warn_min = in_warn_min && (result >= warn_min);
            var in_warn_max = (result > range_max);
            if (max_operator == 'lt') {
                in_warn_max = (result >= range_max);
            }
            in_warn_max = in_warn_max && (result <= warn_max);
            inshoulder = in_warn_min || in_warn_max;
        }
        var outofrange = !inrange && !inshoulder;
        var color_range = (inrange || inshoulder) ? "#a8d6cf" : "#cdcdcd";
        var color_dot = inrange ? "#279989" : (inshoulder ? "#ffae00" : "#ff0000");
        var color_shoulder = (inrange || inshoulder) ? "#d9e9e6" : "#dcdcdc";

        var x = d3.scale.linear()
            .domain([x_min, x_max])
            .range([0, width]);

        var chart = d3.select(canvas)
            .append("svg")
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .attr("width", width + (radius*2))
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + radius + ",0)");

        // Backgrounds
        var bar_height = (radius*2)*0.8;
        var bar_y = (height/2)-((radius*2*0.8)/2);
        var bar_radius = radius*0.9;

        // Out-of-range left
        chart.append("rect")
            .attr("x", x(x_min))
            .attr("y", bar_y)
            .attr("width", x(warn_min)-x(x_min)+bar_radius)
            .attr("height", bar_height)
            .attr("rx", bar_radius)
            .attr("ry", bar_radius)
            .style("fill", "#e9e9e9");

        // Left shoulder
        chart.append("rect")
            .attr("x", x(warn_min))
            .attr("y", bar_y)
            .attr("width", x(range_min)-x(warn_min))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Right shoulder
        chart.append("rect")
            .attr("x", x(range_max))
            .attr("y", bar_y)
            .attr("width", x(warn_max)-x(range_max))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Out-of-range right
        chart.append("rect")
            .attr("x", x(warn_max)-bar_radius)
            .attr("y", bar_y)
            .attr("width", x(x_max)-x(warn_max)+bar_radius)
            .attr("height", bar_height)
            .attr("rx", bar_radius)
            .attr("ry", bar_radius)
            .style("fill", "#e9e9e9");

        // Valid range
        // 8a8d8f a8d6cf
        chart.append("rect")
            .attr("x", x(range_min))
            .attr("y", bar_y)
            .attr("width", x(range_max)-x(range_min))
            .attr("height", bar_height)
            .style("fill", color_range);

        // Min shoulder line
      /*  chart.append("rect")
            .attr("x", x(range_min_shoulder))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Min line
        chart.append("rect")
            .attr("x", x(range_min))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Max line
        chart.append("rect")
            .attr("x", x(range_max))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Max shoulder line
        chart.append("rect")
            .attr("x", x(range_max_shoulder))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");*/

        // Outer dot
        chart.append("circle")
            .attr("cx", x(result))
            .attr("cy", height/2)
            .attr("r", radius)
            .style("fill", "white");

        // Inner dot
        chart.append("circle")
            .attr("cx", x(result))
            .attr("cy", height/2)
            .attr("r", radius-1)
            .style("fill", color_dot);

    }
}

/**
 * Controller class for Instrument Import View
 */
function InstrumentImportView() {

    var that = this;

    /**
     * Entry-point method for Instrument Import View
     */
    that.load = function() {

        // Load interfaces for selected Instrument
        $("#instrument_select").change(function(){
            $('.portalMessage').remove();
            $("#import_form").empty();
            $("#intermediate").toggle(false);
            if($(this).val() == ""){
                $("#exim").empty();
            } else {
              $.ajax({
                type: 'POST',
                dataType: 'json',
                url: window.location.href.replace("/import", "/getImportInterfaces"),
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'instrument_uid': $(this).val()
                      },
                success: function(data){
                  $("#exim").empty();
                  $('#exim').append($('<option>').text('Choose an Interface...')
                            .attr('value', '').attr('selected', 'selected'));
                  $('#exim').append($('<option>').text('Default')
                            .attr('value', 'default'));
                  $.each(data, function(i, value) {
                     $('#exim').append($('<option>').text(value.title).attr('value', value.id));
                  });
                }
              });
            }
        });

        // Load import form for selected data interface
        $("#exim").change(function(){
            $('.portalMessage').remove();
            $("#intermediate").toggle(false);
            if($(this).val() == ""){
                $("#import_form").empty();
            } else {
                $("#import_form").load(
                    window.location.href.replace("/import", "/getImportTemplate"),
                    {'_authenticator': $('input[name="_authenticator"]').val(),
                     'exim': $(this).val()
                    });
            }
        });
        show_default_result_key();

        // Invoke import
        $("[name='firstsubmit']").live('click',  function(event){
            event.preventDefault();
            $('.portalMessage').remove();
            if ($("#intermediate").length == 0) {
                $("#import_form").after("<div id='intermediate'></div>");
            }
            $("#intermediate").toggle(false);
            form = $(this).parents('form');
            options = {
                target: $('#intermediate'),
                data: JSON.stringify(form.formToArray()),
                dataType: 'json',
                processData: false,
                success: function(responseText, statusText, xhr, $form){
                    $("#intermediate").empty();
                    if(responseText['log'].length > 0){
                        str = "<div class='alert alert-info'>";
                        str += "<h3>"+ _t("Log trace") + "</h3><ul>";
                        $.each(responseText['log'], function(i,v){
                            str += "<li>" + v + "</li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                    if(responseText['errors'].length > 0){
                        str = "<div class='alert alert-danger'>";
                        str += "<h3>"+ _t("Errors") + "</h3><ul>";
                        $.each(responseText['errors'], function(i,v){
                            str += "<li><code>" + v + "</code></li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                    if(responseText['warns'].length > 0){
                        str = "<div class='alert alert-warning'>";
                        str += "<h3>"+ _t("Warnings") + "</h3><ul>";
                        $.each(responseText['warns'], function(i,v){
                            str += "<li>" + v + "</li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $("#intermediate").empty();
                    str = "<div class='alert alert-danger'>";
                    str += "<h3>"+ _t("Errors found") + "</h3><ul>";
                    str += "<li>" + textStatus;
                    str += "<pre>" + errorThrown + "</pre></li></ul></div>";
                    $("#intermediate").append(str).toggle(true);
                }

            };
            form.ajaxSubmit(options);
            return false;
        });

    }

    function portalMessage(messages){
        str = "<dl class='portalMessage error alert alert-danger'>"+
            "<dt>"+_('error')+"</dt>"+
            "<dd>";
        $.each(messages, function(i,v){
            str = str + "<ul><li>" + v + "</li></ul>";
        });
        str = str + "</dd></dl>";
        $('.portalMessage').remove();
        $('#viewlet-above-content').append(str);
    }

    function show_default_result_key() {
        /**
         * Show/hide the input element div#default_result when an AS is (un)selected.
         */
        $("select#exim").change(function() {
            setTimeout(function() {
                $('select#analysis_service').bind("select change", function() {
                    if ($('select#analysis_service').val() != '') {
                        $('div#default_result').fadeIn();
                    }
                    else { $('div#default_result').fadeOut(); }
                })
            }, 800);
        });
    }
}

/**
 * Controller class for Instrument Certification Edit view
 */
function InstrumentCertificationEditView() {

    var that = this;

    /**
     * Entry-point method for InstrumentCertificationEditView
     */
    that.load = function() {

        $('#Internal').live('change', function() {
            loadAgency();
        });

        loadAgency();
    }

    /**
     * Loads the Agency Field. If the certification is set as Internal,
     * the Agency field is hided.
     */
    function loadAgency() {
        if ($('#Internal').is(':checked')) {
            $('#archetypes-fieldname-Agency').hide();
        } else {
            $('#archetypes-fieldname-Agency').fadeIn('slow');
        }
    }
}
/**
 * Controller class for Instrument Edit view
 */
function InstrumentEditView() {

    var that = this;

    /**
     * Entry-point method for InstrumentEditView
     */
    that.load = function() {
      // Removing 'More' button of RecordsWidget
      $('#ResultFilesFolder_more').remove();
      // Removing 'Delete' button of rows and also deleting last empty row.
      var rows=$('.records_row_ResultFilesFolder');
      for(i=0;i< rows.length;i++){
        if (i>0 && i==(rows.length-1)) {
          rows[i].remove();
        }else{
          rows[i].children[2].remove();
        }
      }
    }

    $('#ImportDataInterface').change(function() {
        updateFolders();
    });

    /**
    When user adds/removes an Interface from select of Interfaces,
    Interface Results Folder will be updated.
    */
    function updateFolders() {
        // First we delete all rows, and then adding new ones accordingly to
        // selected Interfaces.
        var table = $("#ResultFilesFolder_table");
        var rows = $(".records_row_ResultFilesFolder");
        var values = $('#ImportDataInterface').val();
        rows.remove();

        // If no interface is selected we will add empty row
        if (values == null || (values.length==1 && values[0]=='')) {
          var new_row = $(rows[rows.length-1]).clone();
          for(i=0; i<$(new_row).children().length; i++){
              var td = $(new_row).children()[i];
              var input = $(td).children()[0];
              $(input).val('');
          }
          $(new_row).appendTo($(table));
        }else{
          for(i=0; i< values.length; i++){
            if (values[i]!='') {
              var new_row = $(rows[rows.length-1]).clone();
              var interface_td = $(new_row).children()[0];
              var interface_input = $(interface_td).children()[0];
              $(interface_input).val(values[i]);
              var folder_td = $(new_row).children()[1];
              var folder_input = $(folder_td).children()[0];
              $(folder_input).val('');
              $(new_row).appendTo($(table));
            }
          }
          // Checking if ids are Unique
          renameInputs();
        }
    }

    /**
    Updating IDs Interface Name and Folder inputs to be sure they are unique
    */
    function renameInputs() {
      var table = $("#ResultFilesFolder_table");
      var rows = $(".records_row_ResultFilesFolder");
      for(i=0; i< rows.length; i++){
        var inputs = $(rows[i]).find("input[id^='ResultFilesFolder']");
        for(j=0; j< inputs.length; j++){
          var ID = inputs[j].id;
          var prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
          $(inputs[j]).attr('id', prefix + "-" + i);
        }
      }
    }
}


/**
 * Controller class for Instrument Reference Analyses view
 */
function InstrumentReferenceAnalysesView() {

    var that = this;

    /**
     * Entry-point method for InstrumentReferenceAnalysesView
     */
    that.load = function() {

        // Populate analyses selector
        var data = $.parseJSON($('#graphdata').val());
        var qcrec = false;
        $.map(data, function(value,key){
            $('#selanalyses').append('<option value="'+key+'">'+key+'</option>');
        });

        // Draw the chart and filter rows
        if ($('#selanalyses').val()) {
            updateQCSamples(data[$('#selanalyses').val()]);
            filterRows();
            drawControlChart(null, null);
        }

        $('#selanalyses').change(function(e) {
            updateQCSamples(data[$('#selanalyses').val()]);
            drawControlChart(null, null);
            filterRows();
        });

        $('#selqcsample').change(function(e) {
            drawControlChart(null, null);
            filterRows();
        });

        $('#interpolation').change(function(e) {
            drawControlChart(null, null);
        });

        $('.item-listing-tbody tr').mouseover(function(e) {
            if ($(this).attr('uid') != '') {
                $(this).addClass('selected');
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseover');
            }
        });
        $('.item-listing-tbody tr').mouseout(function(e) {
            $(this).removeClass('selected');
            if ($(this).attr('uid') != '') {
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseout');
            }
        });

        $('#printgraph').click(function(e) {
            e.preventDefault();

            // Scaling for print
            var w = 670;
            var h = $('#chart').attr('height');
            drawControlChart(w, h);

            var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
            var css = '<link href="' + window.portal_url + '/++resource++bika.lims.css/print-graph.css" type="text/css" rel="stylesheet">';
            var h1 = $("span.documentFirstHeading").closest('h1').clone();
            var content = $('#content-core').clone();
            $(content).prepend(h1);
            $(content).find('#selanalyses').after("<span class='bold'>"+$('#selanalyses').val()+"</span>");
            $(content).find('#interpolation').after("<span class='bold'>"+$('#interpolation').val()+"</span>");
            $(content).find('#selqcsample').after("<span class='bold'>"+$('#selqcsample').val()+"</span>");
            $(content).find('#selanalyses').hide();
            $(content).find('#interpolation').hide();
            $(content).find('#selqcsample').hide();

            WinPrint.document.write("<html><head>"+css+"</head><body>"+$(content).html()+"</body></html>");
            WinPrint.document.close();
            WinPrint.focus();
            WinPrint.print();

            // Re-scale
            $("#chart").css('width', '100%');
            $("#chart").removeAttr('height');
            drawControlChart(null, null);

            WinPrint.close();
        });

        $('div.bika-listing-table-container').fadeIn();
    }

    /**
     * Updates the QC Samples picklist
     */
    function updateQCSamples(qcsamples) {
        var presel = $('#selqcsample').val();
        $('#selqcsample option').remove();
        $.map(qcsamples, function(v, k) {
            var selected = k==presel ? ' selected' : '';
            $('#selqcsample').append('<option value="'+k+'"'+selected+'>'+k+'</option>');
        });
    }

    /**
     * Hide/Shows the reference analyses rows from the table in accordance
     * with the selected analysis and qcsample
     */
    function filterRows() {
        var ankeyword = $('#selanalyses').val().split("(");
        ankeyword = ankeyword[ankeyword.length-1].slice(0,-1).trim();
        var idqc = $('#selqcsample').val();
        var count = 0;
        $('div.results-info').remove();
        $('.item-listing-tbody tr').each(function( index ) {
            if ($(this).attr('keyword') != ankeyword
                || $(this).find('td.Partition a').html() != idqc) {
                $(this).hide();
            } else {
                $(this).fadeIn();
                count+=1;
            }
        });
        $('.bika-listing-table').closest('div').before('<div class="results-info">'+count+' results found</div>');
    }

    /**
     * Draws the control chart in accordance with the selected analysis
     * and qc-sample, as well as the interpolation
     */
    function drawControlChart(width, height) {
        var analysiskey = $('#selanalyses').val();
        var reftype = $('#selqcsample').val();
        var interpolation = $('#interpolation').val()
        //if ($("#chart svg").length > 0) {
            var w = width == null ? $("#chart").innerWidth() : width;
            var h = height == null ? $("#chart").innerHeight() : height;
            $("#chart").css('width', width);
            $("#chart").css('height', height);
       // }
        $("#chart").html("");
        $("#chart").show();
        var data = $.parseJSON($('#graphdata').val());
        data = data[analysiskey]
        if (!(reftype in data) || data[reftype].length == 0) {
            // There is no results for this type of refsample
            $("#chart").hide();
            return;
        }
        data = data[reftype];
        var unit = data[data.length-1]['unit'];
        var upper = data[data.length-1]['upper'];
        var lower = data[data.length-1]['lower'];
        var target = data[data.length-1]['target'];
        var ylabel = "Result";
        if (unit == '' || typeof unit == 'undefined') {
            unit = "";
        } else {
            ylabel = unit;
        }

        var uppertxt = $.trim("UCL (" + upper+""+unit+")");
        var lowertxt = $.trim("LCL (" + lower+""+unit+")");
        var centrtxt = $.trim("CL ("+target+""+unit+")");
        chart = new ControlChart();
        chart.setData(data);
        chart.setInterpolation(interpolation);
        chart.setXColumn('date');
        chart.setYColumn('result');
        chart.setPointId('id');
        chart.setYLabel(ylabel);
        chart.setXLabel('Date');
        chart.setUpperLimitText(uppertxt);
        chart.setLowerLimitText(lowertxt);
        chart.setCenterLimitText(centrtxt);
        chart.setCenterLimit(target);
        chart.setUpperLimit(upper);
        chart.setLowerLimit(lower);
        chart.draw('#chart');
    }
}

/**
 * Controller class for Method's Edit view
 */
function MethodEditView() {
    var that = this;
    that.load = function() {}
}

/**
 * Controller class for Reference Sample Analyses View
 */
function ReferenceSampleAnalysesView() {

    var that = this;

    /**
     * Entry-point method for ReferenceSampleAnalysesView
     */
    that.load = function() {

        // Populate analyses selector
        var data = $.parseJSON($('#graphdata').val());
        var qcrec = false;
        $.map(data, function(value,key){
            $('#selanalyses').append('<option value="'+key+'">'+key+'</option>');
            if (qcrec == false) {
                $.map(value, function(v, k) {
                    $('#selqcsample').val(k);
                });
                qcrec = true;
            }
        });

        // Draw the chart and filter rows
        if ($('#selanalyses').val()) {
            filterRows();
            drawControlChart(null, null);
        }

        $('#selanalyses').change(function(e) {
            drawControlChart(null, null);
            filterRows();
        });

       /* $('#selqcsample').change(function(e) {
            drawControlChart();
            filterRows();
        });*/

        $('#interpolation').change(function(e) {
            drawControlChart(null, null);
        });

        $('.item-listing-tbody tr').mouseover(function(e) {
            if ($(this).attr('uid') != '') {
                $(this).addClass('selected');
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseover');
            }
        });
        $('.item-listing-tbody tr').mouseout(function(e) {
            $(this).removeClass('selected');
            if ($(this).attr('uid') != '') {
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseout');
            }
        });

        $('#printgraph').click(function(e) {
            e.preventDefault();

            $('#selanalyses').find('option[selected]').remove();
            $('#selanalyses').find('option[value="'+$(selanalyses).val()+'"]').prop('selected', true);
            // Scaling for print
            var w = 670;
            var h = $('#chart').attr('height');
            drawControlChart(w, h);

            var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
            var css = '<link href="' + window.portal_url + '/++resource++bika.lims.css/print-graph.css" type="text/css" rel="stylesheet">';
            var h1 = $("span.documentFirstHeading").closest('h1').clone();
            var content = $('#content-core').clone();
            $(content).prepend(h1);
            $(content).find('#selanalyses').after("<span class='bold'>"+$('#selanalyses').val()+"</span>");
            $(content).find('#interpolation').after("<span class='bold'>"+$('#interpolation').val()+"</span>");
            $(content).find('#selanalyses').hide();
            $(content).find('#interpolation').hide();

            WinPrint.document.write("<html><head>"+css+"</head><body>"+$(content).html()+"</body></html>");
            WinPrint.document.close();
            WinPrint.focus();
            WinPrint.print();
            WinPrint.close();

            // Re-scale
            $("#chart").css('width', '100%');
            $("#chart").removeAttr('height');
            drawControlChart(null, null);

        });

        $('div.bika-listing-table-container').fadeIn();
    }

    /**
     * Hide/Shows the reference analyses rows from the table in accordance
     * with the selected analysis and qcsample
     */
    function filterRows() {
        var ankeyword = $('#selanalyses').val().split("(");
        ankeyword = ankeyword[ankeyword.length-1].slice(0,-1).trim();
        var count = 0;
        $('div.results-info').remove();
        $('.item-listing-tbody tr').each(function( index ) {
            if ($(this).attr('keyword') != ankeyword) {
                $(this).hide();
            } else {
                $(this).fadeIn();
                count+=1;
            }
        });
        $('.bika-listing-table').closest('div').before('<div class="results-info">'+count+' results found</div>');
    }

    /**
     * Draws the control chart in accordance with the selected analysis
     * and qc-sample, as well as the interpolation
     */
    function drawControlChart(width, height) {
        var analysiskey = $('#selanalyses').val();
        var reftype = $('#selqcsample').val();
        var interpolation = $('#interpolation').val()
        var w = width == null ? $("#chart").innerWidth() : width;
        var h = height == null ? $("#chart").innerHeight() : height;
        $("#chart").css('width', width);
        $("#chart").css('height', height);
        $("#chart").html("");
        $("#chart").show();
        var data = $.parseJSON($('#graphdata').val());
        data = data[analysiskey]
        if (!(reftype in data) || data[reftype].length == 0) {
            // There is no results for this type of refsample
            $("#chart").hide();
            return;
        }
        data = data[reftype];
        var unit = data[data.length-1]['unit'];
        var upper = data[data.length-1]['upper'];
        var lower = data[data.length-1]['lower'];
        var target = data[data.length-1]['target'];
        var ylabel = "Result";
        if (unit == '' || typeof unit == 'undefined') {
            unit = "";
        } else {
            ylabel = unit;
        }

        var uppertxt = $.trim("UCL (" + upper+""+unit+")");
        var lowertxt = $.trim("LCL (" + lower+""+unit+")");
        var centrtxt = $.trim("CL ("+target+""+unit+")");
        chart = new ControlChart();
        chart.setData(data);
        chart.setInterpolation(interpolation);
        chart.setXColumn('date');
        chart.setYColumn('result');
        chart.setPointId('id');
        chart.setYLabel(ylabel);
        chart.setXLabel('Date');
        chart.setUpperLimitText(uppertxt);
        chart.setLowerLimitText(lowertxt);
        chart.setCenterLimitText(centrtxt);
        chart.setCenterLimit(target);
        chart.setUpperLimit(upper);
        chart.setLowerLimit(lower);
        chart.draw('#chart');
    }
}

/**
 * Controller class for ReflexRule's Edit view
 */
function ReflexRuleEditView() {

    var that = this;

    /**
     * Entry-point method for ReflexRuleView
     */
    that.load = function() {

    };

}

/**
 * Controller class for Rejection process in Analysis Request View View and Sample View View
 */
 function RejectionKickOff() {

     var that = this;
     that.load = function() {
        // If rejection workflow is disabled, hide the state link
        var request_data = {
            catalog_name: "portal_catalog",
            portal_type: "BikaSetup",
            include_fields: [
                "RejectionReasons"]
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.success &&
                data.total_objects > 0) {
                var rejection_reasons = data.objects[0].RejectionReasons;
                var reasons_state;
                if(rejection_reasons.length > 0) {
                    reasons_state = rejection_reasons[0].checkbox;
                }
                if (reasons_state === undefined || reasons_state != 'on'){
                    $('a#workflow-transition-reject').closest('li').hide();
                }
            }
        });
        reject_widget_semioverlay_setup();
    };

     function reject_widget_semioverlay_setup() {
         "use strict";
         /*This function creates a hidden div element to insert the rejection
           widget there while the analysis request state is not rejected yet.
           So we can overlay the widget when the user clicks on the reject button.
         */
         if($('div#archetypes-fieldname-RejectionWidget').length > 0){
             // binding a new click action to state's rejection button
             $("a#workflow-transition-reject").unbind();
             $("a#workflow-transition-reject").bind("click", function(e){
                 // Overlays the rejection widget when the user tryes to reject the ar and
                 // defines all the ovelay functionalities
                 e.preventDefault();
                 //$('#semioverlay').fadeIn(500);
                 $('#semioverlay').show();
                 $('input[id="RejectionReasons.checkbox"]').click().prop('disabled', true);
             });
             // Getting widget's td and label
             var td = $('#archetypes-fieldname-RejectionWidget').parent('td');
             var label = "<div class='semioverlay-head'>"+$(td).prev('td').html().trim()+"</div>";
             // Creating the div element
             $('#content').prepend(
                "<div id='semioverlay' style='display:none'>" +
                " <div class='semioverlay-back'> </div>" +
                " <div class='semioverlay-panel'>" +
                " <div class='semioverlay-content'></div>" +
                " <div class='semioverlay-buttons'>" +
                " <input type='button'" +
                " name='semioverlay.reject' value='reject'/>" +
                " <input type='button' name='semioverlay.cancel'" +
                " value='cancel'/></div></div></div>");
             // Moving the widget there
             $('#archetypes-fieldname-RejectionWidget').detach().prependTo('#semioverlay .semioverlay-content');
             // hidding the widget's td and moving the label
             $(td).hide();
             $(label).detach().insertBefore('.semioverlay-content');
             // binding close actions
             $("div#semioverlay input[name='semioverlay.cancel']").bind('click',
                 function(){
                 $('#semioverlay').hide();
                 // Clear all data fields
                 $('input[id="RejectionReasons.checkbox"]').prop('checked', false).prop('disabled', false);
                 $('input[id="RejectionReasons.checkbox.other"]').prop('checked', false);
                 $('input[id="RejectionReasons.textfield.other"]').val('');
                 var options = $('.rejectionwidget-multiselect').find('option');
                 for (var i=0;options.length>i; i++){
                     $(options[i]).attr('selected',false);
                 }
             });
             // binding reject actions
             $("div#semioverlay input[name='semioverlay.reject']").bind('click',function(){
                 $('div#semioverlay .semioverlay-panel').fadeOut();
                 reject_ar_sample();
             });
         }
     }

     function getRejectionWidgetValues(){
         "use strict";
         // Retuns the rejection reason widget's values in JSON format to
         // be used in jsonapi's update function
         var ch_val=0,multi_val = [],other_ch_val=0,other_val='',option;
         ch_val = $('.rejectionwidget-checkbox').prop('checked');
         if (ch_val){
             ch_val=1;
             var selected_options = $('.rejectionwidget-multiselect').find('option');
             for (var i=0;selected_options.length>i; i++){
                 option = selected_options[i];
                 if (option.selected){
                     multi_val.push($(option).val());
                 }
             }
             other_ch_val = $('.rejectionwidget-checkbox-other').prop('checked');
             if (other_ch_val){
                 other_ch_val = 1;
                 other_val = $('.rejectionwidget-input-other').val();
             }
             else{other_ch_val=0;}
         }else{
            // Just set ch_val '0' if it is false.
            ch_val=0;
         }
         // Gathering all values
         var rej_widget_state = {
             checkbox:ch_val,
             selected:multi_val,
             checkbox_other:other_ch_val,
             other:other_val
         };
         return $.toJSON(rej_widget_state);
     }

     function reject_ar_sample(){
         "use strict";
         // Makes all the steps needed to reject the ar or sample
         var requestdata = {};
         //save the rejection widget's values
         var url = window.location.href
            .replace('/base_view', '')
            .replace('/analyses', '')
            .replace('/manage_results', '')
            .replace('/not_requested', '')
            .replace('/log', '');
         var obj_path = url.replace(window.portal_url, '');
         var redirect_state = $("a#workflow-transition-reject").attr('href');
         // requestdata should has the format  {fieldname=fieldvalue}
         requestdata.obj_path= obj_path;
         //fieldvalue data will be something like:
         // [{'checkbox': u'on', 'textfield-2': u'b', 'textfield-1': u'c', 'textfield-0': u'a'}]
         var fieldvalue = getRejectionWidgetValues();
         requestdata.RejectionReasons = fieldvalue;
         var msg = '';
         $.ajax({
             type: "POST",
             url: window.portal_url+"/@@API/update",
             data: requestdata
         })
         .done(function(data) {
            //trigger reject workflow action
            if (data !== null && data.success === true) {
                bika.lims.SiteView.notificationPanel('Rejecting', "succeed");
                // the behaviour for samples is different
                if($('body').hasClass('portaltype-sample')) {
                    // We need to get the authenticator
                    var autentification = $('input[name="_authenticator"]').val();
                    $.ajax({
                        url: window.location.href + '/doActionForSample?workflow_action=reject&_authenticator=' + autentification,
                        type: 'POST',
                        dataType: "json",
                    })
                    .done(function(data2) {
                        if (data2 !== null && data2.success == "true") {
                            window.location.href = window.location.href;
                        } else {
                            bika.lims.SiteView.notificationPanel('Error while updating object state', "error");
                            var msg = '[bika.lims.analysisrequest.js] Error while updating object state';
                            console.warn(msg);
                            window.bika.lims.error(msg);
                            $('#semioverlay input[name="semioverlay.cancel"]').click();
                        }
                    });
                } else {
                    // Redirecting to the same page using the rejection's url
                    bika.lims.SiteView.notificationPanel('Rejecting', "succeed");
                    window.location.href = redirect_state;
                }
            } else if (data.success === false) {
                bika.lims.SiteView.notificationPanel('Error while rejecting the analysis request. Unsuccesful AJAX call.', 'error');
                msg = '[bika.lims.analysisrequest.js] Error while rejecting the analysis request. Unsuccesful AJAX call.';
                console.warn(msg);
                window.bika.lims.error(msg);
                $('#semioverlay input[name="semioverlay.cancel"]').click();
            } else {
                bika.lims.SiteView.notificationPanel('Error while rejecting the analysis request. No data returned.', 'error');
                msg = '[bika.lims.analysisrequest.js] Error while rejecting the analysis request. No data returned.';
                console.warn(msg);
                window.bika.lims.error(msg);
                $('#semioverlay input[name="semioverlay.cancel"]').click();
            }
         })
         .fail(function(){
             bika.lims.SiteView.notificationPanel('Error while rejection the analysis request. AJAX POST failed.','error');
             var msg = '[bika.lims.analysisrequest.js] Error while rejection the analysis request. AJAX POST failed.';
             console.warn(msg);
             window.bika.lims.error(msg);
             $('#semioverlay input[name="semioverlay.cancel"]').click();
         });
     }
 }


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.reports.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.ReportFolderView = (function() {
    function ReportFolderView() {
      this.on_toggle_change = bind(this.on_toggle_change, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    ReportFolderView.prototype.load = function() {
      console.debug("ReportFolderView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    ReportFolderView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       */
      console.debug("ReportFolderView::bind_eventhandler");
      return $("body").on("click", "a[id$='_selector']", this.on_toggle_change);
    };

    ReportFolderView.prototype.on_toggle_change = function(event) {

      /**
       * Event handler when the toggle anchor is clicked
       */
      var div_id;
      console.debug("°°° ReportFolderView::on_toggle_change °°°");
      event.preventDefault();
      $(".criteria").toggle(false);
      div_id = event.currentTarget.id.split("_selector")[0];
      return $("[id='" + div_id + "']").toggle(true);
    };

    return ReportFolderView;

  })();

}).call(this);


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.site.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.SiteView = (function() {
    function SiteView() {
      this.on_service_info_click = bind(this.on_service_info_click, this);
      this.on_reference_definition_list_change = bind(this.on_reference_definition_list_change, this);
      this.on_numeric_field_keypress = bind(this.on_numeric_field_keypress, this);
      this.on_numeric_field_paste = bind(this.on_numeric_field_paste, this);
      this.on_at_float_field_keyup = bind(this.on_at_float_field_keyup, this);
      this.on_at_integer_field_keyup = bind(this.on_at_integer_field_keyup, this);
      this.notify_in_panel = bind(this.notify_in_panel, this);
      this.notificationPanel = bind(this.notificationPanel, this);
      this.set_cookie = bind(this.set_cookie, this);
      this.setCookie = bind(this.setCookie, this);
      this.read_cookie = bind(this.read_cookie, this);
      this.readCookie = bind(this.readCookie, this);
      this.log = bind(this.log, this);
      this.portal_alert = bind(this.portal_alert, this);
      this.portalAlert = bind(this.portalAlert, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.init_referencedefinition = bind(this.init_referencedefinition, this);
      this.init_datepickers = bind(this.init_datepickers, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    SiteView.prototype.load = function() {
      console.debug("SiteView::load");
      this.init_datepickers();
      this.bind_eventhandler();
      return this.allowed_keys = [8, 9, 13, 35, 36, 37, 39, 46, 44, 60, 62, 45, 69, 101, 61];
    };


    /* INITIALIZERS */

    SiteView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("SiteView::bind_eventhandler");
      $("body").on("change", "#ReferenceDefinition\\:list", this.on_reference_definition_list_change);
      $("body").on("keypress", ".numeric", this.on_numeric_field_keypress);
      $("body").on("paste", ".numeric", this.on_numeric_field_paste);
      $("body").on("keyup", "input[name*='\\:int\'], .ArchetypesIntegerWidget input", this.on_at_integer_field_keyup);
      $("body").on("keyup", "input[name*='\\:float\'], .ArchetypesDecimalWidget input", this.on_at_float_field_keyup);
      $("body").on("click", "a.service_info", this.on_service_info_click);
      return $(document).on({
        ajaxStart: function() {
          $("body").addClass("loading");
        },
        ajaxStop: function() {
          $("body").removeClass("loading");
        },
        ajaxError: function() {
          $("body").removeClass("loading");
        }
      });
    };

    SiteView.prototype.init_datepickers = function() {

      /*
       * Initialize date pickers
       */
      var config, curDate, dateFormat, lang, lang_config, make_datepicker_config, y, yearRange;
      console.debug("SiteView::init_datepickers");
      curDate = new Date();
      y = curDate.getFullYear();
      yearRange = "1900:" + y;
      lang = (typeof i18n !== "undefined" && i18n !== null ? i18n.currentLanguage : void 0) || "en";
      lang_config = $.datepicker.regional[lang] || $.datepicker.regional[""];
      dateFormat = _t("date_format_short_datepicker");
      if (dateFormat === "date_format_short_datepicker") {
        dateFormat = "yy-mm-dd";
      }
      config = Object.assign(lang_config, {
        dateFormat: dateFormat,
        timeFormat: "HH:mm",
        showOn: "focus",
        showAnim: "fadeIn",
        changeMonth: true,
        changeYear: true,
        showWeek: true,
        yearRange: yearRange,
        numberOfMonths: 1
      });
      make_datepicker_config = function(options) {
        var default_config;
        if (options === void 0) {
          options = {};
        }
        default_config = Object.assign({}, config);
        return Object.assign(default_config, options);
      };
      $("input.datepicker_nofuture").datepicker(make_datepicker_config({
        maxDate: curDate
      }));
      $("input.datepicker").datepicker(make_datepicker_config());
      $("input.datepicker_2months").datepicker(make_datepicker_config({
        maxDate: curDate,
        numberOfMonths: 2
      }));
      return $("input.datetimepicker_nofuture").datetimepicker(make_datepicker_config({
        maxDate: curDate
      }));
    };

    SiteView.prototype.init_referencedefinition = function() {

      /*
       * Initialize reference definition selection
       * XXX: When is this used?
       */
      console.debug("SiteView::init_referencedefinition");
      if ($('#ReferenceDefinition:list').val() !== '') {
        console.warn("SiteView::init_referencedefinition: Refactor this method!");
        return $('#ReferenceDefinition:list').change();
      }
    };


    /* METHODS */

    SiteView.prototype.get_portal_url = function() {

      /*
       * Return the portal url
       */
      return window.portal_url;
    };

    SiteView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      console.warn("SiteView::get_authenticator: Please use site.authenticator instead");
      return window.site.authenticator();
    };

    SiteView.prototype.portalAlert = function(html) {

      /*
       * BBB: Use portal_alert
       */
      console.warn("SiteView::portalAlert: Please use portal_alert method instead.");
      return this.portal_alert(html);
    };

    SiteView.prototype.portal_alert = function(html) {

      /*
       * Display a portal alert box
       */
      var alerts;
      console.debug("SiteView::portal_alert");
      alerts = $('#portal-alert');
      if (alerts.length === 0) {
        $('#portal-header').append("<div id='portal-alert' style='display:none'><div class='portal-alert-item'>" + html + "</div></div>");
      } else {
        alerts.append("<div class='portal-alert-item'>" + html + "</div>");
      }
      alerts.fadeIn();
    };

    SiteView.prototype.log = function(message) {

      /*
       * Log message via bika.lims.log
       */
      console.debug("SiteView::log: message=" + message);
      return window.bika.lims.log(message);
    };

    SiteView.prototype.readCookie = function(cname) {

      /*
       * BBB: Use read_cookie
       */
      console.warn("SiteView::readCookie: Please use site.read_cookie instead");
      return window.site.read_cookie(cname);
    };

    SiteView.prototype.read_cookie = function(cname) {

      /*
       * Read cookie value
       */
      console.warn("SiteView::read_cookie. Please use site.read_cookie instead");
      return window.site.read_cookie(cname);
    };

    SiteView.prototype.setCookie = function(cname, cvalue) {

      /*
       * BBB: Use set_cookie
       */
      console.warn("SiteView::setCookie. Please use site.set_cookie instead");
      return window.site.set_cookie(cname, cvalue);
    };

    SiteView.prototype.set_cookie = function(cname, cvalue) {

      /*
       * Read cookie value
       */
      console.warn("SiteView::set_cookie. Please use site.set_cookie instead");
      window.site.set_cookie(cname, cvalue);
    };

    SiteView.prototype.notificationPanel = function(data, mode) {

      /*
       * BBB: Use notify_in_panel
       */
      console.warn("SiteView::notificationPanel: Please use notfiy_in_panel method instead.");
      return this.notify_in_panel(data, mode);
    };

    SiteView.prototype.notify_in_panel = function(data, mode) {

      /*
       * Render an alert inside the content panel, e.g.in autosave of ARView
       */
      var html;
      console.debug("SiteView::notify_in_panel:data=" + data + ", mode=" + mode);
      $('#panel-notification').remove();
      html = "<div id='panel-notification' style='display:none'><div class='" + mode + "-notification-item'>" + data + "</div></div>";
      $('div#viewlet-above-content-title').append(html);
      $('#panel-notification').fadeIn('slow', 'linear', function() {
        setTimeout((function() {
          $('#panel-notification').fadeOut('slow', 'linear');
        }), 3000);
      });
    };


    /* EVENT HANDLER */

    SiteView.prototype.on_at_integer_field_keyup = function(event) {

      /*
       * Eventhandler for AT integer fields
       */
      var $el, el;
      console.debug("°°° SiteView::on_at_integer_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/\D/g.test($el.val())) {
        $el.val($el.val().replace(/\D/g, ''));
      }
    };

    SiteView.prototype.on_at_float_field_keyup = function(event) {

      /*
       * Eventhandler for AT float fields
       */
      var $el, el;
      console.debug("°°° SiteView::on_at_float_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/[^-.\d]/g.test($el.val())) {
        $el.val($el.val().replace(/[^.\d]/g, ''));
      }
    };

    SiteView.prototype.on_numeric_field_paste = function(event) {

      /*
       * Eventhandler when the user pasted a value inside a numeric field.
       */
      var $el, el;
      console.debug("°°° SiteView::on_numeric_field_paste °°°");
      el = event.currentTarget;
      $el = $(el);
      window.setTimeout((function() {
        $el.val($el.val().replace(',', '.'));
      }), 0);
    };

    SiteView.prototype.on_numeric_field_keypress = function(event) {

      /*
       * Eventhandler when the user pressed a key inside a numeric field.
       */
      var $el, el, isAllowedKey, key;
      console.debug("°°° SiteView::on_numeric_field_keypress °°°");
      el = event.currentTarget;
      $el = $(el);
      key = event.which;
      isAllowedKey = this.allowed_keys.join(',').match(new RegExp(key));
      if (!key || 48 <= key && key <= 57 || isAllowedKey) {
        window.setTimeout((function() {
          $el.val($el.val().replace(',', '.'));
        }), 0);
        return;
      } else {
        event.preventDefault();
      }
    };

    SiteView.prototype.on_reference_definition_list_change = function(event) {

      /*
       * Eventhandler when the user clicked on the reference defintion dropdown.
       *
       * 1. Add a ReferenceDefintion at /bika_setup/bika_referencedefinitions
       * 2. Add a Supplier in /bika_setup/bika_suppliers
       * 3. Add a ReferenceSample in /bika_setup/bika_suppliers/supplier-1/portal_factory/ReferenceSample
       *
       * The dropdown with the id="ReferenceDefinition:list" is rendered there.
       */
      var $el, authenticator, el, option, uid;
      console.debug("°°° SiteView::on_reference_definition_list_change °°°");
      el = event.currentTarget;
      $el = $(el);
      authenticator = this.get_authenticator();
      uid = $el.val();
      option = $el.children(':selected').html();
      if (uid === '') {
        $('#Blank').prop('checked', false);
        $('#Hazardous').prop('checked', false);
        $('.bika-listing-table').load('referenceresults', {
          '_authenticator': authenticator
        });
        return;
      }
      if (option.search(_t('(Blank)')) > -1 || option.search("(Blank)") > -1) {
        $('#Blank').prop('checked', true);
      } else {
        $('#Blank').prop('checked', false);
      }
      if (option.search(_t('(Hazardous)')) > -1 || option.search("(Hazardous)") > -1) {
        $('#Hazardous').prop('checked', true);
      } else {
        $('#Hazardous').prop('checked', false);
      }
      $('.bika-listing-table').load('referenceresults', {
        '_authenticator': authenticator,
        'uid': uid
      });
    };

    SiteView.prototype.on_service_info_click = function(event) {

      /*
       * Eventhandler when the service info icon was clicked
       */
      var el;
      console.debug("°°° SiteView::on_service_info_click °°°");
      event.preventDefault();
      el = event.currentTarget;
      $(el).prepOverlay({
        subtype: "ajax",
        width: '80%',
        filter: '#content>*:not(div#portal-column-content)',
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function(event) {
            var overlay;
            overlay = this.getOverlay();
            return overlay.draggable();
          },
          onLoad: function(event) {
            event = new Event("DOMContentLoaded", {});
            return window.document.dispatchEvent(event);
          }
        }
      });
      return $(el).click();
    };

    return SiteView;

  })();

}).call(this);


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.utils.attachments.coffee
 */


/**
 * Controller class for calculation events
 */

(function() {
  window.AttachmentsUtils = function() {
    var that;
    that = this;
    that.load = function() {
      $('#AttachFile,#Service,#Analysis').change(function(event) {
        var analysis, attachfile, service;
        attachfile = $('#AttachFile').val();
        if (attachfile === void 0) {
          attachfile = '';
        }
        service = $('#Service').val();
        if (service === void 0) {
          service = '';
        }
        analysis = $('#Analysis').val();
        if (analysis === void 0) {
          analysis = '';
        }
        if (this.id === 'Service') {
          $('#Analysis').val('');
        }
        if (this.id === 'Analysis') {
          $('#Service').val('');
        }
        if (attachfile !== '' && (service !== '' || analysis !== '')) {
          $('#addButton').removeAttr('disabled');
        } else {
          $('#addButton').prop('disabled', true);
        }
      });
      $('#Analysis').combogrid({
        colModel: [
          {
            'columnName': 'analysis_uid',
            'hidden': true
          }, {
            'columnName': 'slot',
            'width': '10',
            'label': _t('Slot')
          }, {
            'columnName': 'service',
            'width': '35',
            'label': _t('Service')
          }, {
            'columnName': 'parent',
            'width': '35',
            'label': _t('Parent')
          }, {
            'columnName': 'type',
            'width': '20',
            'label': _t('Type')
          }
        ],
        url: window.location.href.replace('/manage_results', '') + '/attachAnalyses?_authenticator=' + $('input[name="_authenticator"]').val(),
        showOn: true,
        width: '650px',
        select: function(event, ui) {
          $('#Analysis').val(ui.item.service + (" (slot " + ui.item.slot + ")"));
          $('#analysis_uid').val(ui.item.analysis_uid);
          $(this).change();
          return false;
        }
      });
    };
  };

}).call(this);

/**
 * Controller class for barcode utils
 */
function BarcodeUtils() {

    var that = this;

    that.load = function() {

        $('.qrcode').each(function(i) {
           var code = $(this).attr('data-code');
           var size = $(this).attr('data-size');
           $(this).qrcode({
                "render": "image",
                "size": size, // 37.79 pixel == 10mm
                "color": "#3a3",
                "text": code
            });
        });


        $('.barcode').each(function() {
            var id = $(this).attr('data-id');
            var code = $(this).attr('data-code');
            var barHeight = $(this).attr('data-barHeight');
            var addQuietZone = $(this).attr('data-addQuietZone');
            var showHRI = $(this).attr('data-showHRI');
            $(this).barcode(id, code,
                            {'barHeight': parseInt(barHeight),
                             'addQuietZone': (addQuietZone == 'true'),
                             'showHRI': (showHRI == 'true'),
                             'output': "bmp", });

            if (showHRI == 'true') {
                // When output is set to "bmp", the showHRI parameter (that
                // prints the ID below the barcode) is dissmissed by barcode.js
                // so we need to add it manually
                $(this).find('.barcode-hri').remove();
                var barcode_hri = '<div class="barcode-hri">'+id+'</div>';
                $(this).append(barcode_hri);
            }
        });
    }
}

// This function will redirect based on a barcode sequence.
//
// The string is sent to python, who will return a URL, which
// we will use to set the window location.
//
// A barcode may begin and end with '*' but we can't make this
// assumption about all scanners; so, we will function with a
// 500ms timeout instead.

$(document).ready(function(){

    function barcode_listener() {

        var that = this;

        that.load = function() {

            // if collection gets something worth submitting,
            // it's sent to utils.barcode_entry here.
            function redirect(code){
                authenticator = $('input[name="_authenticator"]').val();
                $.ajax({
                    type: 'POST',
                    url: 'barcode_entry',
                    data: {
                        'entry':code,
                        '_authenticator': authenticator},
                    success: function(responseText, statusText, xhr, $form) {
                        if (responseText.success) {
                            window.location.href = responseText.url;
                        }
                    }
                });
            }

            var collecting = false;
            var code = ""

            $(window).keypress(function(event) {
                // We do not want keypresses that were sent to input or textarea
                if(event.target.tagName == "BODY"){
                    if (collecting) {
                        code = code + String.fromCharCode(event.which);
                    } else {
                        collecting = true;
                        code = String.fromCharCode(event.which);
                        setTimeout(function(){
                            collecting = false;
                            if (code.length > 2){
                                redirect(code);
                            }
                        }, 500)
                    }
                }
            });
        }
    }

    // immediately load the barcode_listener so that barcode entries are detected
    // in all windows (when there is no input element selected).
    window.bika = window.bika || { lims: {} };
    window.bika.lims['barcode_listener'] = new barcode_listener();
    window.bika.lims['barcode_listener'].load();

});


/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.worksheet.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.WorksheetFolderView = (function() {
    function WorksheetFolderView() {
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_template_change = bind(this.on_template_change, this);
      this.select_instrument = bind(this.select_instrument, this);
      this.get_template_instrument = bind(this.get_template_instrument, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
    * Controller class for Worksheets Folder
     */

    WorksheetFolderView.prototype.load = function() {
      console.debug("WorksheetFolderView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    WorksheetFolderView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetFolderView::bind_eventhandler");
      $("body").on("change", "select.template", this.on_template_change);
      return $("body").on("change", "select.instrument", this.on_instrument_change);
    };


    /* METHODS */

    WorksheetFolderView.prototype.get_template_instrument = function() {

      /*
       * TODO: Refactor to get the data directly from the server
       * Returns the JSON parsed value of the HTML element with the class
         `templateinstruments`
       */
      var input, value;
      console.debug("WorksheetFolderView::get_template_instruments");
      input = $("input.templateinstruments");
      value = input.val();
      return JSON.parse(value);
    };

    WorksheetFolderView.prototype.select_instrument = function(instrument_uid) {

      /*
       * Select instrument by UID
       */
      var option, select;
      select = $(".instrument");
      option = select.find("option[value='" + instrument_uid + "']");
      if (option) {
        return option.prop("selected", true);
      }
    };


    /* EVENT HANDLER */

    WorksheetFolderView.prototype.on_template_change = function(event) {

      /*
       * Eventhandler for template change
       */
      var $el, instrument_uid, template_instrument, template_uid;
      console.debug("°°° WorksheetFolderView::on_template_change °°°");
      $el = $(event.currentTarget);
      template_uid = $el.val();
      template_instrument = this.get_template_instrument();
      instrument_uid = template_instrument[template_uid];
      return this.select_instrument(instrument_uid);
    };

    WorksheetFolderView.prototype.on_instrument_change = function(event) {

      /*
       * Eventhandler for instrument change
       */
      var $el, instrument_uid, message;
      console.debug("°°° WorksheetFolderView::on_instrument_change °°°");
      $el = $(event.currentTarget);
      instrument_uid = $el.val();
      if (instrument_uid) {
        message = _t("Only the analyses for which the selected instrument is allowed will be added automatically.");
        return bika.lims.SiteView.notify_in_panel(message, "error");
      }
    };

    return WorksheetFolderView;

  })();

  window.WorksheetAddQCAnalysesView = (function() {
    function WorksheetAddQCAnalysesView() {
      this.on_referencesample_row_click = bind(this.on_referencesample_row_click, this);
      this.on_service_click = bind(this.on_service_click, this);
      this.load_controls = bind(this.load_controls, this);
      this.get_postion = bind(this.get_postion, this);
      this.get_control_type = bind(this.get_control_type, this);
      this.get_selected_services = bind(this.get_selected_services, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's add blank/control views
     */

    WorksheetAddQCAnalysesView.prototype.load = function() {
      console.debug("WorksheetAddQCAnalysesView::load");
      this.bind_eventhandler();
      return this.load_controls();
    };


    /* INITIALIZERS */

    WorksheetAddQCAnalysesView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddQCAnalysesView::bind_eventhandler");
      $("body").on("click", "#worksheet_services input[id*='_cb_']", this.on_service_click);
      return $("body").on("click", "#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr", this.on_referencesample_row_click);
    };


    /* METHODS */

    WorksheetAddQCAnalysesView.prototype.ajax_submit = function(options) {
      var done;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_base_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = (function(_this) {
        return function() {
          return $(_this).trigger("ajax:submit:end");
        };
      })(this);
      return $.ajax(options).done(done);
    };

    WorksheetAddQCAnalysesView.prototype.get_base_url = function() {

      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    };

    WorksheetAddQCAnalysesView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetAddQCAnalysesView.prototype.get_selected_services = function() {

      /*
       * Returns a list of selected service uids
       */
      var $table, services;
      $table = $("table.bika-listing-table");
      services = [];
      $("input:checked", $table).each(function(index, element) {
        return services.push(element.value);
      });
      return services;
    };

    WorksheetAddQCAnalysesView.prototype.get_control_type = function() {

      /*
       * Returns the control type
       */
      var control_type;
      control_type = "b";
      if (window.location.href.search("add_control") > -1) {
        control_type = "c";
      }
      return control_type;
    };

    WorksheetAddQCAnalysesView.prototype.get_postion = function() {

      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    };

    WorksheetAddQCAnalysesView.prototype.load_controls = function() {

      /*
       * Load the controls
       */
      var base_url, element, url;
      base_url = this.get_base_url();
      base_url = base_url.replace("/add_blank", "").replace("/add_control", "");
      url = base_url + "/getWorksheetReferences";
      element = $("#worksheet_add_references");
      if (element.length === 0) {
        console.warn("Element with id='#worksheet_add_references' missing!");
        return;
      }
      return this.ajax_submit({
        url: url,
        data: {
          service_uids: this.get_selected_services().join(","),
          control_type: this.get_control_type(),
          _authenticator: this.get_authenticator()
        }
      }).done(function(data) {
        return element.html(data);
      });
    };


    /* EVENT HANDLER */

    WorksheetAddQCAnalysesView.prototype.on_service_click = function(event) {

      /*
       * Eventhandler when a service checkbox was clicked
       */
      console.debug("°°° WorksheetAddQCAnalysesView::on_category_change °°°");
      return this.load_controls();
    };

    WorksheetAddQCAnalysesView.prototype.on_referencesample_row_click = function(event) {

      /*
       * Eventhandler for a click on the loaded referencesample listing
       *
       * A reference sample for the service need to be added via
       * Setup -> Supplier -> Referene Samples
       */
      var $el, $form, action, control_type, selected_services, uid;
      console.debug("°°° WorksheetAddQCAnalysesView::on_referencesample_row_click °°°");
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      $form = $el.parents("form");
      control_type = this.get_control_type();
      action = "add_blank";
      if (control_type === "c") {
        action = "add_control";
      }
      $form.attr("action", action);
      selected_services = this.get_selected_services().join(",");
      $form.append("<input type='hidden' value='" + selected_services + "' name='selected_service_uids'/>");
      $form.append("<input type='hidden' value='" + uid + "' name='reference_uid'/>");
      $form.append("<input type='hidden' value='" + (this.get_postion()) + "' name='position'/>");
      return $form.submit();
    };

    return WorksheetAddQCAnalysesView;

  })();

  window.WorksheetAddDuplicateAnalysesView = (function() {
    function WorksheetAddDuplicateAnalysesView() {
      this.on_duplicate_row_click = bind(this.on_duplicate_row_click, this);
      this.get_postion = bind(this.get_postion, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's add blank/control views
     */

    WorksheetAddDuplicateAnalysesView.prototype.load = function() {
      console.debug("WorksheetAddDuplicateAnalysesView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    WorksheetAddDuplicateAnalysesView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddDuplicateAnalysesView::bind_eventhandler");
      return $("body").on("click", "#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr", this.on_duplicate_row_click);
    };


    /* METHODS */

    WorksheetAddDuplicateAnalysesView.prototype.get_postion = function() {

      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    };


    /* EVENT HANDLER */

    WorksheetAddDuplicateAnalysesView.prototype.on_duplicate_row_click = function(event) {

      /*
       * Eventhandler for a click on a row of the loaded dduplicate listing
       */
      var $el, $form, uid;
      console.debug("°°° WorksheetAddDuplicateAnalysesView::on_duplicate_row_click °°°");
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      $form = $el.parents("form");
      $form.attr("action", "add_duplicate");
      $form.append("<input type='hidden' value='" + uid + "' name='ar_uid'/>");
      $form.append("<input type='hidden' value='" + (this.get_postion()) + "' name='position'/>");
      return $form.submit();
    };

    return WorksheetAddDuplicateAnalysesView;

  })();

  window.WorksheetManageResultsView = (function() {
    function WorksheetManageResultsView() {
      this.on_wideinterims_apply_click = bind(this.on_wideinterims_apply_click, this);
      this.on_slot_remarks_click = bind(this.on_slot_remarks_click, this);
      this.on_wideiterims_interims_change = bind(this.on_wideiterims_interims_change, this);
      this.on_wideiterims_analyses_change = bind(this.on_wideiterims_analyses_change, this);
      this.on_remarks_balloon_clicked = bind(this.on_remarks_balloon_clicked, this);
      this.on_analysis_instrument_change = bind(this.on_analysis_instrument_change, this);
      this.on_analysis_instrument_focus = bind(this.on_analysis_instrument_focus, this);
      this.on_method_change = bind(this.on_method_change, this);
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_layout_change = bind(this.on_layout_change, this);
      this.on_analyst_change = bind(this.on_analyst_change, this);
      this.on_constraints_loaded = bind(this.on_constraints_loaded, this);
      this.load_analysis_method_constraint = bind(this.load_analysis_method_constraint, this);
      this.is_instrument_allowed = bind(this.is_instrument_allowed, this);
      this.get_method_by_analysis_uid = bind(this.get_method_by_analysis_uid, this);
      this.get_analysis_uids = bind(this.get_analysis_uids, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.init_instruments_and_methods = bind(this.init_instruments_and_methods, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's manage results view
     */

    WorksheetManageResultsView.prototype.load = function() {
      console.debug("WorksheetManageResultsView::load");
      this._ = i18n.MessageFactory("senaite.core");
      this._pmf = i18n.MessageFactory('plone');
      this.bind_eventhandler();
      this.constraints = null;
      this.init_instruments_and_methods();
      return window.ws = this;
    };


    /* INITIALIZERS */

    WorksheetManageResultsView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetManageResultsView::bind_eventhandler");
      $("body").on("change", ".manage_results_header .analyst", this.on_analyst_change);
      $("body").on("change", "#resultslayout_form #resultslayout", this.on_layout_change);
      $("body").on("change", ".manage_results_header .instrument", this.on_instrument_change);
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Method']", this.on_method_change);
      $("body").on("focus", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_focus);
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_change);
      $("body").on("click", "a.add-remark", this.on_remarks_balloon_clicked);
      $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
      $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
      $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
      $("body").on("click", "img.slot-remarks", this.on_slot_remarks_click);

      /* internal events */
      return $(this).on("constraints:loaded", this.on_constraints_loaded);
    };

    WorksheetManageResultsView.prototype.init_instruments_and_methods = function() {

      /*
       * Applies the rules and constraints to each analysis displayed in the
       * manage results view regarding to methods, instruments and results.
       *
       * For example, this service is responsible for disabling the results field
       * if the analysis has no valid instrument available for the selected method,
       * if the service don't allow manual entry of results.
       *
       * Another example is that this service is responsible of populating the
       * list of instruments avialable for an analysis service when the user
       * changes the method to be used.
       *
       * See docs/imm_results_entry_behavior.png for detailed information.
       */
      var analysis_uids;
      analysis_uids = this.get_analysis_uids();
      return this.ajax_submit({
        url: (this.get_portal_url()) + "/get_method_instrument_constraints",
        data: {
          _authenticator: this.get_authenticator,
          uids: JSON.stringify(analysis_uids)
        },
        dataType: "json"
      }).done(function(data) {
        this.constraints = data;
        return $(this).trigger("constraints:loaded", data);
      });
    };


    /* METHODS */

    WorksheetManageResultsView.prototype.ajax_submit = function(options) {
      var done;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_base_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = (function(_this) {
        return function() {
          return $(_this).trigger("ajax:submit:end");
        };
      })(this);
      return $.ajax(options).done(done);
    };

    WorksheetManageResultsView.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url || window.portal_url;
    };

    WorksheetManageResultsView.prototype.get_base_url = function() {

      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    };

    WorksheetManageResultsView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetManageResultsView.prototype.get_analysis_uids = function() {

      /*
       * Returns a list of analysis UIDs
       */
      var analysis_uids, data, value;
      analysis_uids = [];
      value = $("#item_data").val();
      if (!value) {
        return [];
      }
      data = JSON.parse(value);
      $.each(data, function(uid, value) {
        return analysis_uids.push(uid);
      });
      return analysis_uids;
    };

    WorksheetManageResultsView.prototype.get_method_by_analysis_uid = function(analysis_uid) {

      /*
       * Return the method UID of the analysis identified by analysis_uid
       */
      var $method_field, method_uid;
      $method_field = $("select.listing_select_entry[field='Method'][uid='" + analysis_uid + "']");
      method_uid = $method_field.val();
      return method_uid || "";
    };

    WorksheetManageResultsView.prototype.is_instrument_allowed = function(instrument_uid) {

      /*
       * Check if the Instrument is allowed to appear in Instrument list of Analysis.
       *
       * Returns true if multiple use of an Instrument is enabled for assigned
       * Worksheet Template or UID is not in selected Instruments
       *
       * @param {uid} instrument_uid - UID of Instrument.
       */
      var allowed, i_selectors, multiple_enabled;
      allowed = true;
      multiple_enabled = $("#instrument_multiple_use").attr("value");
      if (multiple_enabled !== "True") {
        i_selectors = $("select.listing_select_entry[field='Instrument']");
        $.each(i_selectors, function(index, element) {
          if (element.value === instrument_uid) {
            return allowed = false;
          }
        });
      }
      return allowed;
    };

    WorksheetManageResultsView.prototype.load_analysis_method_constraint = function(analysis_uid, method_uid) {

      /*
       * Applies the constraints and rules to the specified analysis regarding to
       * the method specified.
       *
       * If method is null, the function assumes the rules must apply for the
       * currently selected method.
       *
       * The function uses the variable mi_constraints to find out which is the
       * rule to be applied to the analysis and method specified.
       *
       * See init_instruments_and_methods() function for further information
       * about the constraints and rules retrieval and assignment.
       *
       * @param {string} analysis_uid: Analysis UID
       * @param {string} method_uid: Method UID
       *
       * If `method_uid` is null, uses the method that is currently selected for
       * the specified analysis
       */
      var analysis_constraints, i_selector, ins_old_val, m_selector, me, method_constraints, method_name;
      console.debug("WorksheetManageResultsView::load_analysis_method_constraint:analysis_uid=" + analysis_uid + " method_uid=" + method_uid);
      me = this;
      if (!method_uid) {
        method_uid = this.get_method_by_analysis_uid(analysis_uid);
      }
      analysis_constraints = this.constraints[analysis_uid];
      if (!analysis_constraints) {
        return;
      }
      method_constraints = analysis_constraints[method_uid];
      if (!method_constraints) {
        return;
      }
      if (method_constraints.length < 7) {
        return;
      }
      m_selector = $("select.listing_select_entry[field='Method'][uid='" + analysis_uid + "']");
      i_selector = $("select.listing_select_entry[field='Instrument'][uid='" + analysis_uid + "']");
      $(m_selector).find('option[value=""]').remove();
      if (method_constraints[1] === 1) {
        $(m_selector).prepend("<option value=''>" + (_('Not defined')) + "</option>");
      }
      $(m_selector).val(method_uid);
      $(m_selector).prop("disabled", false);
      $(".method-label[uid='" + analysis_uid + "']").remove();
      if (method_constraints[0] === 0) {
        $(m_selector).hide();
      } else if (method_constraints[0] === 1) {
        $(m_selector).show();
      } else if (method_constraints[0] === 2) {
        if (analysis_constraints.length > 1) {
          $(m_selector).hide();
          method_name = $(m_selector).find("option[value='" + method_uid + "']").innerHtml();
          $(m_selector).after("<span class='method-label' uid='" + analysis_uid + "' href='#'>" + method_name + "</span>");
        }
      } else if (method_constraints[0] === 3) {
        $(m_selector).show();
      }
      ins_old_val = $(i_selector).val();
      if (ins_old_val && ins_old_val !== '') {
        $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + ins_old_val + "'] option[value='" + ins_old_val + "']").prop("disabled", false);
      }
      $(i_selector).find("option").remove();
      if (method_constraints[7]) {
        $.each(method_constraints[7], function(key, value) {
          if (me.is_instrument_allowed(key)) {
            return $(i_selector).append("<option value='" + key + "'>" + value + "</option>");
          } else {
            return $(i_selector).append("<option value='" + key + "' disabled='disabled'>" + value + "</option>");
          }
        });
      }
      if (method_constraints[3] === 1) {
        $(i_selector).prepend("<option selected='selected' value=''>" + (_('None')) + "</option>");
      }
      if (me.is_instrument_allowed(method_constraints[4])) {
        $(i_selector).val(method_constraints[4]);
        $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + method_constraints[4] + "'] option[value='" + method_constraints[4] + "']").prop("disabled", true);
      }
      if (method_constraints[2] === 0) {
        $(i_selector).hide();
      } else if (method_constraints[2] === 1) {
        $(i_selector).show();
      }
      if (method_constraints[5] === 0) {
        $(".interim input[uid='" + analysis_uid + "']").val("");
        $("input[field='Result'][uid='" + analysis_uid + "']").val("");
        $(".interim input[uid='" + analysis_uid + "']").prop("disabled", true);
        $("input[field='Result'][uid='" + analysis_uid + "']").prop("disabled", true);
      } else if (method_constraints[5] === 1) {
        $(".interim input[uid='" + analysis_uid + "']").prop("disabled", false);
        $("input[field='Result'][uid='" + analysis_uid + "']").prop("disabled", false);
      }
      $(".alert-instruments-invalid[uid='" + analysis_uid + "']").remove();
      if (method_constraints[6] && method_constraints[6] !== "") {
        $(i_selector).after("<img uid='" + analysis_uid + "' class='alert-instruments-invalid' src='" + (this.get_portal_url()) + "/++resource++bika.lims.images/warning.png' title='" + method_constraints[6] + "'>");
      }
      return $(".amconstr[uid='" + analysis_uid + "']").remove();
    };


    /* EVENT HANDLER */

    WorksheetManageResultsView.prototype.on_constraints_loaded = function(event) {

      /*
       * Eventhandler when the instrument and method constraints were loaded from the server
       */
      var me;
      console.debug("°°° WorksheetManageResultsView::on_constraints_loaded °°°");
      me = this;
      return $.each(this.get_analysis_uids(), function(index, uid) {
        return me.load_analysis_method_constraint(uid, null);
      });
    };

    WorksheetManageResultsView.prototype.on_analyst_change = function(event) {

      /*
       * Eventhandler when the analyst select changed
       */
      var $el, analyst, base_url, url;
      console.debug("°°° WorksheetManageResultsView::on_analyst_change °°°");
      $el = $(event.currentTarget);
      analyst = $el.val();
      if (analyst === "") {
        return false;
      }
      base_url = this.get_base_url();
      url = base_url.replace("/manage_results", "") + "/set_analyst";
      return this.ajax_submit({
        url: url,
        data: {
          value: analyst,
          _authenticator: this.get_authenticator()
        },
        dataType: "json"
      }).done(function(data) {
        return bika.lims.SiteView.notify_in_panel(this._pmf("Changes saved."), "succeed");
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(this._t("Could not set the selected analyst"), "error");
      });
    };

    WorksheetManageResultsView.prototype.on_layout_change = function(event) {

      /*
       * Eventhandler when the analyst changed
       */
      var $el;
      console.debug("°°° WorksheetManageResultsView::on_layout_change °°°");
      return $el = $(event.currentTarget);
    };

    WorksheetManageResultsView.prototype.on_instrument_change = function(event) {

      /*
       * Eventhandler when the instrument changed
       */
      var $el, base_url, instrument_uid, url;
      console.debug("°°° WorksheetManageResultsView::on_instrument_change °°°");
      $el = $(event.currentTarget);
      instrument_uid = $el.val();
      if (instrument_uid === "") {
        return false;
      }
      base_url = this.get_base_url();
      url = base_url.replace("/manage_results", "") + "/set_instrument";
      return this.ajax_submit({
        url: url,
        data: {
          value: instrument_uid,
          _authenticator: this.get_authenticator()
        },
        dataType: "json"
      }).done(function(data) {
        bika.lims.SiteView.notify_in_panel(this._pmf("Changes saved."), "succeed");
        $("select.listing_select_entry[field='Instrument'] option[value='" + instrument_uid + "']").parent().find("option[value='" + instrument_uid + "']").prop("selected", false);
        return $("select.listing_select_entry[field='Instrument'] option[value='" + instrument_uid + "']").prop("selected", true);
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(this._t("Unable to apply the selected instrument"), "error");
      });
    };

    WorksheetManageResultsView.prototype.on_method_change = function(event) {

      /*
       * Eventhandler when the method changed
       *
       */
      var $el, analysis_uid, method_uid;
      console.debug("°°° WorksheetManageResultsView::on_method_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      method_uid = $el.val();
      return this.load_analysis_method_constraint(analysis_uid, method_uid);
    };

    WorksheetManageResultsView.prototype.on_analysis_instrument_focus = function(event) {

      /*
       * Eventhandler when the instrument of an analysis is focused
       *
       * Only needed to remember the last value
       */
      var $el;
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_focus °°°");
      $el = $(event.currentTarget);
      this.previous_instrument = $el.val();
      return console.info(this.previous_instrument);
    };

    WorksheetManageResultsView.prototype.on_analysis_instrument_change = function(event) {

      /*
       * Eventhandler when the instrument of an analysis changed
       *
       * If a new instrument is chosen for the analysis, disable this Instrument
       * for the other analyses. Also, remove the restriction of previous
       * Instrument of this analysis to be chosen in the other analyses.
       */
      var $el, analysis_uid, instrument_uid;
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      instrument_uid = $el.val();
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + instrument_uid + "'] option[value='" + instrument_uid + "']").prop("disabled", true);
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='" + this.previous_instrument + "']").prop("disabled", false);
      return $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='']").prop("disabled", false);
    };

    WorksheetManageResultsView.prototype.on_remarks_balloon_clicked = function(event) {

      /*
       * Eventhandler when the remarks balloon was clicked
       */
      var $el, remarks;
      console.debug("°°° WorksheetManageResultsView::on_remarks_balloon_clicked °°°");
      $el = $(event.currentTarget);
      event.preventDefault();
      remarks = $el.closest("tr").next("tr").find("td.remarks");
      return $(remarks).find("div.remarks-placeholder").toggle();
    };

    WorksheetManageResultsView.prototype.on_wideiterims_analyses_change = function(event) {

      /*
       * Eventhandler when the wide interims analysis selector changed
       *
       * Search all interim fields which begin with the selected category and fill
       *  the analyses interim fields to the selection
       */
      var $el, category;
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_analyses_change °°°");
      $el = $(event.currentTarget);
      $("#wideinterims_interims").html("");
      category = $el.val();
      return $("input[id^='wideinterim_" + category + "']").each(function(index, element) {
        var itemval, keyword, name;
        name = $(element).attr("name");
        keyword = $(element).attr("keyword");
        itemval = "<option value='" + keyword + "'>" + name + "</option>";
        return $("#wideinterims_interims").append(itemval);
      });
    };

    WorksheetManageResultsView.prototype.on_wideiterims_interims_change = function(event) {

      /*
       * Eventhandler when the wide interims selector changed
       */
      var $el, analysis, idinter, interim;
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_interims_change °°°");
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $el.val();
      idinter = "#wideinterim_" + analysis + "_" + interim;
      return $("#wideinterims_value").val($(idinter).val());
    };

    WorksheetManageResultsView.prototype.on_slot_remarks_click = function(event) {

      /*
       * Eventhandler when the remarks icon was clicked
       */
      var el;
      console.debug("°°° WorksheetManageResultsView::on_slot_remarks_click °°°");
      el = event.currentTarget;
      $(el).prepOverlay({
        subtype: "ajax",
        filter: "h1,div.remarks-widget",
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function(event) {
            var overlay;
            overlay = this.getOverlay();
            $("div.pb-ajax>div", overlay).addClass("container-fluid");
            $("h3", overlay).remove();
            $("textarea", overlay).remove();
            $("input", overlay).remove();
            return overlay.draggable();
          },
          onLoad: function(event) {
            return $.mask.close();
          }
        }
      });
      return $(el).click();
    };

    WorksheetManageResultsView.prototype.on_wideinterims_apply_click = function(event) {

      /*
       * Eventhandler when the wide interim apply button was clicked
       */
      var $el, analysis, empty_only, interim, set_value, value;
      console.debug("°°° WorksheetManageResultsView::on_wideinterims_apply_click °°°");
      event.preventDefault();
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $("#wideinterims_interims").val();
      empty_only = $("#wideinterims_empty").is(":checked");
      value = $("#wideinterims_value").val();
      set_value = function(input, value) {
        var evt, nativeInputValueSetter;
        nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, value);
        evt = new Event('input', {
          bubbles: true
        });
        return input.dispatchEvent(evt);
      };
      return $("tr td input[column_key='" + interim + "']").each(function(index, input) {
        if (empty_only) {
          if ($(this).val() === "" || $(this).val().match(/\d+/) === "0") {
            set_value(input, value);
          }
        } else {
          set_value(input, value);
        }
        return true;
      });
    };

    return WorksheetManageResultsView;

  })();

}).call(this);

/**
 * Controller class for Worksheed Print View
 */
function WorksheetPrintView() {

    var that = this;
    var referrer_cookie_name = '_wspv';

    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    that.load = function() {

        // Store referrer in cookie in case it is lost due to a page reload
        var backurl = document.referrer;
        if (backurl) {
            bika.lims.SiteView.setCookie("ws.print.urlback", backurl);
        } else {
            backurl = bika.lims.SiteView.readCookie("ws.print.urlback");
            if (!backurl) {
                backurl = portal_url;
            }
        }

        load_barcodes();

        $('#print_button').click(function(e) {
            e.preventDefault();
            window.print();
        });

        $('#cancel_button').click(function(e) {
            e.preventDefault();
            location.href = backurl;
        });

        $('#template').change(function(e) {
            var url = window.location.href;
            var seltpl = $(this).val();
            var selcols = $("#numcols").val();
            $('#worksheet-printview').animate({opacity:0.2}, 'slow');
            $.ajax({
                url: url,
                type: 'POST',
                data: { "template":seltpl,
                        "numcols":selcols}
            })
            .always(function(data) {
                var htmldata = data;
                var cssdata = $(htmldata).find('#report-style').html();
                $('#report-style').html(cssdata);
                htmldata = $(htmldata).find('#worksheet-printview').html();
                $('#worksheet-printview').html(htmldata);
                $('#worksheet-printview').animate({opacity:1}, 'slow');
                load_barcodes();
            });
        });

        $('#numcols').change(function(e) {
            var url = window.location.href;
            var selcols = $(this).val();
            var seltpl = $('#template').val();
            $('#worksheet-printview').animate({opacity:0.2}, 'slow');
            $.ajax({
                url: url,
                type: 'POST',
                data: { "template":seltpl,
                        "numcols":selcols}
            })
            .always(function(data) {
                var htmldata = data;
                var cssdata = $(htmldata).find('#report-style').html();
                $('#report-style').html(cssdata);
                htmldata = $(htmldata).find('#worksheet-printview').html();
                $('#worksheet-printview').html(htmldata);
                $('#worksheet-printview').animate({opacity:1}, 'slow');
                load_barcodes();
            });
        });
    }

    function get(name){
       if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
          return decodeURIComponent(name[1]);
    }

    function load_barcodes() {
        // Barcode generator
        $('.barcode').each(function() {
            var id = $(this).attr('data-id');
            var code = $(this).attr('data-code');
            var barHeight = $(this).attr('data-barHeight');
            var addQuietZone = $(this).attr('data-addQuietZone');
            var showHRI = $(this).attr('data-showHRI');
            $(this).barcode(id, code,
                            {'barHeight': parseInt(barHeight),
                             'addQuietZone': Boolean(addQuietZone),
                             'showHRI': Boolean(showHRI) });
        });
    }
}

/**
 * Controller class for Worksheet templates
 */
function WorksheetTemplateEdit() {

    var that = this;

    that.load = function() {
        // Update the analysis list after method change
        var method_selector = $('#archetypes-fieldname-RestrictToMethod')
            .find('select');
        //update_analysis_list(method_selector);
        $(method_selector).bind('change', function(index, element){
            //update_analysis_list(this);
            update_instruments_list(this);
        });
    };
    /**
    * Updates the instruments list deppending on the selected method
    * @param {method_element} is a select object.
    **/
    function update_instruments_list(method_element){
        var method = $(method_element).val();
        $.ajax({
            url: window.portal_url + "/ajaxgetworksheettemplateinstruments",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'method_uid': JSON.stringify(method) },
            dataType: 'json'
        }).done(function(data) {
            var instrument, i;
            if (data !== null && $.isArray(data)){
                instrument = $("#archetypes-fieldname-Instrument")
                    .find('select');
                $(instrument).find("option").remove();
                // Create an option for each instrument
                for (i=0; data.length > i; i++){
                    $(instrument).append(
                        '<option value="' + data[i].uid +
                        '">' + data[i].m_title + '</option>'
                    );
                }
            }
        }).fail(function() {
            window.bika.lims.log(
                    "bika.lims.worksheettemplate: Something went wrong while "+
                    "retrieving instrument list");
        });
    }
    /**
    * This function restricts the available analysis services to those with
    * the same method as the selected in the worksheet template.
    * @param {method_element} is a select object.
    **/
    function update_analysis_list(method_element){
        var method = $(method_element).val();
        $.ajax({
            url: window.portal_url + "/ajaxgetetworksheettemplateserviceswidget",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'method_uid': JSON.stringify(method) },
            dataType: 'json'
        }).done(function(data) {
            if (data !== null){
                var services_div = $(
                    'div#archetypes-fieldname-Service #folderlisting-main-table')
                    .find('.bika-listing-table').remove();
                var instrument, i;
                var table = $(
                    'div#archetypes-fieldname-Service #folderlisting-main-table');
                $(table).append(data);
            }
        }).fail(function() {
            window.bika.lims.log(
                    "bika.lims.worksheettemplate: Something went wrong while "+
                    "retrieving the analysis services list");
        });
    }
}

window.bika = window.bika || { lims: {} };

/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.bika.lims.controllers =  {

    /** JS Utilities **/

    "html":
        ['CommonUtils'],

    // Barcode utils
    ".barcode, .qrcode":
        ['BarcodeUtils'],

    // Range graphics
    ".range-chart":
        ['RangeGraph'],

    // Atachments
    ".attachments":
        ['AttachmentsUtils'],

    /** JS objects to be loaded always **/

    "body":
        ['SiteView'],


    /** JS objects to be loaded on specific views or pages **/

    // Methods
    ".portaltype-method.template-base_edit":
        ['MethodEditView'],

    // Analysis Services
    ".portaltype-analysisservice.template-base_edit":
        ['AnalysisServiceEditView'],

    // Analysis Profile
    ".portaltype-analysisprofile.template-base_edit":
        ['AnalysisProfileEditView'],

    // Instruments
    ".portaltype-instrument.template-referenceanalyses":
        ['InstrumentReferenceAnalysesView'],

    ".portaltype-instrumentcertification.template-base_edit":
        ['InstrumentCertificationEditView'],

    ".portaltype-instrument.template-base_edit":
            ['InstrumentEditView'],

    // Editing a calculation
    ".portaltype-calculation":
        ['CalculationEditView'],

    // Bika Setup
    ".portaltype-bikasetup.template-base_edit":
        ['BikaSetupEditView'],


    // Clients
    ".portaltype-client.template-base_edit":
        ['ClientEditView'],

    "div.overlay #client-base-edit":
        ['ClientOverlayHandler'],

    // Reference Samples
    ".portaltype-referencesample.template-analyses":
        ['ReferenceSampleAnalysesView'],

    // Analysis Request Templates
    ".portaltype-artemplate.template-base_edit":
        ['ARTemplateEditView'],

    // Analysis Requests
    ".portaltype-analysisrequest":
        ['AnalysisRequestView',
     ],
     // Analysis request, but not in ARAdd view
     ".portaltype-analysisrequest:not(.template-ar_add)":
        ['RejectionKickOff',],

    ".portaltype-analysisrequest.template-base_view":
        ['WorksheetManageResultsView',
         'AnalysisRequestViewView',
         'RejectionKickOff',],

    ".portaltype-analysisrequest.template-analyses":
        ['AnalysisRequestAnalysesView'],

	// Common and utilities for AR Add forms
	".portaltype-analysisrequest.template-ar_add": ['AnalysisRequestAddView'],

  // AR Add 2
	"#analysisrequest_add_form": ['AnalysisRequestAdd'],

    // Supply Orders
    ".portaltype-supplyorder.template-base_edit":
        ['SupplyOrderEditView'],

    // Imports
    ".portaltype-plone-site.template-import":
        ['InstrumentImportView'],

    // Batches
    ".portaltype-batchfolder":
        ['BatchFolderView'],

    // Worksheets
    ".portaltype-worksheetfolder":
        ['WorksheetFolderView'],

    ".portaltype-worksheet.template-add_blank":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_control":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_duplicate":
        ['WorksheetAddDuplicateAnalysesView'],

    ".portaltype-worksheet.template-manage_results":
        ['WorksheetManageResultsView'],

    ".portaltype-worksheettemplate.template-base_edit":
        ['WorksheetTemplateEdit'],

    "#worksheet-printview-wrapper":
        ['WorksheetPrintView'],

    ".portaltype-reflexrule.template-base_edit":
        ['ReflexRuleEditView'],

    ".template-labcontacts.portaltype-department":
        ['DepartmentLabContactsView'],

    // Reports folder (not AR Reports)
    ".portaltype-reportfolder":
        ['ReportFolderView'],

    // If RemarksWidget is in use on this page,
    // load RemarksWIdgetview
    ".ArchetypesRemarksWidget": ["RemarksWidgetView"],

    // Add here your view-controller/s assignment

};



var _bika_lims_loaded_js = new Array();

/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
 */
window.bika.lims.initview = function() {
    return window.bika.lims.loadControllers(false, []);
};
/**
 * 'all' is a bool variable used to load all the controllers.
 * 'controllerKeys' is an array which contains specific controllers' keys which aren't
 * in the current view, but you want to be loaded anyway. To deal with overlay
 * widgets, for example.
 * Calling the function "loadControllers(false, [array with desied JS controllers keys from
 * window.bika.lims.controllers])", allows you to force bika to load/reload JS controllers defined inside the array.
 */
window.bika.lims.loadControllers = function(all, controllerKeys) {
    var controllers = window.bika.lims.controllers;
    var prev = _bika_lims_loaded_js.length;
    for (var key in controllers) {
        // Check if the key have value. Also check if this key exists in the controllerKeys array.
        // If controllerKeys contains the key, the JS controllers defined inside window.bika.lims.controllers
        // and indexed with that key will be reloaded/loaded (wherever you are.)
        if ($(key).length || $.inArray(key, controllerKeys) >= 0) {
            controllers[key].forEach(function(js) {
                if (all == true || $.inArray(key, controllerKeys) >= 0 || $.inArray(js, _bika_lims_loaded_js) < 0) {
                    console.debug('[bika.lims.loader] Loading '+js);
                    obj = new window[js]();
                    obj.load();
                    // Register the object for further access
                    window.bika.lims[js]=obj;
                    _bika_lims_loaded_js.push(js);
                }
            });
        }
    }
    return _bika_lims_loaded_js.length - prev;

};

window.bika.lims.initialized = false;
/**
 * Initializes all bika.lims js stuff
 */
window.bika.lims.initialize = function() {
    return window.bika.lims.initview();
};

document.addEventListener("DOMContentLoaded", () => {
    // Initializes bika.lims
    var length = window.bika.lims.initialize();
    window.bika.lims.initialized = true;
  console.debug("*** SENAITE LOADER INITIALIZED ***");
});
