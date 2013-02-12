jQuery( function($) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
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
			fromDate.attr('readonly', false);
			if (!preventFocus) {
				fromDate.focus();
			}
		} else {
			fromDate.datepicker('disable');
			fromDate.attr('readonly', true);
		}
	}	
	
	function evaluateUntilEnabled() {
		if (untilEnabled.is(':checked')) {
			repeatUntil.datepicker('enable');	
			repeatUntil.attr('readonly', false);
			if (!preventFocus) {
				repeatUntil.focus()
			}
		} else {
			repeatUntil.datepicker('disable');
			repeatUntil.attr('readonly', true);
		}
	}	
	
	function evaluateRepeatEnabled() {
		if (repeatEnabled.is(':checked')) {
			repeatunit.attr('readonly', false);
			repeatperiod.attr('disabled', false);
			$('#'+fieldName+"_repeatperiod option:selected").each(function () {
			  repeatperiodselected.val($(this).val())		  
			});
			if (!preventFocus) {
				repeatunit.focus()
			}
		} else {
			repeatunit.attr('readonly', true);
			repeatperiod.attr('disabled', true);
			repeatperiodselected.val("");
		}
	}
	
	
	evaluateFromEnabled();
	evaluateRepeatEnabled();
	evaluateUntilEnabled();
	preventFocus = false;
});
});