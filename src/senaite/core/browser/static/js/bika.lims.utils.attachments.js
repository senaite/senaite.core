
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
