
/*
 * Controller class for Analysis Service Edit view
 */

(function() {
  window.AnalysisServiceEditView = function() {
    var applyStyles, calculation_field, calculation_label, calculation_select_element, catchOriginalValues, default_calculation_chk, insert_manual_methods, instr_chk, instr_fd, instr_sel, instre_fd, instrs_fd, instrs_ms, interim_fd, interim_rw, ldman_chk, ldman_fd, ldsel_chk, loadInterims, manual_chk, manual_fd, method_fd, method_sel, methods_fd, methods_ms, that, updateContainers, validateInstruments;
    that = this;
    manual_fd = $('#archetypes-fieldname-ManualEntryOfResults');
    manual_chk = $('#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults');
    instre_fd = $('#archetypes-fieldname-InstrumentEntryOfResults');
    instr_chk = $('#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults');
    methods_fd = $('#archetypes-fieldname-Methods');
    methods_ms = $('#archetypes-fieldname-Methods #Methods');
    method_fd = $('#archetypes-fieldname-Method');
    method_sel = $('#archetypes-fieldname-Method #Method');
    instrs_fd = $('#archetypes-fieldname-Instruments');
    instrs_ms = $('#archetypes-fieldname-Instruments #Instruments');
    instr_fd = $('#archetypes-fieldname-Instrument');
    instr_sel = $('#archetypes-fieldname-Instrument #Instrument');
    default_calculation_chk = $('#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation');
    calculation_field = $('#archetypes-fieldname-Calculation');
    calculation_label = $(calculation_field).find('label');
    calculation_select_element = $('#archetypes-fieldname-Calculation #Calculation');
    interim_fd = $('#archetypes-fieldname-InterimFields');
    interim_rw = $('#archetypes-fieldname-InterimFields tr.records_row_InterimFields');
    ldsel_chk = $('#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector');
    ldman_fd = $('#archetypes-fieldname-AllowManualDetectionLimit');
    ldman_chk = $('#archetypes-fieldname-AllowManualDetectionLimit #AllowManualDetectionLimit');

    /*
     * Entry-point method for AnalysisServiceEditView
     */
    insert_manual_methods = function() {
      $.ajax({
        url: window.portal_url + '/get_instrument_methods',
        type: 'POST',
        data: {
          '_authenticator': $('input[name="_authenticator"]').val(),
          'uid': $(instr_sel).val()
        },
        dataType: 'json',
        async: false
      }).done(function(data) {
        $(method_sel).find('option').remove();
        if (data !== null && data.methods.length > 0) {
          $.each(data.methods, function(index, value) {
            var option, title, uid;
            uid = value.uid;
            title = value.title;
            console.debug('Adding Method ' + title + ' to the Selection');
            option = '<option value="' + uid + '">' + title + '</option>';
            $(method_sel).append(option);
            $(method_sel).val(uid);
          });
        } else {
          $(method_sel).append('<option value=\'\'>' + _('None') + '</option>');
          $(method_sel).val('');
        }
        $(default_calculation_chk).change();
      });
    };

    /*
     * Controls the visibility and values of fields generated by Plone automatically.
     */
    catchOriginalValues = function() {
      var calcuid, hidd, i, keyword, originals, request_data, rows, title, toremove, unit, value, wide;
      $(manual_chk).attr('data-default', $(manual_chk).is(':checked'));
      $(instr_chk).attr('data-default', $(instr_chk).is(':checked'));
      $(methods_ms).attr('data-default', $(methods_ms).val());
      $(method_sel).attr('data-default', $(method_sel).val());
      $(instrs_ms).attr('data-default', $(instrs_ms).val());
      $(instr_sel).attr('data-default', $(instr_sel).val());
      $(default_calculation_chk).attr('data-default', $(default_calculation_chk).is(':checked'));
      $(calculation_select_element).attr('data-default', $(calculation_select_element).val());
      if (!$(manual_chk).is(':checked')) {
        $(methods_fd).hide();
        $(methods_ms).find('option[selected]').prop('selected', false);
        $(methods_ms).val('');
      }
      if (!$(instr_chk).is(':checked')) {
        $('#invalid-instruments-alert').remove();
        $(instrs_fd).hide();
        if ($(instrs_ms).find('option[value=""]').length === 0) {
          $(instrs_ms).prepend('<option value="">None</option>');
        }
        $(instrs_ms).val('');
        $(instrs_ms).find('option[value=""]').prop('selected', true);
        $(instr_fd).hide();
        if ($(instr_sel).find('option[value=""]').length === 0) {
          $(instr_sel).prepend('<option value="">None</option>');
        }
        $(instr_sel).val('');
        $(instr_sel).find('option[value=""]').prop('selected', true);
        $(manual_chk).click(function(e) {
          e.preventDefault();
        });
      }
      if (!$(calculation_select_element).find(':selected').val()) {
        $(interim_fd).hide();
      }
      $(methods_ms).find('option[value=""]').remove();
      if (!$(default_calculation_chk).is(':checked')) {
        $(calculation_label).show();
      } else {
        $(calculation_label).hide();
      }
      $('body').append('<input type=\'hidden\' id=\'temp_manual_interims\' value=\'[]\'>');
      rows = $('tr.records_row_InterimFields');
      originals = [];
      if ($(rows).length > 1) {
        i = $(rows).length - 2;
        while (i >= 0) {
          keyword = $($($(rows)[i]).find('td input')[0]).val();
          if (keyword !== '') {
            title = $($($(rows)[i]).find('td input')[1]).val();
            value = $($($(rows)[i]).find('td input')[2]).val();
            unit = $($($(rows)[i]).find('td input')[3]).val();
            hidd = $($($(rows)[i]).find('td input')[4]).is(':checked');
            wide = $($($(rows)[i]).find('td input')[5]).is(':checked');
            originals.push([keyword, title, value, unit, hidd, wide]);
          }
          i--;
        }
      }
      toremove = [];
      calcuid = '';
      if ($(default_calculation_chk).is(':checked')) {
        $(calculation_select_element).find('option').remove();
        calcuid = $(calculation_select_element).attr('data-default');
      }
      if (calcuid !== null && calcuid !== '') {
        request_data = {
          catalog_name: 'bika_setup_catalog',
          UID: calcuid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          var manualinterims, row;
          if (data.objects.length > 0) {
            $(calculation_select_element).append('<option value="' + data.objects[0].UID + '">' + data.objects[0].Title + '</option>');
            $(calculation_select_element).val(data.objects[0].UID);
            $(calculation_select_element).find('option').attr('selected', 'selected');
            i = 0;
            while (i < data.objects[0].InterimFields.length) {
              row = data.objects[0].InterimFields[i];
              toremove.push(row.keyword);
              i++;
            }
          } else {
            $(calculation_select_element).append('<option value="' + data + '">' + _('None') + '</option>');
            $(calculation_select_element).val('');
          }
          manualinterims = originals.filter(function(el) {
            return toremove.indexOf(el[0]) < 0;
          });
          $('#temp_manual_interims').val($.toJSON(manualinterims));
        });
      }
    };

    /*
     * Loads the Interim fields Widget for the specificied calculation
     */
    loadInterims = function(calcuid) {
      var i, request_data, rows;
      $(interim_fd).hide();
      if (calcuid === null || calcuid === '') {
        $('#InterimFields_more').click();
        rows = $('tr.records_row_InterimFields');
        if ($(rows).length > 1) {
          i = $(rows).length - 2;
          while (i >= 0) {
            $($(rows)[i]).remove();
            i--;
          }
        }
        $(interim_fd).hide();
        return;
      }
      request_data = {
        catalog_name: 'bika_setup_catalog',
        UID: calcuid
      };
      window.bika.lims.jsonapi_read(request_data, function(data) {
        var _rows, hidd, j, k, keyword, manualinterims, original, originals, row, unit, value, wide;
        $('#InterimFields_more').click();
        _rows = $('tr.records_row_InterimFields');
        originals = [];
        if ($(_rows).length > 1) {
          i = $(_rows).length - 2;
          while (i >= 0) {
            keyword = $($($(_rows)[i]).find('td input')[0]).val();
            if (keyword !== '') {
              value = $($($(_rows)[i]).find('td input')[2]).val();
              unit = $($($(_rows)[i]).find('td input')[3]).val();
              hidd = $($($(_rows)[i]).find('td input')[4]).is(':checked');
              wide = $($($(_rows)[i]).find('td input')[5]).is(':checked');
              originals.push([keyword, value, unit, hidd, wide]);
            }
            $($(_rows)[i]).remove();
            i--;
          }
        }
        if (data.objects.length > 0) {
          $(interim_fd).fadeIn('slow');
          $('[id^=\'InterimFields-keyword-\']').attr('id', 'InterimFields-keyword-0');
          $('[id^=\'InterimFields-title-\']').attr('id', 'InterimFields-title-0');
          $('[id^=\'InterimFields-value-\']').attr('id', 'InterimFields-value-0');
          $('[id^=\'InterimFields-unit-\']').attr('id', 'InterimFields-unit-0');
          i = 0;
          while (i < data.objects[0].InterimFields.length) {
            row = data.objects[0].InterimFields[i];
            original = null;
            j = 0;
            while (j < originals.length) {
              if (originals[j][0] === row.keyword) {
                original = originals[j];
                break;
              }
              j++;
            }
            $('#InterimFields-keyword-' + i).val(row.keyword);
            $('#InterimFields-title-' + i).val(row.title);
            if (original === null) {
              $('#InterimFields-value-' + i).val(row.value);
              $('#InterimFields-unit-' + i).val(row.unit);
            } else {
              $('#InterimFields-value-' + i).val(original[1]);
              $('#InterimFields-unit-' + i).val(original[2]);
            }
            $('#InterimFields_more').click();
            i++;
          }
        }
        manualinterims = $.parseJSON($('#temp_manual_interims').val());
        if (manualinterims.length > 0) {
          $(interim_fd).fadeIn('slow');
          i = $('tr.records_row_InterimFields').length - 1;
          k = 0;
          while (k < manualinterims.length) {
            $('#InterimFields-keyword-' + i).val(manualinterims[k][0]);
            $('#InterimFields-title-' + i).val(manualinterims[k][1]);
            $('#InterimFields-value-' + i).val(manualinterims[k][2]);
            $('#InterimFields-unit-' + i).val(manualinterims[k][3]);
            $('#InterimFields_more').click();
            i++;
            k++;
          }
        }
      });
    };

    /*
     * Checks if the selected instruments aren't out-of-date and their
     * latest Internal Calibration Tests are valid. If an invalid
     * instrument gets selected, shows an alert to the user
     */
    validateInstruments = function() {
      var _, insts;
      $('#invalid-instruments-alert').remove();
      if ($('#InstrumentEntryOfResults').is(':checked')) {
        window.jarn.i18n.loadCatalog('bika');
        _ = window.jarn.i18n.MessageFactory('bika');
        insts = $('#Instruments').val() ? $('#Instruments').val() : [];
        $.each(insts, function(index, value) {
          var request_data;
          request_data = {
            catalog_name: 'uid_catalog',
            UID: value
          };
          window.bika.lims.jsonapi_read(request_data, function(data) {
            var errmsg, html, instrument_path, title;
            if (data.objects[0].Valid !== '1') {
              title = data.objects[0].Title;
              instrument_path = window.location.protocol + '//' + window.location.host + data.objects[0].path;
              if ($('#invalid-instruments-alert').length > 0) {
                $('#invalid-instruments-alert dd').first().append(', ' + title);
              } else {
                errmsg = _('Some of the selected instruments are out-of-date or with failed calibration tests');
                html = '<div id=\'invalid-instruments-alert\' class=\'alert\'>' + '<dt>' + errmsg + ':</dt>' + '<dd> <a href=' + instrument_path + '>' + title + '</a></dd>' + '</div>';
                $('#analysisservice-base-edit').before(html);
              }
            }
          });
        });
      } else {
        loadEmptyInstrument();
      }
    };
    updateContainers = function(target, requestdata) {
      $.ajax({
        type: 'POST',
        url: window.location.href + '/getUpdatedContainers',
        data: requestdata,
        success: function(data) {
          var option;
          option = $(target).val();
          if (option === null || option === void 0) {
            option = [];
          }
          $(target).empty();
          $.each(data, function(i, v) {
            if ($.inArray(v[0], option) > -1) {
              $(target).append('<option value=\'' + v[0] + '\' selected=\'selected\'>' + v[1] + '</option>');
            } else {
              $(target).append('<option value=\'' + v[0] + '\'>' + v[1] + '</option>');
            }
          });
        },
        dataType: 'json'
      });
    };
    applyStyles = function() {
      $($(manual_fd)).after($(methods_fd));
      $(methods_fd).css('border', '1px solid #cfcfcf').css('background-color', '#efefef').css('padding', '10px').css('margin-bottom', '20px');
      $(instrs_fd).css('border', '1px solid #cfcfcf').css('border-bottom', 'none').css('background-color', '#efefef').css('padding', '10px').css('margin-bottom', '0px');
      $(instr_fd).css('border', '1px solid #cfcfcf').css('border-top', 'none').css('background-color', '#efefef').css('padding', '10px').css('margin-bottom', '20px');
    };
    that.load = function() {
      var errmsg, html, title;
      $(ldsel_chk).change(function() {
        if ($(this).is(':checked')) {
          $(ldman_fd).show();
        } else {
          $(ldman_fd).hide();
          $(ldman_chk).prop('checked', false);
        }
      });
      $(ldsel_chk).change();
      $('.portaltype-analysisservice #RequiredVolume, .portaltype-analysisservice #Separate').change(function() {
        var requestdata, separate;
        separate = $('#Separate').prop('checked');
        if (!separate) {
          $('[name=\'Preservation\\:list\']').prop('disabled', false);
        }
        requestdata = {
          'allow_blank': true,
          'show_container_types': !separate,
          'show_containers': separate,
          '_authenticator': $('input[name=\'_authenticator\']').val()
        };
        updateContainers('#Container\\:list', requestdata);
      });
      $('.portaltype-analysisservice [name^=\'PartitionSetup.separate\'],.portaltype-analysisservice [name^=\'PartitionSetup.vol\']').change(function() {
        var minvol, requestdata, separate, target;
        separate = $(this).parents('tr').find('[name^=\'PartitionSetup.separate\']').prop('checked');
        if (!separate) {
          $(this).parents('tr').find('[name^=\'PartitionSetup.preservation\']').prop('disabled', false);
        }
        minvol = $(this).parents('tr').find('[name^=\'PartitionSetup.vol\']').val();
        target = $(this).parents('tr').find('[name^=\'PartitionSetup.container\']');
        requestdata = {
          'allow_blank': true,
          'minvol': minvol,
          'show_container_types': !separate,
          'show_containers': separate,
          '_authenticator': $('input[name=\'_authenticator\']').val()
        };
        updateContainers(target, requestdata);
      });
      $('.portaltype-analysisservice [name^=\'PartitionSetup.sampletype\']').change(function() {
        var request_data, st_element;
        st_element = this;
        request_data = {
          catalog_name: 'uid_catalog',
          UID: $(this).val()
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          var minvol, target;
          minvol = data.objects[0].MinimumVolume;
          target = $(st_element).parents('tr').find('[name^=\'PartitionSetup.vol\']');
          $(target).val(minvol);
          $(st_element).parents('tr').find('[name^=\'PartitionSetup.container\']').change();
        });
      });
      $('.portaltype-analysisservice #Container').bind('selected', function() {
        var container_uid, request_data;
        container_uid = $(this).attr('uid');
        if (container_uid === void 0 || container_uid === null) {
          container_uid = '';
        }
        request_data = {
          catalog_name: 'uid_catalog',
          UID: container_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          if (data.objects.length < 1 || !data.objects[0].PrePreserved || !data.objects[0].Preservation) {
            $('#Preservation').val('');
            $('#Preservation').prop('disabled', false);
          } else {
            $('#Preservation').val(data.objects[0].Preservation);
            $('#Preservation').prop('disabled', true);
          }
        });
      });
      $('.portaltype-analysisservice [name^=\'PartitionSetup.container\']').change(function() {
        var container_uid, request_data, target;
        target = $(this).parents('tr').find('[name^=\'PartitionSetup.preservation\']');
        container_uid = $(this).val();
        if (!container_uid || container_uid.length === 1 && !container_uid[0]) {
          $(target).prop('disabled', false);
          return;
        }
        container_uid = container_uid[0];
        if (container_uid === void 0 || container_uid === null) {
          container_uid = '';
        }
        request_data = {
          catalog_name: 'uid_catalog',
          UID: container_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
          if (data.objects.length < 1 || !data.objects[0].PrePreserved || !data.objects[0].Preservation) {
            $(target).prop('disabled', false);
          } else {
            $(this).val(container_uid);
            $(target).val(data.objects[0].Preservation);
            $(target).prop('disabled', true);
          }
        });
      });
      if ($(instrs_ms).find('option').length === 0) {
        $(manual_chk).prop('checked', true);
        $(manual_chk).prop('readonly', true);
        $(instr_chk).prop('checked', false);
        $(instr_chk).prop('readonly', true);
        errmsg = _('No instruments available');
        title = _('Instrument entry of results option not allowed');
        html = '<div id=\'no-instruments-alert\' class=\'alert\'>' + '<dt>' + errmsg + '</dt>' + '<dd>' + title + '</dd>' + '</div>';
        $('#analysisservice-base-edit').before(html);
      }
      $(manual_chk).change(function() {
        if ($(this).is(':checked')) {
          insert_manual_methods();
          $(methods_fd).fadeIn('slow');
          $(methods_ms).change();
        } else {
          $(methods_fd).hide();
          $(methods_ms).find('option[selected]').prop('selected', false);
          $(methods_ms).val('');
          $(methods_ms).change();
          $(instr_chk).prop('checked', true);
        }
        $(instr_chk).change();
      });
      $(instr_chk).change(function() {
        if ($(this).is(':checked')) {
          $(manual_chk).unbind('click');
          $(instrs_fd).fadeIn('slow');
          $(instrs_ms).find('option[value=""]').remove();
          $(instr_sel).find('option[value=""]').remove();
          $(instr_fd).fadeIn('slow');
          $(method_sel).focus(function(e) {
            $(this).blur();
          });
          $(calculation_select_element).focus(function(e) {
            $(this).blur();
          });
          $(instrs_ms).change();
        } else {
          $('#invalid-instruments-alert').remove();
          $(instrs_fd).hide();
          if ($(instrs_ms).find('option[value=""]').length === 0) {
            $(instrs_ms).prepend('<option value="">None</option>');
          }
          $(instrs_ms).val('');
          $(instrs_ms).find('option[value=""]').prop('selected', true);
          $(instr_fd).hide();
          if ($(instr_sel).find('option[value=""]').length === 0) {
            $(instr_sel).prepend('<option value="">None</option>');
          }
          $(instr_sel).val('');
          $(instr_sel).find('option[value=""]').prop('selected', true);
          $(manual_chk).click(function(e) {
            e.preventDefault();
          });
          $(methods_ms).change();
          $(method_sel).unbind('focus');
          if (!$(manual_chk).is(':checked')) {
            $(manual_chk).prop('checked', true);
            $(manual_chk).change();
          }
        }
      });
      $(methods_ms).change(function(e) {
        var defoption, methods, prevmethod, prevmethodtxt;
        prevmethod = $(method_sel).val();
        prevmethodtxt = $(method_sel).find('option[value="' + prevmethod + '"]').html();

        /*if ($(this).val() == null) {
                // At least one method must be selected
                $(this).val($(this).find('option').first().val());
        }
         */
        if ($(instr_chk).is(':checked')) {
          $(method_sel).change(function(e) {
            $(default_calculation_chk).change();
          });
          return;
        }
        $(method_sel).find('option').remove();
        methods = $(methods_ms).val();
        if (methods !== null) {
          $.each(methods, function(index, value) {
            var option;
            option = $(methods_ms).find('option[value="' + value + '"]').clone();
            $(method_sel).append(option);
          });
        } else {
          $(method_sel).prepend('<option value="">' + _('None') + '</option>');
        }
        defoption = $(method_sel).find('option[value="' + $(method_sel).attr('data-default') + '"]');
        if (defoption === null || defoption === '') {
          defoption = $(method_sel).find('option[value="' + prevmethod + '"]');
          if (defoption === null || defoption === '') {
            defoption = $(method_sel).find('option').first();
          }
        }
        $(method_sel).change();
      });
      $(method_sel).change(function(e) {
        $(default_calculation_chk).change();
      });
      $(instrs_ms).change(function(e) {
        var defoption, insts, previnstr;
        previnstr = $(instr_sel).val();
        if ($(this).val() === null) {
          $(this).val($(this).find('option').first().val());
        }
        $(instr_sel).find('option').remove();
        insts = $(instrs_ms).val();
        $.each(insts, function(index, value) {
          var option;
          option = $(instrs_ms).find('option[value="' + value + '"]').clone();
          $(instr_sel).append(option);
        });
        defoption = $(instr_sel).find('option[value="' + previnstr + '"]');
        if (defoption === null || defoption === '') {
          defoption = $(instr_sel).find('option[value="' + $(instr_sel).attr('data-default') + '"]');
          if (defoption === null || defoption === '') {
            defoption = $(instr_sel).find('option').first();
          }
        }
        $(instr_sel).val($(defoption).val());
        $('#invalid-instruments-alert').remove();
        $.each(insts, function(index, value) {
          var request_data;
          if (value !== '' && $(instr_chk).is(':checked')) {
            request_data = {
              catalog_name: 'uid_catalog',
              UID: value
            };
            window.bika.lims.jsonapi_read(request_data, function(data) {
              var title;
              var errmsg;
              var html;
              var instrument_path;
              if (!$(instr_chk).is(':checked')) {
                $('#invalid-instruments-alert').remove();
              } else if (data.objects[0].Valid !== '1') {
                title = data.objects[0].Title;
                instrument_path = window.location.protocol + '//' + window.location.host + data.objects[0].path;
                if ($('#invalid-instruments-alert').length > 0) {
                  $('#invalid-instruments-alert dd').first().append(', ' + title);
                } else {
                  errmsg = _('Some of the selected instruments are out-of-date or with failed calibration tests');
                  html = '<div id=\'invalid-instruments-alert\' class=\'alert\'>' + '<dt>' + errmsg + ':</dt>' + '<dd> <a href=' + instrument_path + '>' + title + '</a></dd>' + '</div>';
                  $('#analysisservice-base-edit').before(html);
                }
              }
            });
          }
        });
        $(instr_sel).change();
      });
      $(instr_sel).change(function() {
        $(method_sel).find('option').remove();
        $(method_sel).append('<option value=\'\'>' + _('None') + '</option>');
        $(method_sel).val('');
        $.ajax({
          url: window.portal_url + '/get_instrument_methods',
          type: 'POST',
          data: {
            '_authenticator': $('input[name="_authenticator"]').val(),
            'uid': $(instr_sel).val()
          },
          dataType: 'json',
          async: false
        }).done(function(data) {
          $(method_sel).find('option').remove();
          if (data !== null && data.methods.length > 0) {
            $.each(data.methods, function(index, value) {
              var title;
              var option, uid;
              uid = value.uid;
              title = value.title;
              console.debug('Adding Method ' + title + ' to the Selection');
              option = '<option value="' + uid + '">' + title + '</option>';
              $(method_sel).append(option);
              $(method_sel).val(uid);
            });
          } else {
            $(method_sel).append('<option value=\'\'>' + _('None') + '</option>');
            $(method_sel).val('');
          }
          $(default_calculation_chk).change();
        });
      });
      $(default_calculation_chk).change(function() {
        var muid;
        if ($(this).is(':checked')) {
          $(calculation_label).hide();
          muid = $(method_sel).val();
          if (muid !== null && muid !== '') {
            $.ajax({
              url: window.portal_url + '/get_method_calculation',
              type: 'POST',
              data: {
                '_authenticator': $('input[name="_authenticator"]').val(),
                'uid': muid
              },
              dataType: 'json'
            }).done(function(data) {
              $(calculation_select_element).find('option').remove();
              if (data !== null && data['uid']) {
                $(calculation_select_element).prepend('<option value="' + data['uid'] + '">' + data['title'] + '</option>');
              } else {
                $(calculation_select_element).append('<option value="">' + _('None') + '</option>');
              }
              $(calculation_select_element).val($(calculation_select_element).find('option').first().val());
              $(calculation_select_element).change();
            });
          } else {
            $(calculation_select_element).find('option').remove();
            $(calculation_select_element).append('<option value="">' + _('None') + '</option>');
            $(calculation_select_element).change();
          }
        } else {
          $(calculation_select_element).find('option').remove();
          $(calculation_select_element).append('<option value="">' + _('None') + '</option>');
          $(calculation_select_element).val('');
          $(calculation_label).show();
          $.ajax({
            url: window.portal_url + '/get_available_calculations',
            type: 'POST',
            data: {
              '_authenticator': $('input[name="_authenticator"]').val()
            },
            dataType: 'json'
          }).done(function(data) {
            var i;
            $(calculation_select_element).find('option').remove();
            if (data !== null) {
              i = 0;
              while (i < data.length) {
                $(calculation_select_element).append('<option value="' + data[i]['uid'] + '">' + data[i]['title'] + '</option>');
                i++;
              }
            } else {
              $(calculation_select_element).append('<option value="">' + _('None') + '</option>');
            }
            $(calculation_select_element).val($(calculation_select_element).find('option').first().val());
            $(calculation_select_element).change();
          });
        }
      });
      $(calculation_select_element).change(function() {
        loadInterims($(this).val());
      });
      applyStyles();
      catchOriginalValues();
    };
  };

}).call(this);
