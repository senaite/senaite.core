
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
      href = event.currentTarget.href;
      element = $('#PublicationSpecification_uid');
      if (element.length > 0) {
        href = href + '&PublicationSpecification=' + $(element).val();
      }
      window.location.href = href;
    };
    transition_schedule_sampling = function() {

      /* It is not possible to abort a transition using "workflow_script_*".
      The recommended way is to set a guard instead.
      The guard expression should be able to look up a view to facilitate more
      complex guard code, but when a guard returns False the transition isn't
      even listed as available. It is listed after saving the fields.
      */
      var url;
      url = $('#workflow-transition-schedule_sampling').attr('href');
      if (url) {
        $('#workflow-transition-schedule_sampling').click(function() {
          var date, message, sampler;
          date = $('#SamplingDate').val();
          sampler = $('#ScheduledSamplingSampler').val();
          if (date !== '' && date !== void 0 && date !== null && sampler !== '' && sampler !== void 0 && sampler !== null) {
            window.location.href = url;
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
                    catalog_name: "senaite_catalog_setup",
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
                    catalog_name: "senaite_catalog_setup",
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
    coffee --no-header -w -o ../ -c bika.lims.site.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.SiteView = (function() {
    function SiteView() {
      this.on_overlay_panel_click = bind(this.on_overlay_panel_click, this);
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
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    SiteView.prototype.load = function() {
      console.debug("SiteView::load");
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
      $("body").on("click", "a.overlay_panel", this.on_overlay_panel_click);
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

    SiteView.prototype.on_overlay_panel_click = function(event) {

      /*
       * Eventhandler when the service info icon was clicked
       */
      var el;
      console.debug("°°° SiteView::on_overlay_panel_click °°°");
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
    };
  };

}).call(this);

/**
 * Controller class for barcode utils
 */
function BarcodeUtils() {

    var that = this;

    that.load = function() {

        // https://larsjung.de/jquery-qrcode
        $(".qrcode").each(function() {
           let render = $(this).data("render") || "div";
           let size = $(this).data("size");
           let code = $(this).data("code");
           let quiet = $(this).data("quiet") || 0;
           let text = $(this).data("text") || "no text";

           $(this).qrcode({
                render: render,
                size: size, // 37.79 pixel == 10mm
                code: code,
                quiet: quiet, // quiet zone in modules
                text: text.toString()
            });
        });


        // https://barcode-coder.com/en/barcode-jquery-plugin-201.html
        $(".barcode").each(function() {
            let id = $(this).data("id") || "deadbeef";
            let code = $(this).data("code") || "code128";
            let barHeight = $(this).data("barheight") || 10;
            let addQuietZone = $(this).data("addquietzone") || false;
            let showHRI = $(this).data("showhri") || false;
            let output = $(this).data("output") || "svg";
            let color = $(this).data("color") || "#000000";

            $(this).barcode(id.toString(), code, {
                barHeight: barHeight,
                addQuietZone: addQuietZone,
                showHRI: showHRI,
                output: output,
                color: color
            });
        });
    }
}


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

  window.WorksheetManageResultsView = (function() {
    function WorksheetManageResultsView() {
      this.on_wideinterims_apply_click = bind(this.on_wideinterims_apply_click, this);
      this.on_slot_remarks_click = bind(this.on_slot_remarks_click, this);
      this.on_wideiterims_interims_change = bind(this.on_wideiterims_interims_change, this);
      this.on_wideiterims_analyses_change = bind(this.on_wideiterims_analyses_change, this);
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_layout_change = bind(this.on_layout_change, this);
      this.on_analyst_change = bind(this.on_analyst_change, this);
      this.reload_analyses_listing = bind(this.reload_analyses_listing, this);
      this.get_analyses_listing = bind(this.get_analyses_listing, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's manage results view
     */

    WorksheetManageResultsView.prototype.load = function() {
      console.debug("WorksheetManageResultsView::load");
      return this.bind_eventhandler();
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
      $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
      $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
      $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
      return $("body").on("click", "img.slot-remarks", this.on_slot_remarks_click);
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
      url = url.split("?")[0];
      return url.replace("#", "");
    };

    WorksheetManageResultsView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetManageResultsView.prototype.get_analyses_listing = function() {

      /*
       * Returns the root element of the analysis listing for results entry
       */
      var listing, selector;
      selector = "#analyses_form div.ajax-contents-table";
      listing = document.querySelector(selector);
      return listing;
    };

    WorksheetManageResultsView.prototype.reload_analyses_listing = function() {

      /*
       * Reloads the analyses listing for results entry
       */
      var event, listing;
      listing = this.get_analyses_listing();
      event = new Event("reload");
      return listing.dispatchEvent(event);
    };


    /* EVENT HANDLER */

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
        return bika.lims.SiteView.notify_in_panel(_p("Changes saved."), "succeed");
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(_t("Could not set the selected analyst"), "error");
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
        return this.reload_analyses_listing();
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(_t("Unable to apply the selected instrument"), "error");
      });
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

    // Analysis Requests
    ".portaltype-analysisrequest":
        ['AnalysisRequestView'],
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

    // Batches
    ".portaltype-batchfolder":
        ['BatchFolderView'],

    // Worksheets
    ".portaltype-worksheetfolder":
        ['WorksheetFolderView'],

    ".portaltype-worksheet.template-manage_results":
        ['WorksheetManageResultsView'],

    "#worksheet-printview-wrapper":
        ['WorksheetPrintView'],

    // If RemarksWidget is in use on this page,
    // load RemarksWIdgetview
    ".ArchetypesRemarksWidget": ["RemarksWidgetView"],

    // Add here your view-controller/s assignment

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
    var _bika_lims_loaded_js = new Array();
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

document.addEventListener("DOMContentLoaded", function(event) {
    window.bika.lims.loadControllers(false, []);
    console.debug("*** SENAITE LOADER INITIALIZED ***");
});
