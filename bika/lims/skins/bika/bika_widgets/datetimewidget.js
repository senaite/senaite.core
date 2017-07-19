jQuery( function($) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    _ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
    PMF = jarn.i18n.MessageFactory('plone');
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
        yearRange: "-60:+1"
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
      if(!this.value.includes("-") && !this.value.includes("/")){
        alert("Please enter valid date");
        this.text='';
        this.value='';
      }else{
        var d = $(this).datepicker('getDate');
        if (d && d.getFullYear() < 1901){
          alert("Please choose a valid year...");
          this.text='';
          this.value='';
        }
      }
    });
});
});
