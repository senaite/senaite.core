jQuery( function($) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    _ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
    PMF = jarn.i18n.MessageFactory('plone');
	dateFormat = _('date_format_short_datepicker');
    if (dateFormat == 'date_format_short_datepicker'){
        dateFormat = 'yy-mm-dd';
    }

    $('[datepicker="1"]').datepicker({
        dateFormat: dateFormat,
        changeMonth:true,
        changeYear:true,
        yearRange: "-50:+20"
    });

    $('[datetimepicker="1"]').datetimepicker({
        hourGrid: 4,
        minuteGrid: 10,
        // addSliderAccess: true,
        // sliderAccessArgs: { touchonly: false },
        dateFormat: dateFormat,
        timeFormat: "HH:mm",
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
});
});
