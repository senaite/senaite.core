jQuery( function($) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    _ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
    PMF = jarn.i18n.MessageFactory('plone');

    // Get date/datetime formats from Bika Setup via json API.
    var formats = {}
    request_data = {
        portal_type: "BikaSetup",
        aj_async: false,
        include_fields: ["DateFormats"]
    };
    window.bika.lims.jsonapi_read(request_data, function(data){
        var raw_formats = data.objects[0].DateFormats;
        for(i=0;i<raw_formats.length;i++){
            formats[raw_formats[i].Type] = raw_formats[i].UIFormat
        }
    });
    // In case formats are not found in Bika, just use default values.
    if(Object.keys(formats).length == 0){
        console.warn("Date formats not found in Bika Setup. This shouldn't happen.");
        formats = {
            date_format_long:"yy-mm-dd HH:mm",
            date_format_short: "yy-mm-dd",
            time_only: "HH:mm"
        }
    }
    $('[datepicker="1"]').datepicker({
        dateFormat: formats.date_format_short,
        changeMonth:true,
        changeYear:true,
        yearRange: "-50:+20"
    });

    $('[datetimepicker="1"]').datetimepicker({
        dateFormat: formats.date_format_short,
        timeFormat: formats.time_only,
        hourGrid: 4,
        minuteGrid: 10,
        changeMonth:true,
        changeYear:true,
        yearRange: "-100:+1"
    });

    $('[datepicker_nofuture="1"]').live("click", function() {
        $(this).datepicker( "option", "maxDate", "0" )
        .click(function(){$(this).attr("value", "");})
        .focus();
    });

    $('[datepicker_nofuture="1"]').change(function() {
      if (new Date(this.value)>new Date()) {
          alert("Please enter valid date");
          this.text='';
          this.value='';
      }
    });

    $('[datepicker="1"]').change(function() {
      validate_input('date_format_short', this);
    });

    $('[datetimepicker="1"]').change(function() {
      validate_input('date_format_long', this);
    });

    /**
    Validate date/datetime strings according to formats from Bika Setup. Displays an error message if fails.
    @param {String} type is either 'date_format_long' or 'date_format_long'
    @param {Element} field is the '<input>' element of DateTimeField.
    */
    function validate_input(type, field){
        request_data = {
            date_format: type,
            string_value: field.value
         }
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.portal_url + "/ajax_validate_date",
            data: request_data,
            success: function(data) {
                if(data.success){
                    return true;
                }else{
                    field.value = '';
                    field.text = '';
                    window.bika.lims.portalMessage(data.message + " for '" + field.name + "' field.")
                }
            }
        });
    };

});
});
