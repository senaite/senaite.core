jQuery( function($) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');
	dateFormat = _('date_format_short_datepicker');

    $('[datepicker="1"]').datepicker({
        dateFormat: dateFormat,
        changeMonth:true,
        changeYear:true,
        yearRange: "-100:+1"
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
});
});
