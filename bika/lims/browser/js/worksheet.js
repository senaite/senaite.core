jQuery( function($) {
$(document).ready(function(){

	// add Worksheet Templates dropdown menu
	if($("input[name='add_Worksheet']").length == 1){
		$.ajax({
			url: 'get_worksheet_templates',
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val()},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				html = "&nbsp;&nbsp;From template:&nbsp;<select name='wstemplate'><option value=''>None</option>";
				json = $.parseJSON(data);
				for(i=0; i< data.length; i++){
					html = html + "<option value='"+data[i][0]+"'>"+data[i][1]+"</option>";
				}
				html = html + "</select>";
				$('input[name="add_Worksheet"]').after(html);
			}
		});
	}

});
});
