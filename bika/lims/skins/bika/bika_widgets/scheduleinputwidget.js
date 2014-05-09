jQuery( function($) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    _ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
    PMF = jarn.i18n.MessageFactory('plone');

    fieldName = $('#fieldName').val();
    fromEnabled = $('#'+fieldName+"_fromenabled");
	fromDate = $('#'+fieldName+"_fromdate");
	repeatEnabled = $('#'+fieldName+"_repeatenabled");
	repeatunit = $('#'+fieldName+"_repeatunit");
	repeatperiod = $('#'+fieldName+"_repeatperiod");
	untilEnabled = $('#'+fieldName+"_repeatuntilenabled");
	repeatUntil = $('#'+fieldName+"_repeatuntil");
	repeatperiodselected = $('#'+fieldName+"_repeatperiodselected");
    preventFocus = true;
	dateFormat = _('date_format_short_datepicker');

    fromDate.datepicker({
		dateFormat: dateFormat,
		changeMonth:true,
		changeYear:true,
		yearRange: "-100:+1"
	});

	repeatUntil.datepicker({
		dateFormat: dateFormat,
		changeMonth:true,
		changeYear:true,
		yearRange: "-100:+20"
	});

	fromEnabled.click( function(){
	   evaluateFromEnabled();
	});

	untilEnabled.click( function(){
		evaluateUntilEnabled();
	});

	repeatEnabled.click( function(){
		evaluateRepeatEnabled();
	});

	repeatperiod.change(function () {
	  $('#'+fieldName+"_repeatperiod option:selected").each(function () {
		  repeatperiodselected.val($(this).val())
	  });
	});

	function evaluateFromEnabled() {
		if (fromEnabled.is(':checked')) {
			fromDate.datepicker('enable');
			fromDate.prop('readonly', false);
			if (!preventFocus) {
				fromDate.focus();
			}
		} else {
			fromDate.datepicker('disable');
			fromDate.prop('readonly', true);
		}
	}

	function evaluateUntilEnabled() {
		if (untilEnabled.is(':checked')) {
			repeatUntil.datepicker('enable');
			repeatUntil.prop('readonly', false);
			if (!preventFocus) {
				repeatUntil.focus()
			}
		} else {
			repeatUntil.datepicker('disable');
			repeatUntil.prop('readonly', true);
		}
	}

	function evaluateRepeatEnabled() {
		if (repeatEnabled.is(':checked')) {
			repeatunit.prop('readonly', false);
			repeatperiod.prop('disabled', false);
			$('#'+fieldName+"_repeatperiod option:selected").each(function () {
			  repeatperiodselected.val($(this).val())
			});
			if (!preventFocus) {
				repeatunit.focus()
			}
		} else {
			repeatunit.prop('readonly', true);
			repeatperiod.prop('disabled', true);
			repeatperiodselected.val("");
		}
	}


	evaluateFromEnabled();
	evaluateRepeatEnabled();
	evaluateUntilEnabled();
	preventFocus = false;
});
});
