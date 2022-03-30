
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
