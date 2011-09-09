jQuery( function($) {
$(document).ready(function(){

	// return a reference from the Sample popup window back into the widget
	// and populate the form with this sample's data
	$('.select_sample').click(function(){
		item_data = $.parseJSON($('#'+$(this.parentNode).attr("uid")+"_item_data").val());
		column = item_data['column'];
		window.opener.$("#ar_"+column+"_SampleID_button").val(item_data['SampleID']);
		window.opener.$("#ar_"+column+"_SampleID").val(item_data['SampleID']);
		window.opener.$("#deleteSampleButton_" + column).toggle(true);
		window.opener.$("#ar_"+column+"_DateSampled").val(item_data['DateSampled']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_DateSampled").unbind();
		window.opener.$("#ar_"+column+"_ClientReference").val(item_data['ClientReference']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_ClientSampleID").val(item_data['ClientSampleID']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_SampleType").val(item_data['SampleType']).attr('readonly', true);
		window.opener.$("#ar_"+column+"_SamplePoint").val(item_data['SamplePoint']).attr('readonly', true);

		// handle samples that do have field analyses
		// field_analyses is a dict of lists: { catuid: [serviceuid,serviceuid], ... }
		if(item_data['field_analyses'] != null){
			$.each(item_data['field_analyses'], function(catuid,serviceuids){
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
		window.close();
	});


});
});


