(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	// return a reference from the Sample popup window back into the widget
	// and populate the form with this sample's data
	$('.select_sample').click(function(){
		row_data = $.parseJSON($('#'+$(this.parentNode).attr("uid")+"_row_data").val());
		column = row_data['column'];
		window.opener.$("#ar_"+column+"_SampleID_button").val(row_data['SampleID']);
		window.opener.$("#ar_"+column+"_SampleID").val(row_data['SampleID']);
		window.opener.$("#deleteSampleButton_" + column).toggle(true);
		window.opener.$("#ar_"+column+"_SamplingDate")
			.val(row_data['SamplingDate'])
			.removeClass('hasDatepicker')
			.removeData('datepicker')
			.unbind();
		window.opener.$("#ar_"+column+"_ClientReference").val(row_data['ClientReference']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_ClientSampleID").val(row_data['ClientSampleID']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_SampleType").val(row_data['SampleType']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_SamplePoint").val(row_data['SamplePoint']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_SamplingDeviation").val(row_data['SamplingDeviation']).attr('disabled', true);
		window.opener.$("#ar_"+column+"_Composite").val(row_data['Composite']).attr('disabled', true);
		window.opener.$("#ar_"+column+"_AdHoc").val(row_data['AdHoc']).attr('disabled', true);
		window.opener.$("#ar_"+column+"_DefaultContainerType").val('').attr('disabled', true);

		// handle samples that do have field analyses
		// field_analyses is a dict of lists: { catuid: [serviceuid,serviceuid], ... }
		if(row_data['field_analyses'] != null){
			$.each(row_data['field_analyses'], function(catuid,serviceuids){
				window.opener.toggleCat("field", catuid, serviceuids, column, true, true);
			});
		}
		// expand and disable field analyses even if there are no field analyses on this sample
		$.each(window.opener.$("tr[poc='field']").filter(".analysiscategory"), function(){
			window.opener.toggleCat($(this).attr('poc'), this.id, false, column, true, true);
		});

		$.each(window.opener.$('input[id*="_field_"]').filter(".cb"), function(i,e){
			if ($(e).attr('id').indexOf('_'+column+'_') > -1){
				$(e).attr('disabled', true);
			}
		});
		window.opener.recalc_prices();
		window.opener.calculate_parts(column);
		window.close();
	});

	function positionTooltip(event){
		var tPosX = event.pageX+15;
		var tPosY = event.pageY-20;
		$('div.tooltip').css({'font-size':'70%',
		                      'background-color':'#fff',
							  'position': 'absolute',
							  'top': tPosY,
							  'left': tPosX});
	};

	function createTooltip(event, row_data){
		$('<div class="tooltip">' +
			'<table class="analysisrequest listing nosort" cellpadding="0" cellspacing="0">' +
		    '<thead>' +
            '<tr><th>' + _('Analysis Requests') + '</th><td class="left">' + row_data['Requests'] + '</td></tr>' +
            '<tr><th>' + _('Sampling Date') + '</th><td class="left">' + row_data['SamplingDate'] + '</td></tr>' +
            '<tr><th>' + _('Date Received') + '</th><td class="left">' + row_data['DateReceived'] + '</td></tr>' +
			'</thead>' +
			'</table></div>').appendTo('body');
		positionTooltip(event);
	};

	$('.SampleID').mouseover(function(event) {
		row_data = $.parseJSON($('#'+$(this.parentNode).attr("uid")+"_row_data").val());
		createTooltip(event, row_data);
	}).mouseout(function(){
		$(".tooltip").remove();
	});

});
}(jQuery));
